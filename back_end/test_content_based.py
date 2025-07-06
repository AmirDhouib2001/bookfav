#!/usr/bin/env python3
"""
Script de test pour vérifier le fonctionnement du Content-Based filtering avec TF-IDF
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from app import db
from app.models import Book
from recommendation_engine import RecommendationEngine

def create_test_app():
    """Crée une instance de l'application Flask pour les tests."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:0000@localhost:5434/books_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def test_content_based_engine():
    """Teste le moteur de recommandation Content-Based."""
    print("🧪 Test du moteur Content-Based avec TF-IDF")
    print("=" * 50)
    
    # Créer l'application Flask
    app = create_test_app()
    
    with app.app_context():
        # 1. Vérifier les livres en base
        total_books = Book.query.count()
        print(f"📚 Livres en base de données: {total_books}")
        
        if total_books == 0:
            print("❌ Aucun livre en base de données. Ajoutez des livres d'abord.")
            return
        
        # 2. Charger quelques livres pour le test
        books_sample = Book.query.limit(10).all()
        print(f"📖 Échantillon de livres pour le test: {len(books_sample)}")
        
        for i, book in enumerate(books_sample, 1):
            print(f"  {i}. {book.title} par {book.author} ({book.genre})")
        
        # 3. Initialiser le moteur Content-Based
        print("\n🔄 Initialisation du moteur Content-Based...")
        content_engine = RecommendationEngine()
        
        all_books = Book.query.all()
        content_engine.fit(all_books)
        print(f"✅ Moteur initialisé avec {len(all_books)} livres")
        
        # 4. Tester avec différentes préférences utilisateur
        test_preferences = [
            {
                'name': 'Fan de Science-Fiction',
                'preferences': {
                    'genres': ['Science Fiction', 'Sci-Fi'],
                    'authors': ['Frank Herbert']
                }
            },
            {
                'name': 'Amateur de Mystery',
                'preferences': {
                    'genres': ['Mystery', 'Thriller'],
                    'authors': ['Dan Brown']
                }
            },
            {
                'name': 'Lecteur de Fantasy',
                'preferences': {
                    'genres': ['Fantasy'],
                    'authors': ['George R.R. Martin']
                }
            }
        ]
        
        print("\n🎯 Test des recommandations Content-Based:")
        print("=" * 50)
        
        for test_case in test_preferences:
            print(f"\n👤 Profil: {test_case['name']}")
            print(f"   Genres préférés: {test_case['preferences']['genres']}")
            print(f"   Auteurs préférés: {test_case['preferences']['authors']}")
            
            # Générer les recommandations
            recommendations = content_engine.get_recommendations(
                user_preferences=test_case['preferences'],
                n_recommendations=5
            )
            
            if recommendations:
                print(f"📚 Top 5 recommandations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec['title']} par {rec['author']}")
                    print(f"      Genre: {rec['genre']}")
                    print(f"      Score de similarité: {rec['similarity_score']:.3f}")
                    print()
            else:
                print("❌ Aucune recommandation générée")
        
        # 5. Tester les performances
        print("\n⚡ Test de performance:")
        print("=" * 30)
        
        import time
        start_time = time.time()
        
        recommendations = content_engine.get_recommendations(
            user_preferences={'genres': ['Science Fiction'], 'authors': ['Frank Herbert']},
            n_recommendations=10
        )
        
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000
        
        print(f"⏱️ Temps de génération: {processing_time:.2f}ms")
        print(f"📊 Recommandations générées: {len(recommendations)}")
        print(f"🚀 Performance: {len(recommendations)/processing_time*1000:.1f} recommandations/seconde")
        
        print("\n✅ Test du Content-Based filtering terminé avec succès!")

if __name__ == '__main__':
    test_content_based_engine() 