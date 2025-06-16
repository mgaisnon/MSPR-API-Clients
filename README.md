# MSPR - API Clients

![Build](https://img.shields.io/github/actions/workflow/status/mgaisnon/MSPR-API-Clients/ci.yml?branch=main)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![Docker Image](https://img.shields.io/docker/image-size/mgaisnon/mspr-api-clients/latest)

API REST pour la gestion des clients de l'application PayeTonKawa.

## 🚀 Stack technique
- Langage : Python 3.11
- Framework : FastAPI
- Base de données : MySQL
- ORM : SQLAlchemy + Pydantic
- Conteneurisation : Docker

## 🔧 Installation locale
```bash
docker compose up --build
````

API accessible sur : [http://localhost:8001/docs](http://localhost:8001/docs)

## 🔍 Endpoints principaux

* `GET /clients` : Liste des clients
* `POST /clients` : Création d'un client
* `GET /clients/{id}` : Détails d'un client
* `PUT /clients/{id}` : Mise à jour d'un client
* `DELETE /clients/{id}` : Suppression d'un client

## ⚙️ Variables d'environnement

```env
DATABASE_URL=mysql+pymysql://user:password@db-clients:3306/clients_db
```

## 📉 Tests

```bash
pytest --cov=app
```
