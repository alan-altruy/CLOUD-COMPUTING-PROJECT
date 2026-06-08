#!/bin/bash

echo "=== 1. Création / Mise à jour des Volumes ==="
kubectl apply -f mk/volumes.yml

echo "=== 2. Création / Mise à jour des Secrets et ConfigMaps ==="
kubectl create secret generic app-secrets --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
kubectl create configmap mysql-initdb --from-file=db/init.sql --dry-run=client -o yaml | kubectl apply -f -

echo "=== 3. Build et Déploiement des applications ==="
# On build la nouvelle image dans le cluster
minikube image build -t image-search-webapp:latest .

kubectl apply -f mk/mysql-deployment.yaml
kubectl apply -f mk/webapp-deployment.yaml 
kubectl rollout restart deployment webapp

echo "=== 4. Activation de l'Autoscaling (HPA) ==="
kubectl apply -f mk/hpa.yml 

echo "=== 5. Nettoyage des anciens tunnels ==="
# On tue proprement l'ancien port-forward s'il tournait déjà pour éviter les conflits de port
pkill -f "port-forward service/webapp-service" || true

echo "=== 6. Attente de la stabilisation du déploiement ==="

# Attend que TOUS les pods du déploiement 'webapp' soient Ready=True
# --timeout=60s évite que le script ne bloque indéfiniment si ton code Python a une vraie erreur
echo "Attente que l'application soit prête..."
if kubectl rollout status deployment/webapp --timeout=60s; then
    
    echo "=== 7. Exposition sur http://localhost:8080 (via 0.0.0.0) ==="
    # Maintenant on est SÛR que l'app écoute, on peut lancer le port-forward sereinement
    kubectl port-forward service/webapp-service 8080:8080 --address='0.0.0.0' > /dev/null 2>&1 &
    
    echo "Déploiement terminé ! Accédez à l'application via http://localhost:8080"
else
    echo "Le déploiement a échoué ou a mis trop de temps à démarrer."
    echo "Vérifie les logs avec : kubectl logs deployment/webapp"
    exit 1
fi