
# Multimedia Research Engine

Projet réalisé dans le cadre de l'AA « I-ILIA-208: Cloud & Edge Computing  ».

But : un moteur de recherche d'images utilisant des features extraites par deep learning pour retrouver des images similaires.

Le principal Objectif de ce projet est de se familiariser avec les concepts de déploiement d'applications dans le cloud, en particulier en utilisant des conteneurs Docker et Kubernetes (Minikube). Le projet vise à démontrer la persistance des données dans les volumes Docker et Minikube, ainsi que l'autoscaling horizontal (HPA) de l'application web.

## Avancement

### 2 — Déploiement Cloud (SaaS)

- [x] Indexation locale
- [x] Test et configuration Cloud
- [x] Dockerisation de l’application
- [x] Interface Web SaaS
- [x] Configuration d’accès
- [x] Personnalisation du service
- [x] Volumes Docker (cache persistant)
- [x] Base de données (connection)
- [x] Base de données (traçabilité)
- [x] Mise à l’échelle
- [x] Cybersécurité
- [x] Intégration continue (CI/CD)

## Auteurs

- Alan Altruy
- Odan Lafrance

## Manuel d’utilisation

Voir le [manuel d’utilisation](docs/manuels/MANUEL_D_UTILISATION.md) pour les instructions d’installation et d’utilisation de l’application web, ainsi que pour les démonstrations de persistance des volumes et d’autoscaling.

Voir le [manuel d’utilisation local](docs/manuels/MANUEL_D_UTILISATION_LOCAL.md) pour les instructions d’installation et d’utilisation de l’application local avec argument d’image à analyser.

## Liens

- 🌐 Site web : [Accéder à l’application en ligne](https://groupe12.tp-cloud.deepilia.com) - interface SaaS du moteur de recherche multimédia
- 📱 Application Android : [Voir le dépôt GitHub Android](https://github.com/alan-altruy/CLOUD-COMPUTING-PROJECT-ANDROID.git) - application mobile dédiée à l’accès au moteur de recherche
