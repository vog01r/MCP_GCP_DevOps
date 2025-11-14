#!/usr/bin/env python3

"""
Serveur MCP pour GCP - Gestion d'infrastructure cloud avec SSH
Permet de déployer et gérer des VMs GCP en langage naturel via Claude
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from decimal import Decimal
import datetime
from pathlib import Path
import base64

# GCP imports
from google.cloud import compute_v1
from google.oauth2 import service_account

# SSH imports
import paramiko
from paramiko import SSHClient, AutoAddPolicy
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Terraform imports
from python_terraform import Terraform

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration GCP
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', '')
GCP_ZONE = os.getenv('GCP_ZONE', 'us-central1-a')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE', '')

# Répertoire pour stocker les clés SSH
SSH_KEYS_DIR = Path.home() / ".ssh_mcp"
SSH_KEYS_DIR.mkdir(exist_ok=True, mode=0o700)

# Dictionnaire en mémoire pour les clés SSH
ssh_keys_store = {}

# ====================================================================
# GESTION DES CLÉS SSH
# ====================================================================

def generate_ssh_key_pair(key_name):
    """Génère une paire de clés SSH (privée/publique)"""
    # Générer la clé privée
    key = rsa.generate_private_key(
        backend=default_backend(),
        public_exponent=65537,
        key_size=2048
    )

    # Clé privée au format PEM
    private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.Format.TraditionalOpenSSL,
        serialization.NoEncryption()
    ).decode('utf-8')

    # Clé publique au format OpenSSH
    public_key = key.public_key().public_bytes(
        serialization.Encoding.OpenSSH,
        serialization.Format.OpenSSH
    ).decode('utf-8')

    return private_key, public_key

def store_ssh_key(key_name, private_key, public_key, description=""):
    """Stocke une clé SSH de manière sécurisée"""
    # Stocker en mémoire
    ssh_keys_store[key_name] = {
        "private_key": private_key,
        "public_key": public_key,
        "description": description,
        "created_at": datetime.datetime.now().isoformat()
    }

    # Stocker sur disque de manière sécurisée
    private_key_file = SSH_KEYS_DIR / f"{key_name}"
    public_key_file = SSH_KEYS_DIR / f"{key_name}.pub"

    private_key_file.write_text(private_key)
    private_key_file.chmod(0o600)

    public_key_file.write_text(public_key)
    public_key_file.chmod(0o644)

    return True

def load_ssh_key(key_name):
    """Charge une clé SSH depuis le stockage"""
    if key_name in ssh_keys_store:
        return ssh_keys_store[key_name]

    # Essayer de charger depuis le disque
    private_key_file = SSH_KEYS_DIR / key_name
    public_key_file = SSH_KEYS_DIR / f"{key_name}.pub"

    if private_key_file.exists() and public_key_file.exists():
        private_key = private_key_file.read_text()
        public_key = public_key_file.read_text()

        ssh_keys_store[key_name] = {
            "private_key": private_key,
            "public_key": public_key,
            "description": "Loaded from disk",
            "created_at": datetime.datetime.fromtimestamp(
                private_key_file.stat().st_ctime
            ).isoformat()
        }

        return ssh_keys_store[key_name]

    return None

def list_ssh_keys():
    """Liste toutes les clés SSH disponibles"""
    # Charger toutes les clés du disque
    for key_file in SSH_KEYS_DIR.glob("*"):
        if not key_file.name.endswith(".pub") and key_file.is_file():
            key_name = key_file.name
            if key_name not in ssh_keys_store:
                load_ssh_key(key_name)

    # Retourner la liste sans les clés privées (pour la sécurité)
    return {
        name: {
            "public_key": info["public_key"],
            "description": info.get("description", ""),
            "created_at": info.get("created_at", "")
        }
        for name, info in ssh_keys_store.items()
    }

# ====================================================================
# FONCTIONS GCP COMPUTE ENGINE
# ====================================================================

def get_gcp_credentials():
    """Obtient les credentials GCP"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    return credentials

