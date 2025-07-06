from flask import Blueprint, jsonify, request, current_app
from app.models import Book
from app import db
import time
import sys
import os
from sqlalchemy import or_, func

# Importer le moteur de recommandation content-based
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recommendation_engine import RecommendationEngine

books_bp = Blueprint("books", __name__)

# Instance globale du moteur de recommandation content-based
content_engine = RecommendationEngine()
content_engine_loaded = False

def initialize_content_engine():
    """Initialise le moteur de recommandation content-based avec tous les livres."""
    global content_engine_loaded
    try:
        if not content_engine_loaded:
            print("🔄 Initialisation du moteur Content-Based...")
            
            # Charger tous les livres
            all_books = Book.query.all()
            print(f"📚 Livres trouvés en base: {len(all_books)}")
            
            if len(all_books) == 0:
                print("⚠️ Aucun livre en base pour initialiser le content-based")
                return False
            
            # Vérifier que les livres ont des données nécessaires
            books_with_data = []
            for book in all_books:
                if book.title and book.author:
                    books_with_data.append(book)
            
            print(f"📖 Livres avec données suffisantes: {len(books_with_data)}")
            
            if len(books_with_data) == 0:
                print("⚠️ Aucun livre avec données suffisantes")
                return False
            
            # Entraîner le modèle TF-IDF
            print("🤖 Entraînement du modèle TF-IDF...")
            content_engine.fit(books_with_data)
            content_engine_loaded = True
            
            print(f"✅ Moteur Content-Based initialisé avec {len(books_with_data)} livres")
            
            # Test rapide du moteur
            test_preferences = {'genres': ['Fiction'], 'authors': []}
            test_recommendations = content_engine.get_recommendations(test_preferences, 3)
            print(f"🧪 Test du moteur: {len(test_recommendations)} recommandations générées")
            
            if test_recommendations:
                print("🎯 Exemple de recommandation de test:")
                first_rec = test_recommendations[0]
                print(f"   - {first_rec['title']} (Score: {first_rec.get('similarity_score', 'N/A')})")
            
            return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du content-based: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

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
        print(f"Erreur lors de la récupération des livres: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Une erreur est survenue lors de la récupération des livres"}), 500

@books_bp.route("/test", methods=["GET"])
def test_endpoint():
    """Endpoint de test simple pour vérifier la connexion à l'API."""
    return jsonify({
        "message": "API books fonctionnelle", 
        "status": "OK",
        "timestamp": time.time()
    })

