# Exemples Terraform pour GCP

Ce répertoire contient des exemples de configurations Terraform pour déployer de l'infrastructure GCP.

## Exemple 1 : VM avec Nginx

Le fichier `main.tf` déploie une VM GCP avec :
- Nginx installé automatiquement
- Règles de pare-feu pour HTTP et HTTPS
- IP externe pour l'accès public

### Utilisation avec Claude

Vous pouvez utiliser Claude et le serveur MCP pour déployer cette infrastructure en langage naturel :

```
Utilisateur : Déploie l'infrastructure définie dans /opt/git/terraform_examples

Claude :
1. Je vais d'abord initialiser Terraform
   [utilise terraform_init avec working_dir="/opt/git/terraform_examples"]

2. Voyons ce qui va être créé
   [utilise terraform_plan avec working_dir="/opt/git/terraform_examples"]

3. Tout semble bon, j'applique maintenant
   [utilise terraform_apply avec working_dir="/opt/git/terraform_examples"]

Infrastructure déployée ! Voici les détails :
- Nom de l'instance : terraform-vm
- IP externe : 35.xxx.xxx.xxx
- Vous pouvez accéder à votre serveur web à http://35.xxx.xxx.xxx
```

### Utilisation manuelle

1. Copiez le fichier de variables :
```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Modifiez les valeurs dans `terraform.tfvars` selon vos besoins

3. Initialisez Terraform :
```bash
terraform init
```

4. Voyez le plan de déploiement :
```bash
terraform plan
```

5. Appliquez les changements :
```bash
terraform apply
```

6. Pour détruire l'infrastructure :
```bash
terraform destroy
```

## Variables disponibles

- `instance_name` : Nom de l'instance VM (défaut: terraform-vm)
- `machine_type` : Type de machine GCP (défaut: e2-medium)
- `disk_size_gb` : Taille du disque en GB (défaut: 20)

## Outputs

Après le déploiement, Terraform affichera :
- `instance_name` : Nom de l'instance créée
- `instance_external_ip` : IP externe de l'instance
- `instance_internal_ip` : IP interne de l'instance
- `instance_id` : ID de l'instance

## Personnalisation

Vous pouvez modifier `main.tf` pour :
- Changer l'image du système d'exploitation
- Ajouter plus de règles de pare-feu
- Configurer des disques supplémentaires
- Ajouter des métadonnées personnalisées
- Installer d'autres logiciels via le script de démarrage
