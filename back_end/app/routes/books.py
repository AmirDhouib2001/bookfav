from flask import Blueprint, jsonify, request, current_app
from app.models import Book
from app import db
import time
import sys

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
        query = request.args.get('q', '')
        
        if not query:
            return jsonify([])
        
        # Recherche par titre ou auteur
        books = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) | 
            (Book.author.ilike(f'%{query}%'))
        ).limit(100).all()
        
        return jsonify([book.to_dict() for book in books])
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
