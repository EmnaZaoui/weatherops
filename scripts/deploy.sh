#!/bin/bash
# =============================================
# WeatherOps — Script de déploiement automatisé
# =============================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log()    { echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $1"; }
success(){ echo -e "${GREEN}✔ $1${NC}"; }
warn()   { echo -e "${YELLOW}⚠ $1${NC}"; }
error()  { echo -e "${RED}✘ $1${NC}"; exit 1; }

echo -e "${BOLD}${CYAN}"
echo "  ██╗    ██╗███████╗ █████╗ ████████╗██╗  ██╗███████╗██████╗  ██████╗ ██████╗ ███████╗"
echo "  ██║    ██║██╔════╝██╔══██╗╚══██╔══╝██║  ██║██╔════╝██╔══██╗██╔═══██╗██╔══██╗██╔════╝"
echo "  ██║ █╗ ██║█████╗  ███████║   ██║   ███████║█████╗  ██████╔╝██║   ██║██████╔╝███████╗"
echo "  ██║███╗██║██╔══╝  ██╔══██║   ██║   ██╔══██║██╔══╝  ██╔══██╗██║   ██║██╔═══╝ ╚════██║"
echo "  ╚███╔███╔╝███████╗██║  ██║   ██║   ██║  ██║███████╗██║  ██║╚██████╔╝██║     ███████║"
echo "   ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝"
echo -e "${NC}"
echo -e "${BOLD}         Déploiement Automatisé — $(date '+%d/%m/%Y %H:%M:%S')${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ===== ÉTAPE 1: Vérifications préalables =====
log "Étape 1/6 : Vérification de l'environnement..."

command -v docker >/dev/null 2>&1 || error "Docker n'est pas installé"
command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 || error "Docker Compose n'est pas disponible"

success "Docker $(docker --version | cut -d' ' -f3 | tr -d ',')"
success "Docker Compose $(docker compose version --short)"

# ===== ÉTAPE 2: Fichier .env =====
log "Étape 2/6 : Configuration de l'environnement..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        warn ".env créé depuis .env.example (mode démo actif)"
        warn "Ajoutez votre clé OpenWeatherMap dans .env pour les données réelles"
    else
        error "Fichier .env.example introuvable"
    fi
else
    success "Fichier .env trouvé"
fi

# Charger les variables
export $(grep -v '^#' .env | xargs) 2>/dev/null || true

if [ "${OPENWEATHER_API_KEY}" = "demo" ] || [ -z "${OPENWEATHER_API_KEY}" ]; then
    warn "Mode DÉMO actif (données simulées). Ajoutez une vraie clé dans .env"
else
    success "Clé API OpenWeatherMap configurée"
fi

# ===== ÉTAPE 3: Arrêt des anciens conteneurs =====
log "Étape 3/6 : Arrêt des anciens conteneurs..."

if docker compose ps --quiet 2>/dev/null | grep -q .; then
    docker compose down --remove-orphans
    success "Anciens conteneurs arrêtés"
else
    success "Aucun conteneur à arrêter"
fi

# ===== ÉTAPE 4: Build de l'image =====
log "Étape 4/6 : Build de l'image Docker..."

docker compose build --no-cache
success "Image WeatherOps construite"

# ===== ÉTAPE 5: Lancement des services =====
log "Étape 5/6 : Démarrage des services..."

docker compose up -d

# Attendre que le service soit healthy
log "Attente du démarrage (max 60s)..."
MAX_WAIT=60
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' weatherops_app 2>/dev/null || echo "starting")
    if [ "$STATUS" = "healthy" ]; then
        success "Service WeatherOps opérationnel !"
        break
    fi
    sleep 3
    ELAPSED=$((ELAPSED + 3))
    echo -ne "  ⏳ ${ELAPSED}s/${MAX_WAIT}s...\r"
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    warn "Timeout atteint — vérification manuelle nécessaire"
    docker compose logs --tail=20 weatherops
fi

# ===== ÉTAPE 6: Vérification finale =====
log "Étape 6/6 : Vérification de santé..."

sleep 2
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    success "API répond sur http://localhost:8000"
else
    warn "API pas encore prête (code: $HTTP_STATUS)"
fi

HTTP_NGINX=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80 2>/dev/null || echo "000")
if [ "$HTTP_NGINX" = "200" ]; then
    success "Nginx répond sur http://localhost:80"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}${BOLD}  ✅ DÉPLOIEMENT TERMINÉ${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  🌍 Dashboard  : ${CYAN}http://localhost${NC}"
echo -e "  🔌 API        : ${CYAN}http://localhost:8000${NC}"
echo -e "  📖 API Docs   : ${CYAN}http://localhost:8000/docs${NC}"
echo -e "  ❤️  Health     : ${CYAN}http://localhost:8000/health${NC}"
echo ""
echo -e "  Logs en direct : ${YELLOW}docker compose logs -f weatherops${NC}"
echo -e "  Arrêt          : ${YELLOW}docker compose down${NC}"
<<<<<<< HEAD
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
=======
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
