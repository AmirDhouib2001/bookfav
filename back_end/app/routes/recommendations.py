from flask import Blueprint, jsonify, request
from app.models import UserBookRating, Book, AuthUser, UserSession, db
from datetime import datetime
from sqlalchemy import func
import sys
import os

# Importer les services partagés
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from shared_services import get_hybrid_service, initialize_shared_services
except ImportError:
    # Si l'import échoue, nous utiliserons une version simplifiée
    get_hybrid_service = None
    initialize_shared_services = None

recommendations_bp = Blueprint("recommendations", __name__)

def ensure_models_loaded():
    """S'assure que les modèles sont chargés"""
    if get_hybrid_service:
        try:
            hybrid_service = get_hybrid_service()
            if hybrid_service and not hybrid_service.cf_model_loaded:
                from shared_services import load_shared_models_with_context
                success = load_shared_models_with_context()
                if success:
                    print("✅ Service hybride initialisé avec modèles chargés (partagés)")
                else:
                    print("⚠️ Échec du chargement des modèles partagés")
        except Exception as e:
            print(f"❌ Erreur lors du chargement des modèles: {str(e)}")

def get_user_from_session():
    """Récupère l'utilisateur à partir de la session"""
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        return None, jsonify({'error': 'Session ID manquant'}), 401
    
    session = UserSession.get_by_session_id(session_id)
    if not session:
        return None, jsonify({'error': 'Session invalide'}), 401
    
    user = AuthUser.query.get(session.user_id)
    if not user:
        return None, jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    return user, None, None

@recommendations_bp.route("/", methods=["GET"])
def get_recommendations():
    """Route pour les recommandations hybrides"""
    try:
        print("=== DÉBUT ENDPOINT RECOMMENDATIONS HYBRIDES ===")
        
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        # Récupérer les paramètres de la requête
        n_recommendations = request.args.get('count', 10, type=int)
        
        # Générer les recommandations hybrides
        hybrid_service = get_hybrid_service()
        recommendations = hybrid_service.get_hybrid_recommendations(
            user_id=user.user_id, 
            n_recommendations=n_recommendations
        )
        
        if not recommendations:
            return jsonify({'message': 'Aucune recommandation disponible'}), 200
        
        print(f"Recommandations générées: {len(recommendations)}")
        print("=== FIN ENDPOINT RECOMMENDATIONS HYBRIDES ===")
        
        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations),
            'user_id': user.user_id
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération des recommandations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la récupération des recommandations: {str(e)}'}), 500

@recommendations_bp.route("/collaborative", methods=["GET"])
def get_collaborative_recommendations():
    """Route pour les recommandations collaborative filtering uniquement"""
    try:
        print("=== DÉBUT ENDPOINT COLLABORATIVE FILTERING ===")
        
        # S'assurer que les modèles sont chargés
        ensure_models_loaded()
        
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        # Récupérer les paramètres de la requête
        n_recommendations = request.args.get('count', 10, type=int)
        
        # Générer les recommandations collaborative filtering
        hybrid_service = get_hybrid_service()
        raw_recommendations = hybrid_service.get_collaborative_recommendations(
            user_id=user.user_id, 
            n_recommendations=n_recommendations
        )
        
        if not raw_recommendations:
            return jsonify({'message': 'Aucune recommandation collaborative disponible'}), 200
        
        # Enrichir avec les métadonnées des livres
        recommendations = hybrid_service._enrich_recommendations(raw_recommendations)
        
        print(f"Recommandations collaborative générées: {len(recommendations)}")
        print("=== FIN ENDPOINT COLLABORATIVE FILTERING ===")
        
        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations),
            'user_id': user.user_id,
            'type': 'collaborative'
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération des recommandations collaborative: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la récupération des recommandations collaborative: {str(e)}'}), 500

