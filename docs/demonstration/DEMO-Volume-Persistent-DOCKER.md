# Démo : persistance des volumes Docker

## Objectif

Montrer que les données stockées dans un volume Docker persistent même après la suppression des conteneurs.

---

## 1. Utilisez l'application pour générer des données

1. Accédez à l'application web (http://localhost:8080) et connectez-vous avec les identifiants fournis dans le fichier `.env`.
2. Executez une recherche d'image pour générer des données dans la base de données.

---

## 2. Supprimez la base de données et le conteneur webapp

```bash
docker-compose down
```

## 3. Vérifiez que le volume Docker existe toujours

```bash
docker volume ls
```

## 4. Redémarrez l'application

```bash
docker-compose up --build -d
```

---

## 5. Vérifiez que les données sont toujours présentes dans l'application

1. Accédez à l'application web (http://localhost:8080) et connectez-vous avec les mêmes identifiants.
2. Ouvrez les logs du conteneur webapp en temps réel pour observer les requêtes SQL et vérifier que les données sont toujours présentes dans la base de données.

    ```bash
    docker logs -f image-search-webapp
    ```

3. Effectuez la même recherche d'image que précédemment et vérifiez dans les logs que l'historique de recherche ou les descripteurs d'image sont trouvés dans la base de données, ce qui signifie que les données ont été conservées malgré la suppression du conteneur.

    ```bash
    [MYAPP] >> Search history found in database, skipping search process. # Si l'historique de recherche est trouvé dans la base de données, le processus de recherche et d'extraction des caractéristiques est ignoré.
    
    [MYAPP] >> Image descriptor found in database, skipping feature extraction. # Si le descripteur d'image est trouvé dans la base de données, le processus d'extraction des caractéristiques est ignoré.
    ```
