"""
Service de réentraînement asynchrone pour les modèles de recommandation.
Permet de réentraîner les modèles en arrière-plan sans bloquer l'interface utilisateur.
"""

import threading
import time
import logging
from datetime import datetime
from typing import Optional
from hybrid_recommendation_service import HybridRecommendationService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncRetrainService:
    """
    Service de réentraînement asynchrone pour les modèles de recommandation.
    
    Permet de déclencher des réentraînements en arrière-plan sans bloquer l'API.
    """
    
    def __init__(self, hybrid_service: HybridRecommendationService, flask_app=None):
        """
        Initialise le service de réentraînement asynchrone.
        
        Args:
            hybrid_service: Instance du service hybride de recommandation
            flask_app: Instance de l'application Flask (optionnel)
        """
        self.hybrid_service = hybrid_service
        self.is_retraining = False
        self.last_retrain_time = None
        self.retrain_queue = []
        self.lock = threading.Lock()
        
        # Stocker l'application Flask
        self.app = flask_app
        
        if self.app:
            logger.info("✅ Service AsyncRetrain initialisé avec application Flask")
        else:
            logger.warning("⚠️ Service AsyncRetrain initialisé sans application Flask")
        
    def set_flask_app(self, flask_app):
        """
        Définit l'application Flask après l'initialisation.
        
        Args:
            flask_app: Instance de l'application Flask
        """
        self.app = flask_app
        logger.info("✅ Application Flask définie pour AsyncRetrainService")
        
    def trigger_retrain_async(self, user_id: int, isbn: str, old_rating: Optional[int] = None, new_rating: int = None):
        """
        Déclenche un réentraînement asynchrone.
        
        Args:
            user_id: ID de l'utilisateur qui a modifié la note
            isbn: ISBN du livre noté
            old_rating: Ancienne note (None si nouvelle note)
            new_rating: Nouvelle note
        """
        with self.lock:
            # Vérifier si un réentraînement est déjà en cours
            if self.is_retraining:
                logger.info(f"⏳ Réentraînement déjà en cours. Modification enregistrée: User {user_id}, Livre {isbn}")
                return
            
            # Marquer qu'un réentraînement est en cours
            self.is_retraining = True
        
        # Créer un thread pour le réentraînement
        retrain_thread = threading.Thread(
            target=self._retrain_worker,
            args=(user_id, isbn, old_rating, new_rating),
            daemon=True
        )
        retrain_thread.start()
        
        logger.info(f"🚀 Réentraînement asynchrone démarré pour User {user_id}, Livre {isbn}")
    
    def _retrain_worker(self, user_id: int, isbn: str, old_rating: Optional[int], new_rating: int):
        """
        Worker qui effectue le réentraînement en arrière-plan.
        
        Args:
            user_id: ID de l'utilisateur
            isbn: ISBN du livre
            old_rating: Ancienne note
            new_rating: Nouvelle note
        """
        # Vérifier qu'on a accès à l'application Flask
        if not self.app:
            logger.error("❌ Aucune application Flask disponible pour le réentraînement")
            with self.lock:
                self.is_retraining = False
            return
        
        # Créer un contexte d'application Flask pour ce thread
        with self.app.app_context():
            try:
                start_time = datetime.now()
                
                if old_rating is not None:
                    logger.info(f"🔄 Début du réentraînement (modification): User {user_id}, Livre {isbn}, {old_rating} → {new_rating}")
                else:
                    logger.info(f"🔄 Début du réentraînement (nouvelle note): User {user_id}, Livre {isbn}, Note: {new_rating}")
                
                # Effectuer le réentraînement
                success = self.hybrid_service.retrain_collaborative_model()
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                if success:
                    logger.info(f"✅ Réentraînement terminé avec succès en {duration:.2f} secondes")
                    self.last_retrain_time = end_time
                    
                    # Recharger les modèles dans TOUS les services partagés
                    try:
                        from shared_services import reload_shared_models
                        success = reload_shared_models()
                        if success:
                            logger.info("🔄 Modèles rechargés dans tous les services partagés")
                        else:
                            logger.error("❌ Échec du rechargement des modèles partagés")
                    except Exception as e:
                        logger.error(f"❌ Erreur lors du rechargement des modèles: {str(e)}")
                    
                else:
                    logger.error(f"❌ Échec du réentraînement après {duration:.2f} secondes")
                    
            except Exception as e:
                logger.error(f"❌ Erreur lors du réentraînement asynchrone: {str(e)}")
                import traceback
                traceback.print_exc()
            
            finally:
                # Marquer que le réentraînement est terminé
                with self.lock:
                    self.is_retraining = False
                
                logger.info("🏁 Worker de réentraînement terminé")
    
    def get_status(self) -> dict:
        """
        Retourne le statut du service de réentraînement.
        
        Returns:
            dict: Statut du service
        """
        with self.lock:
            return {
                'is_retraining': self.is_retraining,
                'last_retrain_time': self.last_retrain_time.isoformat() if self.last_retrain_time else None,
                'model_loaded': self.hybrid_service.cf_model_loaded,
                'model_path': self.hybrid_service.cf_model_path,
                'has_flask_app': self.app is not None
            }
    
    def force_retrain_sync(self) -> bool:
        """
        Force un réentraînement synchrone (bloquant).
        Utilisé pour les tests ou les situations critiques.
        
        Returns:
            bool: True si succès, False sinon
        """
        logger.info("🔄 Réentraînement synchrone forcé")
        
        if not self.app:
            logger.error("❌ Aucune application Flask disponible pour le réentraînement synchrone")
            return False
        
        # Créer un contexte d'application Flask
        with self.app.app_context():
            try:
                return self.hybrid_service.retrain_collaborative_model()
            except Exception as e:
                logger.error(f"❌ Erreur lors du réentraînement synchrone: {str(e)}")
                return False 