# Manuel d'utilisation

## Pré-requis

- Docker et Docker Compose installés sur votre machine.
- Minikube installé sur votre machine pour le déploiement Kubernetes.

## Installation et déploiement

1. Cloner le projet :

    ```bash
        git clone https://github.com/TValisoa/Image_Search_Engine_2025.git
        cd Image_Search_Engine_2025
    ```

2. Télécharger les fichiers nécessaires (images, modèles, etc.) :

    ```bash
        sh download_files.sh
    ```

3. Créer un fichier `.env` à la racine du projet avec les variables d'environnement nécessaires (exemple : `DB_USER`, `DB_PASSWORD`, etc.) ou utiliser le fichier `.env` fourni comme modèle.

4. Déployer l'application soit avec Docker Compose, soit avec Minikube (Kubernetes) :

    - Avec Docker Compose :

        ```bash
            docker-compose up --build -d
        ```

    - Avec Minikube (Kubernetes) :

        ```bash
            sh ./mk/deploy.sh
        ```

## Accéder à l'application

- Avec Docker Compose : http://localhost:8080

- Avec Minikube (Kubernetes) : obtenir l'adresse IP du service webapp-service :

    ```bash
        minikube service webapp-service
    ```

## Utilisation de l'application

Le nom d'utilisateur et le mot de passe pour accéder à l'application sont fournis dans le fichier `.env`

## Scripts de démonstration

1. Démo de l'autoscaling (HPA) avec Kubernetes: [Voir la démo](../demonstration/DEMO-Autoscaling.md)
2. Démo de la persistance des volumes Docker: [Voir la démo](../demonstration/DEMO-Volume-Persistent-DOCKER.md)
3. Démo de la persistance des volumes Minikube: [Voir la démo](../demonstration/DEMO-Volume-Persistent-MINIKUBE.md)