def list_instances(zone=None, project_id=None):
    """Liste toutes les instances VM dans GCP"""
    if not zone:
        zone = GCP_ZONE
    if not project_id:
        project_id = GCP_PROJECT_ID

    credentials = get_gcp_credentials()
    instance_client = compute_v1.InstancesClient(credentials=credentials)

    instances_list = instance_client.list(project=project_id, zone=zone)

    instances = []
    for instance in instances_list:
        instance_info = {
            "name": instance.name,
            "zone": zone,
            "machine_type": instance.machine_type.split('/')[-1],
            "status": instance.status,
            "internal_ip": instance.network_interfaces[0].network_i_p if instance.network_interfaces else None,
            "external_ip": instance.network_interfaces[0].access_configs[0].nat_i_p if instance.network_interfaces and instance.network_interfaces[0].access_configs else None,
        }
        instances.append(instance_info)

    return instances

def create_instance(instance_name, machine_type="e2-medium", disk_size_gb=10, image_family="debian-11", ssh_key_name=None):
    """Crée une nouvelle instance VM dans GCP"""
    credentials = get_gcp_credentials()
    instance_client = compute_v1.InstancesClient(credentials=credentials)

    # Configuration du disque
    disk = compute_v1.AttachedDisk()
    initialize_params = compute_v1.AttachedDiskInitializeParams()
    initialize_params.source_image = f"projects/debian-cloud/global/images/family/{image_family}"
    initialize_params.disk_size_gb = disk_size_gb
    disk.initialize_params = initialize_params
    disk.auto_delete = True
    disk.boot = True

    # Configuration du réseau
    network_interface = compute_v1.NetworkInterface()
    network_interface.name = "global/networks/default"

    # Ajouter une IP externe
    access_config = compute_v1.AccessConfig()
    access_config.name = "External NAT"
    access_config.type_ = "ONE_TO_ONE_NAT"
    network_interface.access_configs = [access_config]

    # Configuration de l'instance
    instance = compute_v1.Instance()
    instance.name = instance_name
    instance.machine_type = f"zones/{GCP_ZONE}/machineTypes/{machine_type}"
    instance.disks = [disk]
    instance.network_interfaces = [network_interface]

    # Ajouter la clé SSH si fournie
    if ssh_key_name:
        key_info = load_ssh_key(ssh_key_name)
        if key_info:
            metadata = compute_v1.Metadata()
            metadata_item = compute_v1.Items()
            metadata_item.key = "ssh-keys"
            metadata_item.value = f"debian:{key_info['public_key']}"
            metadata.items = [metadata_item]
            instance.metadata = metadata

    # Créer l'instance
    operation = instance_client.insert(
        project=GCP_PROJECT_ID,
        zone=GCP_ZONE,
        instance_resource=instance
    )

    return {
        "instance_name": instance_name,
        "operation": operation.name,
        "status": "creating",
        "zone": GCP_ZONE
    }

def start_instance(instance_name, zone=None):
    """Démarre une instance VM"""
    if not zone:
        zone = GCP_ZONE

    credentials = get_gcp_credentials()
    instance_client = compute_v1.InstancesClient(credentials=credentials)

    operation = instance_client.start(
        project=GCP_PROJECT_ID,
        zone=zone,
        instance=instance_name
    )

    return {
        "instance_name": instance_name,
        "operation": operation.name,
        "status": "starting"
    }

def stop_instance(instance_name, zone=None):
    """Arrête une instance VM"""
    if not zone:
        zone = GCP_ZONE

    credentials = get_gcp_credentials()
    instance_client = compute_v1.InstancesClient(credentials=credentials)

    operation = instance_client.stop(
        project=GCP_PROJECT_ID,
        zone=zone,
        instance=instance_name
    )

    return {
        "instance_name": instance_name,
        "operation": operation.name,
        "status": "stopping"
    }

def delete_instance(instance_name, zone=None):
    """Supprime une instance VM"""
    if not zone:
        zone = GCP_ZONE

    credentials = get_gcp_credentials()
    instance_client = compute_v1.InstancesClient(credentials=credentials)

    operation = instance_client.delete(
        project=GCP_PROJECT_ID,
        zone=zone,
        instance=instance_name
    )

    return {
        "instance_name": instance_name,
        "operation": operation.name,
        "status": "deleting"
    }

