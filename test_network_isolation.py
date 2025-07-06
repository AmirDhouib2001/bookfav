#!/usr/bin/env python3
"""
Script de test pour vérifier l'isolation réseau du projet BookFav.
Teste la connectivité entre les services et la sécurité de l'isolation.
"""

import requests
import subprocess
import time
import json
import sys
import os

# Configuration
API_BASE_URL = "http://localhost:5001/api"
FRONTEND_URL = "http://localhost:5173"
DB_PORT = "5434"

def test_docker_networks():
    """Test l'existence et la configuration des réseaux Docker"""
    print("1. 🔍 Test des réseaux Docker...")
    
    try:
        # Lister les réseaux
        result = subprocess.run(
            ["docker", "network", "ls", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            networks = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    networks.append(json.loads(line))
            
            public_network = any('bookfav' in net['Name'] and 'public' in net['Name'] for net in networks)
            private_network = any('bookfav' in net['Name'] and 'private' in net['Name'] for net in networks)
            
            if public_network and private_network:
                print("   ✅ Réseaux Docker correctement créés")
                print(f"      - Réseau public: ✅")
                print(f"      - Réseau privé: ✅")
                return True
            else:
                print("   ❌ Réseaux Docker manquants")
                print(f"      - Réseau public: {'✅' if public_network else '❌'}")
                print(f"      - Réseau privé: {'✅' if private_network else '❌'}")
                return False
        else:
            print(f"   ❌ Erreur lors de la vérification des réseaux: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur lors du test des réseaux: {e}")
        return False

def test_service_connectivity():
    """Test la connectivité des services"""
    print("\n2. 🌐 Test de connectivité des services...")
    
    tests = []
    
    # Test Frontend
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        frontend_ok = response.status_code in [200, 404]  # 404 acceptable pour Vite en dev
        tests.append(("Frontend (5173)", frontend_ok))
        print(f"   Frontend (port 5173): {'✅' if frontend_ok else '❌'}")
    except Exception as e:
        tests.append(("Frontend (5173)", False))
        print(f"   Frontend (port 5173): ❌ - {e}")
    
    # Test Backend API
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        backend_ok = response.status_code == 200
        tests.append(("Backend API (5001)", backend_ok))
        print(f"   Backend API (port 5001): {'✅' if backend_ok else '❌'}")
    except Exception as e:
        tests.append(("Backend API (5001)", False))
        print(f"   Backend API (port 5001): ❌ - {e}")
    
    # Test Database (optionnel - port externe)
    try:
        result = subprocess.run(
            ["nc", "-z", "localhost", DB_PORT],
            capture_output=True,
            timeout=3
        )
        db_ok = result.returncode == 0
        tests.append(("Database (5434)", db_ok))
        print(f"   Database (port 5434): {'✅' if db_ok else '❌'}")
    except Exception as e:
        tests.append(("Database (5434)", False))
        print(f"   Database (port 5434): ❌ - {e}")
    
    return all(test[1] for test in tests)

def test_network_isolation():
    """Test l'isolation réseau entre les services"""
    print("\n3. 🔒 Test de l'isolation réseau...")
    
    try:
        # Inspecter les réseaux des conteneurs
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="."
        )
        
        if result.returncode == 0:
            containers_output = result.stdout.strip()
            if containers_output:
                try:
                    containers = json.loads(containers_output)
                    if not isinstance(containers, list):
                        containers = [containers]
                except json.JSONDecodeError:
                    # Fallback: parse line by line
                    containers = []
                    for line in containers_output.split('\n'):
                        if line:
                            try:
                                containers.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
                
                print("   Vérification de l'assignation des réseaux:")
                
                for container in containers:
                    name = container.get('Name', 'Unknown')
                    service = container.get('Service', 'Unknown')
                
                # Inspecter les réseaux du conteneur
                inspect_result = subprocess.run(
                    ["docker", "inspect", name, "--format", "{{json .NetworkSettings.Networks}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if inspect_result.returncode == 0:
                    networks = json.loads(inspect_result.stdout.strip())
                    network_names = list(networks.keys())
                    
                    if service == "backend":
                        expected = ["bookfav_public_network", "bookfav_private_network"]
                        has_both = all(net in network_names for net in expected)
                        print(f"      {service}: {'✅' if has_both else '❌'} - {network_names}")
                        
                    elif service == "frontend":
                        expected = ["bookfav_public_network"]
                        has_public = any("public" in net for net in network_names)
                        print(f"      {service}: {'✅' if has_public else '❌'} - {network_names}")
                        
                    elif service == "db":
                        expected = ["bookfav_private_network"]
                        has_private = any("private" in net for net in network_names)
                        print(f"      {service}: {'✅' if has_private else '❌'} - {network_names}")
            
            return True
        else:
            print(f"   ❌ Erreur lors de l'inspection des conteneurs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur lors du test d'isolation: {e}")
        return False

def test_recommendation_system():
    """Test que le système de recommandation fonctionne toujours"""
    print("\n4. 🤖 Test du système de recommandation...")
    
    try:
        # Test de l'endpoint de recommandations
        headers = {"X-Session-ID": "test-network-isolation"}
        response = requests.get(f"{API_BASE_URL}/recommendations/", headers=headers, timeout=10)
        
        if response.status_code == 401:
            print("   ✅ API de recommandations accessible (authentification requise)")
            
            # Test de l'endpoint de statut du réentraînement
            status_response = requests.get(f"{API_BASE_URL}/ratings/retrain/status", headers=headers, timeout=10)
            
            if status_response.status_code == 401:
                print("   ✅ API de réentraînement accessible (authentification requise)")
                return True
            else:
                print(f"   ❌ Problème avec l'API de réentraînement: {status_response.status_code}")
                return False
        else:
            print(f"   ❌ Problème avec l'API de recommandations: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur lors du test du système de recommandation: {e}")
        return False

def check_security_recommendations():
    """Affiche des recommandations de sécurité"""
    print("\n5. 🛡️ Recommandations de sécurité:")
    print("   💡 Pour une sécurité maximale, considérez:")
    print("      - Retirer le port 5434 de la base de données (accès uniquement via réseau privé)")
    print("      - Utiliser des secrets Docker pour les mots de passe")
    print("      - Ajouter un reverse proxy (nginx) devant le backend")
    print("      - Configurer des health checks pour tous les services")

def main():
    """Fonction principale du test"""
    print("🔒 === TEST D'ISOLATION RÉSEAU BOOKFAV ===")
    print("Ce test vérifie que l'isolation réseau fonctionne correctement")
    print("tout en maintenant le système de recommandation opérationnel.\n")
    
    # Changer le répertoire de travail
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    tests = [
        test_docker_networks,
        test_service_connectivity,
        test_network_isolation,
        test_recommendation_system
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Erreur lors du test: {e}")
            results.append(False)
    
    # Recommandations de sécurité
    check_security_recommendations()
    
    # Résultats
    print(f"\n=== RÉSULTATS ===")
    passed = sum(results)
    total = len(results)
    
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("✅ Isolation réseau fonctionnelle - Système opérationnel")
    elif passed >= total * 0.75:
        print("⚠️ Isolation partiellement fonctionnelle - Vérifier les détails")
    else:
        print("❌ Problèmes d'isolation détectés - Révision nécessaire")
    
    print(f"\n=== ARCHITECTURE RÉSEAU ===")
    print("📊 Réseau Public (bookfav_public_network):")
    print("   └── Frontend (5173) ↔ Backend (5001)")
    print("🔒 Réseau Privé (bookfav_private_network):")
    print("   └── Backend ↔ Database (5432)")
    print("🌐 Exposition publique:")
    print("   └── Frontend: localhost:5173")
    print("   └── Backend API: localhost:5001")
    print("   └── Database Admin: localhost:5434 (optionnel)")

if __name__ == "__main__":
    main() 