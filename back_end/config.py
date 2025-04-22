import os

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:0000@localhost:5432/books_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
