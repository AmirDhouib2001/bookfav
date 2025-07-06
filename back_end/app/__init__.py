from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app() -> Flask:
    app = Flask(__name__)
    
    # Configuration directe (remplace config.Config)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@db:5432/books_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Permettre les requêtes CORS de n'importe quelle origine
    CORS(app, origins=["*"], supports_credentials=True)
    print("✅ CORS configuré pour permettre les requêtes de n'importe quelle origine")
    
    # Initialiser la base de données
    db.init_app(app)
    print("✅ SQLAlchemy initialisé")
    
    from app.routes.books import books_bp
    from app.routes.auth import auth_bp
    from app.routes.ratings import ratings_bp
    from app.routes.recommendations import recommendations_bp
    
    app.register_blueprint(books_bp, url_prefix="/api/books")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ratings_bp, url_prefix="/api/ratings")
    app.register_blueprint(recommendations_bp, url_prefix="/api/recommendations")
    print("✅ Routes API enregistrées (including recommendations)")

    # Ne pas créer les tables et ne pas charger les données du CSV
    print("✅ L'application utilise directement les tables existantes dans la base de données")

    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'API is running'}

    return app
