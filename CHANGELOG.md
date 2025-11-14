# Changelog - Serveur MCP GCP

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

## [2.0.0] - 2025-11-13

### Transformation majeure
- **Avant** : Serveur MCP pour PostgreSQL
- **Après** : Serveur MCP pour infrastructure GCP

### Ajouté

#### Gestion des clés SSH
- Génération automatique de paires de clés SSH (privée/publique)
- Stockage sécurisé des clés dans `~/.ssh_mcp/`
- Support pour importer des clés SSH existantes
- Listing des clés SSH disponibles
- Permissions correctes (600 pour privées, 644 pour publiques)

#### Gestion GCP Compute Engine
- Listing de toutes les instances VM
- Création d'instances avec configuration personnalisée
  - Type de machine configurable
  - Taille de disque configurable
  - Famille d'image configurable (Debian, Ubuntu, etc.)
  - Injection automatique de clés SSH
- Démarrage/Arrêt d'instances
- Suppression d'instances
- Récupération des détails complets d'une instance
- Support pour les IPs externes et internes

#### Exécution SSH distante
- Connexion SSH automatique aux VMs
- Exécution de commandes distantes
- Upload de fichiers via SFTP
- Gestion automatique des clés SSH
- Support pour connexions sécurisées

#### Infrastructure as Code - Terraform
- Initialisation de projets Terraform
- Planification de déploiements (terraform plan)
- Application de changements (terraform apply)
- Destruction d'infrastructure (terraform destroy)
- Support pour fichiers de variables
- Mode auto-approve pour automatisation

#### Interprétation langage naturel
- Compréhension des requêtes en français
- Suggestions d'outils à utiliser
- Patterns pour créer, lister, démarrer, arrêter, supprimer des VMs

#### Outils MCP
15 nouveaux outils disponibles :
1. `ssh_generate_key` - Génération de clés SSH
2. `ssh_add_key` - Ajout de clés existantes
3. `ssh_list_keys` - Liste des clés
4. `gcp_list_instances` - Liste des VMs
5. `gcp_create_instance` - Création de VM
6. `gcp_start_instance` - Démarrage de VM
7. `gcp_stop_instance` - Arrêt de VM
8. `gcp_delete_instance` - Suppression de VM
9. `gcp_get_instance` - Détails d'une VM
10. `ssh_execute` - Exécution SSH
11. `ssh_upload_file` - Upload SSH
12. `terraform_init` - Init Terraform
13. `terraform_plan` - Plan Terraform
14. `terraform_apply` - Apply Terraform
15. `terraform_destroy` - Destroy Terraform
16. `gcp_natural_query` - Requêtes en langage naturel

#### Documentation
- README.md complet avec exemples d'utilisation
- QUICKSTART.md pour démarrage rapide
- API_EXAMPLES.md avec exemples curl
- Exemples Terraform dans terraform_examples/
- Guide des commandes courantes

#### Utilitaires
- `start_server.sh` - Script de démarrage interactif
- `mcp_helper.sh` - Gestionnaire du serveur (start, stop, status, logs)
- `.gitignore` - Protection des fichiers sensibles

#### Ressources MCP
- `gcp://instances` - Liste des instances GCP
- `ssh://keys` - Liste des clés SSH

### Modifié

#### Configuration
- Projet GCP : level-surfer-473817-p5
- Zone par défaut : us-central1-a
- Port : 5001 (inchangé)
- Protocole : MCP JSON-RPC 2.0 (inchangé)

#### Dépendances
Ajout de :
- `google-cloud-compute==1.14.1` - GCP SDK
- `google-auth==2.23.4` - Authentification GCP
- `paramiko==3.4.0` - Client SSH
- `cryptography==41.0.7` - Cryptographie pour SSH
- `python-terraform==0.10.1` - Wrapper Terraform

Conservation de :
- `Flask==3.0.0`
- `flask-cors==4.0.0`
- `python-dotenv==1.0.0`

### Supprimé
- Fonctionnalités PostgreSQL (list_fonction, Research_Data, Deep_research, get_schema, etc.)
- Connexions aux bases de données
- Schémas de bases de données
- Fonctions de conversion PostgreSQL

### Sécurité

#### Améliorations
- Stockage sécurisé des clés SSH avec permissions restrictives
- Les clés privées ne sont jamais exposées dans les réponses API
- Utilisation de credentials GCP via service account
- Support pour GOOGLE_APPLICATION_CREDENTIALS

#### À noter
- Les clés SSH sont stockées en clair sur disque (dans un répertoire protégé)
- Le service account a besoin des permissions Compute Engine Admin
- Les opérations Terraform sont auto-approuvées par défaut (configurable)

## [1.0.0] - Date antérieure

### Version initiale
- Serveur MCP pour PostgreSQL
- Accès à flask_crud_db et scraping_db
- Requêtes en langage naturel
- Exécution SQL directe
- Schémas de base de données

---

## Migration depuis la v1.0.0

Si vous utilisiez la version 1.0.0 (PostgreSQL), voici ce qu'il faut savoir :

### Incompatibilités
- **RUPTURE** : Tous les outils PostgreSQL ont été supprimés
- **RUPTURE** : Les endpoints REST spécifiques à PostgreSQL n'existent plus
- **RUPTURE** : Les ressources database:// ont été remplacées

### Comment migrer
1. Sauvegardez votre ancienne configuration si nécessaire
2. Installez les nouvelles dépendances : `pip3 install -r requirements.txt`
3. Configurez vos credentials GCP
4. Redémarrez le serveur

### Si vous avez besoin des deux
Vous pouvez faire tourner les deux versions en parallèle sur des ports différents :
- v1.0.0 (PostgreSQL) sur le port 5001
- v2.0.0 (GCP) sur le port 5002

Il suffit de modifier le port dans `app.run()` à la fin du fichier.

---

## Roadmap future

### Version 2.1.0 (planifié)
- [ ] Support pour Google Cloud Storage (buckets)
- [ ] Support pour Cloud SQL
- [ ] Gestion des réseaux VPC
- [ ] Load balancers GCP
- [ ] Auto-scaling groups
- [ ] Monitoring et alertes

### Version 2.2.0 (planifié)
- [ ] Support multi-cloud (AWS, Azure)
- [ ] Interface web de gestion
- [ ] Graphiques de coûts
- [ ] Templates Terraform prédéfinis
- [ ] CI/CD integration

### Version 3.0.0 (vision)
- [ ] Kubernetes (GKE) management
- [ ] Serverless (Cloud Functions, Cloud Run)
- [ ] ML/AI infrastructure deployment
- [ ] Multi-région deployment
- [ ] Disaster recovery automation

---

## Contributions

Les contributions sont les bienvenues ! Pour proposer une nouvelle fonctionnalité :

1. Ouvrez une issue pour discuter de votre idée
2. Créez une branche depuis main
3. Implémentez votre fonctionnalité
4. Ajoutez des tests et de la documentation
5. Soumettez une pull request

## Licence

MIT License - Voir LICENSE pour plus de détails

---

**Note** : Ce serveur est conçu pour être utilisé avec Claude Desktop via le protocole MCP. Pour plus d'informations sur MCP, consultez la [documentation officielle](https://modelcontextprotocol.io).
