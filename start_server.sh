#!/bin/bash

# Script de démarrage du serveur MCP GCP
# Ce script facilite le démarrage et la gestion du serveur

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Serveur MCP GCP Infrastructure Manager          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 trouvé: $(python3 --version)"

# Vérifier le fichier de credentials GCP
if [ ! -f "service-account-key.json" ]; then
    echo -e "${RED}✗ Fichier service-account-key.json non trouvé${NC}"
    echo -e "${YELLOW}  Veuillez placer votre clé de service GCP dans ce répertoire${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Credentials GCP trouvés"

# Vérifier les dépendances
echo -e "${YELLOW}Vérification des dépendances...${NC}"
if ! python3 -c "import flask, google.cloud.compute_v1, paramiko, python_terraform" &> /dev/null; then
    echo -e "${YELLOW}⚠ Certaines dépendances sont manquantes${NC}"
    echo -e "${YELLOW}  Installation des dépendances...${NC}"
    pip3 install -r requirements.txt
fi

echo -e "${GREEN}✓${NC} Toutes les dépendances sont installées"

# Créer le répertoire SSH si nécessaire
SSH_DIR="$HOME/.ssh_mcp"
if [ ! -d "$SSH_DIR" ]; then
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"
    echo -e "${GREEN}✓${NC} Répertoire SSH créé: $SSH_DIR"
else
    echo -e "${GREEN}✓${NC} Répertoire SSH existant: $SSH_DIR"
fi

# Vérifier si le serveur est déjà en cours d'exécution
if pgrep -f "mcp_server.py" > /dev/null; then
    echo -e "${YELLOW}⚠ Le serveur est déjà en cours d'exécution${NC}"
    echo -e "${YELLOW}  PID: $(pgrep -f mcp_server.py)${NC}"
    echo ""
    read -p "Voulez-vous redémarrer le serveur ? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Arrêt du serveur...${NC}"
        pkill -f "mcp_server.py"
        sleep 2
    else
        echo -e "${GREEN}Le serveur continue de tourner${NC}"
        exit 0
    fi
fi

# Afficher les informations
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo -e "  📁 Répertoire: $SCRIPT_DIR"
echo -e "  🔑 Clés SSH: $SSH_DIR"
echo -e "  🌍 Projet GCP: level-surfer-473817-p5"
echo -e "  📍 Zone: us-central1-a"
echo ""

# Options de démarrage
echo -e "${YELLOW}Comment voulez-vous démarrer le serveur ?${NC}"
echo "  1) Foreground (voir les logs en direct)"
echo "  2) Background (daemon)"
echo "  3) Annuler"
echo ""
read -p "Choix [1-3]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  Démarrage du serveur en mode foreground           ║${NC}"
        echo -e "${GREEN}║  Appuyez sur Ctrl+C pour arrêter                    ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
        echo ""
        python3 mcp_server.py
        ;;
    2)
        echo -e "${GREEN}Démarrage du serveur en arrière-plan...${NC}"
        nohup python3 mcp_server.py > mcp_server.log 2>&1 &
        SERVER_PID=$!
        sleep 2

        if ps -p $SERVER_PID > /dev/null; then
            echo -e "${GREEN}✓${NC} Serveur démarré avec succès"
            echo -e "  PID: $SERVER_PID"
            echo -e "  Logs: $SCRIPT_DIR/mcp_server.log"
            echo -e "  URL: http://0.0.0.0:5001"
            echo ""
            echo -e "${YELLOW}Commandes utiles:${NC}"
            echo -e "  • Voir les logs: tail -f $SCRIPT_DIR/mcp_server.log"
            echo -e "  • Arrêter: kill $SERVER_PID"
            echo -e "  • Status: ps -p $SERVER_PID"
        else
            echo -e "${RED}✗ Erreur au démarrage du serveur${NC}"
            echo -e "${YELLOW}Consultez les logs: cat mcp_server.log${NC}"
            exit 1
        fi
        ;;
    3)
        echo -e "${YELLOW}Annulé${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Choix invalide${NC}"
        exit 1
        ;;
esac
