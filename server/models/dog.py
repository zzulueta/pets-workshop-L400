from datetime import datetime
from enum import Enum
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

# Define an Enum for dog status
class AdoptionStatus(Enum):
    AVAILABLE = 'Available'
    ADOPTED = 'Adopted'
    PENDING = 'Pending'

class Dog(BaseModel):
    """Model representing a dog in the shelter.
    
    Attributes:
        id: Unique identifier for the dog.
        name: Name of the dog.
        breed_id: Foreign key to the breed table.
        age: Age of the dog in years.
        gender: Gender of the dog (Male, Female, or Unknown).
        description: Detailed description of the dog.
        status: Current adoption status of the dog.
        intake_date: Date when the dog was brought to the shelter.
        adoption_date: Date when the dog was adopted (None if not adopted).
    """
    __tablename__ = 'dogs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed_id = db.Column(db.Integer, db.ForeignKey('breeds.id'))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    description = db.Column(db.Text)
    
    # Adoption status
    status = db.Column(
        db.Enum(AdoptionStatus), default=AdoptionStatus.AVAILABLE
    )
    intake_date = db.Column(db.DateTime, default=datetime.now)
    adoption_date = db.Column(db.DateTime, nullable=True)
    
    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Validates the dog's name.
        
        Args:
            key: The attribute key being validated.
            name: The name to validate.
            
        Returns:
            The validated name.
            
        Raises:
            ValueError: If the name is less than 2 characters.
        """
        return self.validate_string_length('Dog name', name, min_length=2)
    
    @validates('gender')
    def validate_gender(self, key: str, gender: str) -> str:
        """Validates the dog's gender.
        
        Args:
            key: The attribute key being validated.
            gender: The gender to validate.
            
        Returns:
            The validated gender.
            
        Raises:
            ValueError: If the gender is not 'Male', 'Female', or 'Unknown'.
        """
        if gender not in ['Male', 'Female', 'Unknown']:
            raise ValueError("Gender must be 'Male', 'Female', or 'Unknown'")
        return gender
    
    @validates('description')
    def validate_description(self, key: str, description: str) -> str:
        """Validates the dog's description.
        
        Args:
            key: The attribute key being validated.
            description: The description to validate.
            
        Returns:
            The validated description.
            
        Raises:
            ValueError: If the description is not None and less than
                10 characters.
        """
        if description is not None:
            return self.validate_string_length(
                'Description', description, min_length=10, allow_none=True
            )
        return description
    
    def __repr__(self) -> str:
        """Returns a string representation of the dog.
        
        Returns:
            A string containing the dog's name, ID, and adoption status.
        """
        return f'<Dog {self.name}, ID: {self.id}, Status: {self.status.value}>'

    def to_dict(self) -> dict:
        """Converts the dog instance to a dictionary.
        
        Returns:
            A dictionary containing the dog's attributes including id, name,
            breed, age, gender, description, and adoption status.
        """
        return {
            'id': self.id,
            'name': self.name,
            'breed': self.breed.name if self.breed else None,
            'age': self.age,
            'gender': self.gender,
            'description': self.description,
            'status': self.status.name if self.status else 'UNKNOWN'
        }
