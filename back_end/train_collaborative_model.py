#!/usr/bin/env python3
"""
Script d'entraînement pour le modèle de recommandation collaborative filtering.
"""

import pandas as pd
import numpy as np
from flask import Flask
from collaborative_filtering_engine import CollaborativeFilteringEngine
from app import db
from app.models import UserBookRating, Book, AuthUser
import os
import sys
from datetime import datetime

def create_app():
    """Crée une instance de l'application Flask pour accéder à la base de données."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:0000@localhost:5434/books_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def load_data_from_db():
    """
    Charge les données de ratings depuis la base de données.
    
    Returns:
        pd.DataFrame: DataFrame avec les colonnes ['user_id', 'isbn', 'rating']
    """
    print("Chargement des données depuis la base de données...")
    
    # Requête pour récupérer les ratings
    ratings_query = db.session.query(
        UserBookRating.user_id,
        UserBookRating.isbn,
        UserBookRating.rating
    ).all()
    
    # Convertir en DataFrame
    ratings_data = pd.DataFrame(ratings_query, columns=['user_id', 'isbn', 'rating'])
    
    print(f"Données chargées: {len(ratings_data)} ratings")
    print(f"Utilisateurs uniques: {ratings_data['user_id'].nunique()}")
    print(f"Livres uniques: {ratings_data['isbn'].nunique()}")
    print(f"Rating moyen: {ratings_data['rating'].mean():.2f}")
    
    return ratings_data

def filter_data(ratings_data, min_user_ratings=5, min_book_ratings=3):
    """
    Filtre les données pour ne garder que les utilisateurs et livres avec suffisamment de ratings.
    
    Args:
        ratings_data: DataFrame des ratings
        min_user_ratings: Nombre minimum de ratings par utilisateur
        min_book_ratings: Nombre minimum de ratings par livre
        
    Returns:
        pd.DataFrame: DataFrame filtré
    """
    print("Filtrage des données...")
    
    # Compter les ratings par utilisateur et par livre
    user_counts = ratings_data['user_id'].value_counts()
    book_counts = ratings_data['isbn'].value_counts()
    
    # Utilisateurs avec assez de ratings
    active_users = user_counts[user_counts >= min_user_ratings].index
    
    # Livres avec assez de ratings
    popular_books = book_counts[book_counts >= min_book_ratings].index
    
    # Filtrer le DataFrame
    filtered_data = ratings_data[
        (ratings_data['user_id'].isin(active_users)) & 
        (ratings_data['isbn'].isin(popular_books))
    ]
    
    print(f"Après filtrage: {len(filtered_data)} ratings")
    print(f"Utilisateurs actifs: {filtered_data['user_id'].nunique()}")
    print(f"Livres populaires: {filtered_data['isbn'].nunique()}")
    
    return filtered_data

def train_model(save_path='models/collaborative_filtering'):
    """
    Entraîne le modèle collaborative filtering.
    
    Args:
        save_path: Chemin de sauvegarde du modèle
    """
    print("=== Entraînement du modèle Collaborative Filtering ===")
    
    # Charger les données
    ratings_data = load_data_from_db()
    
    if len(ratings_data) == 0:
        print("Aucune donnée de rating trouvée dans la base de données.")
        return None
    
    # Filtrer les données
    filtered_data = filter_data(ratings_data)
    
    if len(filtered_data) < 100:
        print("Données insuffisantes pour l'entraînement (moins de 100 ratings après filtrage).")
        print("Utilisation des données non filtrées...")
        filtered_data = ratings_data
    
    # Créer le moteur de recommandation
    cf_engine = CollaborativeFilteringEngine(
        embedding_dim=64,
        hidden_dims=[128, 64, 32],
        dropout_rate=0.3,
        learning_rate=0.001
    )
    
    # Entraîner le modèle
    try:
        print("Début de l'entraînement...")
        history = cf_engine.train(
            filtered_data,
            validation_split=0.2,
            epochs=100,
            batch_size=512,
            verbose=1
        )
        
        # Créer le dossier de sauvegarde si nécessaire
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Sauvegarder le modèle
        cf_engine.save_model(save_path)
        
        print(f"Modèle sauvegardé à: {save_path}")
        
        # Afficher quelques statistiques
        print("\n=== Statistiques d'entraînement ===")
        if history:
            final_loss = history.history['loss'][-1]
            final_val_loss = history.history['val_loss'][-1]
            print(f"Perte finale (entraînement): {final_loss:.4f}")
            print(f"Perte finale (validation): {final_val_loss:.4f}")
        
        return cf_engine
        
    except Exception as e:
        print(f"Erreur lors de l'entraînement: {str(e)}")
        return None

def test_recommendations(cf_engine, n_users=5, n_recommendations=10):
    """
    Teste les recommandations sur quelques utilisateurs.
    
    Args:
        cf_engine: Moteur de recommandation entraîné
        n_users: Nombre d'utilisateurs à tester
        n_recommendations: Nombre de recommandations par utilisateur
    """
    print(f"\n=== Test des recommandations sur {n_users} utilisateurs ===")
    
    # Récupérer quelques utilisateurs actifs
    ratings_data = load_data_from_db()
    if len(ratings_data) == 0:
        print("Aucune donnée pour tester les recommandations.")
        return
    
    # Utilisateurs avec le plus de ratings
    user_counts = ratings_data['user_id'].value_counts()
    test_users = user_counts.head(n_users).index.tolist()
    
    for user_id in test_users:
        print(f"\n--- Utilisateur {user_id} ---")
        
        # Livres déjà notés par l'utilisateur
        user_ratings = ratings_data[ratings_data['user_id'] == user_id]
        rated_books = user_ratings['isbn'].tolist()
        
        print(f"Livres déjà notés: {len(rated_books)}")
        print(f"Rating moyen: {user_ratings['rating'].mean():.2f}")
        
        # Générer des recommandations
        recommendations = cf_engine.get_user_recommendations(
            user_id=user_id,
            n_recommendations=n_recommendations,
            exclude_rated=True,
            rated_books=rated_books
        )
        
        if recommendations:
            print(f"Top {len(recommendations)} recommandations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. ISBN: {rec['isbn']}")
                print(f"     Rating prédit: {rec['predicted_rating']:.2f}")
                print(f"     Confiance: {rec['confidence']:.2f}")
        else:
            print("Aucune recommandation générée.")

def main():
    """Fonction principale."""
    # Créer l'application Flask
    app = create_app()
    
    with app.app_context():
        # Entraîner le modèle
        cf_engine = train_model()
        
        if cf_engine:
            # Tester les recommandations
            test_recommendations(cf_engine)
            
            print("\n=== Entraînement terminé avec succès ===")
            print("Le modèle peut maintenant être utilisé pour les recommandations.")
        else:
            print("Échec de l'entraînement du modèle.")
            sys.exit(1)

if __name__ == '__main__':
    main() 