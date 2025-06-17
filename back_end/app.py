from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Book, UserBook
from sqlalchemy import or_
import os
from recommendation_engine import RecommendationEngine

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'votre_clé_secrète')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/bookfav')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données
db.init_app(app)

# Initialisation de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Initialiser le moteur de recommandation
recommendation_engine = RecommendationEngine()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialiser le moteur de recommandation au démarrage
with app.app_context():
    db.create_all()
    # Charger et entraîner le modèle
    try:
        books = Book.query.all()
        if books:
            recommendation_engine.fit(books)
            print("Moteur de recommandation initialisé avec succès")
        else:
            print("Aucun livre trouvé pour initialiser le moteur de recommandation")
    except Exception as e:
        print(f"Erreur lors de l'initialisation du moteur de recommandation: {str(e)}")

# @app.route('/api/recommendations', methods=['GET'])
# @login_required
# def get_recommendations():
#     try:
#         # Récupérer les préférences de l'utilisateur
#         user_id = session.get('user_id')
#         if not user_id:
#             return jsonify({'error': 'Session utilisateur non trouvée'}), 401

#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({'error': 'Utilisateur non trouvé'}), 404

#         # Récupérer les genres et auteurs préférés
#         favorite_genres = user.favorite_genres or []
#         favorite_authors = user.favorite_authors or []

#         # Préparer les préférences de l'utilisateur
#         user_preferences = {
#             'genres': favorite_genres,
#             'authors': favorite_authors
#         }

#         # Obtenir les recommandations
#         recommendations = recommendation_engine.get_recommendations(user_preferences)

#         # Exclure les livres déjà lus
#         read_books = UserBook.query.filter_by(user_id=user_id).all()
#         if read_books:
#             read_book_ids = [book.book_id for book in read_books]
#             recommendations = [r for r in recommendations if r['id'] not in read_book_ids]

#         if not recommendations:
#             return jsonify({'message': 'Aucune recommandation disponible'}), 200

#         return jsonify(recommendations)

#     except Exception as e:
#         print(f"Erreur lors de la récupération des recommandations: {str(e)}")
#         return jsonify({'error': f'Erreur lors de la récupération des recommandations: {str(e)}'}), 500 