from flask import Blueprint, jsonify, request
from app.models import UserBookRating, Book, AuthUser, UserSession, db
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

ratings_bp = Blueprint("ratings", __name__)

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

@ratings_bp.route("/rate", methods=["POST"])
def rate_book():
    """Permet à un utilisateur de noter un livre"""
    try:
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données JSON manquantes'}), 400
        
        # Validation des données
        isbn = data.get('isbn')
        rating = data.get('rating')
        review = data.get('review', '')
        
        if not isbn:
            return jsonify({'error': 'ISBN du livre manquant'}), 400
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'La note doit être un entier entre 1 et 5'}), 400
        
        # Vérifier que le livre existe
        book = Book.query.filter_by(isbn=isbn).first()
        if not book:
            return jsonify({'error': 'Livre non trouvé'}), 404
        
        # Vérifier si l'utilisateur a déjà noté ce livre
        existing_rating = UserBookRating.query.filter_by(
            user_id=user.user_id, 
            isbn=isbn
        ).first()
        
        if existing_rating:
            # Mettre à jour la note existante
            existing_rating.rating = rating
            existing_rating.review = review
            db.session.commit()
            
            return jsonify({
                'message': 'Note mise à jour avec succès',
                'rating': existing_rating.to_dict()
            }), 200
        else:
            # Créer une nouvelle note
            new_rating = UserBookRating(
                user_id=user.user_id,
                isbn=isbn,
                rating=rating,
                review=review
            )
            
            db.session.add(new_rating)
            db.session.commit()
            
            return jsonify({
                'message': 'Note ajoutée avec succès',
                'rating': new_rating.to_dict()
            }), 201
            
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur d\'intégrité de la base de données'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la notation: {str(e)}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@ratings_bp.route("/book/<string:isbn>", methods=["GET"])
def get_book_ratings(isbn):
    """Récupère toutes les notes d'un livre"""
    try:
        # Vérifier que le livre existe
        book = Book.query.filter_by(isbn=isbn).first()
        if not book:
            return jsonify({'error': 'Livre non trouvé'}), 404
        
        # Récupérer les statistiques des notes
        ratings_stats = db.session.query(
            func.count(UserBookRating.id).label('total_ratings'),
            func.avg(UserBookRating.rating).label('average_rating'),
            func.count(UserBookRating.id).filter(UserBookRating.rating == 5).label('five_stars'),
            func.count(UserBookRating.id).filter(UserBookRating.rating == 4).label('four_stars'),
            func.count(UserBookRating.id).filter(UserBookRating.rating == 3).label('three_stars'),
            func.count(UserBookRating.id).filter(UserBookRating.rating == 2).label('two_stars'),
            func.count(UserBookRating.id).filter(UserBookRating.rating == 1).label('one_star')
        ).filter(UserBookRating.isbn == isbn).first()
        
        # Récupérer les commentaires récents
        recent_reviews = UserBookRating.query.filter_by(isbn=isbn)\
            .filter(UserBookRating.review.isnot(None))\
            .filter(UserBookRating.review != '')\
            .order_by(UserBookRating.created_at.desc())\
            .limit(10).all()
        
        # Formater les données
        stats = {
            'total_ratings': ratings_stats.total_ratings or 0,
            'average_rating': float(ratings_stats.average_rating or 0),
            'five_stars': ratings_stats.five_stars or 0,
            'four_stars': ratings_stats.four_stars or 0,
            'three_stars': ratings_stats.three_stars or 0,
            'two_stars': ratings_stats.two_stars or 0,
            'one_star': ratings_stats.one_star or 0
        }
        
        reviews = []
        for review in recent_reviews:
            user = AuthUser.query.get(review.user_id)
            reviews.append({
                'id': review.id,
                'rating': review.rating,
                'review': review.review,
                'created_at': review.created_at.isoformat(),
                'user': {
                    'username': user.username if user else 'Utilisateur supprimé',
                    'full_name': user.full_name if user else ''
                }
            })
        
        return jsonify({
            'isbn': isbn,
            'book_title': book.title,
            'stats': stats,
            'recent_reviews': reviews
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des notes: {str(e)}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@ratings_bp.route("/user", methods=["GET"])
def get_user_ratings():
    """Récupère toutes les notes d'un utilisateur"""
    try:
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        # Récupérer les notes de l'utilisateur
        user_ratings = UserBookRating.query.filter_by(user_id=user.user_id)\
            .order_by(UserBookRating.created_at.desc()).all()
        
        ratings_data = []
        for rating in user_ratings:
            book = Book.query.filter_by(isbn=rating.isbn).first()
            ratings_data.append({
                'id': rating.id,
                'isbn': rating.isbn,
                'rating': rating.rating,
                'review': rating.review,
                'created_at': rating.created_at.isoformat(),
                'updated_at': rating.updated_at.isoformat(),
                'book': book.to_dict() if book else None
            })
        
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'ratings': ratings_data,
            'total_ratings': len(ratings_data)
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des notes utilisateur: {str(e)}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@ratings_bp.route("/user/book/<string:isbn>", methods=["GET"])
def get_user_book_rating(isbn):
    """Récupère la note d'un utilisateur pour un livre spécifique"""
    try:
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        # Récupérer la note de l'utilisateur pour ce livre
        rating = UserBookRating.query.filter_by(
            user_id=user.user_id, 
            isbn=isbn
        ).first()
        
        if not rating:
            return jsonify({'has_rating': False}), 200
        
        return jsonify({
            'has_rating': True,
            'rating': rating.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération de la note: {str(e)}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@ratings_bp.route("/delete/<int:rating_id>", methods=["DELETE"])
def delete_rating(rating_id):
    """Supprime une note d'un utilisateur"""
    try:
        # Vérifier l'authentification
        user, error_response, status_code = get_user_from_session()
        if error_response:
            return error_response, status_code
        
        # Récupérer la note
        rating = UserBookRating.query.filter_by(
            id=rating_id, 
            user_id=user.user_id
        ).first()
        
        if not rating:
            return jsonify({'error': 'Note non trouvée ou vous n\'êtes pas autorisé à la supprimer'}), 404
        
        db.session.delete(rating)
        db.session.commit()
        
        return jsonify({'message': 'Note supprimée avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la suppression de la note: {str(e)}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500 