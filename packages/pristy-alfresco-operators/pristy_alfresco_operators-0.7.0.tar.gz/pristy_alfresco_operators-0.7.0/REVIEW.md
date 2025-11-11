# Review - pristy-alfresco-operators

Date: 2025-10-16
Version: 0.4.1

## 🔍 Vue d'ensemble

Librairie Python partagée fournissant des opérateurs Airflow personnalisés pour interagir avec l'API REST Alfresco.
Structure propre, bonne séparation des responsabilités, mais quelques points de sécurité et qualité à corriger.

---

## ✅ Points Positifs

1. **Architecture claire** : Chaque opérateur a une responsabilité unique et bien définie
2. **Licences SPDX** : Headers de licence Apache-2.0 présents sur tous les fichiers
3. **Gestion de la pagination** : Bien implémentée dans `fetch_children_node_operator.py` et `search_node_operator.py`
4. **Validation JSON Schema** : Présente dans `PushToKafkaOperator` avant envoi Kafka
5. **Documentation** : Docstrings présentes sur les opérateurs
6. **Tests** : Présence de tests pytest (à vérifier)

---

## 🔴 Points Critiques

### 1. ✅ Injection SQL corrigée (save_folder_to_db.py:36-37)

**Fichier** : `pristy/alfresco_operator/save_folder_to_db.py`

~~Problème : Injection SQL via f-string~~

**✅ CORRIGÉ** : Utilise maintenant `cur.executemany()` avec paramètres préparés

### 2. ✅ Injection SQL corrigée (update_node_db.py:23-34)

Déjà corrigée lors de la review de dag-pristy-assmat. Utilise maintenant `sql.Identifier()` et paramètres préparés.

---

## 🟠 Bugs / Incohérences

### 3. ✅ Gestion des connexions PostgreSQL corrigée

**Fichiers concernés** :
- `save_folder_to_db.py` (✅ corrigé)
- `create_children_table.py` (✅ corrigé)
- `update_node_db.py` (✅ corrigé)

~~Problème : Les connexions ne sont pas fermées en cas d'exception~~

**✅ CORRIGÉ** : Ajout de blocs `try/finally` pour fermer proprement curseurs et connexions

### 4. Gestion d'erreurs Kafka incomplète (push_node_to_kafka.py:100-112)

Le callback `acked()` log les erreurs mais ne met pas à jour l'état en base. Si un message échoue à la livraison, l'état reste "sending" au lieu de "fail".

**Solution** : Implémenter un mécanisme de tracking des erreurs dans `acked()`

### 5. Code mort dans transform_file.py:29

```python
def execute(self, context, mapping_func=None):  # ← mapping_func ignoré
    # ...
    if self.mapping_func is not None:  # ← Utilise self.mapping_func au lieu du paramètre
```

Le paramètre `mapping_func` dans `execute()` n'est jamais utilisé (shadowed par `self.mapping_func`)

---

## 🟡 Qualité du Code

### 6. TODO non résolus

- `search_node_operator.py:11` : "TODO: add parameter to sort field"
- `transform_file.py:25` : "TODO rename to nodes"
- `transform_folder.py:24` : "TODO rename to nodes"

### 7. Duplication de code

**Pagination** : Logique similaire dans :
- `fetch_children_node_operator.py:83-94`
- `search_node_operator.py:85-96`

**Solution** : Extraire une méthode commune ou une classe utilitaire `PaginationHelper`

**Transformation** : Code très similaire dans :
- `transform_file.py:execute()`
- `transform_folder.py:execute()`

**Solution** : Factoriser la création du nœud de base

### 8. Hardcoded values

**Fichiers** :
- `save_folder_to_db.py:37` : Nom de table hardcodé `export_alfresco_folder_children`
- `create_children_table.py:22-32` : Nom de table hardcodé
- `update_node_db.py:12` : Valeur par défaut `export_alfresco_folder_children`

**Solution** : Rendre configurable via paramètre ou Variable Airflow

### 9. Imports au mauvais niveau

