import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error
import pickle
import os
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborativeFilteringEngine:
    """
    Moteur de recommandation utilisant le Collaborative Filtering avec des embeddings.
    Combine Matrix Factorization et Neural Collaborative Filtering.
    """
    
    def __init__(self, embedding_dim: int = 50, hidden_dims: List[int] = [128, 64], 
                 dropout_rate: float = 0.2, learning_rate: float = 0.001):
        """
        Initialise le moteur de recommandation.
        
        Args:
            embedding_dim: Dimension des embeddings
            hidden_dims: Dimensions des couches cachées
            dropout_rate: Taux de dropout
            learning_rate: Taux d'apprentissage
        """
        self.embedding_dim = embedding_dim
        self.hidden_dims = hidden_dims
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        
        # Modèles
        self.model = None
        self.user_encoder = LabelEncoder()
        self.item_encoder = LabelEncoder()
        
        # Métadonnées
        self.n_users = 0
        self.n_items = 0
        self.user_means = {}
        self.item_means = {}
        self.global_mean = 0.0
        
        # Historique d'entraînement
        self.training_history = None
        
        # Embeddings pré-entraînés
        self.user_embeddings = None
        self.item_embeddings = None
        
    def _build_model(self) -> keras.Model:
        """
        Construit le modèle de Neural Collaborative Filtering.
        
        Returns:
            Modèle Keras compilé
        """
        # Entrées
        user_input = keras.layers.Input(shape=(), name='user_id')
        item_input = keras.layers.Input(shape=(), name='item_id')
        
        # Embeddings pour Matrix Factorization
        user_embedding_mf = keras.layers.Embedding(
            input_dim=self.n_users, 
            output_dim=self.embedding_dim,
            name='user_embedding_mf'
        )(user_input)
        
        item_embedding_mf = keras.layers.Embedding(
            input_dim=self.n_items, 
            output_dim=self.embedding_dim,
            name='item_embedding_mf'
        )(item_input)
        
        # Embeddings pour Multi-Layer Perceptron
        user_embedding_mlp = keras.layers.Embedding(
            input_dim=self.n_users, 
            output_dim=self.embedding_dim,
            name='user_embedding_mlp'
        )(user_input)
        
        item_embedding_mlp = keras.layers.Embedding(
            input_dim=self.n_items, 
            output_dim=self.embedding_dim,
            name='item_embedding_mlp'
        )(item_input)
        
        # Flatten les embeddings
        user_vec_mf = keras.layers.Flatten()(user_embedding_mf)
        item_vec_mf = keras.layers.Flatten()(item_embedding_mf)
        user_vec_mlp = keras.layers.Flatten()(user_embedding_mlp)
        item_vec_mlp = keras.layers.Flatten()(item_embedding_mlp)
        
        # Matrix Factorization : produit scalaire
        mf_output = keras.layers.Dot(axes=1)([user_vec_mf, item_vec_mf])
        
        # Multi-Layer Perceptron
        mlp_concat = keras.layers.Concatenate()([user_vec_mlp, item_vec_mlp])
        mlp_dropout = keras.layers.Dropout(self.dropout_rate)(mlp_concat)
        
        # Couches cachées
        mlp_hidden = mlp_dropout
        for dim in self.hidden_dims:
            mlp_hidden = keras.layers.Dense(
                dim, 
                activation='relu',
                kernel_regularizer=keras.regularizers.l2(0.01)
            )(mlp_hidden)
            mlp_hidden = keras.layers.Dropout(self.dropout_rate)(mlp_hidden)
        
        # Sortie MLP
        mlp_output = keras.layers.Dense(1, activation='linear')(mlp_hidden)
        
        # Combinaison MF + MLP
        final_output = keras.layers.Add()([mf_output, mlp_output])
        
        # Activation finale pour les ratings (1-5)
        final_output = keras.layers.Dense(1, activation='sigmoid')(final_output)
        final_output = keras.layers.Lambda(lambda x: x * 4 + 1)(final_output)  # Scale to 1-5
        
        # Créer le modèle
        model = keras.Model(inputs=[user_input, item_input], outputs=final_output)
        
        # Compiler le modèle
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def prepare_data(self, ratings_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Prépare les données pour l'entraînement.
        
        Args:
            ratings_data: DataFrame avec colonnes ['user_id', 'isbn', 'rating']
            
        Returns:
            Tuple (user_ids, item_ids, ratings) encodés
        """
        # Encoder les utilisateurs et items
        user_ids = self.user_encoder.fit_transform(ratings_data['user_id'])
        item_ids = self.item_encoder.fit_transform(ratings_data['isbn'])
        ratings = ratings_data['rating'].values.astype(np.float32)
        
        # Mettre à jour les métadonnées
        self.n_users = len(self.user_encoder.classes_)
        self.n_items = len(self.item_encoder.classes_)
        
        # Calculer les moyennes
        self.global_mean = np.mean(ratings)
        
        # Moyennes par utilisateur
        user_rating_means = ratings_data.groupby('user_id')['rating'].mean().to_dict()
        self.user_means = {
            self.user_encoder.transform([user_id])[0]: mean 
            for user_id, mean in user_rating_means.items()
        }
        
        # Moyennes par item
        item_rating_means = ratings_data.groupby('isbn')['rating'].mean().to_dict()
        self.item_means = {
            self.item_encoder.transform([isbn])[0]: mean 
            for isbn, mean in item_rating_means.items()
        }
        
        logger.info(f"Données préparées: {self.n_users} utilisateurs, {self.n_items} livres")
        logger.info(f"Nombre total de ratings: {len(ratings)}")
        logger.info(f"Rating moyen global: {self.global_mean:.2f}")
        
        return user_ids, item_ids, ratings
    
    def train(self, ratings_data: pd.DataFrame, validation_split: float = 0.2, 
              epochs: int = 50, batch_size: int = 256, verbose: int = 1):
        """
        Entraîne le modèle sur les données de ratings.
        
        Args:
            ratings_data: DataFrame avec colonnes ['user_id', 'isbn', 'rating']
            validation_split: Proportion des données pour la validation
            epochs: Nombre d'époques d'entraînement
            batch_size: Taille des batches
            verbose: Verbosité de l'entraînement
        """
        logger.info("Début de l'entraînement du modèle collaborative filtering")
        
        # Préparer les données
        user_ids, item_ids, ratings = self.prepare_data(ratings_data)
        
        # Diviser en train/validation
        train_user, val_user, train_item, val_item, train_rating, val_rating = train_test_split(
            user_ids, item_ids, ratings, test_size=validation_split, random_state=42
        )
        
        # Construire le modèle
        self.model = self._build_model()
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss', 
                patience=10, 
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss', 
                factor=0.5, 
                patience=5
            )
        ]
        
        # Entraîner le modèle
        self.training_history = self.model.fit(
            [train_user, train_item], 
            train_rating,
            validation_data=([val_user, val_item], val_rating),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        # Extraire les embeddings
        self._extract_embeddings()
        
        # Évaluer le modèle
        train_pred = self.model.predict([train_user, train_item])
        val_pred = self.model.predict([val_user, val_item])
        
        train_rmse = np.sqrt(mean_squared_error(train_rating, train_pred))
        val_rmse = np.sqrt(mean_squared_error(val_rating, val_pred))
        
        logger.info(f"RMSE Entraînement: {train_rmse:.4f}")
        logger.info(f"RMSE Validation: {val_rmse:.4f}")
        
        return self.training_history
    
    def _extract_embeddings(self):
        """Extrait les embeddings des utilisateurs et des items du modèle entraîné."""
        if self.model is None:
            return
        
        # Extraire les embeddings utilisateurs (MF)
        user_embedding_layer = self.model.get_layer('user_embedding_mf')
        self.user_embeddings = user_embedding_layer.get_weights()[0]
        
        # Extraire les embeddings items (MF)
        item_embedding_layer = self.model.get_layer('item_embedding_mf')
        self.item_embeddings = item_embedding_layer.get_weights()[0]
        
        logger.info(f"Embeddings extraits: {self.user_embeddings.shape}, {self.item_embeddings.shape}")
    
    def predict_rating(self, user_id: int, isbn: str) -> float:
        """
        Prédit le rating d'un utilisateur pour un livre.
        
        Args:
            user_id: ID de l'utilisateur
            isbn: ISBN du livre
            
        Returns:
            Rating prédit (1-5)
        """
        if self.model is None:
            logger.warning("Modèle non entraîné")
            return self.global_mean
        
        try:
            # Encoder les IDs
            encoded_user = self.user_encoder.transform([user_id])[0]
            encoded_item = self.item_encoder.transform([isbn])[0]
            
            # Prédire
            prediction = self.model.predict([[encoded_user], [encoded_item]])[0, 0]
            
            # Borner la prédiction entre 1 et 5
            return np.clip(prediction, 1.0, 5.0)
            
        except (ValueError, KeyError):
            # Utilisateur ou item non vu pendant l'entraînement
            # Retourner la moyenne de l'utilisateur ou de l'item ou la moyenne globale
            try:
                encoded_user = self.user_encoder.transform([user_id])[0]
                return self.user_means.get(encoded_user, self.global_mean)
            except ValueError:
                try:
                    encoded_item = self.item_encoder.transform([isbn])[0]
                    return self.item_means.get(encoded_item, self.global_mean)
                except ValueError:
                    return self.global_mean
    
    def get_user_recommendations(self, user_id: int, n_recommendations: int = 10, 
                                exclude_rated: bool = True, 
                                rated_books: Optional[List[str]] = None,
                                min_rating_threshold: float = 3.5) -> List[Dict]:
        """
        Génère des recommandations pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            n_recommendations: Nombre de recommandations à retourner
            exclude_rated: Exclure les livres déjà notés
            rated_books: Liste des ISBN déjà notés par l'utilisateur
            min_rating_threshold: Seuil minimum pour recommander un livre (défaut: 3.5)
            
        Returns:
            Liste des recommandations avec scores
        """
        if self.model is None:
            logger.warning("Modèle non entraîné")
            return []
        
        try:
            # Encoder l'utilisateur
            encoded_user = self.user_encoder.transform([user_id])[0]
            
            # Obtenir tous les items disponibles
            all_items = np.arange(self.n_items)
            user_array = np.full(self.n_items, encoded_user)
            
            # Prédire les ratings pour tous les items
            predictions = self.model.predict([user_array, all_items])
            
            # Créer un DataFrame avec les prédictions
            recommendations = []
            for i, pred in enumerate(predictions.flatten()):
                # Décoder l'ISBN
                isbn = self.item_encoder.inverse_transform([i])[0]
                
                # Exclure les livres déjà notés si demandé
                if exclude_rated and rated_books and isbn in rated_books:
                    continue
                
                # Filtrer par seuil minimum de rating
                if pred >= min_rating_threshold:
                    recommendations.append({
                        'isbn': isbn,
                        'predicted_rating': float(pred),
                        'confidence': self._calculate_confidence(encoded_user, i)
                    })
            
            # Trier par rating prédit décroissant
            recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
            
            # Si pas assez de recommandations avec le seuil, réduire le seuil progressivement
            if len(recommendations) < n_recommendations and min_rating_threshold > 3.0:
                logger.info(f"Pas assez de recommandations avec seuil {min_rating_threshold}, réduction du seuil")
                return self.get_user_recommendations(user_id, n_recommendations, exclude_rated, rated_books, min_rating_threshold - 0.5)
            
            return recommendations[:n_recommendations]
            
        except ValueError:
            logger.warning(f"Utilisateur {user_id} non trouvé dans les données d'entraînement")
            return self._get_popular_recommendations(n_recommendations, exclude_rated, rated_books, min_rating_threshold)
    
    def _calculate_confidence(self, encoded_user: int, encoded_item: int) -> float:
        """
        Calcule un score de confiance pour une prédiction.
        
        Args:
            encoded_user: ID utilisateur encodé
            encoded_item: ID item encodé
            
        Returns:
            Score de confiance entre 0 et 1
        """
        if self.user_embeddings is None or self.item_embeddings is None:
            return 0.5
        
        # Calculer la similarité avec les embeddings
        user_emb = self.user_embeddings[encoded_user]
        item_emb = self.item_embeddings[encoded_item]
        
        # Similarité cosinus
        similarity = np.dot(user_emb, item_emb) / (
            np.linalg.norm(user_emb) * np.linalg.norm(item_emb)
        )
        
        # Normaliser entre 0 et 1
        return (similarity + 1) / 2
    
    def _get_popular_recommendations(self, n_recommendations: int, 
                                   exclude_rated: bool = True, 
                                   rated_books: Optional[List[str]] = None,
                                   min_rating_threshold: float = 3.5) -> List[Dict]:
        """
        Retourne les recommandations basées sur la popularité (fallback).
        
        Args:
            n_recommendations: Nombre de recommandations
            exclude_rated: Exclure les livres déjà notés
            rated_books: Liste des ISBN déjà notés
            min_rating_threshold: Seuil minimum pour recommander un livre
            
        Returns:
            Liste des recommandations populaires
        """
        recommendations = []
        
        # Utiliser les moyennes des items comme proxy de popularité
        sorted_items = sorted(self.item_means.items(), key=lambda x: x[1], reverse=True)
        
        count = 0
        for encoded_item, avg_rating in sorted_items:
            if count >= n_recommendations:
                break
                
            # Filtrer par seuil minimum de rating
            if avg_rating < min_rating_threshold:
                continue
                
            # Décoder l'ISBN
            isbn = self.item_encoder.inverse_transform([encoded_item])[0]
            
            # Exclure les livres déjà notés si demandé
            if exclude_rated and rated_books and isbn in rated_books:
                continue
                
            recommendations.append({
                'isbn': isbn,
                'predicted_rating': float(avg_rating),
                'confidence': 0.5  # Confiance moyenne pour les recommandations populaires
            })
            
            count += 1
        
        return recommendations
    
    def get_similar_users(self, user_id: int, n_similar: int = 10) -> List[Tuple[int, float]]:
        """
        Trouve les utilisateurs similaires basés sur les embeddings.
        
        Args:
            user_id: ID de l'utilisateur
            n_similar: Nombre d'utilisateurs similaires à retourner
            
        Returns:
            Liste de (user_id, similarity_score)
        """
        if self.user_embeddings is None:
            return []
        
        try:
            # Encoder l'utilisateur
            encoded_user = self.user_encoder.transform([user_id])[0]
            user_embedding = self.user_embeddings[encoded_user]
            
            # Calculer la similarité avec tous les autres utilisateurs
            similarities = np.dot(self.user_embeddings, user_embedding) / (
                np.linalg.norm(self.user_embeddings, axis=1) * np.linalg.norm(user_embedding)
            )
            
            # Exclure l'utilisateur lui-même
            similarities[encoded_user] = -1
            
            # Obtenir les top utilisateurs similaires
            top_indices = np.argsort(similarities)[-n_similar:][::-1]
            
            similar_users = []
            for idx in top_indices:
                original_user_id = self.user_encoder.inverse_transform([idx])[0]
                similarity_score = similarities[idx]
                similar_users.append((original_user_id, float(similarity_score)))
            
            return similar_users
            
        except ValueError:
            logger.warning(f"Utilisateur {user_id} non trouvé")
            return []
    
    def save_model(self, filepath: str):
        """
        Sauvegarde le modèle et les métadonnées.
        
        Args:
            filepath: Chemin de sauvegarde (sans extension)
        """
        if self.model is None:
            logger.warning("Aucun modèle à sauvegarder")
            return
        
        # Sauvegarder le modèle Keras
        self.model.save(f"{filepath}_model.h5")
        
        # Sauvegarder les métadonnées
        metadata = {
            'user_encoder': self.user_encoder,
            'item_encoder': self.item_encoder,
            'n_users': self.n_users,
            'n_items': self.n_items,
            'user_means': self.user_means,
            'item_means': self.item_means,
            'global_mean': self.global_mean,
            'embedding_dim': self.embedding_dim,
            'hidden_dims': self.hidden_dims,
            'user_embeddings': self.user_embeddings,
            'item_embeddings': self.item_embeddings
        }
        
        with open(f"{filepath}_metadata.pkl", 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info(f"Modèle sauvegardé: {filepath}")
    
    def load_model(self, filepath: str):
        """
        Charge un modèle sauvegardé.
        
        Args:
            filepath: Chemin du modèle (sans extension)
        """
        try:
            # Charger le modèle Keras
            self.model = keras.models.load_model(f"{filepath}_model.h5")
            
            # Charger les métadonnées
            with open(f"{filepath}_metadata.pkl", 'rb') as f:
                metadata = pickle.load(f)
            
            self.user_encoder = metadata['user_encoder']
            self.item_encoder = metadata['item_encoder']
            self.n_users = metadata['n_users']
            self.n_items = metadata['n_items']
            self.user_means = metadata['user_means']
            self.item_means = metadata['item_means']
            self.global_mean = metadata['global_mean']
            self.embedding_dim = metadata['embedding_dim']
            self.hidden_dims = metadata['hidden_dims']
            self.user_embeddings = metadata.get('user_embeddings')
            self.item_embeddings = metadata.get('item_embeddings')
            
            logger.info(f"Modèle chargé: {filepath}")
            
        except FileNotFoundError:
            logger.error(f"Fichier modèle non trouvé: {filepath}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {str(e)}") 