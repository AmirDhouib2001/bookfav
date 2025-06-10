from app import db
from datetime import datetime, timedelta
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import json

class Book(db.Model):
    isbn = db.Column('isbn', db.String(20), primary_key=True)
    title = db.Column('book_title', db.String(255), nullable=False)
    author = db.Column('book_author', db.String(255), nullable=False)
    year = db.Column('year_of_publication', db.String(10))
    publisher = db.Column('publisher', db.String(255))
    image_url_s = db.Column('image_url_s', db.String(512))
    image_url_m = db.Column('image_url_m', db.String(512))
    image_url_l = db.Column('image_url_l', db.String(512))
    genre = db.Column('genre', db.String(255))
    description = db.Column('description', db.Text)
    
    # Table explicite et options pour gérer les noms de colonnes
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
            'image_url_l': self.image_url_l,
            'genre': self.genre,
            'description': self.description
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

class AuthUser(db.Model):
    __tablename__ = 'auth_users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    last_login = db.Column(db.TIMESTAMP)
    is_active = db.Column(db.Boolean, default=True)
    preferences = db.Column(db.JSON, default={})
    favorite_genres = db.Column(db.ARRAY(db.String), default=[])
    reading_history = db.Column(db.JSON, default=[])
    profile_image_url = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')
    
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<AuthUser {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def create_session(self, ip_address=None, user_agent=None, expires_in_hours=1):
        """Crée une nouvelle session pour l'utilisateur"""
        # Supprimer les anciennes sessions expirées
        UserSession.clean_expired_sessions(self.user_id)
        
        # Créer une nouvelle session
        session = UserSession(
            session_id=str(uuid.uuid4()),
            user_id=self.user_id,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
            ip_address=ip_address,
            user_agent=user_agent,
            data={}
        )
        db.session.add(session)
        db.session.commit()
        return session.session_id
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'profile_image_url': self.profile_image_url,
            'role': self.role,
            'favorite_genres': self.favorite_genres
        }


class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    session_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    expires_at = db.Column(db.TIMESTAMP, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    data = db.Column(db.JSON, default={})
    
    def __repr__(self):
        return f'<UserSession {self.session_id}>'
    
    def is_valid(self):
        """Vérifie si la session est toujours valide"""
        return datetime.utcnow() < self.expires_at
    
    def extend_session(self, hours=1):
        """Prolonge la durée de la session"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        db.session.commit()
    
    @classmethod
    def get_by_session_id(cls, session_id):
        """Récupère une session par son ID et vérifie sa validité"""
        session = cls.query.filter_by(session_id=session_id).first()
        if session and session.is_valid():
            return session
        return None
    
    @classmethod
    def clean_expired_sessions(cls, user_id=None):
        """Supprime les sessions expirées"""
        query = cls.query.filter(cls.expires_at < datetime.utcnow())
        if user_id:
            query = query.filter_by(user_id=user_id)
        query.delete()
        db.session.commit() 