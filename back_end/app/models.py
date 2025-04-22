from app import db
from datetime import datetime

class Book(db.Model):
    isbn = db.Column('isbn', db.String(20), primary_key=True)
    title = db.Column('Book-Title', db.String(255), nullable=False)
    author = db.Column('Book-Author', db.String(255), nullable=False)
    year = db.Column('Year-Of-Publication', db.String(10))
    publisher = db.Column('publisher', db.String(255))
    image_url_s = db.Column('Image-URL-S', db.String(512))
    image_url_m = db.Column('Image-URL-M', db.String(512))
    image_url_l = db.Column('Image-URL-L', db.String(512))
    
    # Table explicite et options pour gérer les noms de colonnes avec tirets
    __tablename__ = 'books'
    __table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return f'<Book {self.title}>'
    
    def to_dict(self):
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'publisher': self.publisher,
            'image_url_s': self.image_url_s,
            'image_url_m': self.image_url_m,
            'image_url_l': self.image_url_l
        }

class Rating(db.Model):
    user_id = db.Column('User-ID', db.Integer, primary_key=True)
    isbn = db.Column('isbn', db.String(20), primary_key=True)
    rating = db.Column('Book-Rating', db.Integer)
    
    __tablename__ = 'ratings'
    __table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return f'<Rating {self.user_id}-{self.isbn}: {self.rating}>'
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'isbn': self.isbn,
            'rating': self.rating
        }

class User(db.Model):
    id = db.Column('User-ID', db.Integer, primary_key=True)
    location = db.Column('Location', db.String(255))
    age = db.Column('Age', db.Integer)
    
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return f'<User {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'age': self.age
        } 