# Exemples d'appels API - Serveur MCP GCP

Ce document contient des exemples de requêtes pour tester directement le serveur MCP via curl ou d'autres clients HTTP.

## Endpoints de base

### Health Check

```bash
curl http://localhost:5001/health
```

**Réponse :**
```json
{
  "status": "healthy",
  "service": "GCP Infrastructure MCP Server",
  "version": "2.0.0",
  "gcp_project": "level-surfer-473817-p5",
  "gcp_zone": "us-central1-a",
  "ssh_keys_count": 0
}
```

### Informations du serveur

```bash
curl http://localhost:5001/
```

**Réponse :**
```json
{
  "name": "GCP Infrastructure MCP Server",
  "version": "2.0.0",
  "protocol": "mcp",
  "capabilities": {
    "tools": true,
    "resources": true
  },
  "features": [
    "GCP Compute Engine Management",
    "SSH Key Management",
    "Remote SSH Execution",
    "Terraform Infrastructure as Code"
  ]
}
```

## Protocole MCP (JSON-RPC 2.0)

### Initialize

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {},
    "id": 1
  }'
```

### Lister les outils disponibles

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2
  }'
```

## Gestion des clés SSH

### Générer une clé SSH

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "ssh_generate_key",
      "arguments": {
        "key_name": "ma-premiere-cle",
        "description": "Clé de test pour mes VMs"
      }
    },
    "id": 3
  }'
```

### Lister les clés SSH

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "ssh_list_keys",
      "arguments": {}
    },
    "id": 4
  }'
```

## Gestion des VMs GCP

### Lister les instances

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "gcp_list_instances",
      "arguments": {}
    },
    "id": 5
  }'
```

### Créer une instance

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "gcp_create_instance",
      "arguments": {
        "instance_name": "test-vm-api",
        "machine_type": "e2-medium",
        "disk_size_gb": 10,
        "image_family": "debian-11",
        "ssh_key_name": "ma-premiere-cle"
      }
    },
    "id": 6
  }'
```

### Obtenir les détails d'une instance

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "gcp_get_instance",
      "arguments": {
        "instance_name": "test-vm-api"
      }
    },
    "id": 7
  }'
```

### Démarrer une instance

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "gcp_start_instance",
      "arguments": {
        "instance_name": "test-vm-api"
      }
    },
    "id": 8
  }'
```

### Arrêter une instance

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "gcp_stop_instance",
      "arguments": {
        "instance_name": "test-vm-api"
      }
    },
    "id": 9
  }'
```

### Supprimer une instance

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "gcp_delete_instance",
      "arguments": {
        "instance_name": "test-vm-api"
      }
    },
    "id": 10
  }'
```

## Exécution SSH

### Exécuter une commande

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "ssh_execute",
      "arguments": {
        "host": "35.123.45.67",
        "username": "debian",
        "command": "uname -a",
        "ssh_key_name": "ma-premiere-cle"
      }
    },
    "id": 11
  }'
```

### Upload un fichier

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "ssh_upload_file",
      "arguments": {
        "host": "35.123.45.67",
        "username": "debian",
        "local_path": "/opt/git/test.txt",
        "remote_path": "/tmp/test.txt",
        "ssh_key_name": "ma-premiere-cle"
      }
    },
    "id": 12
  }'
```

## Terraform

### Initialiser Terraform

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "terraform_init",
      "arguments": {
        "working_dir": "/opt/git/terraform_examples"
      }
    },
    "id": 13
  }'
```

### Planifier un déploiement

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "terraform_plan",
      "arguments": {
        "working_dir": "/opt/git/terraform_examples"
      }
    },
    "id": 14
  }'
```

### Appliquer un déploiement

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "terraform_apply",
      "arguments": {
        "working_dir": "/opt/git/terraform_examples",
        "auto_approve": true
      }
    },
    "id": 15
  }'
```

### Détruire l'infrastructure

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "terraform_destroy",
      "arguments": {
        "working_dir": "/opt/git/terraform_examples",
        "auto_approve": true
      }
    },
    "id": 16
  }'
```

## Langage naturel

### Interpréter une requête

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "gcp_natural_query",
      "arguments": {
        "query": "Crée une nouvelle VM pour mon serveur web"
      }
    },
    "id": 17
  }'
```

## Ressources MCP

### Lister les ressources

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "resources/list",
    "params": {},
    "id": 18
  }'
```

### Lire une ressource (instances GCP)

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "resources/read",
    "params": {
      "uri": "gcp://instances"
    },
    "id": 19
  }'
```

### Lire une ressource (clés SSH)

```bash
curl -X POST http://localhost:5001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "resources/read",
    "params": {
      "uri": "ssh://keys"
    },
    "id": 20
  }'
```

## Script de test complet

Voici un script bash pour tester le workflow complet :

```bash
#!/bin/bash

# Test complet du serveur MCP GCP

BASE_URL="http://localhost:5001/mcp"

echo "1. Test Health Check..."
curl -s http://localhost:5001/health | python3 -m json.tool
echo ""

echo "2. Génération d'une clé SSH..."
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "ssh_generate_key",
      "arguments": {
        "key_name": "test-key",
        "description": "Clé de test"
      }
    },
    "id": 1
  }' | python3 -m json.tool
echo ""

echo "3. Liste des clés SSH..."
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "ssh_list_keys",
      "arguments": {}
    },
    "id": 2
  }' | python3 -m json.tool
echo ""

echo "4. Liste des instances GCP..."
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "gcp_list_instances",
      "arguments": {}
    },
    "id": 3
  }' | python3 -m json.tool
echo ""

echo "Test terminé !"
```

Sauvegardez ce script dans `test_mcp.sh` et exécutez-le avec :

```bash
chmod +x test_mcp.sh
./test_mcp.sh
```

## Utilisation avec Python

Exemple de client Python :

```python
import requests
import json

class MCPClient:
    def __init__(self, base_url="http://localhost:5001/mcp"):
        self.base_url = base_url
        self.request_id = 0

    def call_tool(self, tool_name, arguments):
        self.request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": self.request_id
        }
        response = requests.post(self.base_url, json=payload)
        return response.json()

# Utilisation
client = MCPClient()

# Générer une clé SSH
result = client.call_tool("ssh_generate_key", {
    "key_name": "python-key",
    "description": "Clé générée depuis Python"
})
print(json.dumps(result, indent=2))

# Lister les instances GCP
result = client.call_tool("gcp_list_instances", {})
print(json.dumps(result, indent=2))
```

## Notes

- Toutes les requêtes utilisent le protocole JSON-RPC 2.0
- L'ID de requête peut être n'importe quel nombre ou chaîne unique
- Les réponses suivent le format JSON-RPC 2.0 avec un champ `result` ou `error`
- Pour les outils asynchrones (création de VM), vérifiez le statut avec `gcp_get_instance`
