# 📚 Guide Complet du Système de Recommandation Collaborative

## 🎯 Introduction Simple

Le système de recommandation collaborative fonctionne comme un **système de bouche-à-oreille intelligent**. Il analyse les comportements de tous les utilisateurs pour recommander des livres en se basant sur le principe : "Les utilisateurs qui aiment les mêmes livres que vous aiment aussi ces autres livres".

### Exemple concret :
```
Marie a noté :
- "Harry Potter" → 5/5 ⭐⭐⭐⭐⭐
- "Le Seigneur des Anneaux" → 4/5 ⭐⭐⭐⭐
- "Dune" → 5/5 ⭐⭐⭐⭐⭐

Pierre a noté :
- "Harry Potter" → 5/5 ⭐⭐⭐⭐⭐
- "Le Seigneur des Anneaux" → 4/5 ⭐⭐⭐⭐
- "Foundation" → 5/5 ⭐⭐⭐⭐⭐ (Marie ne l'a pas lu)

→ Le système recommande "Foundation" à Marie !
```

## 🏗️ Architecture Générale

Le projet BookFav comprend **2 systèmes de recommandation distincts** :

### 1. 🤖 **Content-Based Filtering (TF-IDF)**
- **Endpoint**: `/api/books/recommendations`
- **Principe**: Recommande des livres similaires aux préférences de l'utilisateur
- **Technologie**: TF-IDF + Similarité Cosinus
- **Utilise**: Genres, auteurs, titre, description du livre

### 2. 🧠 **Collaborative Filtering (Neural Network)**
- **Endpoint**: `/api/recommendations/collaborative`
- **Principe**: Recommande basé sur les goûts d'utilisateurs similaires
- **Technologie**: Neural Collaborative Filtering (NCF)
- **Utilise**: Historique des notes/interactions des utilisateurs

> 💡 **Important**: Le système hybride existe dans le code mais n'est **PAS utilisé** dans l'interface utilisateur actuelle.

## 🔍 Content-Based Filtering avec TF-IDF

### Comment ça marche :

1. **Vectorisation TF-IDF** :
   - Chaque livre est transformé en vecteur numérique
   - Combine : `titre + auteur + genre + description`
   - TF-IDF calcule l'importance des mots

2. **Préférences utilisateur** :
   - Récupère les genres et auteurs favoris
   - Crée un vecteur de préférences

3. **Similarité cosinus** :
   - Calcule la similarité entre préférences et livres
   - Retourne les livres les plus similaires

### Exemple technique :

```python
# Livre : "Dune" par Frank Herbert (Science Fiction)
# Vecteur TF-IDF : [0.2, 0.8, 0.1, 0.9, ...]
#                   ^    ^    ^    ^
#              "dune" "frank" "sci" "fiction"

# Préférences utilisateur : "Science Fiction", "Frank Herbert"
# Vecteur préférences : [0.0, 0.9, 0.0, 0.8, ...]

# Similarité cosinus = 0.85 → Recommandation forte !
```

### Avantages :
- ✅ **Pas de problème de démarrage à froid** (nouveaux utilisateurs)
- ✅ **Recommandations explicables** (basées sur les caractéristiques)
- ✅ **Pas besoin de données d'autres utilisateurs**
- ✅ **Diversité garantie** (explore différents attributs)

### Inconvénients :
- ❌ **Bulle de filtre** (recommande toujours le même type)
- ❌ **Pas de découverte inattendue**
- ❌ **Dépendant de la qualité des métadonnées**

## 🧠 Collaborative Filtering avec Neural Networks

### Architecture Neural Collaborative Filtering (NCF) :

```
Input Layer:
┌─────────────┐    ┌─────────────┐
│   User ID   │    │   Book ID   │
│    (123)    │    │   (456)     │
└─────────────┘    └─────────────┘
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│ User Embed  │    │ Book Embed  │
│   (64 dim)  │    │   (64 dim)  │
└─────────────┘    └─────────────┘
       │                  │
       └─────────┬────────┘
                 ▼
        ┌─────────────┐
        │   Concat    │
        │  (128 dim)  │
        └─────────────┘
                 │
                 ▼
        ┌─────────────┐
        │   Dense     │
        │  (64 units) │
        └─────────────┘
                 │
                 ▼
        ┌─────────────┐
        │   Dense     │
        │  (32 units) │
        └─────────────┘
                 │
                 ▼
        ┌─────────────┐
        │   Output    │
        │  (1 unit)   │
        │ sigmoid     │
        └─────────────┘
```

### Détails techniques :

- **Embeddings** : 64 dimensions pour utilisateurs et livres
- **Architecture** : MLP avec couches cachées [128, 64, 32, 1]
- **Activation** : ReLU pour les couches cachées, Sigmoid pour la sortie
- **Loss function** : Binary Crossentropy
- **Optimizer** : Adam
- **Dropout** : 0.2 pour éviter le surapprentissage

### Entraînement :

```python
# Données d'entraînement
user_ids = [123, 456, 789, ...]
book_ids = [001, 002, 003, ...]
ratings = [0.8, 0.2, 0.9, ...]  # Normalisé entre 0 et 1

# Modèle
model = tf.keras.Model(inputs=[user_input, book_input], outputs=prediction)
model.compile(optimizer='adam', loss='binary_crossentropy')
model.fit([user_ids, book_ids], ratings, epochs=100)
```

