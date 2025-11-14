#!/bin/bash

# Script helper pour gérer le serveur MCP GCP

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     MCP GCP Infrastructure Manager - Helper         ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Usage:${NC} $0 [commande]"
    echo ""
    echo -e "${GREEN}Commandes disponibles:${NC}"
    echo ""
    echo -e "  ${YELLOW}start${NC}         Démarrer le serveur"
    echo -e "  ${YELLOW}stop${NC}          Arrêter le serveur"
    echo -e "  ${YELLOW}restart${NC}       Redémarrer le serveur"
    echo -e "  ${YELLOW}status${NC}        Voir le statut du serveur"
    echo -e "  ${YELLOW}logs${NC}          Voir les logs en temps réel"
    echo -e "  ${YELLOW}health${NC}        Tester le endpoint health"
    echo -e "  ${YELLOW}keys${NC}          Lister les clés SSH"
    echo -e "  ${YELLOW}install${NC}       Installer/Réinstaller les dépendances"
    echo -e "  ${YELLOW}clean${NC}         Nettoyer les clés SSH et logs"
    echo -e "  ${YELLOW}help${NC}          Afficher cette aide"
    echo ""
    echo -e "${GREEN}Exemples:${NC}"
    echo -e "  $0 start          # Démarrer le serveur"
    echo -e "  $0 logs           # Voir les logs"
    echo -e "  $0 health         # Vérifier que le serveur fonctionne"
    echo ""
}

get_server_pid() {
    pgrep -f "mcp_server.py" || echo ""
}

start_server() {
    local pid=$(get_server_pid)
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}⚠ Le serveur est déjà en cours d'exécution (PID: $pid)${NC}"
        return 1
    fi

    echo -e "${GREEN}Démarrage du serveur...${NC}"
    cd "$SCRIPT_DIR"
    nohup python3 mcp_server.py > mcp_server.log 2>&1 &
    sleep 2

    pid=$(get_server_pid)
    if [ -n "$pid" ]; then
        echo -e "${GREEN}✓ Serveur démarré (PID: $pid)${NC}"
        echo -e "  URL: http://0.0.0.0:5001"
        echo -e "  Logs: $SCRIPT_DIR/mcp_server.log"
    else
        echo -e "${RED}✗ Échec du démarrage${NC}"
        echo -e "${YELLOW}Consultez les logs: cat $SCRIPT_DIR/mcp_server.log${NC}"
        return 1
    fi
}

stop_server() {
    local pid=$(get_server_pid)
    if [ -z "$pid" ]; then
        echo -e "${YELLOW}⚠ Le serveur n'est pas en cours d'exécution${NC}"
        return 1
    fi

    echo -e "${YELLOW}Arrêt du serveur (PID: $pid)...${NC}"
    kill "$pid"
    sleep 2

    if [ -z "$(get_server_pid)" ]; then
        echo -e "${GREEN}✓ Serveur arrêté${NC}"
    else
        echo -e "${RED}✗ Le serveur ne répond pas, arrêt forcé...${NC}"
        kill -9 "$pid"
        echo -e "${GREEN}✓ Serveur arrêté (force)${NC}"
    fi
}

restart_server() {
    echo -e "${BLUE}Redémarrage du serveur...${NC}"
    stop_server 2>/dev/null || true
    sleep 1
    start_server
}

show_status() {
    local pid=$(get_server_pid)

    echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Status du serveur MCP GCP                       ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ -n "$pid" ]; then
        echo -e "  Statut: ${GREEN}En cours d'exécution${NC}"
        echo -e "  PID: $pid"
        echo -e "  CPU/Mem: $(ps -p $pid -o %cpu,%mem | tail -n 1)"
        echo -e "  Uptime: $(ps -p $pid -o etime= | xargs)"
        echo -e "  URL: http://0.0.0.0:5001"
        echo ""

        # Tester le endpoint health
        if command -v curl &> /dev/null; then
            echo -e "${YELLOW}Test du endpoint health...${NC}"
            if curl -s http://localhost:5001/health > /dev/null; then
                echo -e "  Health: ${GREEN}✓ OK${NC}"
            else
                echo -e "  Health: ${RED}✗ Erreur${NC}"
            fi
        fi
    else
        echo -e "  Statut: ${RED}Arrêté${NC}"
    fi
    echo ""
}

