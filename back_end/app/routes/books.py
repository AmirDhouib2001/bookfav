from flask import Blueprint, jsonify, request, current_app
from app.models import Book
from app import db
import time
import sys
from sqlalchemy import or_, func

books_bp = Blueprint("books", __name__)

@books_bp.route("/", methods=["GET"])
def list_books():
    try:
        # Log détaillé pour le débogage
        print("\n----- DÉBUT DE LA REQUÊTE DE LIVRES -----", file=sys.stderr)
        print(f"Query params: {request.args}", file=sys.stderr)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limiter per_page à 100 maximum pour éviter les problèmes de performance
        per_page = min(per_page, 100)
        
        # Compter le nombre total de livres
        total_books = Book.query.count()
        print(f"Nombre total de livres en base: {total_books}", file=sys.stderr)
        
        if total_books == 0:
            print("ATTENTION: Aucun livre dans la base de données!", file=sys.stderr)
            return jsonify({
                'books': [],
                'total': 0,
                'pages': 0,
                'current_page': page,
                'error': 'Base de données vide'
            })
        
        # Récupérer les livres pour la page demandée
        books = Book.query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Convertir les objets en dictionnaires
        books_list = [book.to_dict() for book in books.items]
        
        print(f"Retour de {len(books_list)} livres pour la page {page}", file=sys.stderr)
        if len(books_list) > 0:
            print(f"Premier livre: {books_list[0]['title']} par {books_list[0]['author']}", file=sys.stderr)
        
        response_data = {
            'books': books_list,
            'total': books.total,
            'pages': books.pages,
            'current_page': books.page
        }
        
        print("----- FIN DE LA REQUÊTE DE LIVRES -----\n", file=sys.stderr)
        return jsonify(response_data)
    except Exception as e:
        print(f"ERREUR dans list_books: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f"Une erreur s'est produite: {str(e)}",
            'books': []
        }), 500

@books_bp.route("/test", methods=["GET"])
def test_endpoint():
    """Point de terminaison simple pour tester la connexion à l'API"""
    return jsonify({
        'message': 'API de test fonctionnelle',
        'timestamp': time.time(),
        'success': True
    })

