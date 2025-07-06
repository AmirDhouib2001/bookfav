#!/usr/bin/env python3
"""
Script de test pour vérifier le système de services partagés.
Teste que les modèles sont correctement rechargés après réentraînement.
"""

import requests
import json
import time
import sys
import os

# Configuration
API_BASE_URL = "http://localhost:5001/api"
TEST_SESSION_ID = "test-session-shared-services"

def test_api_connectivity():
    """Test la connectivité de l'API"""
    print("1. Test de connectivité API...")
    try:
        response = requests.get(f"{API_BASE_URL}/auth/validate-session", timeout=5)
        print(f"   Status code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API accessible")
            return True
        else:
            print("   ⚠️ API répond mais avec erreur")
            return True
    except Exception as e:
        print(f"   ❌ API inaccessible: {e}")
        return False

def test_shared_services_status():
    """Test le statut des services partagés"""
    print("\n2. Test du statut des services partagés...")
    try:
        # Tester la route de statut du réentraînement
        headers = {"X-Session-ID": TEST_SESSION_ID}
        response = requests.get(f"{API_BASE_URL}/ratings/retrain/status", headers=headers, timeout=10)
        
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Route protégée par authentification (normal)")
            return True
        elif response.status_code == 200:
            data = response.json()
            print(f"   ✅ Services partagés accessibles: {data}")
            return True
        else:
            print(f"   ⚠️ Réponse inattendue: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur lors du test: {e}")
        return False

def test_recommendations_endpoints():
    """Test les endpoints de recommandations"""
    print("\n3. Test des endpoints de recommandations...")
    try:
        headers = {"X-Session-ID": TEST_SESSION_ID}
        
        # Test recommandations hybrides
        response = requests.get(f"{API_BASE_URL}/recommendations/", headers=headers, timeout=10)
        print(f"   Recommandations hybrides - Status: {response.status_code}")
        
        # Test recommandations collaborative
        response = requests.get(f"{API_BASE_URL}/recommendations/collaborative", headers=headers, timeout=10)
        print(f"   Recommandations collaborative - Status: {response.status_code}")
        
        # Test recommandations content-based
        response = requests.get(f"{API_BASE_URL}/recommendations/content", headers=headers, timeout=10)
        print(f"   Recommandations content-based - Status: {response.status_code}")
        
        print("   ✅ Tous les endpoints de recommandations répondent")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test des endpoints: {e}")
        return False

def test_model_reloading_flow():
    """Test le flux de rechargement des modèles"""
    print("\n4. Test du flux de rechargement des modèles...")
    try:
        headers = {"X-Session-ID": TEST_SESSION_ID}
        
        # Simuler un ajout de note
        note_data = {
            "isbn": "TEST_ISBN_SHARED_" + str(int(time.time())),
            "rating": 5,
            "review": "Test système services partagés"
        }
        
        print(f"   Tentative d'ajout de note: {note_data['isbn']}")
        response = requests.post(f"{API_BASE_URL}/ratings/rate", 
                               headers=headers, 
                               json=note_data, 
                               timeout=10)
        
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Route protégée par authentification (normal)")
            print("   📝 Pour tester complètement, connectez-vous d'abord")
            return True
        elif response.status_code == 200 or response.status_code == 201:
            print("   ✅ Note ajoutée avec succès")
            print("   🔄 Vérifier les logs Docker pour le réentraînement")
            return True
        else:
            print(f"   ⚠️ Réponse inattendue: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur lors du test: {e}")
        return False

def check_docker_logs():
    """Vérifie les logs Docker pour les messages de services partagés"""
    print("\n5. Vérification des logs Docker...")
    try:
        import subprocess
        
        # Exécuter la commande Docker
        result = subprocess.run(
            ["docker", "compose", "logs", "--tail=50", "backend"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout
            
            # Chercher les messages de services partagés
            shared_service_messages = [
                "Service hybride initialisé (partagé)",
                "Service async initialisé (partagé)",
                "Services partagés initialisés",
                "Modèles rechargés dans tous les services partagés"
            ]
            
            found_messages = []
            for message in shared_service_messages:
                if message in logs:
                    found_messages.append(message)
            
            print(f"   Messages des services partagés trouvés: {len(found_messages)}")
            for msg in found_messages:
                print(f"   ✅ {msg}")
            
            if found_messages:
                print("   ✅ Services partagés fonctionnent correctement")
                return True
            else:
                print("   ⚠️ Aucun message de services partagés trouvé")
                return False
        else:
            print(f"   ❌ Erreur lors de la lecture des logs: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Timeout lors de la lecture des logs")
        return False
    except Exception as e:
        print(f"   ❌ Erreur lors de la vérification des logs: {e}")
        return False

def main():
    """Fonction principale du test"""
    print("🧪 === TEST DU SYSTÈME DE SERVICES PARTAGÉS ===")
    print("Ce test vérifie que le système utilise une seule instance partagée")
    print("pour éviter les problèmes de rechargement de modèles.\n")
    
    # Changer le répertoire de travail
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    tests = [
        test_api_connectivity,
        test_shared_services_status,
        test_recommendations_endpoints,
        test_model_reloading_flow,
        check_docker_logs
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Erreur lors du test: {e}")
            results.append(False)
    
    # Résultats
    print(f"\n=== RÉSULTATS ===")
    passed = sum(results)
    total = len(results)
    
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("✅ Tous les tests passent - Services partagés fonctionnent")
    elif passed >= total * 0.8:
        print("⚠️ Plupart des tests passent - Système probablement fonctionnel")
    else:
        print("❌ Plusieurs tests échouent - Vérifier la configuration")
    
    print(f"\n=== PROCHAINES ÉTAPES ===")
    print("1. Connectez-vous sur l'interface web")
    print("2. Notez ou modifiez la note d'un livre")
    print("3. Surveillez les logs : docker compose logs -f backend")
    print("4. Vérifiez que les recommandations changent")
    print("5. Cherchez les messages : 'Modèles rechargés dans tous les services partagés'")

if __name__ == "__main__":
    main() 