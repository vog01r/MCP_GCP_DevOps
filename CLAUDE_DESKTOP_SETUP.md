# Configuration Claude Desktop - Serveur MCP GCP

Votre serveur MCP GCP est maintenant accessible via HTTPS ! 🎉

## URL du serveur
```
https://gcp.mcp.syneralys.com
```

## Configuration Claude Desktop

### Étape 1 : Ouvrir le fichier de configuration

**Sur macOS :**
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Sur Windows :**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Sur Linux :**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

### Étape 2 : Ajouter la configuration

Ajoutez cette configuration dans votre fichier `claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "gcp-infrastructure": {
      "url": "https://gcp.mcp.syneralys.com/mcp"
    }
  }
}
```

Si vous avez déjà d'autres serveurs MCP configurés, ajoutez simplement la section `gcp-infrastructure` :

```json
{
  "mcpServers": {
    "autre-serveur": {
      "command": "...",
      "args": ["..."]
    },
    "gcp-infrastructure": {
      "url": "https://gcp.mcp.syneralys.com/mcp"
    }
  }
}
```

### Étape 3 : Redémarrer Claude Desktop

Fermez complètement Claude Desktop et relancez-le.

### Étape 4 : Vérifier la connexion

Dans Claude Desktop, vous devriez voir le serveur MCP GCP disponible. Vous pouvez tester en demandant :

**"Liste toutes mes VMs GCP"**

ou

**"Génère une nouvelle clé SSH"**

## Endpoints disponibles

Vous pouvez aussi tester le serveur directement :

**Health check :**
```bash
curl https://gcp.mcp.syneralys.com/health
```

**Informations du serveur :**
```bash
curl https://gcp.mcp.syneralys.com/
```

**Endpoint MCP (JSON-RPC) :**
```bash
curl -X POST https://gcp.mcp.syneralys.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {},
    "id": 1
  }'
```

## Outils disponibles

Une fois connecté, vous aurez accès à 16 outils :

### 🔑 Gestion SSH
- `ssh_generate_key` - Générer une clé SSH
- `ssh_add_key` - Ajouter une clé existante
- `ssh_list_keys` - Lister les clés

### ☁️ GCP Compute Engine
- `gcp_list_instances` - Lister les VMs
- `gcp_create_instance` - Créer une VM
- `gcp_start_instance` - Démarrer une VM
- `gcp_stop_instance` - Arrêter une VM
- `gcp_delete_instance` - Supprimer une VM
- `gcp_get_instance` - Détails d'une VM

### 🔐 SSH Remote
- `ssh_execute` - Exécuter une commande SSH
- `ssh_upload_file` - Upload un fichier

### 🏗️ Terraform
- `terraform_init` - Initialiser Terraform
- `terraform_plan` - Planifier
- `terraform_apply` - Appliquer
- `terraform_destroy` - Détruire

### 💬 Langage naturel
- `gcp_natural_query` - Requête en français

## Exemples d'utilisation

### Créer une VM et installer nginx
```
"Je veux créer une VM nommée 'web-server' et installer nginx dessus"
```

### Lister les VMs
```
"Montre-moi toutes mes VMs GCP"
```

### Exécuter une commande SSH
```
"Exécute 'df -h' sur ma VM 'web-server'"
```

### Déployer avec Terraform
```
"Déploie l'infrastructure Terraform"
```

## Statut du serveur

Le serveur est configuré comme suit :
- **Domaine :** gcp.mcp.syneralys.com
- **IP :** 46.105.76.243
- **Port :** 5001 (interne)
- **SSL :** Let's Encrypt (auto-renouvelé)
- **Service :** systemd (démarre automatiquement)
- **Reverse proxy :** nginx

### Vérifier que le service tourne

```bash
sudo systemctl status mcp-gcp.service
```

### Voir les logs en temps réel

```bash
sudo journalctl -u mcp-gcp.service -f
```

### Redémarrer le serveur

```bash
sudo systemctl restart mcp-gcp.service
```

## Sécurité

- ✅ HTTPS avec certificat Let's Encrypt valide
- ✅ Renouvellement automatique du certificat
- ✅ CORS configuré pour accepter les requêtes Claude Desktop
- ✅ Service systemd avec redémarrage automatique
- ✅ Headers de sécurité configurés

## Renouvellement du certificat SSL

Le certificat Let's Encrypt est automatiquement renouvelé par certbot. Vous pouvez vérifier :

```bash
sudo certbot certificates
```

Pour forcer un renouvellement :

```bash
sudo certbot renew --dry-run
```

## Dépannage

### Le serveur ne répond pas
```bash
# Vérifier le service
sudo systemctl status mcp-gcp.service

# Redémarrer
sudo systemctl restart mcp-gcp.service

# Voir les logs
sudo journalctl -u mcp-gcp.service -n 50
```

### Problème de certificat SSL
```bash
# Vérifier le certificat
sudo certbot certificates

# Renouveler
sudo certbot renew --force-renewal
```

### Problème nginx
```bash
# Tester la config
sudo nginx -t

# Redémarrer nginx
sudo systemctl restart nginx

# Voir les logs
sudo tail -f /var/log/nginx/mcp-gcp-error.log
```

## Support

Pour toute question :
- Documentation complète : `README.md`
- Guide rapide : `QUICKSTART.md`
- Exemples API : `API_EXAMPLES.md`

---

**Félicitations ! Votre serveur MCP GCP est maintenant accessible depuis Claude Desktop via HTTPS ! 🚀**
