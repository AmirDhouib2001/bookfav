# 🔍 Guide - Comment voir les Similarity Scores

## 🎯 Le problème que vous aviez

Vous voyiez `"recommendation_type": "popular"` au lieu des vrais scores Content-Based parce que le système utilisait le **fallback** (livres populaires) au lieu du vrai TF-IDF.

## ✅ Solutions implémentées

### 1. **Endpoint de test (sans authentification)**
```
GET http://localhost:5001/api/books/test-recommendations
```

**Paramètres optionnels :**
- `genres[]` : genres à tester (défaut: Science Fiction, Fantasy)
- `authors[]` : auteurs à tester (défaut: Frank Herbert)
- `count` : nombre de recommandations (défaut: 10)

**Exemple d'utilisation :**
```bash
# Test basic
curl "http://localhost:5001/api/books/test-recommendations"

# Test avec paramètres personnalisés
curl "http://localhost:5001/api/books/test-recommendations?genres=Fantasy&authors=J.R.R.%20Tolkien&count=5"
```

**Réponse attendue :**
```json
{
  "debug_stats": {
    "total_recommendations": 5,
    "recommendations_with_scores": 5,
    "score_range": {
      "min": 0.12,
      "max": 0.89
    },
    "content_engine_loaded": true
  },
  "recommendations": [
    {
      "title": "Dune",
      "author": "Frank Herbert",
      "similarity_score": 0.89,
      "rank": 1,
      "recommendation_type": "test_content_based",
      "debug_info": {
        "has_similarity_score": true,
        "score_value": 0.89,
        "author_match": true,
        "genre_match": true
      }
    }
  ]
}
```

### 2. **Endpoint principal amélioré**
```
GET http://localhost:5001/api/books/recommendations
Headers: X-Session-ID: your-session-id
```

**Maintenant inclut :**
- `similarity_score` : Score TF-IDF (0.0 à 1.0)
- `confidence` : Copie du score pour compatibilité
- `recommendation_type` : Type de recommandation
- Tri par score décroissant

**Réponse attendue :**
```json
[
  {
    "title": "Foundation",
    "author": "Isaac Asimov",
    "genre": "Science Fiction",
    "similarity_score": 0.78,
    "confidence": 0.78,
    "recommendation_type": "content_based_tfidf"
  }
]
```

## 🛠️ Comment tester rapidement

### Méthode 1: Script Python
```bash
cd bookfav/back_end
python test_similarity_scores.py
```

### Méthode 2: Browser Dev Tools
1. Ouvrez `http://localhost:5001/api/books/test-recommendations` dans votre navigateur
2. Ou utilisez les Dev Tools Network pour voir la réponse

### Méthode 3: curl
```bash
curl -X GET "http://localhost:5001/api/books/test-recommendations" | jq .
```

## 🔍 Debugging - Pourquoi pas de scores ?

### Types de réponses possibles :

1. **`"recommendation_type": "content_based_tfidf"`** ✅
   - Vrai Content-Based avec TF-IDF
   - Scores visibles

2. **`"recommendation_type": "popular"`** ⚠️
   - Fallback (livres populaires)
   - Raisons possibles :
     - Pas de session authentifiée
     - Utilisateur sans préférences
     - Erreur d'initialisation du moteur

3. **`"recommendation_type": "popular_fallback"`** ⚠️
   - Mélange de TF-IDF + livres populaires
   - Pas assez de recommandations TF-IDF trouvées

4. **`"recommendation_type": "no_score"`** ❌
   - Erreur dans le système de scores

## 📊 Interprétation des scores

### Similarity Score (0.0 à 1.0)
- **0.8 - 1.0** : Très haute similarité (excellent match)
- **0.6 - 0.8** : Bonne similarité (bon match)
- **0.4 - 0.6** : Similarité moyenne (match acceptable)
- **0.2 - 0.4** : Faible similarité (match faible)
- **0.0 - 0.2** : Très faible similarité (mauvais match)

### Exemple pratique :
```
Utilisateur aime: "Science Fiction" + "Frank Herbert"

Résultats:
1. Dune (Frank Herbert, Science Fiction) → Score: 0.92 (parfait!)
2. Foundation (Isaac Asimov, Science Fiction) → Score: 0.67 (bon)
3. Hyperion (Dan Simmons, Science Fiction) → Score: 0.54 (acceptable)
4. Harry Potter (J.K. Rowling, Fantasy) → Score: 0.12 (mauvais)
```

## 🚀 Pour voir les scores dans votre interface

1. **Connectez-vous** à votre application
2. **Ajoutez des préférences** dans votre profil utilisateur
3. **Allez sur le Dashboard** et regardez les recommandations
4. **Ouvrez les Dev Tools** → Network → Regardez la réponse de `/books/recommendations`

Vous devriez maintenant voir les `similarity_score` ! 🎯

## 🔧 Dépannage

Si vous ne voyez toujours pas les scores :

1. Vérifiez les logs backend (terminal)
2. Testez l'endpoint de debug : `/books/test-recommendations`
3. Vérifiez que vous avez des livres en base de données
4. Vérifiez que votre utilisateur a des préférences définies

---

*Guide créé automatiquement - 2025* 