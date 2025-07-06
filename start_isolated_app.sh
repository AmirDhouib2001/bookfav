#!/bin/bash

# Script de démarrage pour BookFav avec isolation réseau
# Gère le démarrage et l'arrêt de l'application avec les réseaux isolés

set -e

# Variables
PROJECT_NAME="bookfav"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages colorés
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction pour afficher l'aide
show_help() {
    cat << EOF
🔒 Script de démarrage BookFav avec isolation réseau

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  start       Démarre l'application avec isolation réseau
  stop        Arrête l'application
  restart     Redémarre l'application
  status      Affiche le statut des services
  logs        Affiche les logs des services
  test        Lance les tests d'isolation réseau
  clean       Nettoie les conteneurs et réseaux
  help        Affiche cette aide

Options:
  -d, --detach    Démarre en arrière-plan (par défaut)
  -f, --follow    Suit les logs en temps réel
  -v, --verbose   Mode verbeux
  --no-cache      Reconstruction sans cache

Examples:
  $0 start                    # Démarre l'application
  $0 logs -f                  # Suit les logs en temps réel
  $0 test                     # Lance les tests d'isolation
  $0 clean                    # Nettoie tout

Architecture réseau:
  📊 Réseau Public : Frontend ↔ Backend
  🔒 Réseau Privé : Backend ↔ Database
  🌐 Ports exposés : 5173 (Frontend), 5001 (Backend), 5434 (DB Admin)
EOF
}

# Fonction pour vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé ou n'est pas dans le PATH"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose n'est pas installé ou n'est pas dans le PATH"
        exit 1
    fi
    
    # Vérifier le fichier docker-compose.yml
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "Fichier docker-compose.yml introuvable: $DOCKER_COMPOSE_FILE"
        exit 1
    fi
    
    # Vérifier les permissions Docker
    if ! docker info &> /dev/null; then
        log_error "Impossible d'accéder au daemon Docker. Vérifiez vos permissions."
        exit 1
    fi
    
    log_success "Prérequis validés"
}

# Fonction pour démarrer l'application
start_app() {
    log_info "Démarrage de l'application BookFav avec isolation réseau..."
    
    cd "$SCRIPT_DIR"
    
    # Créer les réseaux si nécessaire
    log_info "Création des réseaux isolés..."
    
    # Vérifier la configuration réseau
    if ! docker network ls | grep -q "bookfav_public_network"; then
        log_info "Création du réseau public..."
    fi
    
    if ! docker network ls | grep -q "bookfav_private_network"; then
        log_info "Création du réseau privé..."
    fi
    
    # Démarrer les services
    if [ "$DETACH" = true ]; then
        docker compose up -d
    else
        docker compose up
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Application démarrée avec succès!"
        log_info "Services disponibles:"
        log_info "  - Frontend: http://localhost:5173"
        log_info "  - Backend API: http://localhost:5001"
        log_info "  - Database Admin: localhost:5434"
        log_info ""
        log_info "Architecture réseau:"
        log_info "  📊 Réseau Public: Frontend ↔ Backend"
        log_info "  🔒 Réseau Privé: Backend ↔ Database"
    else
        log_error "Erreur lors du démarrage de l'application"
        exit 1
    fi
}

# Fonction pour arrêter l'application
stop_app() {
    log_info "Arrêt de l'application BookFav..."
    
    cd "$SCRIPT_DIR"
    docker compose down
    
    if [ $? -eq 0 ]; then
        log_success "Application arrêtée avec succès!"
    else
        log_error "Erreur lors de l'arrêt de l'application"
        exit 1
    fi
}

# Fonction pour redémarrer l'application
restart_app() {
    log_info "Redémarrage de l'application BookFav..."
    stop_app
    sleep 2
    start_app
}

# Fonction pour afficher le statut
show_status() {
    log_info "Statut des services BookFav..."
    
    cd "$SCRIPT_DIR"
    docker compose ps
    
    echo ""
    log_info "Statut des réseaux:"
    docker network ls | grep bookfav || log_warning "Aucun réseau BookFav trouvé"
}

# Fonction pour afficher les logs
show_logs() {
    log_info "Logs des services BookFav..."
    
    cd "$SCRIPT_DIR"
    if [ "$FOLLOW" = true ]; then
        docker compose logs -f
    else
        docker compose logs
    fi
}

# Fonction pour lancer les tests
run_tests() {
    log_info "Lancement des tests d'isolation réseau..."
    
    cd "$SCRIPT_DIR"
    
    # Vérifier si Python est disponible
    if command -v python3 &> /dev/null; then
        python3 test_network_isolation.py
    else
        log_error "Python3 n'est pas disponible pour lancer les tests"
        exit 1
    fi
}

# Fonction pour nettoyer
clean_app() {
    log_info "Nettoyage des conteneurs et réseaux BookFav..."
    
    cd "$SCRIPT_DIR"
    
    # Arrêter et supprimer les conteneurs
    docker compose down -v --remove-orphans
    
    # Supprimer les réseaux personnalisés
    docker network rm bookfav_public_network bookfav_private_network 2>/dev/null || true
    
    # Nettoyer les images non utilisées (optionnel)
    if [ "$VERBOSE" = true ]; then
        docker system prune -f
    fi
    
    log_success "Nettoyage terminé!"
}

# Variables par défaut
DETACH=true
FOLLOW=false
VERBOSE=false
NO_CACHE=false

# Traitement des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        start)
            COMMAND="start"
            shift
            ;;
        stop)
            COMMAND="stop"
            shift
            ;;
        restart)
            COMMAND="restart"
            shift
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        logs)
            COMMAND="logs"
            shift
            ;;
        test)
            COMMAND="test"
            shift
            ;;
        clean)
            COMMAND="clean"
            shift
            ;;
        help|--help|-h)
            show_help
            exit 0
            ;;
        -d|--detach)
            DETACH=true
            shift
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        *)
            log_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Commande par défaut
if [ -z "$COMMAND" ]; then
    COMMAND="start"
fi

# Vérifier les prérequis
check_prerequisites

# Exécuter la commande
case $COMMAND in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    test)
        run_tests
        ;;
    clean)
        clean_app
        ;;
    *)
        log_error "Commande inconnue: $COMMAND"
        show_help
        exit 1
        ;;
esac 