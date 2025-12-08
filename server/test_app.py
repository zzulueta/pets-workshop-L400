import unittest
from unittest.mock import patch, MagicMock
import json
from app import app  # Changed from relative import to absolute import

# filepath: server/test_app.py
class TestApp(unittest.TestCase):
    def setUp(self):
        # Create a test client using Flask's test client
        self.app = app.test_client()
        self.app.testing = True
        # Turn off database initialization for tests
        app.config['TESTING'] = True
        
    def _create_mock_dog(self, dog_id, name, breed):
        """Helper method to create a mock dog with standard attributes"""
        dog = MagicMock(spec=['to_dict', 'id', 'name', 'breed'])
        dog.id = dog_id
        dog.name = name
        dog.breed = breed
        dog.to_dict.return_value = {'id': dog_id, 'name': name, 'breed': breed}
        return dog
        
    def _setup_query_mock(self, mock_query, dogs):
        """Helper method to configure the query mock"""
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.all.return_value = dogs
        return mock_query_instance

    @patch('app.db.session.query')
    def test_get_dogs_success(self, mock_query):
        """Test successful retrieval of multiple dogs"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Buddy", "Labrador")
        dog2 = self._create_mock_dog(2, "Max", "German Shepherd")
        mock_dogs = [dog1, dog2]
        
        self._setup_query_mock(mock_query, mock_dogs)
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
        # Verify first dog
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], "Buddy")
        self.assertEqual(data[0]['breed'], "Labrador")
        
        # Verify second dog
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], "Max")
        self.assertEqual(data[1]['breed'], "German Shepherd")
        
        # Verify query was called
        mock_query.assert_called_once()
        
    @patch('app.db.session.query')
    def test_get_dogs_empty(self, mock_query):
        """Test retrieval when no dogs are available"""
        # Arrange
        self._setup_query_mock(mock_query, [])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
        
    @patch('app.db.session.query')
    def test_get_dogs_structure(self, mock_query):
        """Test the response structure for a single dog"""
        # Arrange
        dog = self._create_mock_dog(1, "Buddy", "Labrador")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        data = json.loads(response.data)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertEqual(set(data[0].keys()), {'id', 'name', 'breed'})

    @patch('app.db.session.query')
    def test_get_dogs_single_dog(self, mock_query):
        """Test retrieval with exactly one dog (boundary case)"""
        # Arrange
        dog = self._create_mock_dog(1, "Solo", "Poodle")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], "Solo")
        self.assertEqual(data[0]['breed'], "Poodle")

    @patch('app.db.session.query')
    def test_get_dogs_large_dataset(self, mock_query):
        """Test retrieval with many dogs (edge case: large dataset)"""
        # Arrange
        mock_dogs = [
            self._create_mock_dog(i, f"Dog{i}", f"Breed{i}")
            for i in range(1, 101)
        ]
        self._setup_query_mock(mock_query, mock_dogs)
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 100)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[99]['id'], 100)

    @patch('app.db.session.query')
    def test_get_dogs_special_characters_in_name(self, mock_query):
        """Test dogs with special characters in names (validation)"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Max's Dog", "Labrador")
        dog2 = self._create_mock_dog(2, "Fifi-Lou", "Poodle")
        dog3 = self._create_mock_dog(3, "Dog #1", "Beagle")
        self._setup_query_mock(mock_query, [dog1, dog2, dog3])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], "Max's Dog")
        self.assertEqual(data[1]['name'], "Fifi-Lou")
        self.assertEqual(data[2]['name'], "Dog #1")

    @patch('app.db.session.query')
    def test_get_dogs_unicode_names(self, mock_query):
        """Test dogs with unicode characters in names (edge case)"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Fröhlich", "German Shepherd")
        dog2 = self._create_mock_dog(2, "Señor", "Chihuahua")
        dog3 = self._create_mock_dog(3, "小狗", "Shiba Inu")
        self._setup_query_mock(mock_query, [dog1, dog2, dog3])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], "Fröhlich")
        self.assertEqual(data[1]['name'], "Señor")
        self.assertEqual(data[2]['name'], "小狗")

    @patch('app.db.session.query')
    def test_get_dogs_long_names(self, mock_query):
        """Test dogs with very long names (boundary test)"""
        # Arrange
        long_name = "A" * 100
        long_breed = "B" * 100
        dog = self._create_mock_dog(1, long_name, long_breed)
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], long_name)
        self.assertEqual(data[0]['breed'], long_breed)

    @patch('app.db.session.query')
    def test_get_dogs_empty_string_names(self, mock_query):
        """Test dogs with empty string names (edge case)"""
        # Arrange
        dog = self._create_mock_dog(1, "", "")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "")
        self.assertEqual(data[0]['breed'], "")

    @patch('app.db.session.query')
    def test_get_dogs_mixed_case_names(self, mock_query):
        """Test dogs with mixed case names (constraint validation)"""
        # Arrange
        dog1 = self._create_mock_dog(1, "ALLCAPS", "GERMAN SHEPHERD")
        dog2 = self._create_mock_dog(2, "lowercase", "poodle")
        dog3 = self._create_mock_dog(3, "MixedCase", "Golden Retriever")
        self._setup_query_mock(mock_query, [dog1, dog2, dog3])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], "ALLCAPS")
        self.assertEqual(data[1]['name'], "lowercase")
        self.assertEqual(data[2]['name'], "MixedCase")

    @patch('app.db.session.query')
    def test_get_dogs_whitespace_names(self, mock_query):
        """Test dogs with whitespace in names (edge case)"""
        # Arrange
        dog1 = self._create_mock_dog(1, "  Leading", "Breed1")
        dog2 = self._create_mock_dog(2, "Trailing  ", "Breed2")
        dog3 = self._create_mock_dog(3, "Mid  dle", "Breed3")
        self._setup_query_mock(mock_query, [dog1, dog2, dog3])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], "  Leading")
        self.assertEqual(data[1]['name'], "Trailing  ")
        self.assertEqual(data[2]['name'], "Mid  dle")

    @patch('app.db.session.query')
    def test_get_dogs_numeric_ids(self, mock_query):
        """Test dogs with various numeric IDs (boundary test)"""
        # Arrange
        dog1 = self._create_mock_dog(0, "Zero", "Breed1")
        dog2 = self._create_mock_dog(1, "One", "Breed2")
        dog3 = self._create_mock_dog(999999, "Max", "Breed3")
        self._setup_query_mock(mock_query, [dog1, dog2, dog3])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['id'], 0)
        self.assertEqual(data[1]['id'], 1)
        self.assertEqual(data[2]['id'], 999999)

    @patch('app.db.session.query')
    def test_get_dogs_negative_ids(self, mock_query):
        """Test dogs with negative IDs (edge case: unusual data)"""
        # Arrange
        dog = self._create_mock_dog(-1, "Negative", "Breed")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], -1)

    @patch('app.db.session.query')
    def test_get_dogs_content_type(self, mock_query):
        """Test that response has correct JSON content type (constraint)"""
        # Arrange
        dog = self._create_mock_dog(1, "Buddy", "Labrador")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

    @patch('app.db.session.query')
    def test_get_dogs_json_parseable(self, mock_query):
        """Test that response is valid JSON (constraint validation)"""
        # Arrange
        dog = self._create_mock_dog(1, "Buddy", "Labrador")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        try:
            data = json.loads(response.data)
            self.assertIsInstance(data, list)
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")

    @patch('app.db.session.query')
    def test_get_dogs_field_types(self, mock_query):
        """Test that all fields have correct types (constraint validation)"""
        # Arrange
        dog = self._create_mock_dog(1, "Buddy", "Labrador")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertIsInstance(data[0]['id'], int)
        self.assertIsInstance(data[0]['name'], str)
        self.assertIsInstance(data[0]['breed'], str)

    @patch('app.db.session.query')
    def test_get_dogs_duplicate_ids(self, mock_query):
        """Test handling of duplicate IDs (edge case: data integrity)"""
        # Arrange
        dog1 = self._create_mock_dog(1, "First", "Breed1")
        dog2 = self._create_mock_dog(1, "Second", "Breed2")
        self._setup_query_mock(mock_query, [dog1, dog2])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[1]['id'], 1)

    @patch('app.db.session.query')
    def test_get_dogs_query_called_correctly(self, mock_query):
        """Test that database query is constructed correctly (test)"""
        # Arrange
        dog = self._create_mock_dog(1, "Buddy", "Labrador")
        mock_query_instance = self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        mock_query.assert_called_once()
        mock_query_instance.join.assert_called_once()
        mock_query_instance.all.assert_called_once()

    @patch('app.db.session.query')
    def test_get_dogs_http_method(self, mock_query):
        """Test that only GET method is accepted (constraint validation)"""
        # Arrange
        dog = self._create_mock_dog(1, "Buddy", "Labrador")
        self._setup_query_mock(mock_query, [dog])
        
        # Act - Test GET (should work)
        response_get = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response_get.status_code, 200)
        
        # Act - Test POST (should fail)
        response_post = self.app.post('/api/dogs')
        self.assertEqual(response_post.status_code, 405)
        
        # Act - Test PUT (should fail)
        response_put = self.app.put('/api/dogs')
        self.assertEqual(response_put.status_code, 405)
        
        # Act - Test DELETE (should fail)
        response_delete = self.app.delete('/api/dogs')
        self.assertEqual(response_delete.status_code, 405)

    # Tests for /api/dogs/<int:id> endpoint (get_dog function)
    
    @patch('app.db.session.query')
    def test_get_dog_success(self, mock_query):
        """Test successful retrieval of a specific dog by ID"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 1
        mock_dog.name = "Buddy"
        mock_dog.breed = "Labrador"
        mock_dog.age = 3
        mock_dog.description = "A friendly dog"
        mock_dog.gender = "Male"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/1')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], "Buddy")
        self.assertEqual(data['breed'], "Labrador")
        self.assertEqual(data['age'], 3)
        self.assertEqual(data['description'], "A friendly dog")
        self.assertEqual(data['gender'], "Male")
        self.assertEqual(data['status'], "AVAILABLE")

    @patch('app.db.session.query')
    def test_get_dog_not_found(self, mock_query):
        """Test retrieval of non-existent dog returns 404"""
        # Arrange
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = None
        
        # Act
        response = self.app.get('/api/dogs/999')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Dog not found")

    @patch('app.db.session.query')
    def test_get_dog_response_structure(self, mock_query):
        """Test that response contains all required fields"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 5
        mock_dog.name = "Rex"
        mock_dog.breed = "Beagle"
        mock_dog.age = 2
        mock_dog.description = "Loves to play"
        mock_dog.gender = "Male"
        mock_dog.status = AdoptionStatus.PENDING
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/5')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        required_fields = {
            'id', 'name', 'breed', 'age', 'description', 'gender', 'status'
        }
        self.assertEqual(set(data.keys()), required_fields)

    @patch('app.db.session.query')
    def test_get_dog_adopted_status(self, mock_query):
        """Test retrieval of dog with ADOPTED status"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 10
        mock_dog.name = "Charlie"
        mock_dog.breed = "Poodle"
        mock_dog.age = 5
        mock_dog.description = "Happy adopted dog"
        mock_dog.gender = "Female"
        mock_dog.status = AdoptionStatus.ADOPTED
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/10')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], "ADOPTED")

    @patch('app.db.session.query')
    def test_get_dog_zero_id(self, mock_query):
        """Test retrieval with ID 0 (boundary case)"""
        # Arrange
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = None
        
        # Act
        response = self.app.get('/api/dogs/0')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Dog not found")

    @patch('app.db.session.query')
    def test_get_dog_negative_id(self, mock_query):
        """Test retrieval with negative ID (edge case)"""
        # Arrange - Flask won't match negative IDs to <int:id> route
        # Act
        response = self.app.get('/api/dogs/-1')
        
        # Assert - Should return 404 (route not found)
        self.assertEqual(response.status_code, 404)

    @patch('app.db.session.query')
    def test_get_dog_very_large_id(self, mock_query):
        """Test retrieval with very large ID (boundary case)"""
        # Arrange
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = None
        
        # Act
        response = self.app.get('/api/dogs/999999999')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Dog not found")

    @patch('app.db.session.query')
    def test_get_dog_special_characters_in_fields(self, mock_query):
        """Test dog with special characters in name and description"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 15
        mock_dog.name = "Max's Best Friend"
        mock_dog.breed = "Mixed-Breed"
        mock_dog.age = 4
        mock_dog.description = (
            "A dog with 'special' & unique <characteristics>!"
        )
        mock_dog.gender = "Male"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/15')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], "Max's Best Friend")
        self.assertEqual(
            data['description'],
            "A dog with 'special' & unique <characteristics>!"
        )

    @patch('app.db.session.query')
    def test_get_dog_unicode_characters(self, mock_query):
        """Test dog with unicode characters in fields"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 20
        mock_dog.name = "Fröhlich"
        mock_dog.breed = "German Shëpherd"
        mock_dog.age = 6
        mock_dog.description = "Ein schöner Hund 🐕"
        mock_dog.gender = "Female"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/20')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], "Fröhlich")
        self.assertEqual(data['breed'], "German Shëpherd")
        self.assertEqual(data['description'], "Ein schöner Hund 🐕")

    @patch('app.db.session.query')
    def test_get_dog_age_zero(self, mock_query):
        """Test dog with age 0 (boundary case - puppy)"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 25
        mock_dog.name = "Tiny Puppy"
        mock_dog.breed = "Chihuahua"
        mock_dog.age = 0
        mock_dog.description = "Very young puppy"
        mock_dog.gender = "Unknown"
        mock_dog.status = AdoptionStatus.PENDING
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/25')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['age'], 0)
        self.assertEqual(data['gender'], "Unknown")

    @patch('app.db.session.query')
    def test_get_dog_very_old_age(self, mock_query):
        """Test dog with very old age (boundary case)"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 30
        mock_dog.name = "Old Timer"
        mock_dog.breed = "Golden Retriever"
        mock_dog.age = 20
        mock_dog.description = "Senior dog needing care"
        mock_dog.gender = "Male"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/30')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['age'], 20)

    @patch('app.db.session.query')
    def test_get_dog_content_type(self, mock_query):
        """Test that response has correct content type"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 35
        mock_dog.name = "Test Dog"
        mock_dog.breed = "Test Breed"
        mock_dog.age = 5
        mock_dog.description = "Test description"
        mock_dog.gender = "Male"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/35')
        
        # Assert
        self.assertEqual(response.content_type, 'application/json')

    @patch('app.db.session.query')
    def test_get_dog_http_method_constraints(self, mock_query):
        """Test that only GET method is accepted for single dog endpoint"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 40
        mock_dog.name = "Method Test"
        mock_dog.breed = "Test Breed"
        mock_dog.age = 3
        mock_dog.description = "Testing HTTP methods"
        mock_dog.gender = "Female"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act & Assert - GET should work
        response_get = self.app.get('/api/dogs/40')
        self.assertEqual(response_get.status_code, 200)
        
        # Act & Assert - POST should fail
        response_post = self.app.post('/api/dogs/40')
        self.assertEqual(response_post.status_code, 405)
        
        # Act & Assert - PUT should fail
        response_put = self.app.put('/api/dogs/40')
        self.assertEqual(response_put.status_code, 405)
        
        # Act & Assert - DELETE should fail
        response_delete = self.app.delete('/api/dogs/40')
        self.assertEqual(response_delete.status_code, 405)

    @patch('app.db.session.query')
    def test_get_dog_invalid_id_type(self, mock_query):
        """Test with invalid ID type (string instead of int)"""
        # Act - Flask won't match non-integer to <int:id>
        response = self.app.get('/api/dogs/invalid')
        
        # Assert - Should return 404 (route not found)
        self.assertEqual(response.status_code, 404)

    @patch('app.db.session.query')
    def test_get_dog_field_types(self, mock_query):
        """Test that response fields have correct data types"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 45
        mock_dog.name = "Type Test"
        mock_dog.breed = "Test Breed"
        mock_dog.age = 7
        mock_dog.description = "Testing data types"
        mock_dog.gender = "Male"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/45')
        
        # Assert
        data = json.loads(response.data)
        self.assertIsInstance(data['id'], int)
        self.assertIsInstance(data['name'], str)
        self.assertIsInstance(data['breed'], str)
        self.assertIsInstance(data['age'], int)
        self.assertIsInstance(data['description'], str)
        self.assertIsInstance(data['gender'], str)
        self.assertIsInstance(data['status'], str)

    @patch('app.db.session.query')
    def test_get_dog_female_gender(self, mock_query):
        """Test dog with Female gender"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 50
        mock_dog.name = "Lady"
        mock_dog.breed = "Collie"
        mock_dog.age = 4
        mock_dog.description = "Beautiful female dog"
        mock_dog.gender = "Female"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/50')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['gender'], "Female")

    @patch('app.db.session.query')
    def test_get_dog_long_description(self, mock_query):
        """Test dog with very long description (boundary case)"""
        # Arrange
        from models.dog import AdoptionStatus
        long_description = "A" * 1000
        mock_dog = MagicMock()
        mock_dog.id = 55
        mock_dog.name = "Verbose"
        mock_dog.breed = "Husky"
        mock_dog.age = 3
        mock_dog.description = long_description
        mock_dog.gender = "Male"
        mock_dog.status = AdoptionStatus.PENDING
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/55')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['description'], long_description)
        self.assertEqual(len(data['description']), 1000)

    @patch('app.db.session.query')
    def test_get_dog_query_execution(self, mock_query):
        """Test that database query is executed correctly"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 60
        mock_dog.name = "Query Test"
        mock_dog.breed = "Bulldog"
        mock_dog.age = 5
        mock_dog.description = "Testing query execution"
        mock_dog.gender = "Male"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/60')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        mock_query.assert_called_once()
        mock_query_instance.join.assert_called_once()
        mock_query_instance.filter.assert_called_once()
        mock_query_instance.first.assert_called_once()

    @patch('app.db.session.query')
    def test_get_dog_pending_status(self, mock_query):
        """Test dog with PENDING adoption status"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 65
        mock_dog.name = "Pending Pup"
        mock_dog.breed = "Dachshund"
        mock_dog.age = 2
        mock_dog.description = "Adoption pending"
        mock_dog.gender = "Female"
        mock_dog.status = AdoptionStatus.PENDING
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/65')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], "PENDING")

    @patch('app.db.session.query')
    def test_get_dog_json_serialization(self, mock_query):
        """Test that response is properly JSON serialized"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog = MagicMock()
        mock_dog.id = 70
        mock_dog.name = "JSON Dog"
        mock_dog.breed = "Pug"
        mock_dog.age = 4
        mock_dog.description = "Testing JSON"
        mock_dog.gender = "Male"
        mock_dog.status = AdoptionStatus.AVAILABLE
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/70')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        # Should be able to parse JSON without error
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)

    @patch('app.db.session.query')
    def test_get_dog_human_age_young_dog(self, mock_query):
        """Test human age calculation for dog 1 year old (boundary)"""
        # Arrange
        mock_dog = MagicMock()
        mock_dog.id = 1
        mock_dog.name = "Puppy"
        mock_dog.age = 1
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/1/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['dog_name'], "Puppy")
        self.assertEqual(data['dog_age'], 1)
        self.assertEqual(data['human_age'], 10.5)
        
    @patch('app.db.session.query')
    def test_get_dog_human_age_older_dog(self, mock_query):
        """Test human age calculation for dog older than 2 years"""
        # Arrange
        mock_dog = MagicMock()
        mock_dog.id = 2
        mock_dog.name = "Senior"
        mock_dog.age = 5
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/2/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['dog_name'], "Senior")
        self.assertEqual(data['dog_age'], 5)
        self.assertEqual(data['human_age'], 33.0)  # (2 * 10.5) + ((5 - 2) * 4)
        
    @patch('app.db.session.query')
    def test_get_dog_human_age_exactly_two_years(self, mock_query):
        """Test human age calculation for dog exactly 2 years (boundary)"""
        # Arrange
        mock_dog = MagicMock()
        mock_dog.id = 3
        mock_dog.name = "Toddler"
        mock_dog.age = 2
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/3/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['dog_name'], "Toddler")
        self.assertEqual(data['dog_age'], 2)
        self.assertEqual(data['human_age'], 21.0)  # 2 * 10.5
        
    @patch('app.db.session.query')
    def test_get_dog_human_age_three_years(self, mock_query):
        """Test human age calculation for dog just over boundary (3 years)"""
        # Arrange
        mock_dog = MagicMock()
        mock_dog.id = 4
        mock_dog.name = "Young Adult"
        mock_dog.age = 3
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/4/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['dog_name'], "Young Adult")
        self.assertEqual(data['dog_age'], 3)
        self.assertEqual(data['human_age'], 25.0)  # (2 * 10.5) + ((3 - 2) * 4)
        
    @patch('app.db.session.query')
    def test_get_dog_human_age_zero_years(self, mock_query):
        """Test human age calculation for newborn dog (edge case: 0 years)"""
        # Arrange
        mock_dog = MagicMock()
        mock_dog.id = 5
        mock_dog.name = "Newborn"
        mock_dog.age = 0
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/5/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['dog_name'], "Newborn")
        self.assertEqual(data['dog_age'], 0)
        self.assertEqual(data['human_age'], 0.0)
        
    @patch('app.db.session.query')
    def test_get_dog_human_age_very_old_dog(self, mock_query):
        """Test human age calculation for very old dog (edge case: 20 years)"""
        # Arrange
        mock_dog = MagicMock()
        mock_dog.id = 6
        mock_dog.name = "Ancient"
        mock_dog.age = 20
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/6/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['dog_name'], "Ancient")
        self.assertEqual(data['dog_age'], 20)
        self.assertEqual(data['human_age'], 93.0)  # (2 * 10.5) + ((20 - 2) * 4)
        
    @patch('app.db.session.query')
    def test_get_dog_human_age_not_found(self, mock_query):
        """Test 404 error when dog is not found (constraint validation)"""
        # Arrange
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = None
        
        # Act
        response = self.app.get('/api/dogs/999/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Dog not found")
        
    @patch('app.db.session.query')
    def test_get_dog_human_age_zero_id(self, mock_query):
        """Test behavior with zero dog ID (edge case: minimum valid ID)"""
        # Arrange
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = None
        
        # Act
        response = self.app.get('/api/dogs/0/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Dog not found")
        
    @patch('app.db.session.query')
    def test_get_dog_human_age_response_structure(self, mock_query):
        """Test response structure has correct keys and types (constraint)"""
        # Arrange
        mock_dog = MagicMock()
        mock_dog.id = 1
        mock_dog.name = "Buddy"
        mock_dog.age = 3
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/1/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(set(data.keys()), {'dog_name', 'dog_age', 'human_age'})
        self.assertIsInstance(data['dog_name'], str)
        self.assertIsInstance(data['dog_age'], int)
        self.assertIsInstance(data['human_age'], float)
        
    @patch('app.db.session.query')
    def test_get_dog_human_age_large_id(self, mock_query):
        """Test with very large dog ID (edge case: boundary test)"""
        # Arrange
        mock_dog = MagicMock()
        mock_dog.id = 999999
        mock_dog.name = "Max ID"
        mock_dog.age = 5
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
        mock_query_instance.first.return_value = mock_dog
        
        # Act
        response = self.app.get('/api/dogs/999999/human-age')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['dog_name'], "Max ID")
        self.assertEqual(data['dog_age'], 5)
        self.assertEqual(data['human_age'], 33.0)


if __name__ == '__main__':
    unittest.main()