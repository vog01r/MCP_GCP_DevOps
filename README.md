# Serveur MCP GCP Infrastructure

## 🎥 Démonstration vidéo

<div align="center">

![Démonstration du serveur MCP GCP](1114.mp4)

**👉 [Voir la vidéo complète](1114.mp4)**

*Découvrez comment déployer votre infrastructure GCP en langage naturel avec Claude*

</div>

---

Serveur MCP (Model Context Protocol) pour gérer l'infrastructure GCP (Google Cloud Platform) en langage naturel via Claude. Ce serveur permet de déployer et gérer des machines virtuelles, de gérer des clés SSH, et de déployer de l'infrastructure avec Terraform.

> **⚠️ AVERTISSEMENT IMPORTANT - SÉCURITÉ**
> 
> Ce projet est **uniquement à but de présentation des travaux sur l'intelligence artificielle** et ne doit **PAS être utilisé en production** sans modifications de sécurité majeures.
> 
> **🔴 Aucune authentification OAuth n'est implémentée** : Le serveur MCP est accessible publiquement sans authentification. Toute personne ayant accès à l'URL du serveur peut l'utiliser et potentiellement accéder à vos ressources GCP.
> 
> **⚠️ Utilisez uniquement dans un environnement de développement isolé ou avec des mesures de sécurité appropriées (pare-feu, authentification, etc.).**

> **📋 Note sur l'utilisation avec Claude**
> 
> Pour que Claude puisse s'authentifier facilement avec votre serveur MCP, il est **fortement recommandé** d'utiliser un **nom de domaine avec HTTPS** plutôt qu'une adresse IP ou HTTP. Claude nécessite une connexion sécurisée (HTTPS) pour fonctionner correctement avec les serveurs MCP externes.

## Fonctionnalités

### 🔑 Gestion des clés SSH
- **Générer des clés SSH** : Créer automatiquement une paire de clés SSH (privée/publique)
- **Stocker les clés** : Stockage sécurisé des clés SSH (en mémoire et sur disque dans `~/.ssh_mcp`)
- **Lister les clés** : Voir toutes les clés SSH disponibles
- **Ajouter des clés existantes** : Importer vos propres clés SSH

### ☁️ Gestion des VMs GCP (Compute Engine)
- **Lister les instances** : Voir toutes les VMs dans votre projet GCP
- **Créer une instance** : Déployer une nouvelle VM avec configuration personnalisée
- **Démarrer/Arrêter une instance** : Contrôler l'état des VMs
- **Supprimer une instance** : Nettoyer les ressources
- **Obtenir les détails** : Voir les informations détaillées d'une VM (IPs, disques, etc.)

### 🔐 Exécution SSH distante
- **Exécuter des commandes** : Lancer des commandes sur les VMs via SSH
- **Upload de fichiers** : Transférer des fichiers vers les VMs via SFTP

### 🏗️ Infrastructure as Code avec Terraform
- **Initialiser Terraform** : Préparer un projet Terraform
- **Planifier** : Voir les changements avant de les appliquer
- **Appliquer** : Déployer l'infrastructure
- **Détruire** : Nettoyer les ressources Terraform

### 💬 Langage naturel
- Interprétation des requêtes en français pour faciliter l'utilisation

## Installation

