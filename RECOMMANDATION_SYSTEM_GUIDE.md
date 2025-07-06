# 🎯 Guide du Système de Recommandation Hybride

## 📋 Vue d'ensemble

Ce système de recommandation hybride combine deux approches principales :
- **Collaborative Filtering** : Utilise des embeddings neuronaux pour apprendre les préférences
- **Content-Based Filtering** : Recommande basé sur les métadonnées des livres

## 🏗️ Architecture

### 1. **Collaborative Filtering Engine** (`collaborative_filtering_engine.py`)
- **Technologie** : TensorFlow/Keras avec Neural Collaborative Filtering
- **Modèle** : Combinaison de Matrix Factorization et Multi-Layer Perceptron
- **Embeddings** : Représentations vectorielles des utilisateurs et livres
- **Dimensions** : 64 dimensions par défaut, optimisable

### 2. **Content-Based Engine** (`recommendation_engine.py`)
- **Technologie** : TF-IDF + similarité cosinus
- **Données** : Métadonnées des livres (titre, auteur, genre, description)
- **Stratégie** : Recommandation basée sur les préférences utilisateur

### 3. **Hybrid Service** (`hybrid_recommendation_service.py`)
- **Poids** : 70% Collaborative + 30% Content-Based (configurable)
- **Stratégie adaptative** : Selon le nombre de ratings de l'utilisateur
- **Fallback** : Recommandations par popularité

## 🚀 Installation et Configuration

### 1. Installation des dépendances
```bash
cd bookfav/back_end
pip install -r requirements.txt
```

### 2. Configuration de la base de données
Assurez-vous que votre base de données PostgreSQL contient :
- `user_book_ratings` : Table des évaluations
- `books` : Table des livres
- `auth_users` : Table des utilisateurs

### 3. Premier entraînement du modèle
```bash
# Depuis le répertoire back_end
python train_collaborative_model.py
```

## 📊 Utilisation

### 1. **Recommandations pour un utilisateur**
```bash
GET /api/recommendations?count=10
```

**Réponse** :
```json
{
  "recommendations": [
    {
      "isbn": "1234567890",
      "title": "Titre du livre",
      "author": "Auteur",
      "predicted_rating": 4.2,
      "confidence": 0.85,
      "recommendation_type": "hybrid"
    }
  ],
  "count": 10,
  "user_id": 123
}
```

### 2. **Explication d'une recommandation**
```bash
GET /api/recommendations/explain?isbn=1234567890
```

**Réponse** :
```json
{
  "book_title": "Titre du livre",
  "book_author": "Auteur",
  "explanation": "Vous avez bien noté d'autres livres du genre Science-Fiction • Ce livre a une note moyenne de 4.3/5"
}
```

### 3. **Utilisateurs similaires**
```bash
GET /api/users/similar?count=5
```

### 4. **Statistiques du système**
```bash
GET /api/recommendations/stats
```

## 🎛️ Stratégies de Recommandation

### Pour un **nouvel utilisateur** (< 3 ratings)
1. **Content-Based** : Utilise les préférences explicites (genres/auteurs favoris)
2. **Fallback** : Recommandations par popularité

### Pour un **utilisateur actif** (≥ 3 ratings)
1. **Collaborative Filtering** : Prédictions basées sur les embeddings
2. **Content-Based** : Compléments basés sur les métadonnées
3. **Hybride** : Combinaison pondérée des deux approches

## 🔧 Paramètres Configurables

### Dans `HybridRecommendationService.__init__()` :
```python
# Poids des algorithmes
cf_weight = 0.7          # Poids du collaborative filtering
content_weight = 0.3     # Poids du content-based

# Seuil pour utiliser CF
min_ratings_for_cf = 3   # Minimum de ratings pour CF
```

### Dans `CollaborativeFilteringEngine.__init__()` :
```python
# Architecture du modèle
embedding_dim = 64       # Dimension des embeddings
hidden_dims = [128, 64, 32]  # Couches cachées
dropout_rate = 0.3       # Taux de dropout
learning_rate = 0.001    # Taux d'apprentissage
```

## 📈 Entraînement et Optimisation

### 1. **Entraînement manuel**
```bash
python train_collaborative_model.py
```

### 2. **Réentraînement via API** (admin requis)
```bash
POST /api/recommendations/retrain
```

### 3. **Paramètres d'entraînement**
- **Epochs** : 100 (avec early stopping)
- **Batch size** : 512
- **Validation split** : 20%
- **Callbacks** : Early stopping, learning rate reduction

## 🎯 Métriques et Évaluation

### Métriques d'entraînement :
- **RMSE** : Erreur quadratique moyenne
- **MAE** : Erreur absolue moyenne
- **Loss** : Fonction de perte (MSE)

### Métriques business :
- **Couverture** : Pourcentage de livres recommandables
- **Diversité** : Variété des recommandations
- **Nouveauté** : Recommandations de livres récents

## 🛠️ Maintenance

### 1. **Monitoring**
- Surveiller les performances des recommandations
- Analyser les statistiques via `/api/recommendations/stats`

### 2. **Réentraînement périodique**
- Recommandé : Une fois par semaine
- Déclenché automatiquement après X nouvelles évaluations

### 3. **Optimisation**
- Ajuster les poids hybrides selon les métriques
- Modifier l'architecture du modèle selon les performances

## 🔍 Debugging

### 1. **Vérifier l'état des modèles**
```bash
GET /api/recommendations/stats
```

### 2. **Logs d'application**
Les logs incluent des informations sur :
- Chargement des modèles
- Génération des recommandations
- Erreurs et exceptions

### 3. **Fichiers de modèles**
- `models/collaborative_filtering_model.h5` : Modèle Keras
- `models/collaborative_filtering_metadata.pkl` : Métadonnées

## 🚨 Problèmes courants

### 1. **Modèle non chargé**
- Vérifier l'existence des fichiers de modèle
- Réentraîner si nécessaire

### 2. **Pas de recommandations**
- Vérifier les données utilisateur
- Fallback vers les recommandations populaires

### 3. **Performance lente**
- Optimiser la taille des embeddings
- Réduire le nombre de couches cachées

## 📋 API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/recommendations` | GET | Obtenir des recommandations |
| `/api/recommendations/explain` | GET | Expliquer une recommandation |
| `/api/recommendations/retrain` | POST | Réentraîner le modèle (admin) |
| `/api/users/similar` | GET | Utilisateurs similaires |
| `/api/recommendations/stats` | GET | Statistiques du système |

## 🎨 Personnalisation

### Adapter les poids hybrides :
```python
# Plus de collaborative filtering
hybrid_service = HybridRecommendationService(
    cf_weight=0.8, 
    content_weight=0.2
)

# Plus de content-based
hybrid_service = HybridRecommendationService(
    cf_weight=0.5, 
    content_weight=0.5
)
```

### Modifier l'architecture du modèle :
```python
cf_engine = CollaborativeFilteringEngine(
    embedding_dim=128,        # Plus d'embeddings
    hidden_dims=[256, 128, 64],  # Plus de profondeur
    dropout_rate=0.4          # Plus de régularisation
)
```

---

## 📞 Support

Pour toute question ou problème :
1. Vérifiez les logs d'application
2. Consultez les statistiques du système
3. Testez avec différents utilisateurs
4. Réentraînez le modèle si nécessaire

Le système s'adapte automatiquement aux différents types d'utilisateurs et fournit des recommandations personnalisées et explicables. 