@books_bp.route("/init-test-data", methods=["GET"])
def init_test_data():
    try:
        # Compter les livres existants
        book_count = Book.query.count()
        
        if book_count > 0:
            return jsonify({
                "message": f"Base de données déjà initialisée avec {book_count} livres",
                "count": book_count
            }), 200
        
        # Créer quelques livres de test
        test_books = [
            {
                "isbn": "978-0-385-33312-0",
                "title": "The Da Vinci Code",
                "author": "Dan Brown",
                "year": "2003",
                "publisher": "Doubleday",
                "genre": "Mystery",
                "description": "A thriller involving a murder at the Louvre Museum."
            },
            {
                "isbn": "978-0-7432-7355-0",
                "title": "Angels & Demons",
                "author": "Dan Brown",
                "year": "2000",
                "publisher": "Pocket Books",
                "genre": "Mystery",
                "description": "Robert Langdon's first adventure in Vatican City."
            },
            {
                "isbn": "978-0-553-10354-3",
                "title": "A Game of Thrones",
                "author": "George R.R. Martin",
                "year": "1996",
                "publisher": "Bantam Books",
                "genre": "Fantasy",
                "description": "The first book in the epic fantasy series A Song of Ice and Fire."
            },
            {
                "isbn": "978-0-345-33968-3",
                "title": "Dune",
                "author": "Frank Herbert",
                "year": "1965",
                "publisher": "Chilton Books",
                "genre": "Science Fiction",
                "description": "A science fiction epic set on the desert planet Arrakis."
            },
            {
                "isbn": "978-0-7432-7356-7",
                "title": "The Digital Fortress",
                "author": "Dan Brown",
                "year": "1998",
                "publisher": "St. Martin's Press",
                "genre": "Thriller",
                "description": "A techno-thriller about NSA cryptography."
            }
        ]
        
        created_books = []
        for book_data in test_books:
            book = Book(
                isbn=book_data["isbn"],
                title=book_data["title"],
                author=book_data["author"],
                year=book_data["year"],
                publisher=book_data["publisher"],
                genre=book_data["genre"],
                description=book_data["description"]
            )
            db.session.add(book)
            created_books.append(book_data)
        
        db.session.commit()
        
        return jsonify({
            "message": f"Base de données initialisée avec {len(test_books)} livres de test",
            "books": created_books
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'initialisation des données de test: {str(e)}")
        return jsonify({"error": "Erreur lors de l'initialisation des données de test"}), 500

@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@books_bp.route("/isbn/<string:isbn>", methods=["GET"])
def get_book_by_isbn(isbn):
    """Récupère un livre par son ISBN."""
    book = Book.query.filter_by(isbn=isbn).first_or_404()
    return jsonify(book.to_dict(include_ratings=True))

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
            'current_page': books.page,
            'search_params': {
                'query': query,
                'title': title,
                'author': author,
                'genre': genre,
                'description': description
            }
        }
        
        return jsonify(response_data)
    except Exception as e:
        print(f"Erreur lors de la recherche de livres: {str(e)}")
        return jsonify({"error": "Une erreur est survenue lors de la recherche"}), 500

@books_bp.route("/", methods=["POST"])
def create_book():
    data = request.get_json()
    book = Book(title=data["title"], author=data["author"], description=data.get("description"))
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
    """Récupère des recommandations Content-Based avec TF-IDF pour l'utilisateur."""
    try:
        print("=== DÉBUT ENDPOINT CONTENT-BASED RECOMMENDATIONS ===")
        
        # Initialiser le moteur content-based dès le début
        print("🔄 Initialisation du moteur Content-Based...")
        if not initialize_content_engine():
            print("❌ Impossible d'initialiser le moteur content-based")
            return get_popular_books()
        
        print("✅ Moteur Content-Based initialisé avec succès")
        
        # Récupération de l'ID de session depuis les headers
        session_id = request.headers.get('X-Session-ID')
        print(f"Session ID reçu: {session_id}")
        
        # Initialiser les préférences par défaut
        user_preferences = {
            'genres': ['Fiction', 'Science Fiction', 'Fantasy', 'Mystery'],
            'authors': []
        }
        
        # Essayer de récupérer les vraies préférences utilisateur si possible
        if session_id:
            try:
                from app.models import UserSession, AuthUser
                session = UserSession.get_by_session_id(session_id)
                print(f"Session trouvée: {session is not None}")
                
                if session:
                    user = AuthUser.query.get(session.user_id)
                    print(f"Utilisateur trouvé: {user.username if user else 'None'}")
                    
                    if user:
                        # Récupérer les genres et auteurs préférés
                        favorite_genres = user.favorite_genres or []
                        favorite_authors = user.favorite_authors or []
                        print(f"📋 Genres préférés: {favorite_genres}")
                        print(f"📋 Auteurs préférés: {favorite_authors}")
                        
                        # Si l'utilisateur a des préférences, les utiliser
                        if favorite_genres or favorite_authors:
                            user_preferences = {
                                'genres': favorite_genres,
                                'authors': favorite_authors
                            }
                            print("✅ Utilisation des préférences utilisateur personnalisées")
                        else:
                            print("⚠️ Utilisateur sans préférences, utilisation des préférences par défaut")
                            
                        # Prolonger la session si valide
                        session.extend_session(hours=1)
                    else:
                        print("⚠️ Utilisateur non trouvé, utilisation des préférences par défaut")
                else:
                    print("⚠️ Session invalide, utilisation des préférences par défaut")
            except Exception as e:
                print(f"⚠️ Erreur lors de la récupération de l'utilisateur: {e}")
                print("🔄 Utilisation des préférences par défaut")
        else:
            print("⚠️ Pas de session ID, utilisation des préférences par défaut")
        
        print(f"📋 Préférences finales utilisées: {user_preferences}")
        
        # Générer les recommandations avec TF-IDF
        print("🔄 Génération des recommandations Content-Based avec TF-IDF...")
        
        recommendations = content_engine.get_recommendations(
            user_preferences=user_preferences,
            n_recommendations=20
        )
        
        print(f"📚 Recommandations Content-Based générées: {len(recommendations)}")
        
        # Debug: afficher les premiers résultats
        if recommendations:
            print("🔍 Premiers résultats:")
            for i, rec in enumerate(recommendations[:3]):
                print(f"  {i+1}. {rec['title']} - Score: {rec.get('similarity_score', 'N/A')}")
        
        # Si pas assez de recommandations, compléter avec des livres populaires
        if len(recommendations) < 10:
            print("⚠️ Pas assez de recommandations Content-Based, ajout de livres populaires")
            popular_books_data = get_popular_books_data()
            
            # Éviter les doublons
            existing_isbns = [rec['isbn'] for rec in recommendations]
            for book_data in popular_books_data:
                if book_data['isbn'] not in existing_isbns and len(recommendations) < 20:
                    # Ajouter un score artificiel pour les livres populaires
                    book_data['similarity_score'] = 0.1  # Score faible pour les livres populaires
                    book_data['recommendation_type'] = 'popular_fallback'
                    recommendations.append(book_data)
        
        print(f"📖 Total de livres recommandés: {len(recommendations)}")
        
        # Ajouter des métadonnées pour le debugging
        for rec in recommendations:
            if 'recommendation_type' not in rec:
                rec['recommendation_type'] = 'content_based_tfidf'
            if 'similarity_score' in rec:
                rec['confidence'] = rec['similarity_score']
            
            # S'assurer que tous les scores sont visibles
            if 'similarity_score' not in rec:
                rec['similarity_score'] = 0.0
                rec['recommendation_type'] = 'no_score'
        
        # Trier par score décroissant
        recommendations.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        print("=== FIN ENDPOINT CONTENT-BASED RECOMMENDATIONS ===")
        return jsonify(recommendations)
        
    except Exception as e:
        print(f"❌ ERREUR dans content-based recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return get_popular_books()

def get_popular_books():
    """Retourne une sélection de livres populaires comme fallback."""
    try:
        print("=== DÉBUT GET_POPULAR_BOOKS ===")
        recommendations_data = get_popular_books_data()
        print("=== FIN GET_POPULAR_BOOKS ===")
        return jsonify(recommendations_data)
    except Exception as e:
        print(f"Erreur lors de la récupération des livres populaires: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

def get_popular_books_data():
    """Retourne les données des livres populaires."""
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
            'description': book.description,
            'recommendation_type': 'popular'
        })
    
    return recommendations

@books_bp.route("/test-recommendations", methods=["GET"])
def test_recommendations():
    """Endpoint de test pour débugger les recommandations Content-Based avec scores visibles."""
    try:
        print("=== DÉBUT TEST RECOMMENDATIONS ===")
        
        # Initialiser le moteur content-based
        if not initialize_content_engine():
            return jsonify({"error": "Impossible d'initialiser le moteur content-based"}), 500
        
        # Récupérer les paramètres de test (ou utiliser des valeurs par défaut)
        test_genres = request.args.getlist('genres') or ['Science Fiction', 'Fantasy']
        test_authors = request.args.getlist('authors') or ['Frank Herbert']
        n_recommendations = request.args.get('count', 10, type=int)
        
        print(f"🧪 Test avec:")
        print(f"   - Genres: {test_genres}")
        print(f"   - Auteurs: {test_authors}")
        print(f"   - Nombre: {n_recommendations}")
        
        # Créer les préférences de test
        user_preferences = {
            'genres': test_genres,
            'authors': test_authors
        }
        
        # Générer les recommandations
        recommendations = content_engine.get_recommendations(
            user_preferences=user_preferences,
            n_recommendations=n_recommendations
        )
        
        print(f"📚 Recommandations générées: {len(recommendations)}")
        
        # Ajouter des métadonnées de debug
        for i, rec in enumerate(recommendations):
            rec['rank'] = i + 1
            rec['recommendation_type'] = 'test_content_based'
            rec['debug_info'] = {
                'has_similarity_score': 'similarity_score' in rec,
                'score_value': rec.get('similarity_score', 'N/A'),
                'title_length': len(rec.get('title', '')),
                'author_match': any(author.lower() in rec.get('author', '').lower() for author in test_authors),
                'genre_match': any(genre.lower() in rec.get('genre', '').lower() for genre in test_genres)
            }
        
        # Trier par score pour le debug
        recommendations.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        # Statistiques de debug
        debug_stats = {
            'total_recommendations': len(recommendations),
            'recommendations_with_scores': len([r for r in recommendations if 'similarity_score' in r]),
            'score_range': {
                'min': min([r.get('similarity_score', 0) for r in recommendations]) if recommendations else 0,
                'max': max([r.get('similarity_score', 0) for r in recommendations]) if recommendations else 0
            },
            'test_preferences': user_preferences,
            'content_engine_loaded': content_engine_loaded
        }
        
        print("=== FIN TEST RECOMMENDATIONS ===")
        
        return jsonify({
            'debug_stats': debug_stats,
            'recommendations': recommendations
        })
        
    except Exception as e:
        print(f"❌ Erreur dans test-recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
