import os
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, Response, request
from models import init_db, db, Dog, Breed
from models.dog import AdoptionStatus

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "dogshelter.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
init_db(app)

@app.route('/api/dogs', methods=['GET'])
def get_dogs() -> Response:
    """
    Get filtered list of dogs based on query parameters.
    
    Query parameters:
    - search: str - search in dog name or breed
    - breed: str - comma-separated list of breed names
    - age_min: int - minimum age
    - age_max: int - maximum age
    - gender: str - Male, Female, or Unknown
    - status: str - AVAILABLE, PENDING, or ADOPTED
    """
    # Start with base query
    query = db.session.query(
        Dog.id, 
        Dog.name, 
        Breed.name.label('breed'),
        Dog.age,
        Dog.gender,
        Dog.status
    ).join(Breed, Dog.breed_id == Breed.id)
    
    # Apply search filter
    search_term = request.args.get('search', '').strip()
    if search_term:
        search_filter = f"%{search_term}%"
        query = query.filter(
            db.or_(
                Dog.name.ilike(search_filter),
                Breed.name.ilike(search_filter)
            )
        )
    
    # Apply breed filter
    breed_param = request.args.get('breed', '').strip()
    if breed_param:
        breed_names = [b.strip() for b in breed_param.split(',') if b.strip()]
        if breed_names:
            query = query.filter(Breed.name.in_(breed_names))
    
    # Apply age range filter
    age_min = request.args.get('age_min', type=int)
    age_max = request.args.get('age_max', type=int)
    if age_min is not None:
        query = query.filter(Dog.age >= age_min)
    if age_max is not None:
        query = query.filter(Dog.age <= age_max)
    
    # Apply gender filter
    gender = request.args.get('gender', '').strip()
    if gender and gender != 'Any':
        query = query.filter(Dog.gender == gender)
    
    # Apply status filter (default to AVAILABLE)
    status_param = request.args.get('status', 'AVAILABLE').strip().upper()
    if status_param and status_param != 'ALL':
        try:
            status_enum = AdoptionStatus[status_param]
            query = query.filter(Dog.status == status_enum)
        except KeyError:
            pass  # Invalid status, ignore filter
    
    # Execute query
    dogs_query = query.all()
    
    # Convert the result to a list of dictionaries
    dogs_list: List[Dict[str, Any]] = [
        {
            'id': dog.id,
            'name': dog.name,
            'breed': dog.breed,
            'age': dog.age,
            'gender': dog.gender,
            'status': dog.status.name
        }
        for dog in dogs_query
    ]
    
    return jsonify({
        'dogs': dogs_list,
        'total': len(dogs_list)
    })

@app.route('/api/dogs/<int:id>', methods=['GET'])
def get_dog(id: int) -> tuple[Response, int] | Response:
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

@app.route('/api/breeds', methods=['GET'])
def get_breeds() -> Response:
    """Get all available breeds."""
    breeds = db.session.query(Breed.name).order_by(Breed.name).all()
    breed_list = [breed.name for breed in breeds]
    return jsonify(breed_list)

## HERE

if __name__ == '__main__':
    app.run(debug=True, port=5100) # Port 5100 to avoid macOS conflicts