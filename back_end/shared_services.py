"""
Services partagés pour l'application BookFav.
Centralise les instances des services pour éviter les duplications.
"""

import logging
from typing import Optional
from hybrid_recommendation_service import HybridRecommendationService
from async_retrain_service import AsyncRetrainService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SharedServices:
    """
    Classe singleton pour gérer les services partagés de l'application.
    """
    _instance = None
    _hybrid_service: Optional[HybridRecommendationService] = None
    _async_retrain_service: Optional[AsyncRetrainService] = None
    _flask_app = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedServices, cls).__new__(cls)
        return cls._instance
    
    def initialize(self, flask_app=None):
        """
        Initialise les services partagés.
        
        Args:
            flask_app: Instance de l'application Flask
        """
        self._flask_app = flask_app
        
        # Initialiser le service hybride si pas encore fait
        if self._hybrid_service is None:
            self._hybrid_service = HybridRecommendationService()
            logger.info("✅ Service hybride initialisé (partagé)")
        
        # Initialiser le service async si on a l'application Flask
        if flask_app and self._async_retrain_service is None:
            self._async_retrain_service = AsyncRetrainService(self._hybrid_service, flask_app)
            logger.info("✅ Service async initialisé (partagé)")
    
    def get_hybrid_service(self) -> HybridRecommendationService:
        """
        Récupère l'instance partagée du service hybride.
        
        Returns:
            Instance du service hybride
        """
        if self._hybrid_service is None:
            self._hybrid_service = HybridRecommendationService()
            logger.info("✅ Service hybride créé à la demande")
        return self._hybrid_service
    
    def get_async_retrain_service(self) -> Optional[AsyncRetrainService]:
        """
        Récupère l'instance partagée du service async.
        
        Returns:
            Instance du service async ou None si pas initialisé
        """
        return self._async_retrain_service
    
    def set_flask_app(self, flask_app):
        """
        Définit l'application Flask et initialise le service async si nécessaire.
        
        Args:
            flask_app: Instance de l'application Flask
        """
        self._flask_app = flask_app
        
        if self._async_retrain_service is None and self._hybrid_service is not None:
            self._async_retrain_service = AsyncRetrainService(self._hybrid_service, flask_app)
            logger.info("✅ Service async initialisé après définition de l'app Flask")
    
    def reload_models(self):
        """
        Recharge les modèles dans le service hybride partagé.
        Utilisé après réentraînement pour mettre à jour tous les utilisateurs du service.
        """
        if self._hybrid_service is None:
            logger.warning("⚠️ Service hybride non initialisé, impossible de recharger les modèles")
            return False
        
        try:
            # Vérifier si on a accès à un contexte Flask
            if self._flask_app:
                with self._flask_app.app_context():
                    # Importer ici pour éviter les imports circulaires
                    from app.models import Book
                    books = Book.query.all()
                    self._hybrid_service.load_models(books)
                    logger.info("🔄 Modèles rechargés dans le service hybride partagé")
                    return True
            else:
                logger.warning("⚠️ Aucun contexte Flask disponible pour recharger les modèles")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur lors du rechargement des modèles: {str(e)}")
            return False
    
    def load_models_with_context(self):
        """
        Charge les modèles avec un contexte Flask approprié.
        """
        if self._hybrid_service is None:
            logger.warning("⚠️ Service hybride non initialisé")
            return False
        
        if self._flask_app:
            try:
                with self._flask_app.app_context():
                    self._hybrid_service.initialize_with_flask_context()
                    logger.info("✅ Modèles initialisés avec contexte Flask")
                    return True
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'initialisation des modèles avec contexte: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        else:
            logger.warning("⚠️ Aucun contexte Flask disponible")
            return False
    
    def get_status(self) -> dict:
        """
        Retourne le statut des services partagés.
        
        Returns:
            dict: Statut des services
        """
        return {
            'hybrid_service_initialized': self._hybrid_service is not None,
            'async_service_initialized': self._async_retrain_service is not None,
            'flask_app_set': self._flask_app is not None,
            'cf_model_loaded': self._hybrid_service.cf_model_loaded if self._hybrid_service else False,
            'content_model_loaded': self._hybrid_service.content_model_loaded if self._hybrid_service else False
        }

# Instance globale des services partagés
shared_services = SharedServices()

# Fonctions d'accès rapide
def get_hybrid_service() -> HybridRecommendationService:
    """Récupère l'instance partagée du service hybride."""
    return shared_services.get_hybrid_service()

def get_async_retrain_service() -> Optional[AsyncRetrainService]:
    """Récupère l'instance partagée du service async."""
    return shared_services.get_async_retrain_service()

def initialize_shared_services(flask_app=None):
    """Initialise les services partagés."""
    shared_services.initialize(flask_app)

def reload_shared_models():
    """Recharge les modèles dans tous les services."""
    return shared_services.reload_models()

def load_shared_models_with_context():
    """Charge les modèles avec un contexte Flask approprié."""
    return shared_services.load_models_with_context() 