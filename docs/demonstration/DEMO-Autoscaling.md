# Démo Kubernetes - Autoscaling (HPA)

Cette démo montre le fonctionnement de l’autoscaling horizontal (HPA) de la webapp déployée sur Kubernetes (Minikube).

---

## Accès à l’application (obtention de l’adresse IP)

```bash
minikube service webapp-service
```

---

## Vérifier l’état du cluster

### Pods

```bash
kubectl get pods
```

### Autoscaling (HPA)

```bash
kubectl get hpa
```

---

## Observer le scaling en direct

```bash
kubectl get hpa -w
```

```bash
kubectl get pods -w
```

---

## Générer de la charge CPU (déclencher le scaling)

```bash
while true; do curl http://localhost:8080; done
```
