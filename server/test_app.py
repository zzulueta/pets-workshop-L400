import unittest
from unittest.mock import patch, MagicMock
import json
from app import app
from models.dog import AdoptionStatus

# filepath: server/test_app.py
class TestApp(unittest.TestCase):
    def setUp(self):
        # Create a test client using Flask's test client
        self.app = app.test_client()
        self.app.testing = True
        # Turn off database initialization for tests
        app.config['TESTING'] = True
        
    def _create_mock_dog(self, dog_id, name, breed, age=5, gender='Male', status=AdoptionStatus.AVAILABLE):
        """Helper method to create a mock dog with standard attributes"""
        dog = MagicMock()
        dog.id = dog_id
        dog.name = name
        dog.breed = breed
        dog.age = age
        dog.gender = gender
        dog.status = status
        return dog
        
    def _setup_query_mock(self, mock_query, dogs):
        """Helper method to configure the query mock"""
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.filter.return_value = mock_query_instance
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
        self.assertIn('dogs', data)
        self.assertIn('total', data)
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['dogs']), 2)
        
        # Verify first dog
        self.assertEqual(data['dogs'][0]['id'], 1)
        self.assertEqual(data['dogs'][0]['name'], "Buddy")
        self.assertEqual(data['dogs'][0]['breed'], "Labrador")
        
        # Verify second dog
        self.assertEqual(data['dogs'][1]['id'], 2)
        self.assertEqual(data['dogs'][1]['name'], "Max")
        self.assertEqual(data['dogs'][1]['breed'], "German Shepherd")
        
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
        self.assertEqual(data['dogs'], [])
        self.assertEqual(data['total'], 0)
        
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
        self.assertIn('dogs', data)
        self.assertIn('total', data)
        self.assertTrue(isinstance(data['dogs'], list))
        self.assertEqual(len(data['dogs']), 1)
        self.assertEqual(set(data['dogs'][0].keys()), {'id', 'name', 'breed', 'age', 'gender', 'status'})

    @patch('app.db.session.query')
    def test_get_dogs_with_search(self, mock_query):
        """Test search filter by name"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Buddy", "Labrador")
        self._setup_query_mock(mock_query, [dog1])
        
        # Act
        response = self.app.get('/api/dogs?search=Buddy')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['dogs'][0]['name'], "Buddy")

    @patch('app.db.session.query')
    def test_get_dogs_with_breed_filter(self, mock_query):
        """Test breed filter"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Buddy", "Labrador")
        self._setup_query_mock(mock_query, [dog1])
        
        # Act
        response = self.app.get('/api/dogs?breed=Labrador')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['dogs'][0]['breed'], "Labrador")

    @patch('app.db.session.query')
    def test_get_dogs_with_age_filter(self, mock_query):
        """Test age range filter"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Puppy", "Labrador", age=1)
        self._setup_query_mock(mock_query, [dog1])
        
        # Act
        response = self.app.get('/api/dogs?age_min=0&age_max=2')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['dogs'][0]['age'], 1)

    @patch('app.db.session.query')
    def test_get_dogs_with_gender_filter(self, mock_query):
        """Test gender filter"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Bella", "Poodle", gender='Female')
        self._setup_query_mock(mock_query, [dog1])
        
        # Act
        response = self.app.get('/api/dogs?gender=Female')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['dogs'][0]['gender'], "Female")

    @patch('app.db.session.query')
    def test_get_dogs_with_status_filter(self, mock_query):
        """Test status filter"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Max", "Beagle", status=AdoptionStatus.PENDING)
        self._setup_query_mock(mock_query, [dog1])
        
        # Act
        response = self.app.get('/api/dogs?status=PENDING')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['dogs'][0]['status'], 'PENDING')

    @patch('app.db.session.query')
    def test_get_dogs_with_multiple_filters(self, mock_query):
        """Test multiple filters combined"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Buddy", "Labrador", age=3, gender='Male')
        self._setup_query_mock(mock_query, [dog1])
        
        # Act
        response = self.app.get('/api/dogs?breed=Labrador&age_min=2&age_max=5&gender=Male')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['dogs'][0]['name'], "Buddy")

    @patch('app.db.session.query')
    def test_get_breeds(self, mock_query):
        """Test breeds endpoint"""
        # Arrange
        breed1 = MagicMock()
        breed1.name = "Labrador"
        breed2 = MagicMock()
        breed2.name = "German Shepherd"
        
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.order_by.return_value = mock_query_instance
        mock_query_instance.all.return_value = [breed1, breed2]
        
        # Act
        response = self.app.get('/api/breeds')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertIn("Labrador", data)
        self.assertIn("German Shepherd", data)


if __name__ == '__main__':
    unittest.main()