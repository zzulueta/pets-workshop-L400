import os
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, Response
from models import init_db, db, Dog, Breed

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "dogshelter.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
init_db(app)

@app.route('/api/dogs', methods=['GET'])
def get_dogs() -> Response:
    query = db.session.query(
        Dog.id, 
        Dog.name, 
        Breed.name.label('breed')
    ).join(Breed, Dog.breed_id == Breed.id)
    
    dogs_query = query.all()
    
    # Convert the result to a list of dictionaries
    dogs_list: List[Dict[str, Any]] = [
        {
            'id': dog.id,
            'name': dog.name,
            'breed': dog.breed
        }
        for dog in dogs_query
    ]
    
    return jsonify(dogs_list)

@app.route('/api/dogs/<int:id>', methods=['GET'])
def get_dog(id: int) -> tuple[Response, int] | Response:
    """
    Retrieve a specific dog by ID from the database.
    This function queries the database for a dog with the given ID, joining with the
    Breed table to include the breed name. If found, returns the dog's details as JSON.
    Args:
        id (int): The unique identifier of the dog to retrieve.
    Returns:
        tuple[Response, int] | Response: A tuple containing a JSON response with error 
            message and 404 status code if the dog is not found, or a JSON response 
            containing the dog's details (id, name, breed, age, description, gender, 
            and status) if found.
    Raises:
        None: Errors are handled by returning appropriate HTTP responses.
    """
    # Query the specific dog by ID and join with breed to get breed name
    dog_query = db.session.query(
        Dog.id,
        Dog.name,
        Breed.name.label('breed'),
        Dog.age,
        Dog.description,
        Dog.gender,
        Dog.status
    ).join(Breed, Dog.breed_id == Breed.id).filter(Dog.id == id).first()
    
    # Return 404 if dog not found
    if not dog_query:
        return jsonify({"error": "Dog not found"}), 404
    
    # Convert the result to a dictionary
    dog: Dict[str, Any] = {
        'id': dog_query.id,
        'name': dog_query.name,
        'breed': dog_query.breed,
        'age': dog_query.age,
        'description': dog_query.description,
        'gender': dog_query.gender,
        'status': dog_query.status.name
    }
    
    return jsonify(dog)


@app.route('/api/dogs/<int:id>/human-age', methods=['GET'])
def get_dog_human_age(id: int) -> tuple[Response, int] | Response:
    """
    Calculate and return a dog's age in human years.
    
    Uses the formula:
    - First 2 years: 10.5 human years each
    - Years after 2: 4 human years each
    
    Args:
        id: The unique identifier of the dog
        
    Returns:
        JSON response with dog_name, dog_age, and human_age, or 404 error
    """
    # Query the specific dog by ID
    dog_query = db.session.query(
        Dog.id,
        Dog.name,
        Dog.age
    ).filter(Dog.id == id).first()
    
    # Return 404 if dog not found
    if not dog_query:
        return jsonify({"error": "Dog not found"}), 404
    
    # Calculate human age using the formula
    dog_age: int = dog_query.age
    if dog_age <= 2:
        human_age: float = dog_age * 10.5
    else:
        human_age: float = (2 * 10.5) + ((dog_age - 2) * 4)
    
    # Prepare response
    response: Dict[str, Any] = {
        'dog_name': dog_query.name,
        'dog_age': dog_age,
        'human_age': human_age
    }
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=5100)  # Port 5100 to avoid macOS conflicts
