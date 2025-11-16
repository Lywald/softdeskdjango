# Guide de Test - Permissions JWT

## Prérequis

1. Serveur en cours d'exécution : `poetry run python manage.py runserver`
2. Au moins 2 utilisateurs créés :
   - User 1 (alice) - Auteur du projet
   - User 2 (bob) - Contributeur

## 1. Obtenir un Token JWT

### Request
```bash
POST /api/token/
Content-Type: application/json

{
  "username": "alice",
  "password": "your_password"
}
```

### Response (exemple)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Garder le token `access` pour les prochaines requêtes**

---

## 2. Créer un Projet (comme Alice)

### Request
```bash
POST /api/projects/
Authorization: Bearer <alice_access_token>
Content-Type: application/json

{
  "name": "Mon Super Projet",
  "description": "Description du projet",
  "type": "back-end"
}
```

### Response (✅ 201 Created)
```json
{
  "id": 1,
  "name": "Mon Super Projet",
  "description": "Description du projet",
  "type": "back-end",
  "author": 1,
  "created_time": "2025-11-02T18:10:15Z"
}
```

---

## 3. Ajouter un Contributeur (comme Alice)

### Request
```bash
POST /api/contributors/
Authorization: Bearer <alice_access_token>
Content-Type: application/json

{
  "user": 2,
  "project": 1
}
```

### Response (✅ 201 Created)
```json
{
  "id": 1,
  "user": 2,
  "project": 1,
  "created_time": "2025-11-02T18:10:20Z"
}
```

---

## 4. Créer une Issue (comme Bob, contributeur)

### Request
```bash
POST /api/issues/
Authorization: Bearer <bob_access_token>
Content-Type: application/json

{
  "name": "Bug de connexion",
  "description": "L'utilisateur ne peut pas se connecter",
  "priority": "HIGH",
  "tag": "BUG",
  "status": "To Do",
  "project": 1,
  "assignee": null
}
```

### Response (✅ 201 Created)
```json
{
  "id": 1,
  "name": "Bug de connexion",
  "description": "L'utilisateur ne peut pas se connecter",
  "priority": "HIGH",
  "tag": "BUG",
  "status": "To Do",
  "project": 1,
  "author": 2,
  "assignee": null,
  "created_time": "2025-11-02T18:10:25Z"
}
```

---

## 5. Tester l'Accès Contrôlé

### 5a. Bob lit sa propre issue ✅
```bash
GET /api/issues/1/
Authorization: Bearer <bob_access_token>
```
**Résultat** : ✅ 200 OK

### 5b. Bob modifie sa propre issue ✅
```bash
PUT /api/issues/1/
Authorization: Bearer <bob_access_token>
Content-Type: application/json

{
  "status": "In Progress"
}
```
**Résultat** : ✅ 200 OK

### 5c. Alice essaie de modifier l'issue de Bob ❌
```bash
PUT /api/issues/1/
Authorization: Bearer <alice_access_token>
Content-Type: application/json

{
  "status": "Finished"
}
```
**Résultat** : ❌ 403 Forbidden

---

## 6. Tester sans Authentification ❌

### Request
```bash
GET /api/projects/
```

### Response (❌ 401 Unauthorized)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 7. Tester le Refresh Token

### Request
```bash
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "<bob_refresh_token>"
}
```

### Response (✅ 200 OK)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Matrice de Test Complète

| Test | HTTP | Endpoint | Token | Attendu |
|------|------|----------|-------|---------|
| Sans auth | GET | /api/projects/ | ❌ | 401 |
| Alice lit ses projets | GET | /api/projects/ | alice | 200 |
| Alice crée projet | POST | /api/projects/ | alice | 201 |
| Alice modifie son projet | PUT | /api/projects/1/ | alice | 200 |
| Bob lit le projet d'Alice | GET | /api/projects/1/ | bob | 200 |
| Bob modifie le projet d'Alice | PUT | /api/projects/1/ | bob | 403 |
| Bob crée issue (contributeur) | POST | /api/issues/ | bob | 201 |
| Bob modifie sa issue | PUT | /api/issues/1/ | bob | 200 |
| Alice modifie issue de Bob | PUT | /api/issues/1/ | alice | 403 |
| Non-contributeur lit issue | GET | /api/issues/1/ | charlie | 403 |

---

## Dépannage

### Erreur : "Token is invalid or expired"
- Régénérer un nouveau token via POST /api/token/

### Erreur : "Authentication credentials were not provided"
- Ajouter le header : `Authorization: Bearer <token>`

### Erreur : "You do not have permission to perform this action"
- Vérifier votre rôle (auteur vs contributeur vs non-membre)

---

**Version** : 1.0  
**Date** : 2025-11-02
