from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config.Config")
    
    # Permettre les requêtes CORS de n'importe quelle origine
    CORS(app, origins=["*"], supports_credentials=True)
    print("✅ CORS configuré pour permettre les requêtes de n'importe quelle origine")
    
    # Initialiser la base de données
    db.init_app(app)
    print("✅ SQLAlchemy initialisé")
    
    from app.routes.books import books_bp
    app.register_blueprint(books_bp, url_prefix="/api/books")
    print("✅ Routes API enregistrées")

    # Créer les tables de la base de données
    with app.app_context():
        db.create_all()
        print("✅ Tables de base de données créées")
        
        # Charger les livres depuis le CSV seulement s'il n'y a pas de livres dans la base
        from app.utils import load_books_from_csv
        print("Vérification des livres dans la base de données...")
        loaded_count = load_books_from_csv(limit=100, force_reload=False)
        print(f"✅ Base de données contient {loaded_count} livres")

    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'API is running'}

    return app
