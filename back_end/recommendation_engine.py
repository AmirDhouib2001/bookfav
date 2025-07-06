from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Any
from app.models import Book

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
            text = f"{book.title or ''} {book.author or ''} {book.genre or ''} {book.publisher or ''}"
            if book.description:
                text += f" {book.description}"
            book_texts.append(text.strip())
        return book_texts

    def fit(self, books: List[Book]):
        """Entraîne le modèle sur les livres disponibles."""
        if not books:
            print("⚠️ Aucun livre fourni pour l'entraînement")
            return
        
        book_texts = self.prepare_book_data(books)
        print(f"🔤 Textes préparés pour {len(book_texts)} livres")
        
        if not book_texts or all(not text.strip() for text in book_texts):
            print("⚠️ Aucun texte valide trouvé")
            return
            
        try:
            self.book_vectors = self.vectorizer.fit_transform(book_texts)
            print(f"✅ Modèle TF-IDF entraîné avec succès")
            print(f"📊 Dimensions de la matrice: {self.book_vectors.shape}")
        except Exception as e:
            print(f"❌ Erreur lors de l'entraînement TF-IDF: {e}")
            self.book_vectors = None

    def get_recommendations(self, user_preferences: Dict[str, List[str]], n_recommendations: int = 10) -> List[Dict[str, Any]]:
        """Génère des recommandations basées sur les préférences de l'utilisateur."""
        # Vérifier que le modèle est initialisé
        if self.book_vectors is None or self.books is None:
            print("⚠️ Modèle non initialisé")
            return []
        
        if len(self.books) == 0:
            print("⚠️ Aucun livre disponible")
            return []

        try:
            # Créer un vecteur pour les préférences de l'utilisateur
            user_text = " ".join(user_preferences.get('genres', []) + user_preferences.get('authors', []))
            
            if not user_text.strip():
                print("⚠️ Préférences utilisateur vides")
                user_text = "fiction"  # Utiliser un terme générique
            
            print(f"🔍 Texte utilisateur: '{user_text}'")
            user_vector = self.vectorizer.transform([user_text])

            # Calculer la similarité cosinus
            similarities = cosine_similarity(user_vector, self.book_vectors).flatten()
            print(f"📊 Similarités calculées: min={similarities.min():.3f}, max={similarities.max():.3f}")

            # Obtenir les indices des livres les plus similaires
            top_indices = similarities.argsort()[-n_recommendations:][::-1]

            # Formater les recommandations
            recommendations = []
            for idx in top_indices:
                book = self.books[idx]
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
                    'similarity_score': float(similarities[idx])
                })

            print(f"✅ {len(recommendations)} recommandations générées")
            return recommendations
            
        except Exception as e:
            print(f"❌ Erreur dans get_recommendations: {e}")
            import traceback
            traceback.print_exc()
            return [] 