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
    from app.routes.auth import auth_bp
    from app.routes.ratings import ratings_bp
    
    app.register_blueprint(books_bp, url_prefix="/api/books")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ratings_bp, url_prefix="/api/ratings")
    print("✅ Routes API enregistrées")

    # Ne pas créer les tables et ne pas charger les données du CSV
    print("✅ L'application utilise directement les tables existantes dans la base de données")

    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'API is running'}

    return app