### Avantages :
- ✅ **Découverte de patterns complexes** (relations non-linéaires)
- ✅ **Recommandations surprenantes** (sérendipité)
- ✅ **Amélioration avec les données** (plus d'utilisateurs = mieux)
- ✅ **Pas besoin de métadonnées** sur les livres

### Inconvénients :
- ❌ **Problème de démarrage à froid** (nouveaux utilisateurs/livres)
- ❌ **Boîte noire** (difficile à expliquer)
- ❌ **Besoin de beaucoup de données** d'interactions

## 🔧 Implémentation Technique

### Structure des fichiers :

```
bookfav/back_end/
├── recommendation_engine.py          # Content-Based TF-IDF
├── collaborative_filtering_engine.py # Collaborative Neural Network
├── hybrid_recommendation_service.py  # Hybride (non utilisé)
├── train_collaborative_model.py      # Entraînement du modèle
└── app/routes/
    ├── books.py                      # Endpoint content-based
    └── recommendations.py            # Endpoint collaborative
```

### Endpoints API :

1. **Content-Based** : `GET /api/books/recommendations`
   ```http
   GET /api/books/recommendations
   Headers: X-Session-ID: abc123
   
   Response:
   [
     {
       "isbn": "978-0-345-33968-3",
       "title": "Dune",
       "author": "Frank Herbert",
       "genre": "Science Fiction",
       "similarity_score": 0.85,
       "recommendation_type": "content_based_tfidf"
     }
   ]
   ```

2. **Collaborative** : `GET /api/recommendations/collaborative`
   ```http
   GET /api/recommendations/collaborative
   Headers: X-Session-ID: abc123
   
   Response:
   [
     {
       "isbn": "978-0-553-10354-3",
       "title": "A Game of Thrones",
       "author": "George R.R. Martin",
       "predicted_rating": 0.89,
       "recommendation_type": "collaborative_neural"
     }
   ]
   ```

### Initialisation des modèles :

```python
# Content-Based (TF-IDF)
content_engine = RecommendationEngine()
all_books = Book.query.all()
content_engine.fit(all_books)  # Entraîne TF-IDF sur tous les livres

# Collaborative (Neural Network)
collaborative_engine = CollaborativeFilteringEngine()
collaborative_engine.load_model('models/collaborative_model.h5')
```

## 📊 Données et Performances

### Dataset utilisé :
- **Fichier** : `data/ratings_utf8_clean.csv`
- **Taille** : ~2MB (plusieurs milliers de ratings)
- **Colonnes** : `User-ID`, `ISBN`, `Book-Rating`

### Métriques de performance :

**Content-Based TF-IDF** :
- ⚡ **Temps de génération** : ~5-10ms
- 🎯 **Précision** : Basée sur la similarité cosinus
- 📈 **Scalabilité** : Linéaire avec le nombre de livres

**Collaborative Neural** :
- ⚡ **Temps de génération** : ~20-50ms
- 🎯 **Précision** : Évaluée sur dataset de test
- 📈 **Scalabilité** : Constante après entraînement

## 🚀 Utilisation et Test

### Tester le Content-Based :

```bash
cd bookfav/back_end
python test_content_based.py
```

### Tester le Collaborative :

```bash
cd bookfav/back_end
python test_collaborative.py
```

### Entraîner le modèle Neural :

```bash
cd bookfav
./train_model.sh
```

## 🔍 Analyse des Recommandations

### Content-Based - Exemple de sortie :

```json
{
  "title": "Foundation",
  "author": "Isaac Asimov",
  "genre": "Science Fiction",
  "similarity_score": 0.78,
  "confidence": 0.78,
  "recommendation_type": "content_based_tfidf"
}
```

**Interprétation** :
- Score de 0.78 = forte similarité avec les préférences
- Recommandé car l'utilisateur aime la SF
- Expliqué par les métadonnées du livre

### Collaborative - Exemple de sortie :

```json
{
  "title": "The Martian",
  "author": "Andy Weir",
  "predicted_rating": 0.89,
  "recommendation_type": "collaborative_neural"
}
```

**Interprétation** :
- Score de 0.89 = prédiction élevée que l'utilisateur aimera
- Basé sur les goûts d'utilisateurs similaires
- Peut être surprenant/inattendu

## 💡 Optimisations Possibles

### Pour améliorer le système :

1. **Content-Based** :
   - Utiliser des embeddings pré-entraînés (Word2Vec, BERT)
   - Intégrer les résumés de livres
   - Pondérer différemment les attributs

2. **Collaborative** :
   - Essayer des architectures plus complexes (Autoencoders, VAE)
   - Utiliser des données implicites (clics, temps de lecture)
   - Implémenter du deep learning (Wide & Deep, Neural CF)

3. **Système hybride** :
   - Combiner les deux approches avec du machine learning
   - Utiliser des méta-apprenants
   - Adapter les poids selon le contexte

## 🎯 Conclusion

Le système BookFav implémente deux approches complémentaires :

- **Content-Based** : Rapide, explicable, bon pour nouveaux utilisateurs
- **Collaborative** : Découverte, personnalisé, basé sur la communauté

Chaque approche a ses forces et faiblesses, et dans un système réel, une approche hybride serait idéale pour combiner le meilleur des deux mondes.

---

*Guide généré automatiquement - Dernière mise à jour : 2025* 