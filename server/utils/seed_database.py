# Standard library imports for file operations, system path manipulation, and data structures
import csv
import os
import sys
import random
from datetime import datetime, timedelta
from collections import defaultdict

# Add the parent directory to sys.path to allow importing from models
# This is necessary because we're in the utils/ subdirectory and need to access the models/ directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Flask and database imports
from flask import Flask
from models import init_db, db, Breed, Dog
from models.dog import AdoptionStatus

def create_app():
    """Create and configure Flask app for database operations.
    
    This function sets up a minimal Flask application context needed for
    SQLAlchemy database operations during the seeding process.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Get the server directory path (one level up from utils)
    # This ensures the database file is created in the server/ directory
    server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Configure SQLite database connection
    # Using SQLite for simplicity - database file will be 'dogshelter.db' in server/
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(server_dir, "dogshelter.db")}'
    # Disable modification tracking to reduce overhead (not needed for seeding)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app context
    # This sets up SQLAlchemy to work with our Flask app
    init_db(app)
    
    return app

def create_breeds():
    """Seed the database with breeds from the CSV file.
    
    This function reads breed data from breeds.csv and populates the Breed table.
    It includes a check to prevent duplicate seeding if breeds already exist.
    """
    # Create Flask app instance to establish database connection
    app = create_app()
    
    # Construct the path to breeds.csv in the models/ directory
    # Navigate up two levels from utils/ to server/, then into models/
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'models', 'breeds.csv')
    
    # Use Flask's app context to enable database operations
    with app.app_context():
        # Check if breeds already exist to avoid duplicate seeding
        # This is idempotent - safe to run multiple times
        existing_breeds = Breed.query.count()
        if existing_breeds > 0:
            print(f"Database already contains {existing_breeds} breeds. Skipping seed.")
            return
        
        # Read the CSV file and add breeds to the database
        with open(csv_path, 'r') as file:
            # DictReader treats first row as headers, returns each row as a dictionary
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Create a new Breed object from CSV data
                # CSV columns: 'Breed' and 'Description'
                breed = Breed(name=row['Breed'], description=row['Description'])
                # Add to session (queued for insertion)
                db.session.add(breed)
            
            # Commit all breed insertions to the database in a single transaction
            # This is more efficient than committing after each breed
            db.session.commit()
            
        # Verify the seeding was successful by counting total breeds
        breed_count = Breed.query.count()
        print(f"Successfully seeded {breed_count} breeds to the database.")

def create_dogs():
    """Seed the database with dogs from the CSV file, ensuring at least 3 dogs per breed.
    
    This function implements a two-pass algorithm:
    1. First pass: Ensures each breed gets at least 3 dogs
    2. Second pass: Randomly distributes remaining dogs across all breeds
    
    This approach guarantees diverse representation for each breed while maintaining
    randomness for the remaining assignments.
    """
    # Create Flask app instance to establish database connection
    app = create_app()
    
    # Construct the path to dogs.csv in the models/ directory
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'models', 'dogs.csv')
    
    # Use Flask's app context to enable database operations
    with app.app_context():
        # Check if dogs already exist to avoid duplicate seeding
        # This is idempotent - safe to run multiple times
        existing_dogs = Dog.query.count()
        if existing_dogs > 0:
            print(f"Database already contains {existing_dogs} dogs. Skipping seed.")
            return
        
        # Get all breeds from the database (must be seeded first)
        breeds = Breed.query.all()
        if not breeds:
            print("No breeds found in database. Please seed breeds first.")
            return
        
        # Track how many dogs are assigned to each breed for reporting
        # defaultdict(int) automatically initializes missing keys to 0
        breed_counts = defaultdict(int)
        
        # Read the CSV file
        dogs_data = []
        with open(csv_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                dogs_data.append(row)
        
        def create_dog(dog_info, breed_id):
            """Helper function to create a dog with consistent attributes"""
            dog = Dog(
                name=dog_info['Name'],
                description=dog_info['Description'],
                breed_id=breed_id,
                age=int(dog_info['Age']),
                gender=dog_info['Gender'],
                status=random.choice(list(AdoptionStatus)),
                intake_date=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            db.session.add(dog)
            breed_counts[breed_id] += 1
            return dog
        
        # FIRST PASS: Assign at least 3 dogs to each breed
        # This ensures every breed has adequate representation in the database
        for breed in breeds:
            # Attempt to assign 3 dogs to this breed
            for _ in range(3):
                # Safety check: stop if we've run out of dogs in the CSV
                if not dogs_data:
                    break
                
                # Select a random dog from the remaining unassigned dogs
                dog_info = random.choice(dogs_data)
                # Remove from the pool so it won't be assigned twice
                dogs_data.remove(dog_info)
                
                # Create the dog and assign it to this breed
                create_dog(dog_info, breed.id)
        
        # SECOND PASS: Assign remaining dogs randomly across all breeds
        # This distributes any leftover dogs without preference
        for dog_info in dogs_data:
            # Pick a random breed for this dog
            breed = random.choice(breeds)
            # Create the dog and assign it to the chosen breed
            create_dog(dog_info, breed.id)
        
        # Commit all the changes
        db.session.commit()
        
        # Verify the seeding
        dog_count = Dog.query.count()
        print(f"Successfully seeded {dog_count} dogs to the database.")
        
        # Print distribution of dogs across breeds
        for breed in breeds:
            count = breed_counts[breed.id]
            print(f"Breed '{breed.name}': {count} dogs")

def seed_database():
    """Run all seeding functions in the correct order.
    
    ORDER MATTERS: Breeds must be seeded before dogs because dogs have
    a foreign key relationship to breeds (each dog must belong to a breed).
    """
    # Step 1: Seed breeds first (dogs depend on breeds existing)
    create_breeds()
    # Step 2: Seed dogs (will reference the breeds created above)
    create_dogs()

# Entry point when script is run directly (not imported)
if __name__ == '__main__':
    seed_database()