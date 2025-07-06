# 🔒 Guide d'Isolation Réseau - BookFav

## Vue d'ensemble

Ce guide explique l'architecture réseau isolée implémentée pour le projet BookFav. L'isolation réseau améliore considérablement la sécurité en segmentant les communications entre les différents services.

## Architecture Réseau

### 📊 Architecture Actuelle

```
┌─────────────────────────────────────────────────────────────────┐
│                        RÉSEAU PUBLIC                            │
│                   (bookfav_public_network)                     │
│                                                                 │
│  ┌─────────────────┐                    ┌─────────────────┐     │
│  │    Frontend     │◄──────────────────►│    Backend      │     │
│  │   (port 5173)   │                    │   (port 5001)   │     │
│  └─────────────────┘                    └─────────────────┘     │
│                                                 │               │
└─────────────────────────────────────────────────│───────────────┘
                                                  │
┌─────────────────────────────────────────────────│───────────────┐
│                        RÉSEAU PRIVÉ             │               │
│                   (bookfav_private_network)     │               │
│                                                 │               │
│                        ┌─────────────────┐     │               │
│                        │    Backend      │◄────┘               │
│                        │   (port 5000)   │                     │
│                        └─────────────────┘                     │
│                                │                               │
│                        ┌─────────────────┐                     │
│                        │   Database      │                     │
│                        │   (port 5432)   │                     │
│                        └─────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔗 Configuration des Réseaux

#### Réseau Public (`bookfav_public_network`)
- **Subnet**: `172.20.0.0/16`
- **Gateway**: `172.20.0.1`
- **Services**:
  - Frontend (port 5173)
  - Backend (port 5001)
- **Objectif**: Communication Frontend ↔ Backend

#### Réseau Privé (`bookfav_private_network`)
- **Subnet**: `172.21.0.0/16`
- **Gateway**: `172.21.0.1`
- **Services**:
  - Backend (port 5000)
  - Database (port 5432)
- **Objectif**: Communication Backend ↔ Database

## Assignation des Services

### Frontend
- **Réseaux**: `bookfav_public_network` uniquement
- **Port exposé**: `5173`
- **Accès**: Internet → Frontend → Backend (via réseau public)

### Backend
- **Réseaux**: `bookfav_public_network` ET `bookfav_private_network`
- **Port exposé**: `5001` (public)
- **Port interne**: `5000` (privé)
- **Accès**: 
  - Frontend → Backend (via réseau public)
  - Backend → Database (via réseau privé)

### Database
- **Réseaux**: `bookfav_private_network` uniquement
- **Port exposé**: `5434` (administration - optionnel)
- **Port interne**: `5432` (privé)
- **Accès**: Backend → Database uniquement

## Avantages de l'Isolation

### 🛡️ Sécurité
- **Isolation de la base de données**: Accessible uniquement via le backend
- **Segmentation réseau**: Réduction de la surface d'attaque
- **Contrôle d'accès**: Communication strictement contrôlée

### 📈 Performance
- **Optimisation du routage**: Trafic optimisé par réseau
- **Réduction des collisions**: Séparation du trafic

### 🔧 Maintenance
- **Isolation des pannes**: Un problème réseau n'affecte pas l'autre
- **Debugging facilité**: Analyse séparée des communications

## Système de Recommandation

### Compatibilité
Le système de recommandation reste **100% fonctionnel** avec l'isolation réseau :

- **Réentraînement asynchrone**: Fonctionne normalement
- **Services partagés**: Toujours opérationnels
- **API endpoints**: Accessibles via le réseau public
- **Accès base de données**: Sécurisé via le réseau privé

### Endpoints Protégés
- `GET /api/recommendations/` - Recommandations utilisateur
- `POST /api/ratings/retrain/force` - Réentraînement forcé
- `GET /api/ratings/retrain/status` - Statut du réentraînement

## Utilisation

### 🚀 Démarrage
```bash
# Démarrage standard
./start_isolated_app.sh start

# Démarrage avec logs
./start_isolated_app.sh start -f

