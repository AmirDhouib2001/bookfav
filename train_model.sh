#!/bin/bash

# Script pour entraîner le modèle de recommandation avec Docker
# Usage: ./train_model.sh [OPTIONS]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
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

# Fonction d'aide
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --service     Utiliser le service trainer dédié (intelligent)"
    echo "  --force       Forcer le réentraînement même si un modèle existe"
    echo "  --exec        Exécuter dans le conteneur backend existant"
    echo "  --manual      Entraînement manuel avec docker_train.py"
    echo "  --interactive Ouvrir un shell interactif dans le conteneur"
    echo "  --status      Vérifier l'état des conteneurs et des modèles"
    echo "  --logs        Afficher les logs du service trainer"
    echo "  --help        Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 --service              # Entraînement intelligent (recommandé)"
    echo "  $0 --force                # Forcer un nouveau modèle"
    echo "  $0 --exec                 # Entraîner dans le conteneur backend"
    echo "  $0 --status               # Vérifier l'état des modèles"
    echo ""
    echo "Mode intelligent (par défaut):"
    echo "  - N'entraîne que si aucun modèle n'existe"
    echo "  - Ou si le modèle est trop ancien (>30 jours)"
    echo "  - Utilise le modèle existant sinon"
    echo ""
}

# Vérifier si Docker Compose est disponible
check_docker_compose() {
    if command -v "docker" >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    elif command -v "docker-compose" >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker-compose"
    else
        log_error "Docker Compose n'est pas installé ou n'est pas dans le PATH"
        exit 1
    fi
    log_info "Utilisation de: $DOCKER_COMPOSE"
}

# Vérifier l'état des conteneurs
check_containers() {
    log_info "Vérification de l'état des conteneurs..."
    $DOCKER_COMPOSE ps
    
    # Vérifier si la base de données est en cours d'exécution
    if ! $DOCKER_COMPOSE ps | grep -q "db.*running"; then
        log_error "Le conteneur de base de données n'est pas en cours d'exécution"
        log_info "Démarrez vos conteneurs avec: $DOCKER_COMPOSE up -d"
        exit 1
    fi
    
    log_success "Conteneurs opérationnels"
}

# Vérifier l'état des modèles
check_model_status() {
    log_info "Vérification de l'état des modèles..."
    
    if [ -f "models/collaborative_filtering_model.h5" ] && [ -f "models/collaborative_filtering_metadata.pkl" ]; then
        model_date=$(stat -c %Y "models/collaborative_filtering_model.h5" 2>/dev/null || stat -f %m "models/collaborative_filtering_model.h5" 2>/dev/null)
        current_date=$(date +%s)
        age_days=$(( (current_date - model_date) / 86400 ))
        
        log_success "Modèle existant trouvé"
        log_info "Âge du modèle: $age_days jours"
        
        if [ $age_days -gt 30 ]; then
            log_warning "Modèle ancien (>30 jours) - réentraînement recommandé"
        else
            log_success "Modèle récent - prêt à l'emploi"
        fi
    else
        log_warning "Aucun modèle trouvé - entraînement nécessaire"
    fi
    
    # Afficher la taille du dossier models
    if [ -d "models" ]; then
        size=$(du -sh models 2>/dev/null | cut -f1)
        log_info "Taille du dossier models: $size"
    fi
}

# Entraîner avec le service dédié (mode intelligent)
train_with_service() {
    local force_flag=""
    
    if [ "$1" = "--force" ]; then
        log_info "Mode forcé activé - le modèle sera réentraîné"
        # Modifier temporairement le service pour forcer l'entraînement
        log_info "Entraînement avec le service trainer dédié (mode forcé)..."
        $DOCKER_COMPOSE --profile training run --rm trainer python smart_train.py --force
    else
        log_info "Entraînement avec le service trainer dédié (mode intelligent)..."
        $DOCKER_COMPOSE --profile training up trainer
    fi
    
    log_success "Service trainer terminé"
}

# Entraîner dans le conteneur backend existant
train_with_exec() {
    log_info "Entraînement dans le conteneur backend existant..."
    
    # Vérifier si le conteneur backend est en cours d'exécution
    if ! $DOCKER_COMPOSE ps | grep -q "backend.*running"; then
        log_error "Le conteneur backend n'est pas en cours d'exécution"
        exit 1
    fi
    
    # Exécuter le script d'entraînement intelligent
    log_info "Exécution du script d'entraînement intelligent..."
    $DOCKER_COMPOSE exec backend python smart_train.py
    
    log_success "Entraînement terminé dans le conteneur backend"
}

# Entraînement manuel
train_manual() {
    log_info "Entraînement manuel avec docker_train.py..."
    
    if ! $DOCKER_COMPOSE ps | grep -q "backend.*running"; then
        log_error "Le conteneur backend n'est pas en cours d'exécution"
        exit 1
    fi
    
    $DOCKER_COMPOSE exec backend python docker_train.py
    
    log_success "Entraînement manuel terminé"
}

# Ouvrir un shell interactif
open_interactive_shell() {
    log_info "Ouverture d'un shell interactif dans le conteneur backend..."
    
    if ! $DOCKER_COMPOSE ps | grep -q "backend.*running"; then
        log_error "Le conteneur backend n'est pas en cours d'exécution"
        exit 1
    fi
    
    log_info "Shell interactif ouvert. Commandes utiles:"
    log_info "  python smart_train.py          # Entraînement intelligent"
    log_info "  python smart_train.py --force  # Forcer l'entraînement"
    log_info "  python docker_train.py         # Entraînement manuel"
    log_info "  ls -la models/                 # Voir les modèles"
    log_info "  exit                           # Quitter le shell"
    
    $DOCKER_COMPOSE exec backend bash
}

# Afficher les logs du service trainer
show_trainer_logs() {
    log_info "Affichage des logs du service trainer..."
    $DOCKER_COMPOSE --profile training logs trainer
}

# Script principal
main() {
    check_docker_compose
    
    case "$1" in
        --service)
            check_containers
            train_with_service
            ;;
        --force)
            check_containers
            train_with_service --force
            ;;
        --exec)
            check_containers
            train_with_exec
            ;;
        --manual)
            check_containers
            train_manual
            ;;
        --interactive)
            check_containers
            open_interactive_shell
            ;;
        --status)
            check_containers
            check_model_status
            ;;
        --logs)
            show_trainer_logs
            ;;
        --help|"")
            show_help
            ;;
        *)
            log_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
}

# Changer vers le répertoire du script
cd "$(dirname "$0")"

# Exécuter le script principal
main "$@" 