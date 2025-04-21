from flask import Blueprint, jsonify

books_bp = Blueprint("books", __name__)

@books_bp.route("/", methods=["GET"])
def list_books():
    return jsonify({"message": "Liste des livres 📚"})
