from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Book, UserBook
from sqlalchemy import or_
import os
from shared_services import initialize_shared_services, get_hybrid_service

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialiser les modèles de recommandation au démarrage
with app.app_context():
    db.create_all()
    
    # Initialiser les services partagés APRÈS avoir créé le contexte d'application
    initialize_shared_services(app)
    hybrid_service = get_hybrid_service()
    
    # Charger et initialiser les modèles avec le contexte partagé
    try:
        from shared_services import load_shared_models_with_context
        success = load_shared_models_with_context()
        if success:
            print("✅ Service de recommandation hybride initialisé avec succès (partagé)")
        else:
            print("⚠️ Échec de l'initialisation du service de recommandation partagé")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du service de recommandation: {str(e)}")

# Route pour les recommandations hybrides
@app.route('/api/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    try:
        # Récupérer l'ID utilisateur depuis la session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Session utilisateur non trouvée'}), 401

        # Récupérer les paramètres de la requête
        n_recommendations = request.args.get('count', 10, type=int)
        
        # Générer les recommandations hybrides
        recommendations = hybrid_service.get_hybrid_recommendations(
            user_id=user_id, 
            n_recommendations=n_recommendations
        )

        if not recommendations:
            return jsonify({'message': 'Aucune recommandation disponible'}), 200

        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations),
            'user_id': user_id
        })

    except Exception as e:
        print(f"Erreur lors de la récupération des recommandations: {str(e)}")
        return jsonify({'error': f'Erreur lors de la récupération des recommandations: {str(e)}'}), 500

# Route pour expliquer une recommandation
@app.route('/api/recommendations/explain', methods=['GET'])
@login_required
def explain_recommendation():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Session utilisateur non trouvée'}), 401

        isbn = request.args.get('isbn')
        if not isbn:
            return jsonify({'error': 'ISBN requis'}), 400

        # Générer l'explication
        explanation = hybrid_service.get_explanation(user_id, isbn)
        
        return jsonify(explanation)

    except Exception as e:
        print(f"Erreur lors de la génération de l'explication: {str(e)}")
        return jsonify({'error': f'Erreur lors de la génération de l\'explication: {str(e)}'}), 500

# Route pour réentraîner le modèle collaborative filtering
@app.route('/api/recommendations/retrain', methods=['POST'])
@login_required
def retrain_model():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Session utilisateur non trouvée'}), 401

        # Vérifier si l'utilisateur a les permissions (par exemple, admin)
        from app.models import AuthUser
        user = AuthUser.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Permissions insuffisantes'}), 403

        # Réentraîner le modèle
        success = hybrid_service.retrain_collaborative_model()
        
        if success:
            return jsonify({
                'message': 'Modèle réentraîné avec succès',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Échec du réentraînement du modèle'}), 500

    except Exception as e:
        print(f"Erreur lors du réentraînement: {str(e)}")
        return jsonify({'error': f'Erreur lors du réentraînement: {str(e)}'}), 500

# Route pour obtenir des utilisateurs similaires
@app.route('/api/users/similar', methods=['GET'])
@login_required
def get_similar_users():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Session utilisateur non trouvée'}), 401

        n_similar = request.args.get('count', 5, type=int)
        
        # Obtenir les utilisateurs similaires
        similar_users = hybrid_service.cf_engine.get_similar_users(user_id, n_similar)
        
        if not similar_users:
            return jsonify({'message': 'Aucun utilisateur similaire trouvé'}), 200

        # Enrichir avec les informations des utilisateurs
        from app.models import AuthUser
        enriched_users = []
        for similar_user_id, similarity_score in similar_users:
            user = AuthUser.query.get(similar_user_id)
            if user:
                enriched_users.append({
                    'user_id': similar_user_id,
                    'username': user.username,
                    'similarity_score': similarity_score,
                    'favorite_genres': user.favorite_genres or []
                })

        return jsonify({
            'similar_users': enriched_users,
            'count': len(enriched_users)
        })

    except Exception as e:
        print(f"Erreur lors de la récupération des utilisateurs similaires: {str(e)}")
        return jsonify({'error': f'Erreur lors de la récupération des utilisateurs similaires: {str(e)}'}), 500

# Route pour les statistiques du système de recommandation
@app.route('/api/recommendations/stats', methods=['GET'])
@login_required
def get_recommendation_stats():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Session utilisateur non trouvée'}), 401

        # Récupérer les statistiques
        from app.models import UserBookRating
        from sqlalchemy import func
        
        # Statistiques utilisateur
        user_stats = db.session.query(
            func.count(UserBookRating.id).label('total_ratings'),
            func.avg(UserBookRating.rating).label('avg_rating'),
            func.min(UserBookRating.created_at).label('first_rating'),
            func.max(UserBookRating.created_at).label('last_rating')
        ).filter(UserBookRating.user_id == user_id).first()
        
        # Statistiques globales
        global_stats = db.session.query(
            func.count(func.distinct(UserBookRating.user_id)).label('total_users'),
            func.count(func.distinct(UserBookRating.isbn)).label('total_books'),
            func.count(UserBookRating.id).label('total_ratings'),
            func.avg(UserBookRating.rating).label('global_avg_rating')
        ).first()
        
        # État des modèles
        model_status = {
            'collaborative_filtering': hybrid_service.cf_model_loaded,
            'content_based': hybrid_service.content_model_loaded,
            'hybrid_weights': {
                'collaborative': hybrid_service.cf_weight,
                'content': hybrid_service.content_weight
            }
        }
        
        return jsonify({
            'user_stats': {
                'total_ratings': user_stats.total_ratings or 0,
                'average_rating': float(user_stats.avg_rating or 0),
                'first_rating': user_stats.first_rating.isoformat() if user_stats.first_rating else None,
                'last_rating': user_stats.last_rating.isoformat() if user_stats.last_rating else None
            },
            'global_stats': {
                'total_users': global_stats.total_users or 0,
                'total_books': global_stats.total_books or 0,
                'total_ratings': global_stats.total_ratings or 0,
                'global_average_rating': float(global_stats.global_avg_rating or 0)
            },
            'model_status': model_status
        })

    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques: {str(e)}")
        return jsonify({'error': f'Erreur lors de la récupération des statistiques: {str(e)}'}), 500 