### Prérequis
- Python 3.8+
- Compte GCP avec un projet configuré
- Fichier de clé de service GCP (service-account-key.json)
- **Nom de domaine avec certificat SSL/TLS** (recommandé pour l'utilisation avec Claude)
- **Reverse proxy (Nginx/Apache) avec HTTPS** configuré (recommandé)

### Étapes d'installation

1. Cloner le dépôt :
```bash
git clone <votre-repo>
cd <votre-repo>
```

2. Installer les dépendances :
```bash
pip3 install -r requirements.txt
```

3. Configurer les credentials GCP :
   - Placer votre fichier `service-account-key.json` dans le répertoire du projet
   - Assurez-vous que le service account a les permissions nécessaires :
     - Compute Engine Admin
     - Service Account User

4. (Optionnel) Installer Terraform si vous voulez utiliser les fonctionnalités Terraform :
```bash
# Ubuntu/Debian
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

## Utilisation

### Configuration HTTPS avec nom de domaine (Recommandé)

Pour que Claude puisse s'authentifier facilement, configurez votre serveur avec HTTPS et un nom de domaine :

1. **Obtenir un certificat SSL** (Let's Encrypt recommandé) :
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

2. **Configurer Nginx comme reverse proxy** :
```nginx
server {
    listen 443 ssl;
    server_name votre-domaine.com;

    ssl_certificate /etc/letsencrypt/live/votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Redémarrer Nginx** :
```bash
sudo systemctl restart nginx
```

### Démarrage du serveur

```bash
python3 mcp_server.py
```

Le serveur démarrera sur `http://0.0.0.0:5001` (utilisez HTTPS via le reverse proxy pour la production)

### Configuration dans Claude Desktop

Pour utiliser le serveur MCP avec Claude via HTTPS, configurez l'URL de votre serveur :

```json
{
  "mcpServers": {
    "gcp-infrastructure": {
      "url": "https://votre-domaine.com",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
```

**Note** : Utilisez votre nom de domaine avec HTTPS (ex: `https://mcp.votre-domaine.com`) pour que Claude puisse s'authentifier correctement.

Pour une utilisation locale uniquement, vous pouvez aussi utiliser la commande directe :

```json
{
  "mcpServers": {
    "gcp-infrastructure": {
      "command": "python3",
      "args": ["/opt/git/mcp_server.py"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/opt/git/service-account-key.json"
      }
    }
  }
}
```

## Outils disponibles

### Gestion des clés SSH

#### `ssh_generate_key`
Génère une nouvelle paire de clés SSH.

**Paramètres :**
- `key_name` (requis) : Nom de la clé
- `description` (optionnel) : Description de la clé

**Exemple :**
```json
{
  "key_name": "ma-cle-vm",
  "description": "Clé pour mes VMs GCP"
}
```

#### `ssh_list_keys`
Liste toutes les clés SSH disponibles.

#### `ssh_add_key`
Ajoute une clé SSH existante.

**Paramètres :**
- `key_name` (requis) : Nom de la clé
- `private_key` (requis) : Clé privée au format PEM
- `public_key` (requis) : Clé publique
- `description` (optionnel) : Description

### Gestion des VMs GCP

#### `gcp_list_instances`
Liste toutes les instances VM.

**Paramètres :**
- `zone` (optionnel) : Zone GCP (défaut: us-central1-a)

#### `gcp_create_instance`
Crée une nouvelle instance VM.

**Paramètres :**
- `instance_name` (requis) : Nom de l'instance
- `machine_type` (optionnel) : Type de machine (défaut: e2-medium)
- `disk_size_gb` (optionnel) : Taille du disque en GB (défaut: 10)
- `image_family` (optionnel) : Famille d'image (défaut: debian-11)
- `ssh_key_name` (optionnel) : Nom de la clé SSH à utiliser

**Exemple :**
```json
{
  "instance_name": "mon-serveur-web",
  "machine_type": "e2-medium",
  "disk_size_gb": 20,
  "image_family": "debian-11",
  "ssh_key_name": "ma-cle-vm"
}
```

#### `gcp_start_instance`
Démarre une instance VM.

**Paramètres :**
- `instance_name` (requis) : Nom de l'instance
- `zone` (optionnel) : Zone GCP

#### `gcp_stop_instance`
Arrête une instance VM.

**Paramètres :**
- `instance_name` (requis) : Nom de l'instance
- `zone` (optionnel) : Zone GCP

#### `gcp_delete_instance`
Supprime une instance VM.

**Paramètres :**
- `instance_name` (requis) : Nom de l'instance
- `zone` (optionnel) : Zone GCP

#### `gcp_get_instance`
Obtient les détails d'une instance.

**Paramètres :**
- `instance_name` (requis) : Nom de l'instance
- `zone` (optionnel) : Zone GCP

### Exécution SSH

#### `ssh_execute`
Exécute une commande SSH sur une machine distante.

**Paramètres :**
- `host` (requis) : Adresse IP ou hostname
- `username` (requis) : Nom d'utilisateur SSH
- `command` (requis) : Commande à exécuter
- `ssh_key_name` (requis) : Nom de la clé SSH à utiliser

**Exemple :**
```json
{
  "host": "35.123.45.67",
  "username": "debian",
  "command": "sudo apt update && sudo apt install -y nginx",
  "ssh_key_name": "ma-cle-vm"
}
```

#### `ssh_upload_file`
Upload un fichier via SSH.

**Paramètres :**
- `host` (requis) : Adresse IP ou hostname
- `username` (requis) : Nom d'utilisateur SSH
- `local_path` (requis) : Chemin local du fichier
- `remote_path` (requis) : Chemin distant du fichier
- `ssh_key_name` (requis) : Nom de la clé SSH à utiliser

### Terraform

#### `terraform_init`
Initialise Terraform dans un répertoire.

**Paramètres :**
- `working_dir` (requis) : Répertoire de travail Terraform

#### `terraform_plan`
Planifie un déploiement Terraform.

**Paramètres :**
- `working_dir` (requis) : Répertoire de travail Terraform
- `var_file` (optionnel) : Fichier de variables

#### `terraform_apply`
Applique un déploiement Terraform.

**Paramètres :**
- `working_dir` (requis) : Répertoire de travail Terraform
- `var_file` (optionnel) : Fichier de variables
- `auto_approve` (optionnel) : Auto-approuver (défaut: true)

#### `terraform_destroy`
Détruit l'infrastructure Terraform.

**Paramètres :**
- `working_dir` (requis) : Répertoire de travail Terraform
- `auto_approve` (optionnel) : Auto-approuver (défaut: true)

### Langage naturel

#### `gcp_natural_query`
Interprète une requête en langage naturel.

**Paramètres :**
- `query` (requis) : Requête en français

**Exemple :**
```json
{
  "query": "Crée une nouvelle VM pour mon serveur web"
}
```

## Exemples d'utilisation avec Claude

### Exemple 1 : Créer une VM avec clé SSH

```
Utilisateur : Je veux créer une VM sur GCP pour héberger un site web

Claude : Je vais vous aider à créer une VM. D'abord, générons une clé SSH :
[utilise ssh_generate_key]

Maintenant, créons la VM avec cette clé :
[utilise gcp_create_instance avec la clé SSH]

Votre VM est en cours de création ! Une fois démarrée, vous pourrez vous y connecter.
```

### Exemple 2 : Installer un logiciel sur une VM

```
Utilisateur : Installe nginx sur ma VM "mon-serveur-web"

Claude : Je vais d'abord obtenir l'adresse IP de votre VM :
[utilise gcp_get_instance]

Maintenant j'installe nginx via SSH :
[utilise ssh_execute avec la commande d'installation]

Nginx est maintenant installé sur votre VM !
```

### Exemple 3 : Déployer avec Terraform

```
Utilisateur : Déploie l'infrastructure définie dans /opt/terraform/infrastructure

Claude : Je vais initialiser Terraform :
[utilise terraform_init]

Voyons ce qui va être créé :
[utilise terraform_plan]

Tout semble correct. J'applique maintenant :
[utilise terraform_apply]

Infrastructure déployée avec succès !
```

## Architecture

### Stockage des clés SSH
Les clés SSH sont stockées de manière sécurisée :
- **En mémoire** : Pour un accès rapide pendant l'exécution
- **Sur disque** : Dans `~/.ssh_mcp/` avec permissions restrictives (600 pour les clés privées, 644 pour les publiques)

### Configuration GCP
- **Projet** : level-surfer-473817-p5
- **Zone par défaut** : us-central1-a
- **Credentials** : service-account-key.json

## Sécurité

### ⚠️ AVERTISSEMENTS CRITIQUES

**Ce serveur MCP n'implémente AUCUNE authentification OAuth ou autre mécanisme de sécurité.**

**Risques de sécurité :**
- 🔴 **Accès public non authentifié** : Toute personne ayant l'URL peut utiliser votre serveur
- 🔴 **Exposition des ressources GCP** : Accès potentiel à vos VMs, clés SSH, et infrastructure
- 🔴 **Pas de rate limiting** : Vulnérable aux attaques par déni de service
- 🔴 **Pas de logging d'audit** : Impossible de tracer qui a utilisé le serveur

**Recommandations pour la production :**
1. ✅ **Implémenter OAuth 2.0** ou un autre mécanisme d'authentification
2. ✅ **Utiliser HTTPS obligatoire** (certificat SSL valide)
3. ✅ **Configurer un pare-feu** pour limiter l'accès par IP
4. ✅ **Ajouter un rate limiting** pour prévenir les abus
5. ✅ **Activer les logs d'audit** pour tracer toutes les actions
6. ✅ **Utiliser un reverse proxy** (Nginx/Traefik) avec authentification
7. ✅ **Restreindre les permissions GCP** au strict minimum nécessaire

### Bonnes pratiques
1. **Clés SSH** : Stockées avec permissions restrictives (600)
2. **Service Account** : Utilise les credentials GCP avec permissions minimales nécessaires
3. **Clés privées** : Jamais exposées dans les réponses de l'API (seules les clés publiques sont retournées)
4. **HTTPS obligatoire** : Utilisez toujours HTTPS en production, jamais HTTP
5. **Nom de domaine** : Utilisez un nom de domaine valide avec certificat SSL pour Claude

### Permissions GCP requises
Le service account doit avoir au minimum :
- `roles/compute.instanceAdmin.v1`
- `roles/iam.serviceAccountUser`

## Dépannage

### Le serveur ne démarre pas
- Vérifiez que toutes les dépendances sont installées : `pip3 install -r requirements.txt`
- Vérifiez que le fichier `service-account-key.json` existe et est valide

### Erreur de connexion GCP
- Vérifiez que le service account a les bonnes permissions
- Vérifiez que le projet GCP est correct dans le code (`GCP_PROJECT_ID`)

### Erreur SSH
- Vérifiez que la clé SSH existe : utilisez `ssh_list_keys`
- Vérifiez que la VM a bien la clé publique dans ses métadonnées
- Vérifiez que le pare-feu GCP autorise le port SSH (22)

### Erreur Terraform
- Vérifiez que Terraform est installé : `terraform --version`
- Vérifiez que le répertoire de travail contient des fichiers Terraform valides

## API Reference

### Endpoints REST

#### GET /
Informations sur le serveur

#### GET /health
Health check du serveur

#### POST /mcp
Endpoint principal MCP (JSON-RPC 2.0)

## À propos de ce projet

**Ce dépôt GitHub est uniquement à but de présentation des travaux sur l'intelligence artificielle.**

Ce projet démontre l'intégration d'un serveur MCP (Model Context Protocol) avec Google Cloud Platform pour permettre à Claude (et autres assistants IA) de gérer l'infrastructure cloud en langage naturel.

**Objectifs pédagogiques :**
- Démonstration de l'utilisation du protocole MCP
- Intégration avec les APIs GCP
- Gestion d'infrastructure via IA conversationnelle
- Exemples de code pour la communauté

**⚠️ Ne pas utiliser en production sans modifications de sécurité majeures.**

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## Licence

MIT License

## Support

Pour toute question ou problème, ouvrez une issue sur GitHub.
