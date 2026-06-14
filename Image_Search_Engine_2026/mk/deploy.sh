#!/bin/bash
# Force l'utilisation du vrai disque dur dur pour les fichiers temporaires de build
export TMPDIR=$HOME/minikube_build_tmp
mkdir -p $TMPDIR

# Lancer minikube (si pas déjà lancé) avec 2.5GB de RAM et 2 CPUs pour éviter les problèmes de mémoire
minikube start --memory=2500 --cpus=2

# Vérifier que l'addon metrics-server est activé pour l'autoscaling
minikube addons enable metrics-server

echo "=== 1. Création / Mise à jour des Volumes ==="
kubectl apply -f mk/volumes.yml

echo "=== 2. Création / Mise à jour des Secrets et ConfigMaps ==="
kubectl create secret generic app-secrets --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
kubectl create configmap mysql-initdb --from-file=db/init.sql --dry-run=client -o yaml | kubectl apply -f -

echo "=== 3. Build et Déploiement des applications ==="
# On build la nouvelle image dans le cluster en supprimant les anciennes images pour éviter de saturer le disque
minikube ssh "docker system prune -f"
minikube image build -t image-search-webapp:latest .

kubectl apply -f mk/mysql-deployment.yaml
kubectl apply -f mk/webapp-deployment.yaml 
kubectl rollout restart deployment webapp

echo "=== 4. Activation de l'Autoscaling (HPA) ==="
kubectl apply -f mk/hpa.yml 

# Nettoyage du dossier temporaire de build
rm -rf $TMPDIR/*
minikube ssh "docker system prune -f"