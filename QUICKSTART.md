# Guide de démarrage rapide - Serveur MCP GCP

Ce guide vous permet de démarrer rapidement avec le serveur MCP GCP pour gérer votre infrastructure cloud via Claude.

## Démarrage en 5 minutes

### 1. Démarrer le serveur

```bash
cd /opt/git
python3 mcp_server.py
```

Vous devriez voir :
```
🚀 Serveur MCP GCP démarré sur http://0.0.0.0:5001
📡 Projet GCP: level-surfer-473817-p5
📍 Zone par défaut: us-central1-a
🔑 Répertoire des clés SSH: /home/ubuntu/.ssh_mcp
📡 Fonctionnalités disponibles:
   ✓ Gestion des VMs GCP (créer, lister, démarrer, arrêter, supprimer)
   ✓ Gestion des clés SSH (générer, stocker, utiliser)
   ✓ Exécution SSH distante sur les VMs
   ✓ Déploiement Terraform
   ✓ Interprétation en langage naturel
```

### 2. Scénarios d'utilisation courants

#### Scénario 1 : Créer une VM et installer un serveur web

Avec Claude, vous pouvez dire :

```
"Je veux créer une nouvelle VM sur GCP et installer nginx dessus"
```

Claude va :
1. Générer une clé SSH pour vous
2. Créer la VM avec cette clé
3. Attendre que la VM démarre
4. Se connecter via SSH et installer nginx
5. Vous donner l'IP pour accéder à votre serveur

#### Scénario 2 : Lister toutes vos VMs

```
"Montre-moi toutes mes VMs GCP"
```

Claude va lister toutes vos VMs avec leurs détails (nom, statut, IPs, etc.)

#### Scénario 3 : Exécuter une commande sur une VM

```
"Exécute 'df -h' sur ma VM nommée 'mon-serveur-web'"
```

Claude va se connecter via SSH et exécuter la commande.

#### Scénario 4 : Déployer avec Terraform

```
"Déploie l'infrastructure Terraform dans /opt/git/terraform_examples"
```

Claude va :
1. Initialiser Terraform
2. Montrer le plan de déploiement
3. Appliquer les changements
4. Vous donner les outputs (IPs, noms, etc.)

### 3. Flux de travail complet

Voici un exemple de workflow complet pour déployer une application :

```
Vous : "Je veux déployer un serveur web avec une base de données"

Claude : "Je vais vous aider. D'abord, créons les ressources nécessaires."

1. Génération de clé SSH
   Claude utilise : ssh_generate_key

2. Création de la VM web
   Claude utilise : gcp_create_instance
   Nom: web-server
   Type: e2-medium
   Clé SSH: la clé générée

3. Création de la VM base de données
   Claude utilise : gcp_create_instance
   Nom: db-server
   Type: e2-standard-2
   Clé SSH: la même clé

4. Installation de nginx sur la VM web
   Claude utilise : ssh_execute
   Commande: apt update && apt install -y nginx

5. Installation de PostgreSQL sur la VM db
   Claude utilise : ssh_execute
   Commande: apt update && apt install -y postgresql

Claude : "Votre infrastructure est prête !
- Serveur web: http://<IP-externe-web>
- Serveur DB: <IP-interne-db>

Vous pouvez maintenant configurer votre application."
```

## Commandes utiles

### Tester le serveur localement

```bash
# Test du endpoint health
curl http://localhost:5001/health

# Devrait retourner :
{
  "status": "healthy",
  "service": "GCP Infrastructure MCP Server",
  "version": "2.0.0",
  "gcp_project": "level-surfer-473817-p5",
  "gcp_zone": "us-central1-a",
  "ssh_keys_count": 0
}
```

### Vérifier les clés SSH générées

```bash
ls -la ~/.ssh_mcp/
```

### Redémarrer le serveur

```bash
# Trouver le processus
ps aux | grep mcp_server

# Tuer le processus
kill <PID>

# Redémarrer
python3 mcp_server.py
```

## Exemples de requêtes Claude

### Gestion de VMs

- "Crée une VM nommée 'api-server' avec 4GB de RAM"
- "Liste toutes mes VMs actives"
- "Arrête la VM 'test-server'"
- "Supprime toutes les VMs qui commencent par 'test-'"
- "Montre-moi les détails de 'production-web'"

### SSH et configuration

- "Génère une nouvelle clé SSH appelée 'production-key'"
- "Liste toutes mes clés SSH"
- "Connecte-toi à la VM 'web-server' et exécute 'top'"
- "Upload le fichier config.json vers /etc/app/config.json sur 'api-server'"
- "Installe Docker sur toutes mes VMs"

### Terraform

- "Initialise Terraform dans mon dossier infrastructure"
- "Montre-moi ce qui va être créé par Terraform"
- "Applique les changements Terraform"
- "Détruis toute l'infrastructure Terraform"

### Déploiement complet

- "Déploie une application web complète avec load balancer"
- "Crée un cluster de 3 VMs pour mon application"
- "Configure un environnement de développement avec une VM et une base de données"

## Conseils

### Sécurité
- Les clés SSH sont stockées dans `~/.ssh_mcp/` avec les bonnes permissions
- Ne partagez jamais vos clés privées
- Utilisez des clés différentes pour dev/staging/production
- Supprimez les VMs de test régulièrement pour éviter les coûts

### Performance
- Utilisez des types de machines appropriés (e2-micro pour les tests, e2-standard pour la production)
- N'oubliez pas d'arrêter les VMs non utilisées
- Utilisez des disques de la bonne taille (pas trop grands pour éviter les coûts)

### Terraform
- Toujours faire `terraform plan` avant `terraform apply`
- Utilisez des fichiers de variables pour faciliter les changements
- Commentez vos fichiers Terraform pour la documentation

## Dépannage rapide

### Le serveur ne démarre pas
```bash
# Vérifier les dépendances
pip3 install -r requirements.txt

# Vérifier le fichier de credentials
ls -l service-account-key.json
```

### Erreur de connexion GCP
```bash
# Vérifier les permissions du service account
# Aller dans GCP Console > IAM & Admin > Service Accounts
# Vérifier que le service account a les rôles nécessaires
```

### Erreur SSH
```bash
# Lister les clés
ls -la ~/.ssh_mcp/

# Vérifier les permissions
chmod 600 ~/.ssh_mcp/*
chmod 644 ~/.ssh_mcp/*.pub
```

## Prochaines étapes

1. **Explorez les exemples Terraform** : `cd terraform_examples && cat README.md`
2. **Lisez la documentation complète** : `cat README.md`
3. **Expérimentez avec Claude** : Essayez différentes commandes en langage naturel
4. **Créez vos propres templates Terraform** : Personnalisez les déploiements

## Support

Pour toute question, consultez :
- README.md : Documentation complète
- terraform_examples/README.md : Exemples Terraform
- GitHub Issues : Pour rapporter des bugs

Bon déploiement ! 🚀