@books_bp.route("/init-test-data", methods=["GET"])
def init_test_data():
    """Route pour initialiser des données de test si la base est vide"""
    try:
        # Vérifier s'il y a déjà des livres
        existing_count = Book.query.count()
        if existing_count > 0:
            return jsonify({
                'message': f'La base contient déjà {existing_count} livres. Aucune action effectuée.',
                'count': existing_count
            })
        
        # Livres de test à ajouter
        test_books = [
            {
                'isbn': '9780439064873',
                'title': 'Harry Potter et la Pierre Philosophale',
                'author': 'J.K. Rowling',
                'year': '1997',
                'publisher': 'Bloomsbury',
                'image_url_s': 'https://m.media-amazon.com/images/I/51UoqRAxwEL._SY291_BO1,204,203,200_QL40_ML2_.jpg',
                'image_url_m': 'https://m.media-amazon.com/images/I/51UoqRAxwEL._SY291_BO1,204,203,200_QL40_ML2_.jpg',
                'image_url_l': 'https://m.media-amazon.com/images/I/51UoqRAxwEL._SY291_BO1,204,203,200_QL40_ML2_.jpg'
            },
            {
                'isbn': '9780439064880',
                'title': 'Le Seigneur des Anneaux',
                'author': 'J.R.R. Tolkien',
                'year': '1954',
                'publisher': 'Allen & Unwin',
                'image_url_s': 'https://m.media-amazon.com/images/I/51Zt3-YZ8kL._SX218_BO1,204,203,200_QL40_ML2_.jpg',
                'image_url_m': 'https://m.media-amazon.com/images/I/51Zt3-YZ8kL._SX218_BO1,204,203,200_QL40_ML2_.jpg',
                'image_url_l': 'https://m.media-amazon.com/images/I/51Zt3-YZ8kL._SX218_BO1,204,203,200_QL40_ML2_.jpg'
            },
            {
                'isbn': '9780439064897',
                'title': '1984',
                'author': 'George Orwell',
                'year': '1949',
                'publisher': 'Secker & Warburg',
                'image_url_s': 'https://m.media-amazon.com/images/I/41DoIQLHzlL._SX323_BO1,204,203,200_.jpg',
                'image_url_m': 'https://m.media-amazon.com/images/I/41DoIQLHzlL._SX323_BO1,204,203,200_.jpg',
                'image_url_l': 'https://m.media-amazon.com/images/I/41DoIQLHzlL._SX323_BO1,204,203,200_.jpg'
            },
            {
                'isbn': '9780439064903',
                'title': 'Le Petit Prince',
                'author': 'Antoine de Saint-Exupéry',
                'year': '1943',
                'publisher': 'Gallimard',
                'image_url_s': 'https://m.media-amazon.com/images/I/51fS8KQsqAL._SX314_BO1,204,203,200_.jpg',
                'image_url_m': 'https://m.media-amazon.com/images/I/51fS8KQsqAL._SX314_BO1,204,203,200_.jpg',
                'image_url_l': 'https://m.media-amazon.com/images/I/51fS8KQsqAL._SX314_BO1,204,203,200_.jpg'
            },
            {
                'isbn': '9780439064910',
                'title': 'Orgueil et Préjugés',
                'author': 'Jane Austen',
                'year': '1813',
                'publisher': 'T. Egerton',
                'image_url_s': 'https://m.media-amazon.com/images/I/41k1JbIihCL._SX324_BO1,204,203,200_.jpg',
                'image_url_m': 'https://m.media-amazon.com/images/I/41k1JbIihCL._SX324_BO1,204,203,200_.jpg',
                'image_url_l': 'https://m.media-amazon.com/images/I/41k1JbIihCL._SX324_BO1,204,203,200_.jpg'
            }
        ]
        
        # Ajouter les livres de test
        for book_data in test_books:
            book = Book(**book_data)
            db.session.add(book)
        
        db.session.commit()
        
        return jsonify({
            'message': f'5 livres de test ont été ajoutés avec succès',
            'count': 5
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"ERREUR dans init_test_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        return jsonify(book.to_dict())
    except Exception as e:
        print(f"ERREUR dans get_book: {str(e)}")
        return jsonify({'error': str(e)}), 500

@books_bp.route("/isbn/<string:isbn>", methods=["GET"])
def get_book_by_isbn(isbn):
    try:
        book = Book.query.filter_by(isbn=isbn).first_or_404()
        return jsonify(book.to_dict())
    except Exception as e:
        print(f"ERREUR dans get_book_by_isbn: {str(e)}")
        return jsonify({'error': str(e)}), 500

@books_bp.route("/search", methods=["GET"])
def search_books():
    try:
        # Récupérer tous les paramètres de recherche
        title = request.args.get('title', '')
        author = request.args.get('author', '')
        genre = request.args.get('genre', '')
        description = request.args.get('description', '')
        query = request.args.get('q', '')  # Recherche générale
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        # Limiter per_page à 100 maximum pour éviter les problèmes de performance
        per_page = min(per_page, 100)
        
        # Construire la requête de base
        book_query = Book.query
        
        # Appliquer les filtres de recherche si fournis
        if query:
            book_query = book_query.filter(
            (Book.title.ilike(f'%{query}%')) | 
                (Book.author.ilike(f'%{query}%')) |
                (Book.genre.ilike(f'%{query}%')) |
                (Book.description.ilike(f'%{query}%'))
            )
        
        if title:
            book_query = book_query.filter(Book.title.ilike(f'%{title}%'))
            
        if author:
            book_query = book_query.filter(Book.author.ilike(f'%{author}%'))
            
        if genre:
            book_query = book_query.filter(Book.genre.ilike(f'%{genre}%'))
            
        if description:
            book_query = book_query.filter(Book.description.ilike(f'%{description}%'))
        
        # Compter le nombre total de résultats
        total_books = book_query.count()
        
        # Paginer les résultats
        books = book_query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Convertir les objets en dictionnaires
        books_list = [book.to_dict() for book in books.items]
        
        response_data = {
            'books': books_list,
            'total': books.total,
            'pages': books.pages,
            'current_page': books.page
        }
        
        return jsonify(response_data)
    except Exception as e:
        print(f"ERREUR dans search_books: {str(e)}")
        return jsonify({'error': str(e)}), 500

@books_bp.route("/", methods=["POST"])
def create_book():
    data = request.get_json()
    book = Book(
        title=data["title"],
        author=data["author"],
        description=data.get("description", "")
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.description = data.get("description", book.description)
    
    db.session.commit()
    return jsonify(book.to_dict())

@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Livre supprimé avec succès"})

@books_bp.route("/genres", methods=["GET"])
def get_genres():
    """Récupère la liste des genres disponibles dans la base de données."""
    try:
        # Récupérer tous les genres uniques
        genres = db.session.query(Book.genre).distinct().all()
        
        # Extraire les valeurs de genre des tuples renvoyés par la requête
        genre_list = [genre[0] for genre in genres if genre[0]]
        
        # Trier les genres par ordre alphabétique
        genre_list.sort()
        
        return jsonify(genre_list)
    except Exception as e:
        print(f"Erreur lors de la récupération des genres: {str(e)}")
        return jsonify({"error": "Une erreur est survenue lors de la récupération des genres"}), 500

@books_bp.route("/authors", methods=["GET"])
def get_authors():
    """Récupère la liste des 100 auteurs les plus fréquents dans la base de données."""
    try:
        # Récupérer les 100 auteurs les plus fréquents
        authors_query = db.session.query(
            Book.author, 
            func.count(Book.author).label('author_count')
        ).group_by(
            Book.author
        ).having(
            Book.author.isnot(None)
        ).order_by(
            func.count(Book.author).desc()
        ).limit(100).all()
        
        # Extraire les valeurs d'auteur des tuples renvoyés par la requête
        author_list = [author[0] for author in authors_query if author[0]]
        
        print(f"Nombre d'auteurs récupérés: {len(author_list)}")
        
        return jsonify(author_list)
    except Exception as e:
        print(f"Erreur lors de la récupération des auteurs: {str(e)}")
        return jsonify({"error": "Une erreur est survenue lors de la récupération des auteurs"}), 500

@books_bp.route("/recommendations", methods=["GET"])
def get_recommendations():
    """Récupère des recommandations personnalisées pour l'utilisateur."""
    try:
        print("=== DÉBUT ENDPOINT RECOMMENDATIONS ===")
        
        # Récupération de l'ID de session depuis les headers
        session_id = request.headers.get('X-Session-ID')
        print(f"Session ID reçu: {session_id}")
        
        if not session_id:
            print("Pas de session ID, retour de livres populaires")
            return get_popular_books()
        
        # Validation de la session
        from app.models import UserSession, AuthUser
        session = UserSession.get_by_session_id(session_id)
        print(f"Session trouvée: {session is not None}")
        
        if not session:
            print("Session invalide, retour de livres populaires")
            return get_popular_books()
        
        # Récupération de l'utilisateur
        user = AuthUser.query.get(session.user_id)
        print(f"Utilisateur trouvé: {user.username if user else 'None'}")
        
        if not user:
            print("Utilisateur non trouvé, retour de livres populaires")
            return get_popular_books()
        
        # Récupérer les genres et auteurs préférés
        favorite_genres = user.favorite_genres or []
        favorite_authors = user.favorite_authors or []
        print(f"Genres préférés: {favorite_genres}")
        print(f"Auteurs préférés: {favorite_authors}")
        
        # Si l'utilisateur n'a pas de préférences, retourner des livres populaires
        if not favorite_genres and not favorite_authors:
            print("Pas de préférences utilisateur, retour de livres populaires")
            return get_popular_books()
        
        # Construire la requête basée sur les préférences
        query = Book.query
        conditions = []
        
        # Ajouter les conditions pour les genres
        if favorite_genres:
            for genre in favorite_genres:
                conditions.append(Book.genre.ilike(f'%{genre}%'))
        
        # Ajouter les conditions pour les auteurs
        if favorite_authors:
            for author in favorite_authors:
                conditions.append(Book.author.ilike(f'%{author}%'))
        
        print(f"Nombre de conditions: {len(conditions)}")
        
        # Appliquer les conditions avec OR
        if conditions:
            query = query.filter(or_(*conditions))
        
        # Récupérer les recommandations (limité à 20)
        recommended_books = query.limit(20).all()
        print(f"Livres trouvés avec préférences: {len(recommended_books)}")
        
        # Si pas assez de recommandations, compléter avec des livres populaires
        if len(recommended_books) < 10:
            popular_books = Book.query.limit(20 - len(recommended_books)).all()
            print(f"Livres populaires ajoutés: {len(popular_books)}")
            # Éviter les doublons
            existing_isbns = [book.isbn for book in recommended_books]
            for book in popular_books:
                if book.isbn not in existing_isbns and len(recommended_books) < 20:
                    recommended_books.append(book)
        
        print(f"Total de livres recommandés: {len(recommended_books)}")
        
        # Convertir en format JSON
        recommendations = []
        for book in recommended_books:
            recommendations.append({
                'isbn': book.isbn,
                'title': book.title,
                'author': book.author,
                'year': book.year,
                'publisher': book.publisher,
                'image_url_s': book.image_url_s,
                'image_url_m': book.image_url_m,
                'image_url_l': book.image_url_l,
                'genre': book.genre,
                'description': book.description
            })
        
        # Prolonger la session
        session.extend_session(hours=1)
        
        print("=== FIN ENDPOINT RECOMMENDATIONS ===")
        return jsonify(recommendations)
        
    except Exception as e:
        print(f"ERREUR dans recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return get_popular_books()

def get_popular_books():
    """Retourne une sélection de livres populaires comme fallback."""
    try:
        print("=== DÉBUT GET_POPULAR_BOOKS ===")
        # Récupérer 20 livres au hasard comme "populaires"
        books = Book.query.limit(20).all()
        print(f"Livres populaires trouvés: {len(books)}")
        
        recommendations = []
        for book in books:
            recommendations.append({
                'isbn': book.isbn,
                'title': book.title,
                'author': book.author,
                'year': book.year,
                'publisher': book.publisher,
                'image_url_s': book.image_url_s,
                'image_url_m': book.image_url_m,
                'image_url_l': book.image_url_l,
                'genre': book.genre,
                'description': book.description
            })
        
        print("=== FIN GET_POPULAR_BOOKS ===")
        return jsonify(recommendations)
        
    except Exception as e:
        print(f"Erreur lors de la récupération des livres populaires: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500