@recommendations_bp.route("/content", methods=["GET"])
def get_content_recommendations():
    """Route pour les recommandations content-based uniquement"""
    try:
        print("=== DÉBUT ENDPOINT CONTENT-BASED ===")
        
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        # Récupérer les paramètres de la requête
        n_recommendations = request.args.get('count', 10, type=int)
        
        # Générer les recommandations content-based
        hybrid_service = get_hybrid_service()
        raw_recommendations = hybrid_service.get_content_recommendations(
            user_id=user.user_id, 
            n_recommendations=n_recommendations
        )
        
        if not raw_recommendations:
            return jsonify({'message': 'Aucune recommandation content-based disponible'}), 200
        
        # Enrichir avec les métadonnées des livres
        recommendations = hybrid_service._enrich_recommendations(raw_recommendations)
        
        print(f"Recommandations content-based générées: {len(recommendations)}")
        print("=== FIN ENDPOINT CONTENT-BASED ===")
        
        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations),
            'user_id': user.user_id,
            'type': 'content'
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération des recommandations content-based: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la récupération des recommandations content-based: {str(e)}'}), 500

@recommendations_bp.route("/explain", methods=["GET"])
def explain_recommendation():
    """Route pour expliquer une recommandation"""
    try:
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        isbn = request.args.get('isbn')
        if not isbn:
            return jsonify({'error': 'ISBN requis'}), 400
        
        # Générer l'explication
        hybrid_service = get_hybrid_service()
        explanation = hybrid_service.get_explanation(user.user_id, isbn)
        
        return jsonify(explanation)
        
    except Exception as e:
        print(f"Erreur lors de la génération de l'explication: {str(e)}")
        return jsonify({'error': f'Erreur lors de la génération de l\'explication: {str(e)}'}), 500

@recommendations_bp.route("/stats", methods=["GET"])
def get_recommendation_stats():
    """Route pour les statistiques du système de recommandation"""
    try:
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        # Statistiques utilisateur
        user_stats = db.session.query(
            func.count(UserBookRating.id).label('total_ratings'),
            func.avg(UserBookRating.rating).label('avg_rating'),
            func.min(UserBookRating.created_at).label('first_rating'),
            func.max(UserBookRating.created_at).label('last_rating')
        ).filter(UserBookRating.user_id == user.user_id).first()
        
        # Statistiques globales
        global_stats = db.session.query(
            func.count(func.distinct(UserBookRating.user_id)).label('total_users'),
            func.count(func.distinct(UserBookRating.isbn)).label('total_books'),
            func.count(UserBookRating.id).label('total_ratings'),
            func.avg(UserBookRating.rating).label('global_avg_rating')
        ).first()
        
        # État des modèles
        hybrid_service = get_hybrid_service()
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

@recommendations_bp.route("/retrain", methods=["POST"])
def retrain_model():
    """Route pour réentraîner le modèle collaborative filtering"""
    try:
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        # Vérifier si l'utilisateur a les permissions (par exemple, admin)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        # Réentraîner le modèle
        hybrid_service = get_hybrid_service()
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

@recommendations_bp.route("/similar-users", methods=["GET"])
def get_similar_users():
    """Route pour obtenir des utilisateurs similaires"""
    try:
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        n_similar = request.args.get('count', 5, type=int)
        
        # Obtenir les utilisateurs similaires
        hybrid_service = get_hybrid_service()
        similar_users = hybrid_service.cf_engine.get_similar_users(user.user_id, n_similar)
        
        if not similar_users:
            return jsonify({'message': 'Aucun utilisateur similaire trouvé'}), 200
        
        # Enrichir avec les informations des utilisateurs
        enriched_users = []
        for similar_user_id, similarity_score in similar_users:
            similar_user = AuthUser.query.get(similar_user_id)
            if similar_user:
                enriched_users.append({
                    'user_id': similar_user_id,
                    'username': similar_user.username,
                    'similarity_score': similarity_score,
                    'favorite_genres': similar_user.favorite_genres or []
                })
        
        return jsonify({
            'similar_users': enriched_users,
            'count': len(enriched_users)
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération des utilisateurs similaires: {str(e)}")
        return jsonify({'error': f'Erreur lors de la récupération des utilisateurs similaires: {str(e)}'}), 500 