**Fichier** : `search_node_operator.py:13`
```python
class AlfrescoSearchOperator(BaseOperator):
    from requests import Response  # ← Import dans la classe
```

**Solution** : Déplacer l'import en haut du fichier

### 10. Gestion des fichiers sans `with`

**Fichier** : `push_node_to_kafka.py:38-41`
```python
with open(dag_param['local_source_file'], 'rb') as f:
    file_content = f.read()
```

✅ Correct, mais manque de gestion d'erreur si le fichier n'existe pas

---

## 🔵 Améliorations Architecturales

### 11. Validation incomplète

**Fichier** : `push_node_to_kafka.py:96-98`

La validation jsonschema lance une `RuntimeError` sans mettre à jour l'état en base. Le record reste en état "new" ou "running".

**Solution** : Appeler `update_state_db(local_db_id, "validation_error", ...)` avant le raise

### 12. Logs insuffisants

- Pas de métriques (nombre de nœuds traités, temps d'exécution, taille des données)
- Logs de debug mais peu de logs info pour le monitoring
- Pas de logs structurés (JSON)

### 13. Dépendance à `importlib.resources`

**Fichier** : `push_node_to_kafka.py:17`

```python
with resources.open_text("pristy.schema", "node_injector.schema.json") as schema_file:
```

Utilise l'ancien `importlib.resources` au lieu de `importlib.resources.files()` (Python 3.9+)

### 14. Pas de retry policy

Les opérateurs n'ont pas de stratégie de retry configurée par défaut. Dépend entièrement de la configuration Airflow au niveau DAG.

**Suggestion** : Définir des valeurs par défaut raisonnables (ex: `retries=3, retry_delay=timedelta(minutes=5)`)

### 15. Nom de table PostgreSQL hardcodé

Tous les opérateurs utilisent la table `export_alfresco_folder_children` sans possibilité de la configurer.

**Solution** : Ajouter un paramètre `table_name` avec valeur par défaut

---

## 📋 Actions Prioritaires

### ✅ Urgent (Sécurité) - TRAITÉ
1. ~~**Corriger injection SQL** dans `save_folder_to_db.py:36-37`~~ ✅
2. ~~**Ajouter try/finally** pour fermer les connexions PostgreSQL~~ ✅

### 🟠 Important (Stabilité)
3. **Corriger gestion erreurs Kafka** dans `push_node_to_kafka.py`

### 🟡 Améliorations (Qualité)
4. **Factoriser duplication** : pagination, transformation
5. **Résoudre TODOs** : rename `child` → `nodes`, ajouter sort parameter
6. **Enrichir logs** avec métriques et contexte

### 🔵 Nice-to-have
7. **Tests unitaires** : Vérifier couverture et ajouter tests manquants
8. **Documentation** : Ajouter exemples d'utilisation dans README
9. **Type hints** : Compléter les annotations de types

---

## 🧪 Tests à Vérifier

```bash
cd /home/jlesage/Projets/Airflow/pristy-alfresco-operators
pytest tests/ -v
```

Vérifier :
- Couverture de code
- Tests d'intégration avec PostgreSQL/Kafka
- Tests de validation jsonschema
- Tests de gestion d'erreurs

---

## 📦 Dépendances

Actuelles (v0.4.1) :
```toml
apache-airflow>=2.9.1,<3.0.0
requests>=2.32.4
jsonschema>=4.24.0
pendulum>=3.1.0
apache-airflow-providers-apache-kafka>=1.6.1
apache-airflow-providers-http>=4.13.3
apache-airflow-providers-postgres>=5.14.0
```

✅ Dépendances à jour et bien gérées

---

## 🎯 Conclusion

**Note globale** : 7/10

**Forces** :
- Architecture propre et modulaire
- Bonne gestion de la pagination
- Validation jsonschema présente

**Faiblesses** :
- ⚠️ Injection SQL critique à corriger immédiatement
- Gestion des ressources (connexions) à améliorer
- Duplication de code à factoriser

**Recommandation** : Corriger les points critiques avant la prochaine release (v0.4.2)