show_logs() {
    if [ ! -f "$SCRIPT_DIR/mcp_server.log" ]; then
        echo -e "${YELLOW}⚠ Aucun fichier de log trouvé${NC}"
        return 1
    fi

    echo -e "${GREEN}Logs du serveur (Ctrl+C pour quitter):${NC}"
    echo ""
    tail -f "$SCRIPT_DIR/mcp_server.log"
}

check_health() {
    echo -e "${BLUE}Test du endpoint health...${NC}"

    if ! command -v curl &> /dev/null; then
        echo -e "${RED}✗ curl n'est pas installé${NC}"
        return 1
    fi

    local pid=$(get_server_pid)
    if [ -z "$pid" ]; then
        echo -e "${RED}✗ Le serveur n'est pas en cours d'exécution${NC}"
        return 1
    fi

    local response=$(curl -s http://localhost:5001/health)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Serveur OK${NC}"
        echo ""
        echo "$response" | python3 -m json.tool
    else
        echo -e "${RED}✗ Le serveur ne répond pas${NC}"
        return 1
    fi
}

list_ssh_keys() {
    local ssh_dir="$HOME/.ssh_mcp"

    echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Clés SSH disponibles                            ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ ! -d "$ssh_dir" ] || [ -z "$(ls -A $ssh_dir 2>/dev/null)" ]; then
        echo -e "${YELLOW}⚠ Aucune clé SSH trouvée${NC}"
        echo -e "  Répertoire: $ssh_dir"
        return 0
    fi

    echo -e "  Répertoire: $ssh_dir"
    echo ""

    for key_file in "$ssh_dir"/*; do
        if [[ $key_file != *.pub ]]; then
            local key_name=$(basename "$key_file")
            local key_size=$(wc -c < "$key_file")
            local key_date=$(stat -c %y "$key_file" 2>/dev/null || stat -f %Sm "$key_file" 2>/dev/null)

            echo -e "  ${GREEN}•${NC} $key_name"
            echo -e "    Taille: $key_size bytes"
            echo -e "    Date: $key_date"

            if [ -f "$key_file.pub" ]; then
                echo -e "    ${GREEN}✓${NC} Clé publique présente"
            else
                echo -e "    ${RED}✗${NC} Clé publique manquante"
            fi
            echo ""
        fi
    done
}

install_deps() {
    echo -e "${BLUE}Installation des dépendances...${NC}"
    cd "$SCRIPT_DIR"

    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}✗ Fichier requirements.txt non trouvé${NC}"
        return 1
    fi

    pip3 install -r requirements.txt

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Dépendances installées${NC}"
    else
        echo -e "${RED}✗ Erreur lors de l'installation${NC}"
        return 1
    fi
}

clean_data() {
    echo -e "${YELLOW}Cette opération va supprimer:${NC}"
    echo -e "  • Toutes les clés SSH dans ~/.ssh_mcp"
    echo -e "  • Les fichiers de logs"
    echo ""
    read -p "Êtes-vous sûr ? (y/N) " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Annulé${NC}"
        return 0
    fi

    # Supprimer les clés SSH
    if [ -d "$HOME/.ssh_mcp" ]; then
        rm -rf "$HOME/.ssh_mcp"
        echo -e "${GREEN}✓ Clés SSH supprimées${NC}"
    fi

    # Supprimer les logs
    if [ -f "$SCRIPT_DIR/mcp_server.log" ]; then
        rm "$SCRIPT_DIR/mcp_server.log"
        echo -e "${GREEN}✓ Logs supprimés${NC}"
    fi

    echo -e "${GREEN}✓ Nettoyage terminé${NC}"
}

# Main
case "${1:-help}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    health)
        check_health
        ;;
    keys)
        list_ssh_keys
        ;;
    install)
        install_deps
        ;;
    clean)
        clean_data
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Commande inconnue: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
