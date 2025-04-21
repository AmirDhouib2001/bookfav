from flask import Flask
from flask_cors import CORS

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config.Config")
    CORS(app)

    from app.routes.books import books_bp
    app.register_blueprint(books_bp, url_prefix="/api/books")

    return app
