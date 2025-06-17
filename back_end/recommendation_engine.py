from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Any
from models import Book

class RecommendationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.book_vectors = None
        self.books = None

    def prepare_book_data(self, books: List[Book]) -> List[str]:
        """Prépare les données des livres pour la vectorisation."""
        self.books = books
        book_texts = []
        for book in books:
            # Combiner les informations pertinentes du livre
            text = f"{book.title} {book.author} {book.genre} {book.publisher}"
            if book.description:
                text += f" {book.description}"
            book_texts.append(text)
        return book_texts

    def fit(self, books: List[Book]):
        """Entraîne le modèle sur les livres disponibles."""
        book_texts = self.prepare_book_data(books)
        self.book_vectors = self.vectorizer.fit_transform(book_texts)

    def get_recommendations(self, user_preferences: Dict[str, List[str]], n_recommendations: int = 10) -> List[Dict[str, Any]]:
        """Génère des recommandations basées sur les préférences de l'utilisateur."""
        if not self.book_vectors or not self.books:
            return []

        # Créer un vecteur pour les préférences de l'utilisateur
        user_text = " ".join(user_preferences.get('genres', []) + user_preferences.get('authors', []))
        user_vector = self.vectorizer.transform([user_text])

        # Calculer la similarité cosinus
        similarities = cosine_similarity(user_vector, self.book_vectors).flatten()

        # Obtenir les indices des livres les plus similaires
        top_indices = similarities.argsort()[-n_recommendations:][::-1]

        # Formater les recommandations
        recommendations = []
        for idx in top_indices:
            book = self.books[idx]
            recommendations.append({
                'id': book.id,
                'isbn': book.isbn,
                'title': book.title,
                'author': book.author,
                'year': book.year,
                'publisher': book.publisher,
                'image_url_s': book.image_url_s,
                'image_url_m': book.image_url_m,
                'image_url_l': book.image_url_l,
                'genre': book.genre,
                'similarity_score': float(similarities[idx])
            })

        return recommendations 