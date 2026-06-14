# Manuel d'utilisation

## Pré-requis

- Docker et Docker Compose installés sur votre machine.

## Installation et création de l'image Docker

1. Cloner le projet :

    ```bash
        git clone https://github.com/TValisoa/Image_Search_Engine_2025.git
        cd Image_Search_Engine_2025
    ```

2. Télécharger les fichiers nécessaires (images, modèles, etc.) :

    ```bash
        sh download_files.sh
    ```

3. Build l'image Docker de l'application web :

    ```bash
        docker build -f Dockerfile.local -t image-search-local .
    ```

## Exécution de l'application en local

Exécuter l'application en local avec Run et l'emplacement de votre image à analyser, qui doivent etre importer dans le conteneur Docker (exemple : `/app/static/images.orig/12.jpg`) :

```bash
    docker run image-search-local run /app/static/images.orig/12.jpg
```
