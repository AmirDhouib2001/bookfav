#!/usr/bin/env python3
"""
Script de test rapide pour vérifier les similarity_scores du Content-Based filtering
"""

import requests
import json
import sys

def test_recommendations_endpoint():
    """Teste l'endpoint des recommandations pour vérifier les similarity_scores"""
    
    print("🧪 Test des Similarity Scores - Content-Based Filtering")
    print("=" * 60)
    
    # URL de l'API
    api_url = 'http://localhost:5001/api'
    
    # Test 1: Endpoint de test sans session
    print("\n📋 Test 1: Endpoint de test sans authentification")
    print("-" * 45)
    
    try:
        response = requests.get(
            f"{api_url}/books/test-recommendations",
            params={
                'genres': ['Science Fiction', 'Fantasy'],
                'authors': ['Frank Herbert'],
                'count': 5
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de test accessible")
            
            debug_stats = data.get('debug_stats', {})
            recommendations = data.get('recommendations', [])
            
            print(f"📊 Statistiques:")
            print(f"   - Total recommandations: {debug_stats.get('total_recommendations', 0)}")
            print(f"   - Avec scores: {debug_stats.get('recommendations_with_scores', 0)}")
            print(f"   - Score min: {debug_stats.get('score_range', {}).get('min', 'N/A')}")
            print(f"   - Score max: {debug_stats.get('score_range', {}).get('max', 'N/A')}")
            print(f"   - Moteur chargé: {debug_stats.get('content_engine_loaded', False)}")
            
            if recommendations:
                print(f"\n🎯 Top 3 recommandations avec scores:")
                for i, rec in enumerate(recommendations[:3], 1):
                    score = rec.get('similarity_score', 'N/A')
                    title = rec.get('title', 'Titre inconnu')
                    author = rec.get('author', 'Auteur inconnu')
                    rec_type = rec.get('recommendation_type', 'Inconnu')
                    
                    print(f"   {i}. {title}")
                    print(f"      Auteur: {author}")
                    print(f"      Score: {score}")
                    print(f"      Type: {rec_type}")
                    print()
            else:
                print("❌ Aucune recommandation retournée")
                
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        print("💡 Vérifiez que le serveur backend est démarré sur le port 5001")
    
    # Test 2: Endpoint principal (nécessite une session)
    print("\n📋 Test 2: Endpoint principal (nécessite authentification)")
    print("-" * 55)
    
    try:
        response = requests.get(
            f"{api_url}/books/recommendations",
            headers={'X-Session-ID': 'test-session-id'},
            timeout=10
        )
        
        print(f"🔍 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                first_rec = data[0]
                has_score = 'similarity_score' in first_rec
                rec_type = first_rec.get('recommendation_type', 'Inconnu')
                
                print(f"✅ Endpoint principal accessible")
                print(f"📊 Recommandations retournées: {len(data)}")
                print(f"🎯 Premier résultat:")
                print(f"   - Titre: {first_rec.get('title', 'N/A')}")
                print(f"   - Type: {rec_type}")
                print(f"   - A un score: {has_score}")
                if has_score:
                    print(f"   - Score: {first_rec.get('similarity_score', 'N/A')}")
                
                # Vérifier si c'est du vrai Content-Based ou du fallback
                if rec_type == 'popular':
                    print("⚠️ Attention: Résultats de type 'popular' (fallback)")
                    print("💡 Cela peut indiquer un problème d'authentification ou de préférences")
                elif rec_type == 'content_based_tfidf':
                    print("✅ Vrais résultats Content-Based avec TF-IDF")
                    
            else:
                print("❌ Aucune recommandation retournée")
        else:
            print(f"⚠️ Status non-200, probablement normal (session invalide)")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 60)
    print("📝 Résumé:")
    print("   1. Pour voir les scores, utilisez: /books/test-recommendations")
    print("   2. Pour le vrai endpoint, connectez-vous d'abord")
    print("   3. Vérifiez les logs du backend pour plus de détails")
    print("=" * 60)

if __name__ == '__main__':
    test_recommendations_endpoint() 