def get_instance_details(instance_name, zone=None):
    """Obtient les détails d'une instance"""
    if not zone:
        zone = GCP_ZONE

    credentials = get_gcp_credentials()
    instance_client = compute_v1.InstancesClient(credentials=credentials)

    instance = instance_client.get(
        project=GCP_PROJECT_ID,
        zone=zone,
        instance=instance_name
    )

    return {
        "name": instance.name,
        "zone": zone,
        "machine_type": instance.machine_type.split('/')[-1],
        "status": instance.status,
        "internal_ip": instance.network_interfaces[0].network_i_p if instance.network_interfaces else None,
        "external_ip": instance.network_interfaces[0].access_configs[0].nat_i_p if instance.network_interfaces and instance.network_interfaces[0].access_configs else None,
        "creation_timestamp": instance.creation_timestamp,
        "disks": [
            {
                "device_name": disk.device_name,
                "source": disk.source.split('/')[-1] if disk.source else None
            }
            for disk in instance.disks
        ]
    }

# ====================================================================
# FONCTIONS SSH
# ====================================================================

def execute_ssh_command(host, username, command, ssh_key_name):
    """Exécute une commande SSH sur une machine distante"""
    key_info = load_ssh_key(ssh_key_name)
    if not key_info:
        return {
            "success": False,
            "error": f"Clé SSH '{ssh_key_name}' non trouvée"
        }

    try:
        # Créer le client SSH
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())

        # Charger la clé privée depuis une chaîne
        from io import StringIO
        key_file = StringIO(key_info['private_key'])
        private_key = paramiko.RSAKey.from_private_key(key_file)

        # Se connecter
        ssh.connect(
            hostname=host,
            username=username,
            pkey=private_key,
            timeout=10
        )

        # Exécuter la commande
        stdin, stdout, stderr = ssh.exec_command(command)

        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        exit_code = stdout.channel.recv_exit_status()

        ssh.close()

        return {
            "success": exit_code == 0,
            "output": output,
            "error": error,
            "exit_code": exit_code
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def upload_file_ssh(host, username, local_path, remote_path, ssh_key_name):
    """Upload un fichier via SSH"""
    key_info = load_ssh_key(ssh_key_name)
    if not key_info:
        return {
            "success": False,
            "error": f"Clé SSH '{ssh_key_name}' non trouvée"
        }

    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())

        from io import StringIO
        key_file = StringIO(key_info['private_key'])
        private_key = paramiko.RSAKey.from_private_key(key_file)

        ssh.connect(
            hostname=host,
            username=username,
            pkey=private_key,
            timeout=10
        )

        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        ssh.close()

        return {
            "success": True,
            "message": f"Fichier uploadé: {local_path} -> {remote_path}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ====================================================================
# FONCTIONS TERRAFORM
# ====================================================================

def terraform_init(working_dir):
    """Initialise Terraform dans un répertoire"""
    try:
        tf = Terraform(working_dir=working_dir)
        return_code, stdout, stderr = tf.init()

        return {
            "success": return_code == 0,
            "output": stdout,
            "error": stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def terraform_plan(working_dir, var_file=None):
    """Planifie un déploiement Terraform"""
    try:
        tf = Terraform(working_dir=working_dir)
        kwargs = {}
        if var_file:
            kwargs['var_file'] = var_file

        return_code, stdout, stderr = tf.plan(**kwargs)

        return {
            "success": return_code == 0,
            "output": stdout,
            "error": stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def terraform_apply(working_dir, var_file=None, auto_approve=True):
    """Applique un déploiement Terraform"""
    try:
        tf = Terraform(working_dir=working_dir)
        kwargs = {}
        if var_file:
            kwargs['var_file'] = var_file
        if auto_approve:
            kwargs['skip_plan'] = True

        return_code, stdout, stderr = tf.apply(**kwargs)

        return {
            "success": return_code == 0,
            "output": stdout,
            "error": stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def terraform_destroy(working_dir, auto_approve=True):
    """Détruit l'infrastructure Terraform"""
    try:
        tf = Terraform(working_dir=working_dir)
        kwargs = {}
        if auto_approve:
            kwargs['force'] = True

        return_code, stdout, stderr = tf.destroy(**kwargs)

        return {
            "success": return_code == 0,
            "output": stdout,
            "error": stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ====================================================================
# TRAITEMENT LANGAGE NATUREL
# ====================================================================

def natural_language_to_gcp_action(query):
    """Traduit une requête en langage naturel en action GCP"""
    query_lower = query.lower()

    # Patterns de création de VM
    if any(word in query_lower for word in ["créer", "crée", "créer une vm", "nouvelle vm", "créer machine"]):
        return {
            "action": "create_instance",
            "suggestion": "Utilisez l'outil 'gcp_create_instance' avec les paramètres appropriés"
        }

    # Patterns de liste
    elif any(word in query_lower for word in ["liste", "affiche", "montre", "voir"]) and "vm" in query_lower:
        return {
            "action": "list_instances",
            "suggestion": "Utilisez l'outil 'gcp_list_instances'"
        }

    # Patterns de démarrage
    elif any(word in query_lower for word in ["démarre", "démarrer", "start", "lance"]):
        return {
            "action": "start_instance",
            "suggestion": "Utilisez l'outil 'gcp_start_instance' avec le nom de l'instance"
        }

    # Patterns d'arrêt
    elif any(word in query_lower for word in ["arrête", "arrêter", "stop"]):
        return {
            "action": "stop_instance",
            "suggestion": "Utilisez l'outil 'gcp_stop_instance' avec le nom de l'instance"
        }

    # Patterns de suppression
    elif any(word in query_lower for word in ["supprime", "supprimer", "delete", "détruit"]):
        return {
            "action": "delete_instance",
            "suggestion": "Utilisez l'outil 'gcp_delete_instance' avec le nom de l'instance"
        }

    return {
        "action": "unknown",
        "suggestion": "Requête non reconnue. Utilisez les outils GCP disponibles."
    }

# ====================================================================
# ENDPOINTS MCP - Format JSON-RPC
# ====================================================================

@app.route('/', methods=['GET', 'POST'])
def root():
    """Endpoint racine - Support JSON-RPC et REST"""
    if request.method == 'GET':
        return jsonify({
            "name": "GCP Infrastructure MCP Server",
            "version": "2.0.0",
            "protocol": "mcp",
            "capabilities": {
                "tools": True,
                "resources": True
            },
            "features": [
                "GCP Compute Engine Management",
                "SSH Key Management",
                "Remote SSH Execution",
                "Terraform Infrastructure as Code"
            ]
        })
    else:
        return handle_jsonrpc()

@app.route('/mcp', methods=['GET', 'POST'])
def mcp_endpoint():
    """Endpoint principal MCP en format JSON-RPC"""
    if request.method == 'GET':
        # Endpoint de découverte pour les clients MCP
        return jsonify({
            "jsonrpc": "2.0",
            "name": "GCP Infrastructure MCP Server",
            "version": "2.0.0",
            "protocol": "mcp",
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": True,
                "resources": True
            },
            "serverInfo": {
                "name": "GCP Infrastructure MCP Server",
                "version": "2.0.0"
            },
            "features": [
                "GCP Compute Engine Management",
                "SSH Key Management",
                "Remote SSH Execution",
                "Terraform Infrastructure as Code"
            ],
            "endpoint": {
                "method": "POST",
                "contentType": "application/json",
                "format": "JSON-RPC 2.0"
            }
        })
    else:
        return handle_jsonrpc()

def handle_jsonrpc():
    """Gère les requêtes JSON-RPC selon le protocole MCP"""
    data = request.get_json()
    if not data:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        }), 400

    if isinstance(data, list):
        results = [process_jsonrpc_request(req) for req in data]
        return jsonify(results)
    else:
        result = process_jsonrpc_request(data)
        return jsonify(result)

def process_jsonrpc_request(request_data):
    """Traite une requête JSON-RPC individuelle"""
    jsonrpc = request_data.get("jsonrpc", "2.0")
    method = request_data.get("method")
    params = request_data.get("params", {})
    request_id = request_data.get("id")

    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "GCP Infrastructure MCP Server",
                    "version": "2.0.0"
                }
            }

        elif method == "tools/list":
            result = {
                "tools": [
                    # SSH Key Management
                    {
                        "name": "ssh_generate_key",
                        "description": "Génère une nouvelle paire de clés SSH",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "key_name": {"type": "string", "description": "Nom de la clé SSH"},
                                "description": {"type": "string", "description": "Description optionnelle"}
                            },
                            "required": ["key_name"]
                        }
                    },
                    {
                        "name": "ssh_add_key",
                        "description": "Ajoute une clé SSH existante",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "key_name": {"type": "string", "description": "Nom de la clé SSH"},
                                "private_key": {"type": "string", "description": "Clé privée SSH au format PEM"},
                                "public_key": {"type": "string", "description": "Clé publique SSH"},
                                "description": {"type": "string", "description": "Description optionnelle"}
                            },
                            "required": ["key_name", "private_key", "public_key"]
                        }
                    },
                    {
                        "name": "ssh_list_keys",
                        "description": "Liste toutes les clés SSH disponibles",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },

                    # GCP Compute Engine
                    {
                        "name": "gcp_list_instances",
                        "description": "Liste toutes les instances VM dans GCP",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "zone": {"type": "string", "description": "Zone GCP (défaut: us-central1-a)"}
                            },
                            "required": []
                        }
                    },
                    {
                        "name": "gcp_create_instance",
                        "description": "Crée une nouvelle instance VM dans GCP",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "instance_name": {"type": "string", "description": "Nom de l'instance"},
                                "machine_type": {"type": "string", "description": "Type de machine (défaut: e2-medium)"},
                                "disk_size_gb": {"type": "integer", "description": "Taille du disque en GB (défaut: 10)"},
                                "image_family": {"type": "string", "description": "Famille d'image (défaut: debian-11)"},
                                "ssh_key_name": {"type": "string", "description": "Nom de la clé SSH à utiliser"}
                            },
                            "required": ["instance_name"]
                        }
                    },
                    {
                        "name": "gcp_start_instance",
                        "description": "Démarre une instance VM",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "instance_name": {"type": "string", "description": "Nom de l'instance"},
                                "zone": {"type": "string", "description": "Zone GCP"}
                            },
                            "required": ["instance_name"]
                        }
                    },
                    {
                        "name": "gcp_stop_instance",
                        "description": "Arrête une instance VM",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "instance_name": {"type": "string", "description": "Nom de l'instance"},
                                "zone": {"type": "string", "description": "Zone GCP"}
                            },
                            "required": ["instance_name"]
                        }
                    },
                    {
                        "name": "gcp_delete_instance",
                        "description": "Supprime une instance VM",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "instance_name": {"type": "string", "description": "Nom de l'instance"},
                                "zone": {"type": "string", "description": "Zone GCP"}
                            },
                            "required": ["instance_name"]
                        }
                    },
                    {
                        "name": "gcp_get_instance",
                        "description": "Obtient les détails d'une instance",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "instance_name": {"type": "string", "description": "Nom de l'instance"},
                                "zone": {"type": "string", "description": "Zone GCP"}
                            },
                            "required": ["instance_name"]
                        }
                    },

                    # SSH Remote Execution
                    {
                        "name": "ssh_execute",
                        "description": "Exécute une commande SSH sur une machine distante",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "host": {"type": "string", "description": "Adresse IP ou hostname"},
                                "username": {"type": "string", "description": "Nom d'utilisateur SSH"},
                                "command": {"type": "string", "description": "Commande à exécuter"},
                                "ssh_key_name": {"type": "string", "description": "Nom de la clé SSH à utiliser"}
                            },
                            "required": ["host", "username", "command", "ssh_key_name"]
                        }
                    },
                    {
                        "name": "ssh_upload_file",
                        "description": "Upload un fichier via SSH",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "host": {"type": "string", "description": "Adresse IP ou hostname"},
                                "username": {"type": "string", "description": "Nom d'utilisateur SSH"},
                                "local_path": {"type": "string", "description": "Chemin local du fichier"},
                                "remote_path": {"type": "string", "description": "Chemin distant du fichier"},
                                "ssh_key_name": {"type": "string", "description": "Nom de la clé SSH à utiliser"}
                            },
                            "required": ["host", "username", "local_path", "remote_path", "ssh_key_name"]
                        }
                    },

                    # Terraform
                    {
                        "name": "terraform_init",
                        "description": "Initialise Terraform dans un répertoire",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "working_dir": {"type": "string", "description": "Répertoire de travail Terraform"}
                            },
                            "required": ["working_dir"]
                        }
                    },
                    {
                        "name": "terraform_plan",
                        "description": "Planifie un déploiement Terraform",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "working_dir": {"type": "string", "description": "Répertoire de travail Terraform"},
                                "var_file": {"type": "string", "description": "Fichier de variables"}
                            },
                            "required": ["working_dir"]
                        }
                    },
                    {
                        "name": "terraform_apply",
                        "description": "Applique un déploiement Terraform",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "working_dir": {"type": "string", "description": "Répertoire de travail Terraform"},
                                "var_file": {"type": "string", "description": "Fichier de variables"},
                                "auto_approve": {"type": "boolean", "description": "Auto-approuver (défaut: true)"}
                            },
                            "required": ["working_dir"]
                        }
                    },
                    {
                        "name": "terraform_destroy",
                        "description": "Détruit l'infrastructure Terraform",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "working_dir": {"type": "string", "description": "Répertoire de travail Terraform"},
                                "auto_approve": {"type": "boolean", "description": "Auto-approuver (défaut: true)"}
                            },
                            "required": ["working_dir"]
                        }
                    },

                    # Natural Language Helper
                    {
                        "name": "gcp_natural_query",
                        "description": "Interprète une requête en langage naturel pour GCP",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Requête en français"}
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            # SSH Key Management
            if tool_name == "ssh_generate_key":
                key_name = arguments.get("key_name")
                description = arguments.get("description", "")

                private_key, public_key = generate_ssh_key_pair(key_name)
                store_ssh_key(key_name, private_key, public_key, description)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps({
                            "success": True,
                            "key_name": key_name,
                            "public_key": public_key,
                            "message": f"Clé SSH '{key_name}' générée et stockée avec succès"
                        }, indent=2)
                    }]
                }

            elif tool_name == "ssh_add_key":
                key_name = arguments.get("key_name")
                private_key = arguments.get("private_key")
                public_key = arguments.get("public_key")
                description = arguments.get("description", "")

                store_ssh_key(key_name, private_key, public_key, description)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps({
                            "success": True,
                            "key_name": key_name,
                            "message": f"Clé SSH '{key_name}' ajoutée avec succès"
                        }, indent=2)
                    }]
                }

            elif tool_name == "ssh_list_keys":
                keys = list_ssh_keys()

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps({
                            "success": True,
                            "keys": keys,
                            "count": len(keys)
                        }, indent=2)
                    }]
                }

            # GCP Compute Engine
            elif tool_name == "gcp_list_instances":
                zone = arguments.get("zone")
                instances = list_instances(zone)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps({
                            "success": True,
                            "instances": instances,
                            "count": len(instances)
                        }, indent=2)
                    }]
                }

            elif tool_name == "gcp_create_instance":
                instance_name = arguments.get("instance_name")
                machine_type = arguments.get("machine_type", "e2-medium")
                disk_size_gb = arguments.get("disk_size_gb", 10)
                image_family = arguments.get("image_family", "debian-11")
                ssh_key_name = arguments.get("ssh_key_name")

                instance_result = create_instance(
                    instance_name, machine_type, disk_size_gb, image_family, ssh_key_name
                )

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(instance_result, indent=2)
                    }]
                }

            elif tool_name == "gcp_start_instance":
                instance_name = arguments.get("instance_name")
                zone = arguments.get("zone")

                instance_result = start_instance(instance_name, zone)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(instance_result, indent=2)
                    }]
                }

            elif tool_name == "gcp_stop_instance":
                instance_name = arguments.get("instance_name")
                zone = arguments.get("zone")

                instance_result = stop_instance(instance_name, zone)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(instance_result, indent=2)
                    }]
                }

            elif tool_name == "gcp_delete_instance":
                instance_name = arguments.get("instance_name")
                zone = arguments.get("zone")

                instance_result = delete_instance(instance_name, zone)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(instance_result, indent=2)
                    }]
                }

            elif tool_name == "gcp_get_instance":
                instance_name = arguments.get("instance_name")
                zone = arguments.get("zone")

                instance_result = get_instance_details(instance_name, zone)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(instance_result, indent=2)
                    }]
                }

            # SSH Remote Execution
            elif tool_name == "ssh_execute":
                host = arguments.get("host")
                username = arguments.get("username")
                command = arguments.get("command")
                ssh_key_name = arguments.get("ssh_key_name")

                ssh_result = execute_ssh_command(host, username, command, ssh_key_name)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(ssh_result, indent=2)
                    }]
                }

            elif tool_name == "ssh_upload_file":
                host = arguments.get("host")
                username = arguments.get("username")
                local_path = arguments.get("local_path")
                remote_path = arguments.get("remote_path")
                ssh_key_name = arguments.get("ssh_key_name")

                upload_result = upload_file_ssh(host, username, local_path, remote_path, ssh_key_name)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(upload_result, indent=2)
                    }]
                }

            # Terraform
            elif tool_name == "terraform_init":
                working_dir = arguments.get("working_dir")
                tf_result = terraform_init(working_dir)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(tf_result, indent=2)
                    }]
                }

            elif tool_name == "terraform_plan":
                working_dir = arguments.get("working_dir")
                var_file = arguments.get("var_file")

                tf_result = terraform_plan(working_dir, var_file)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(tf_result, indent=2)
                    }]
                }

            elif tool_name == "terraform_apply":
                working_dir = arguments.get("working_dir")
                var_file = arguments.get("var_file")
                auto_approve = arguments.get("auto_approve", True)

                tf_result = terraform_apply(working_dir, var_file, auto_approve)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(tf_result, indent=2)
                    }]
                }

            elif tool_name == "terraform_destroy":
                working_dir = arguments.get("working_dir")
                auto_approve = arguments.get("auto_approve", True)

                tf_result = terraform_destroy(working_dir, auto_approve)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(tf_result, indent=2)
                    }]
                }

            # Natural Language
            elif tool_name == "gcp_natural_query":
                query = arguments.get("query")
                nl_result = natural_language_to_gcp_action(query)

                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(nl_result, indent=2)
                    }]
                }

            else:
                raise ValueError(f"Outil '{tool_name}' non trouvé")

        elif method == "resources/list":
            result = {
                "resources": [
                    {
                        "uri": "gcp://instances",
                        "name": "Liste des instances GCP",
                        "description": "Toutes les instances VM GCP",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "ssh://keys",
                        "name": "Liste des clés SSH",
                        "description": "Toutes les clés SSH disponibles",
                        "mimeType": "application/json"
                    }
                ]
            }

        elif method == "resources/read":
            uri = params.get("uri")

            if uri == "gcp://instances":
                instances = list_instances()
                result = {
                    "contents": [{
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(instances, indent=2)
                    }]
                }

            elif uri == "ssh://keys":
                keys = list_ssh_keys()
                result = {
                    "contents": [{
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(keys, indent=2)
                    }]
                }

            else:
                raise ValueError(f"Ressource '{uri}' non trouvée")

        else:
            raise ValueError(f"Méthode '{method}' non supportée")

        return {
            "jsonrpc": jsonrpc,
            "result": result,
            "id": request_id
        }

    except Exception as e:
        return {
            "jsonrpc": jsonrpc,
            "error": {
                "code": -32603,
                "message": str(e)
            },
            "id": request_id
        }

# ====================================================================
# HEALTH CHECK
# ====================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "GCP Infrastructure MCP Server",
        "version": "2.0.0",
        "gcp_project": GCP_PROJECT_ID,
        "gcp_zone": GCP_ZONE,
        "ssh_keys_count": len(ssh_keys_store)
    })

if __name__ == '__main__':
    print(f"🚀 Serveur MCP GCP démarré sur http://0.0.0.0:5001")
    print(f"📡 Projet GCP: {GCP_PROJECT_ID}")
    print(f"📍 Zone par défaut: {GCP_ZONE}")
    print(f"🔑 Répertoire des clés SSH: {SSH_KEYS_DIR}")
    print(f"📡 Fonctionnalités disponibles:")
    print(f"   ✓ Gestion des VMs GCP (créer, lister, démarrer, arrêter, supprimer)")
    print(f"   ✓ Gestion des clés SSH (générer, stocker, utiliser)")
    print(f"   ✓ Exécution SSH distante sur les VMs")
    print(f"   ✓ Déploiement Terraform")
    print(f"   ✓ Interprétation en langage naturel")
    app.run(debug=False, host='0.0.0.0', port=5001)
