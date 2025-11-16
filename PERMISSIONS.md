# Architecture des Permissions - SoftDesk API

## Vue d'ensemble

L'API SoftDesk implémente un système complet de permissions basé sur **JWT (Json Web Token)** et des classes de permissions personnalisées. Cette architecture garantit que :

1. **Seuls les utilisateurs authentifiés** peuvent accéder aux ressources
2. **Les auteurs** ont le contrôle total sur leurs ressources
3. **Les contributeurs** peuvent accéder aux ressources du projet sans pouvoir les modifier
4. **Les données sensibles** sont protégées conformément au **RGPD**

---

## 1. Authentification JWT

### Installation et Configuration

```python
# settings.py
INSTALLED_APPS = [
    'rest_framework_simplejwt',
    ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
}
```

### Endpoints JWT

- **POST** `/api/token/` - Obtenir un token JWT (username + password)
- **POST** `/api/token/refresh/` - Renouveler le token d'accès

### Utilisation du Token

Ajouter le header à chaque requête authentifiée :

```
Authorization: Bearer <access_token>
```

---

## 2. Classes de Permissions Personnalisées

### `IsAuthor`

**Fichier** : `projects/permissions.py`

```python
class IsAuthor(permissions.BasePermission):
    """
    Permission: Seul l'auteur peut modifier la ressource.
    Lecture: Autorisée pour tous (SAFE_METHODS)
    """
```

**Utilisation** :
- ❌ Pas utilisée directement (pour future extension)

---

### `IsAuthorOrReadOnly`

**Logique** :
- ✅ Lecture (GET, HEAD, OPTIONS) : Autorisée pour tous
- ✅ Modification (POST, PUT, DELETE) : Uniquement l'auteur

**Ressources protégées** :
- **Projects** : L'auteur du projet peut le modifier, les autres peuvent le lire

**Exemple** :
```
GET /api/projects/1/          → ✅ Tous (lecture seule)
PUT /api/projects/1/          → ✅ Auteur du projet
DELETE /api/projects/1/       → ✅ Auteur du projet
```

---

### `IsProjectAuthorOrContributorReadOnly`

**Logique** :
- ✅ L'auteur du projet : Accès complet (CRUD)
- ✅ Les contributeurs du projet : Lecture seule (GET)
- ❌ Les utilisateurs non-membres : Accès refusé

**Ressources protégées** :
- **Issues** : Seuls les membres du projet peuvent les voir
- **Comments** : Seuls les membres du projet peuvent les voir

**Exemple d'Issue** :
```
GET /api/issues/1/            → ✅ Auteur du projet OU contributeur
POST /api/issues/             → ✅ Auteur du projet OU contributeur
PUT /api/issues/1/            → ✅ Auteur du problème (issue)
DELETE /api/issues/1/         → ✅ Auteur du problème
```

---

## 3. Permissions par Ressource

### 📊 Projects

| Action | Accès | Détails |
|--------|-------|---------|
| **List (GET)** | Public* | Retourne tous les projets |
| **Create (POST)** | Authentifié | L'utilisateur devient auteur |
| **Read (GET id)** | Public* | Lecture seule |
| **Update (PUT)** | Auteur | Seul l'auteur peut modifier |
| **Delete** | Auteur | Seul l'auteur peut supprimer |

*Public : accessible sans token, mais l'authentification globale est activée

**Permission Class** : `IsAuthenticated, IsAuthorOrReadOnly`

```python
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

---

### 👥 Contributors

| Action | Accès | Détails |
|--------|-------|---------|
| **List (GET)** | Authentifié | Liste les contributeurs |
| **Create (POST)** | Auteur du projet | Ajouter un contributeur |
| **Delete** | Auteur du projet | Retirer un contributeur |

**Permission Class** : `IsAuthenticated`

**Logique supplémentaire** :
- Filtrer les contributeurs par `project_id` si fourni

```python
def get_queryset(self):
    queryset = Contributor.objects.all()
    project_id = self.request.query_params.get('project_id')
    if project_id:
        queryset = queryset.filter(project_id=project_id)
    return queryset
```

---

### 🐛 Issues

| Action | Accès | Détails |
|--------|-------|---------|
| **List (GET)** | Auteur du projet OU contributeur | Voir les issues du projet |
| **Create (POST)** | Auteur du projet OU contributeur | Créer une issue |
| **Update (PUT)** | Auteur de l'issue | Modifier son issue |
| **Delete** | Auteur de l'issue | Supprimer son issue |

**Permission Class** : `IsAuthenticated, IsProjectAuthorOrContributorReadOnly`

```python
class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthorOrContributorReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

---

### 💬 Comments

| Action | Accès | Détails |
|--------|-------|---------|
| **List (GET)** | Auteur du projet OU contributeur | Voir les commentaires |
| **Create (POST)** | Auteur du projet OU contributeur | Ajouter un commentaire |
| **Update (PUT)** | Auteur du commentaire | Modifier son commentaire |
| **Delete** | Auteur du commentaire | Supprimer son commentaire |

**Permission Class** : `IsAuthenticated, IsProjectAuthorOrContributorReadOnly`