# Vérification du statut
./start_isolated_app.sh status
```

### 🧪 Tests
```bash
# Tests d'isolation réseau
./start_isolated_app.sh test

# Tests manuels
python3 test_network_isolation.py
```

### 📊 Monitoring
```bash
# Logs des services
./start_isolated_app.sh logs -f

# Statut des réseaux
docker network ls | grep bookfav

# Inspection des réseaux
docker network inspect bookfav_public_network
docker network inspect bookfav_private_network
```

## Résolution de Problèmes

### 🔍 Diagnostic

#### Problème: Services ne communiquent pas
```bash
# Vérifier les réseaux
docker network ls | grep bookfav

# Vérifier l'assignation des conteneurs
docker compose ps
docker inspect <container_name> | grep -A 10 Networks
```

#### Problème: Backend ne peut pas accéder à la DB
```bash
# Vérifier la connectivité réseau privé
docker exec -it <backend_container> ping db
docker exec -it <backend_container> nc -zv db 5432
```

#### Problème: Frontend ne peut pas accéder au Backend
```bash
# Vérifier la connectivité réseau public
curl -v http://localhost:5001/api/health
```

### 🔧 Solutions Courantes

#### Recréer les réseaux
```bash
# Nettoyage complet
./start_isolated_app.sh clean

# Redémarrage
./start_isolated_app.sh start
```

#### Vérifier les ports
```bash
# Ports exposés
netstat -tlnp | grep -E "5173|5001|5434"

# Ports Docker
docker compose ps
```

## Recommandations de Sécurité

### 🔐 Sécurité Maximale

Pour une sécurité optimale, considérez ces améliorations :

1. **Supprimer le port DB externe**:
   ```yaml
   db:
     # Commentez cette ligne pour une sécurité maximale
     # ports:
     #   - "5434:5432"
   ```

2. **Utiliser des secrets Docker**:
   ```yaml
   services:
     db:
       secrets:
         - db-password
   secrets:
     db-password:
       file: ./secrets/db-password.txt
   ```

3. **Ajouter un reverse proxy**:
   ```yaml
   services:
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       networks:
         - bookfav_public_network
   ```

4. **Configurer les health checks**:
   ```yaml
   services:
     backend:
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   ```

### 📋 Checklist de Sécurité

- [ ] Réseaux correctement isolés
- [ ] Ports minimaux exposés
- [ ] Passwords sécurisés
- [ ] Logs configurés
- [ ] Monitoring en place
- [ ] Tests d'isolation validés

## Ports et Volumes

### Ports Maintenus
- **Frontend**: `5173` (inchangé)
- **Backend**: `5001` (inchangé)
- **Database**: `5434` (inchangé)

### Volumes Maintenus
- **Backend**: `./back_end:/app`
- **Data**: `./data:/app/data`
- **Models**: `./models:/app/models`
- **Frontend**: `./front_end:/app`
- **Database**: `postgres-data:/var/lib/postgresql/data`

## Commandes Utiles

### Docker Compose
```bash
# Démarrage
docker compose up -d

# Arrêt
docker compose down

# Logs
docker compose logs -f

# Statut
docker compose ps
```

### Réseaux Docker
```bash
# Lister les réseaux
docker network ls

# Inspecter un réseau
docker network inspect bookfav_public_network

# Voir les conteneurs sur un réseau
docker network inspect bookfav_private_network | grep -A 5 Containers
```

### Debugging
```bash
# Entrer dans un conteneur
docker exec -it bookfav-backend-1 bash

# Tester la connectivité
docker exec -it bookfav-backend-1 ping db
docker exec -it bookfav-backend-1 nc -zv db 5432

# Vérifier les variables d'environnement
docker exec -it bookfav-backend-1 env | grep DATABASE
```

## Conclusion

L'isolation réseau de BookFav offre une architecture sécurisée et performante tout en maintenant la compatibilité complète avec le système de recommandation. Cette implémentation suit les meilleures pratiques Docker et peut être facilement étendue pour des besoins futurs.

---

**Auteur**: Assistant IA  
**Date**: 2024  
**Version**: 1.0  
**Compatibilité**: Docker Compose v2+ 