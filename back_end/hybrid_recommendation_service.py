"""
Service de recommandation hybride combinant Content-Based et Collaborative Filtering.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import os
from app import db
from sqlalchemy import func
from collaborative_filtering_engine import CollaborativeFilteringEngine
from recommendation_engine import RecommendationEngine
from app.models import UserBookRating, Book, AuthUser

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridRecommendationService:
    """
    Service de recommandation hybride qui combine :
    1. Collaborative Filtering (basé sur les ratings des utilisateurs)
    2. Content-Based Filtering (basé sur les métadonnées des livres)
    """
    
    def __init__(self, cf_model_path: str = 'models/collaborative_filtering', 
                 cf_weight: float = 0.7, content_weight: float = 0.3):
        """
        Initialise le service de recommandation hybride.
        
        Args:
            cf_model_path: Chemin vers le modèle collaborative filtering
            cf_weight: Poids du collaborative filtering (0-1)
            content_weight: Poids du content-based filtering (0-1)
        """
        self.cf_weight = cf_weight
        self.content_weight = content_weight
        self.cf_model_path = cf_model_path
        
        # Moteurs de recommandation
        self.cf_engine = CollaborativeFilteringEngine()
        self.content_engine = RecommendationEngine()
        
        # État des modèles
        self.cf_model_loaded = False
        self.content_model_loaded = False
        
        # Métadonnées
        self.min_ratings_for_cf = 3  # Minimum de ratings pour utiliser CF
        
        # Essayer de charger le modèle CF immédiatement
        self._try_load_cf_model()
    
    def _try_load_cf_model(self):
        """
        Essaie de charger le modèle collaborative filtering au démarrage.
        """
        try:
            cf_model_file = f"{self.cf_model_path}_model.h5"
            cf_metadata_file = f"{self.cf_model_path}_metadata.pkl"
            
            if os.path.exists(cf_model_file) and os.path.exists(cf_metadata_file):
                logger.info("🔄 Chargement du modèle CF au démarrage...")
                self.cf_engine.load_model(self.cf_model_path)
                self.cf_model_loaded = True
                logger.info("✅ Modèle collaborative filtering chargé au démarrage")
            else:
                logger.info("⚠️ Modèle CF non trouvé au démarrage, chargement différé")
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement CF au démarrage: {str(e)}")
    
    def initialize_with_flask_context(self):
        """
        Initialise les modèles avec un contexte Flask disponible.
        """
        try:
            # Charger le modèle CF s'il n'est pas déjà chargé
            if not self.cf_model_loaded:
                self._try_load_cf_model()
            
            # Charger le modèle content-based avec les données de la DB
            if not self.content_model_loaded:
                from app.models import Book
                books = Book.query.all()
                if books:
                    logger.info(f"🔄 Chargement du modèle content-based avec {len(books)} livres")
                    self.content_engine.fit(books)
                    self.content_model_loaded = True
                    logger.info("✅ Modèle content-based chargé avec succès")
                else:
                    logger.warning("⚠️ Aucun livre trouvé pour le modèle content-based")
                    
            logger.info(f"📊 État des modèles: CF={self.cf_model_loaded}, Content={self.content_model_loaded}")
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation avec contexte Flask: {str(e)}")
            import traceback
            traceback.print_exc()
        
    def load_models(self, books_data: Optional[List[Book]] = None):
        """
        Charge les modèles de recommandation.
        
        Args:
            books_data: Liste des livres pour le content-based filtering
        """
        logger.info("Chargement des modèles de recommandation...")
        
        # Charger le modèle collaborative filtering
        try:
            cf_model_file = f"{self.cf_model_path}_model.h5"
            cf_metadata_file = f"{self.cf_model_path}_metadata.pkl"
            
            logger.info(f"Recherche du modèle CF à: {cf_model_file}")
            logger.info(f"Recherche des métadonnées à: {cf_metadata_file}")
            
            if os.path.exists(cf_model_file) and os.path.exists(cf_metadata_file):
                logger.info("Fichiers du modèle CF trouvés, chargement...")
                self.cf_engine.load_model(self.cf_model_path)
                self.cf_model_loaded = True
                logger.info("✅ Modèle collaborative filtering chargé avec succès")
            else:
                logger.warning(f"❌ Modèle collaborative filtering non trouvé:")
                logger.warning(f"  - Modèle h5: {os.path.exists(cf_model_file)}")
                logger.warning(f"  - Métadonnées pkl: {os.path.exists(cf_metadata_file)}")
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle CF: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Charger le modèle content-based
        try:
            if books_data:
                logger.info(f"Chargement du modèle content-based avec {len(books_data)} livres")
                self.content_engine.fit(books_data)
                self.content_model_loaded = True
                logger.info("✅ Modèle content-based chargé avec succès")
            else:
                logger.warning("⚠️ Aucune donnée de livres fournie pour le content-based filtering")
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle content-based: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def get_user_ratings_count(self, user_id: int) -> int:
        """
        Récupère le nombre de ratings d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Nombre de ratings
        """
        try:
            from app import db
            count = db.session.query(UserBookRating).filter_by(user_id=user_id).count()
            return count
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du nombre de ratings: {str(e)}")
            return 0
    
    def get_user_rated_books(self, user_id: int) -> List[str]:
        """
        Récupère la liste des livres déjà notés par un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des ISBN des livres notés
        """
        try:
            from app import db
            rated_books = db.session.query(UserBookRating.isbn).filter_by(user_id=user_id).all()
            return [book.isbn for book in rated_books]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des livres notés: {str(e)}")
            return []
    
    def get_collaborative_recommendations(self, user_id: int, n_recommendations: int = 20, 
                                       min_rating_threshold: float = 3.5) -> List[Dict]:
        """
        Génère des recommandations avec collaborative filtering.
        
        Args:
            user_id: ID de l'utilisateur
            n_recommendations: Nombre de recommandations
            min_rating_threshold: Seuil minimum pour recommander un livre
            
        Returns:
            Liste des recommandations CF
        """
        if not self.cf_model_loaded:
            logger.warning("Modèle collaborative filtering non chargé")
            return []
        
        try:
            # Récupérer les livres déjà notés
            rated_books = self.get_user_rated_books(user_id)
            
            # Générer les recommandations avec seuil minimum
            recommendations = self.cf_engine.get_user_recommendations(
                user_id=user_id,
                n_recommendations=n_recommendations,
                exclude_rated=True,
                rated_books=rated_books,
                min_rating_threshold=min_rating_threshold
            )
            
            # Ajouter le type de recommandation
            for rec in recommendations:
                rec['recommendation_type'] = 'collaborative'
                rec['score'] = rec.get('predicted_rating', 0)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations CF: {str(e)}")
            return []
    
    def get_content_recommendations(self, user_id: int, n_recommendations: int = 20) -> List[Dict]:
        """
        Génère des recommandations avec content-based filtering.
        
        Args:
            user_id: ID de l'utilisateur
            n_recommendations: Nombre de recommandations
            
        Returns:
            Liste des recommandations content-based
        """
        if not self.content_model_loaded:
            logger.warning("Modèle content-based non chargé")
            return []
        
        try:
            from app import db
            
            # Récupérer les préférences de l'utilisateur
            user = db.session.query(AuthUser).filter_by(user_id=user_id).first()
            if not user:
                logger.warning(f"Utilisateur {user_id} non trouvé")
                return []
            
            # Préparer les préférences
            user_preferences = {
                'genres': user.favorite_genres or [],
                'authors': user.favorite_authors or []
            }
            
            # Si l'utilisateur n'a pas de préférences explicites, utiliser ses ratings
            if not user_preferences['genres'] and not user_preferences['authors']:
                user_ratings = db.session.query(UserBookRating, Book).join(
                    Book, UserBookRating.isbn == Book.isbn
                ).filter(
                    UserBookRating.user_id == user_id,
                    UserBookRating.rating >= 4  # Livres bien notés
                ).all()
                
                if user_ratings:
                    # Extraire les genres et auteurs des livres bien notés
                    liked_genres = [rating.Book.genre for rating, book in user_ratings if book.genre]
                    liked_authors = [rating.Book.author for rating, book in user_ratings if book.author]
                    
                    user_preferences['genres'] = list(set(liked_genres))
                    user_preferences['authors'] = list(set(liked_authors))
            
            # Générer les recommandations
            recommendations = self.content_engine.get_recommendations(
                user_preferences, n_recommendations
            )
            
            # Ajouter le type de recommandation
            for rec in recommendations:
                rec['recommendation_type'] = 'content'
                rec['score'] = rec.get('similarity_score', 0)
                rec['confidence'] = rec.get('similarity_score', 0)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations content-based: {str(e)}")
            return []
    
    def get_popular_recommendations(self, user_id: int, n_recommendations: int = 20) -> List[Dict]:
        """
        Génère des recommandations basées sur la popularité (fallback).
        
        Args:
            user_id: ID de l'utilisateur
            n_recommendations: Nombre de recommandations
            
        Returns:
            Liste des recommandations populaires
        """
        try:
            
            
            # Récupérer les livres déjà notés par l'utilisateur
            rated_books = self.get_user_rated_books(user_id)
            
            # Requête pour les livres les mieux notés
            popular_books = db.session.query(
                Book.isbn,
                func.avg(UserBookRating.rating).label('avg_rating'),
                func.count(UserBookRating.id).label('rating_count')
            ).join(
                UserBookRating, Book.isbn == UserBookRating.isbn
            ).filter(
                ~Book.isbn.in_(rated_books) if rated_books else True
            ).group_by(
                Book.isbn
            ).having(
                func.count(UserBookRating.id) >= 3  # Au moins 3 ratings
            ).order_by(
                func.avg(UserBookRating.rating).desc()
            ).limit(n_recommendations).all()
            
            recommendations = []
            for book in popular_books:
                recommendations.append({
                    'isbn': book.isbn,
                    'predicted_rating': float(book.avg_rating),
                    'score': float(book.avg_rating),
                    'confidence': min(book.rating_count / 10.0, 1.0),  # Confiance basée sur le nombre de ratings
                    'recommendation_type': 'popular'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations populaires: {str(e)}")
            return []
    
    def combine_recommendations(self, cf_recs: List[Dict], content_recs: List[Dict]) -> List[Dict]:
        """
        Combine les recommandations de différentes sources.
        
        Args:
            cf_recs: Recommandations collaborative filtering
            content_recs: Recommandations content-based
            
        Returns:
            Liste des recommandations combinées
        """
        # Dictionnaire pour stocker les scores combinés
        combined_scores = {}
        
        # Ajouter les scores CF
        for rec in cf_recs:
            isbn = rec['isbn']
            cf_score = rec.get('score', 0)
            combined_scores[isbn] = {
                'cf_score': cf_score,
                'content_score': 0,
                'combined_score': cf_score * self.cf_weight,
                'recommendation_type': 'collaborative',
                'confidence': rec.get('confidence', 0.5),
                'isbn': isbn
            }
        
        # Ajouter les scores content-based
        for rec in content_recs:
            isbn = rec['isbn']
            content_score = rec.get('score', 0)
            
            if isbn in combined_scores:
                # Livre déjà dans les recommandations CF
                combined_scores[isbn]['content_score'] = content_score
                combined_scores[isbn]['combined_score'] = (
                    combined_scores[isbn]['cf_score'] * self.cf_weight + 
                    content_score * self.content_weight
                )
                combined_scores[isbn]['recommendation_type'] = 'hybrid'
            else:
                # Nouveau livre
                combined_scores[isbn] = {
                    'cf_score': 0,
                    'content_score': content_score,
                    'combined_score': content_score * self.content_weight,
                    'recommendation_type': 'content',
                    'confidence': rec.get('confidence', 0.5),
                    'isbn': isbn
                }
        
        # Convertir en liste et trier
        combined_recs = list(combined_scores.values())
        combined_recs.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return combined_recs
    
    def get_hybrid_recommendations(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """
        Génère des recommandations hybrides pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            n_recommendations: Nombre de recommandations à retourner
            
        Returns:
            Liste des recommandations avec métadonnées
        """
        logger.info(f"Génération de recommandations hybrides pour l'utilisateur {user_id}")
        
        # Vérifier le nombre de ratings de l'utilisateur
        user_ratings_count = self.get_user_ratings_count(user_id)
        
        # Stratégie adaptative selon le nombre de ratings
        if user_ratings_count >= self.min_ratings_for_cf and self.cf_model_loaded:
            # Utilisateur avec assez de ratings : utiliser CF + content
            logger.info(f"Utilisateur actif ({user_ratings_count} ratings) : CF + content-based")
            
            cf_recs = self.get_collaborative_recommendations(user_id, n_recommendations * 2)
            content_recs = self.get_content_recommendations(user_id, n_recommendations * 2)
            
            if cf_recs or content_recs:
                combined_recs = self.combine_recommendations(cf_recs, content_recs)
                recommendations = combined_recs[:n_recommendations]
            else:
                # Fallback vers popularité
                recommendations = self.get_popular_recommendations(user_id, n_recommendations)
        
        elif self.content_model_loaded:
            # Nouvel utilisateur : utiliser content-based + popularité
            logger.info(f"Nouvel utilisateur ({user_ratings_count} ratings) : content-based + popularité")
            
            content_recs = self.get_content_recommendations(user_id, n_recommendations)
            
            if content_recs:
                recommendations = content_recs[:n_recommendations]
            else:
                # Fallback vers popularité
                recommendations = self.get_popular_recommendations(user_id, n_recommendations)
        
        else:
            # Aucun modèle disponible : utiliser popularité
            logger.info("Aucun modèle disponible : recommandations par popularité")
            recommendations = self.get_popular_recommendations(user_id, n_recommendations)
        
        # Enrichir les recommandations avec les métadonnées des livres
        enriched_recommendations = self._enrich_recommendations(recommendations)
        
        logger.info(f"Recommandations générées: {len(enriched_recommendations)}")
        return enriched_recommendations
    
    def _enrich_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """
        Enrichit les recommandations avec les métadonnées des livres.
        
        Args:
            recommendations: Liste des recommandations de base
            
        Returns:
            Liste des recommandations enrichies
        """
        if not recommendations:
            return []
        
        try:
            from app import db
            
            # Récupérer les ISBNs
            isbns = [rec['isbn'] for rec in recommendations]
            
            # Requête pour récupérer les métadonnées des livres
            books = db.session.query(Book).filter(Book.isbn.in_(isbns)).all()
            books_dict = {book.isbn: book for book in books}
            
            # Enrichir les recommandations
            enriched = []
            for rec in recommendations:
                isbn = rec['isbn']
                book = books_dict.get(isbn)
                
                if book:
                    enriched_rec = {
                        'isbn': isbn,
                        'title': book.title,
                        'author': book.author,
                        'year': book.year,
                        'publisher': book.publisher,
                        'genre': book.genre,
                        'description': book.description,
                        'image_url_s': book.image_url_s,
                        'image_url_m': book.image_url_m,
                        'image_url_l': book.image_url_l,
                        'predicted_rating': rec.get('combined_score', rec.get('score', 0)),
                        'confidence': rec.get('confidence', 0.5),
                        'recommendation_type': rec.get('recommendation_type', 'unknown')
                    }
                    enriched.append(enriched_rec)
            
            return enriched
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enrichissement des recommandations: {str(e)}")
            return recommendations
    
    def get_explanation(self, user_id: int, isbn: str) -> Dict:
        """
        Génère une explication pour une recommandation.
        
        Args:
            user_id: ID de l'utilisateur
            isbn: ISBN du livre
            
        Returns:
            Dictionnaire avec l'explication
        """
        try:
            from app import db
            from sqlalchemy import func
            
            # Récupérer le livre
            book = db.session.query(Book).filter_by(isbn=isbn).first()
            if not book:
                return {'explanation': 'Livre non trouvé'}
            
            # Récupérer les ratings de l'utilisateur
            user_ratings = db.session.query(UserBookRating, Book).join(
                Book, UserBookRating.isbn == Book.isbn
            ).filter(UserBookRating.user_id == user_id).all()
            
            explanations = []
            
            # Explication basée sur les genres
            if user_ratings:
                liked_genres = [rating.Book.genre for rating, book_data in user_ratings 
                              if rating.rating >= 4 and book_data.genre]
                if book.genre in liked_genres:
                    explanations.append(f"Vous avez bien noté d'autres livres du genre {book.genre}")
            
            # Explication basée sur les auteurs
            if user_ratings:
                liked_authors = [rating.Book.author for rating, book_data in user_ratings 
                               if rating.rating >= 4 and book_data.author]
                if book.author in liked_authors:
                    explanations.append(f"Vous avez bien noté d'autres livres de {book.author}")
            
            # Explication basée sur la popularité
            avg_rating = db.session.query(func.avg(UserBookRating.rating)).filter_by(isbn=isbn).scalar()
            if avg_rating and avg_rating >= 4:
                explanations.append(f"Ce livre a une note moyenne de {avg_rating:.1f}/5")
            
            # Explication par défaut
            if not explanations:
                explanations.append("Ce livre pourrait vous intéresser selon vos préférences")
            
            return {
                'book_title': book.title,
                'book_author': book.author,
                'explanation': ' • '.join(explanations)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'explication: {str(e)}")
            return {'explanation': 'Explication non disponible'}
    
    def retrain_collaborative_model(self):
        """
        Réentraîne le modèle collaborative filtering avec les nouvelles données.
        """
        try:
            from train_collaborative_model import train_model
            
            logger.info("Réentraînement du modèle collaborative filtering...")
            cf_engine = train_model(self.cf_model_path)
            
            if cf_engine:
                self.cf_engine = cf_engine
                self.cf_model_loaded = True
                logger.info("Modèle collaborative filtering réentraîné avec succès")
                return True
            else:
                logger.error("Échec du réentraînement du modèle")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors du réentraînement: {str(e)}")
            return False 