```python
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthorOrContributorReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

---

## 4. Flux de Sécurité Complet

### Scénario : Création d'une Issue par un Contributeur

**Étape 1** : Obtenir un token
```bash
POST /api/token/
{
  "username": "alice",
  "password": "password123"
}
# Réponse:
{
  "access": "eyJ0eXAiOiJKV1QiLC...",
  "refresh": "eyJ0eXAiOiJKV1QiLC..."
}
```

**Étape 2** : Ajouter un contributeur au projet
```bash
POST /api/contributors/
Authorization: Bearer <alice_token>
{
  "user": 2,  # bob
  "project": 1
}
# ✅ Réussi si alice est auteur du projet
```

**Étape 3** : Bob crée une issue
```bash
POST /api/issues/
Authorization: Bearer <bob_token>
{
  "name": "Bug de connexion",
  "description": "Impossible de se connecter",
  "priority": "HIGH",
  "tag": "BUG",
  "project": 1
}
# ✅ Réussi car bob est contributeur du projet 1
# author sera auto-défini : bob
```

**Étape 4** : Autres contributeurs lisent l'issue
```bash
GET /api/issues/1/
Authorization: Bearer <any_contributor_token>
# ✅ Réussi, lecture seule
```

**Étape 5** : Seul Bob peut modifier son issue
```bash
PUT /api/issues/1/
Authorization: Bearer <bob_token>
{
  "status": "In Progress"
}
# ✅ Réussi
```

```bash
PUT /api/issues/1/
Authorization: Bearer <alice_token>
{
  "status": "In Progress"
}
# ❌ 403 Forbidden - alice n'est pas l'auteur
```

---

## 5. Conformité RGPD et Confidentialité

### Protection des Données

**Champs sensibles exposés** :
- Les sérializers n'exposent que les champs publics
- Les tokens JWT ne contiennent pas de mots de passe
- Les accès au champ `author` sont contrôlés par les permissions

**Exemple - ProjectSerializer** :
```python
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        # Champs publics uniquement
        fields = ['id', 'name', 'description', 'type', 'author', 'created_time']
        # Les champs modifiés automatiquement
        read_only_fields = ['id', 'author', 'created_time']
```

### Masquage des Données par Rôle

**Propriétaire** : Accès complet aux ressources
**Contributeur** : Accès en lecture seule
**Non-authentifié** : ❌ Accès refusé (401 Unauthorized)

---

## 6. Matrice de Permissions Complète

```
┌─────────────────────┬──────────────┬─────────────────┬──────────────────┐
│ Ressource           │ Non-Auth     │ Contributeur    │ Auteur           │
├─────────────────────┼──────────────┼─────────────────┼──────────────────┤
│ Project LIST        │ ❌ 401       │ ✅ GET          │ ✅ GET           │
│ Project CREATE      │ ❌ 401       │ ✅ POST         │ ✅ POST          │
│ Project READ        │ ❌ 401       │ ✅ GET          │ ✅ GET           │
│ Project UPDATE      │ ❌ 401       │ ❌ 403          │ ✅ PUT           │
│ Project DELETE      │ ❌ 401       │ ❌ 403          │ ✅ DELETE        │
├─────────────────────┼──────────────┼─────────────────┼──────────────────┤
│ Issue in Project    │ ❌ 401       │ ✅ GET/POST     │ ✅ ALL           │
│ Issue by Other      │ ❌ 401       │ ✅ GET (l.seule)│ ✅ All           │
│ Comment in Issue    │ ❌ 401       │ ✅ GET/POST     │ ✅ ALL           │
│ Comment by Author   │ ❌ 401       │ ❌ 403 (PUT)    │ ✅ PUT/DELETE    │
└─────────────────────┴──────────────┴─────────────────┴──────────────────┘

Légende:
✅ Autorisé
❌ Refusé
401 = Non authentifié
403 = Non autorisé
```

---

## 7. Tester les Permissions

### Cas de Test : Lecture d'une Issue sans authentification

```bash
GET /api/issues/1/
# ❌ 401 Unauthorized
# {
#   "detail": "Authentication credentials were not provided."
# }
```

### Cas de Test : Modification d'une Issue par non-auteur

```bash
PUT /api/issues/1/
Authorization: Bearer <token_contributeur>
# ❌ 403 Forbidden
# {
#   "detail": "You do not have permission to perform this action."
# }
```

### Cas de Test : Accès à une Issue en tant que contributeur

```bash
GET /api/issues/1/
Authorization: Bearer <token_contributeur>
# ✅ 200 OK
# {
#   "id": 1,
#   "name": "Bug de connexion",
#   "author": 2,
#   ...
# }
```

---

## 8. Résumé de l'Implémentation

| Aspect | Solution |
|--------|----------|
| **Authentification** | JWT (SimpleJWT) |
| **Token Lifetime** | 1 heure (accès), 7 jours (refresh) |
| **Permissions par ressource** | Classes personnalisées dans `permissions.py` |
| **Contrôle d'accès** | Basé sur l'auteur et le rôle (contributeur/auteur) |
| **Données sensibles** | Masquées selon le rôle |
| **Confidentialité** | RGPD compliant (contrôle d'accès granulaire) |

---

## 9. Fichiers Modifiés

- ✅ `softdesksupport/settings.py` - Config JWT + REST Framework
- ✅ `softdesksupport/urls.py` - Endpoints JWT
- ✅ `projects/permissions.py` - Classes de permissions (NEW)
- ✅ `projects/views.py` - Application des permissions
- ✅ `projects/serializers.py` - Docstrings + RGPD

---

## 10. Points Clés

1. **Authentification obligatoire** : Tous les endpoints nécessitent un token JWT
2. **Auteur privilégié** : L'auteur d'une ressource peut la modifier/supprimer
3. **Contributeur restreint** : Les contributeurs ne peuvent que lire
4. **Projet isolé** : Les resources d'un projet ne sont visibles que aux membres
5. **Sécurité en cascade** : Les comments héritent de la visibilité de leur issue

---

**Version** : 1.0  
**Date** : 2025-11-02  
**Auteur** : SoftDesk Team
