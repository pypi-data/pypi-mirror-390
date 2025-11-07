# 🚦 \*\*Simulateur de Trafic petit simulateur de trafic écrit en Python.

## 🧩 **Dépendances**

- ✅ Aucune bibliothèque de tracé externe n'est requise. Le simulateur exporte les séries temporelles de positions en CSV (`data/positions.csv`).
- 🖼️ Si vous souhaitez visualiser les résultats, installez une bibliothèque de tracé (par ex. `matplotlib`) séparément.

## ▶️ **Exécution**

Lancer la simulation depuis la racine du projet :

```powershell
python main.py
```

## 📝 **Notes Importantes**

- 📦 Le package local `io` a été renommé en `io_pkg` pour éviter les conflits avec le module standard `io` de Python.
- ⚠️ Si vous rencontrez un `ImportError` lié à `io`, utilisez `from io_pkg import ...` au lieu de `from io import ...`.

## ℹ️ **Fichiers Utiles**

- `data/config_reseau.json` — configuration d'exemple (routes et véhicules)
- `data/resultats.json` — statistiques exportées après une simulation
- `data/positions.csv` — positions temporelles exportées par `Simulateur.tracer_positions()`

## 💡 **Astuce**

Pour exécuter les tests :

```powershell
python -m pytest -q
```

## 🏗️ **Architecture du Projet**

La structure réelle trouvée dans ce dépôt (raccourcie aux fichiers pertinents) est :

```
simulateur_trafic/
├─ .github/                     # workflows CI (optionnel)
├─ core/
│  ├─ __init__.py
│  ├─ analyseur.py
│  └─ simulateur.py
├─ data/
│  └─ config_reseau.json
├─ docs/
│  ├─ conf.py
│  ├─ index.rst
│  └─ modules.rst
├─ exceptions/                  # 🆕 Module d'exceptions personnalisées
│  ├─ __init__.py
│  ├─ base_exceptions.py
│  ├─ vehicule_exceptions.py
│  ├─ route_exceptions.py
│  ├─ simulateur_exceptions.py
│  ├─ analyseur_exceptions.py
│  └─ README.md
├─ io_pkg/
│  ├─ __init__.py
│  ├─ affichage.py
│  └─ export.py
├─ junit-tests/                 # Tests unittest/JUnit
│  └─ ...
├─ main.py
├─ models/
│  ├─ __init__.py
│  ├─ reseau.py
│  ├─ route.py
│  └─ vehicule.py
├─ README.md
├─ requirements.txt
├─ demo_exceptions.py           # 🆕 Démonstration des exceptions
├─ TP_RAPPORT_EXCEPTIONS.md     # 🆕 Rapport TP exceptions
└─ tests/
   ├─ conftest.py
   ├─ test_vehicule.py
   ├─ test_route.py
   ├─ test_reseau.py
   └─ test_exceptions.py        # 🆕 Tests des exceptions
```

## 🧭 **Flux de Données**

- Le `Simulateur` charge `data/config_reseau.json` au démarrage.
- Il instancie les `Route` et `Vehicule` dans `models`.
- À chaque pas de simulation, le `Simulateur` met à jour chaque `Route`, qui appelle `Vehicule.avancer(delta_t)`.
- Les `Analyseur` calcule des statistiques (nombre de véhicules, vitesses, moyenne).
- `io_pkg.Affichage` affiche l'état dans la console ; `io_pkg.Export` écrit `resultats.json`.
- Optionnel: `Simulateur.tracer_positions()` exporte `data/positions.csv` pour visualisation.

## 🔌 **Points d'Extension / Guide Développement**

- Ajouter des comportements de véhicules : modifier `models/vehicule.py` (accélération, freins, changement de vitesse).
- Ajouter des stratégies de routage : étendre `models/reseau.py` et `models/route.py`.
- Remplacer l'affichage : implémenter une nouvelle classe dans `io_pkg` (par ex. `affichage_gui.py`) et l'injecter dans `Simulateur`.
- Ajouter de nouveaux analyseurs : créer des modules dans `core/` et les appeler depuis `Simulateur`.

## 🧪 **Tests et CI**

### **Tests pytest** (dossier `tests/`)

Exécuter les tests avec pytest :

```powershell
python -m pytest -q
```

**Tests des exceptions:**

```powershell
python -m pytest tests/test_exceptions.py -v
```

### **Tests unittest/JUnit** (dossier `junit-tests/`)

Le projet inclut également des tests au format **unittest** (bibliothèque standard Python) qui génèrent des rapports compatibles JUnit XML.

#### **Structure des tests JUnit**

- `test_vehicule_unittest.py` — Tests unitaires pour la classe Vehicule
- `test_route_unittest.py` — Tests unitaires pour la classe Route
- `test_reseau_unittest.py` — Tests unitaires pour la classe ReseauRoutier
- `test_simulateur_unittest.py` — Tests d'intégration pour le Simulateur
- `run_junit_tests.py` — Script pour exécuter tous les tests et générer les rapports XML
- `xml-reports/` — (généré) Rapports JUnit XML après exécution

#### **Exécution des tests JUnit**

**Option 1: Avec génération de rapports JUnit XML (recommandé)**

Installer d'abord le générateur de rapports XML :

```powershell
pip install unittest-xml-reporting
```

Puis exécuter tous les tests :

```powershell
python junit-tests/run_junit_tests.py
```

Les rapports XML seront générés dans `junit-tests/xml-reports/`.

**Option 2: Exécution unittest standard (sans XML)**

Exécuter tous les tests :

```powershell
python -m unittest discover junit-tests -p "test_*_unittest.py" -v
```

Exécuter un fichier de test spécifique :

```powershell
python junit-tests/test_vehicule_unittest.py
```

#### **Format des rapports JUnit**

Les rapports XML générés sont au format JUnit et peuvent être utilisés avec :

- Jenkins
- GitLab CI
- GitHub Actions
- Azure DevOps
- SonarQube
- Autres outils CI/CD

#### **Note importante**

Les tests pytest originaux sont conservés dans le dossier `tests/` et restent inchangés. Les deux formats de tests coexistent.

### **CI/CD**

Un workflow GitHub Actions (si présent) installe les dépendances, exécute les tests et construit la documentation Sphinx.

# 🚨 Module d'Exceptions Personnalisées

Ce dossier contient toutes les exceptions personnalisées du simulateur de trafic, organisées par domaine fonctionnel.

## 📋 Structure

```
exceptions/
├── __init__.py                    # Point d'entrée, exporte toutes les exceptions
├── base_exceptions.py             # Exception de base SimulateurException
├── vehicule_exceptions.py         # Exceptions liées aux véhicules
├── route_exceptions.py            # Exceptions liées aux routes
├── simulateur_exceptions.py       # Exceptions du simulateur principal
└── analyseur_exceptions.py        # Exceptions de l'analyseur statistique
```

## 🎯 Types d'Exceptions

### **Exception de Base**

- `SimulateurException` - Classe parente de toutes les exceptions du projet

### **Exceptions Véhicule** (`vehicule_exceptions.py`)

| Exception                   | Code   | Description                              |
| --------------------------- | ------ | ---------------------------------------- |
| `VehiculeException`         | -      | Classe de base pour les erreurs véhicule |
| `VitesseNegativeException`  | VEH001 | Vitesse négative détectée                |
| `PositionInvalideException` | VEH002 | Position hors limites                    |

### **Exceptions Route** (`route_exceptions.py`)

| Exception                        | Code   | Description                           |
| -------------------------------- | ------ | ------------------------------------- |
| `RouteException`                 | -      | Classe de base pour les erreurs route |
| `RoutePleineException`           | RTE001 | Capacité maximale atteinte            |
| `VehiculeDejaPresent`            | RTE002 | Véhicule déjà sur la route            |
| `RouteInexistanteException`      | RTE003 | Route non trouvée dans le réseau      |
| `LongueurRouteInvalideException` | RTE004 | Longueur de route <= 0                |

### **Exceptions Simulateur** (`simulateur_exceptions.py`)

| Exception                       | Code   | Description                        |
| ------------------------------- | ------ | ---------------------------------- |
| `ConfigurationException`        | -      | Classe de base pour erreurs config |
| `FichierConfigurationException` | SIM001 | Fichier config manquant/invalide   |
| `IterationsInvalidesException`  | SIM002 | Nombre d'itérations invalide       |

### **Exceptions Analyseur** (`analyseur_exceptions.py`)

| Exception                   | Code   | Description                         |
| --------------------------- | ------ | ----------------------------------- |
| `AnalyseurException`        | -      | Classe de base pour erreurs analyse |
| `DivisionParZeroException`  | ANA001 | Division par zéro dans les calculs  |
| `DonneesMaquantesException` | ANA002 | Données manquantes pour l'analyse   |
| `RouteVideException`        | ANA003 | Calcul sur route sans véhicule      |

## 💡 Utilisation

### Import des exceptions

```python
# Import individuel
from exceptions import VitesseNegativeException, RoutePleineException

# Import de toutes les exceptions
from exceptions import *

# Import par catégorie
from exceptions.vehicule_exceptions import VitesseNegativeException
from exceptions.route_exceptions import RoutePleineException
```

### Exemple 1: Validation dans Vehicule

```python
from exceptions import VitesseNegativeException, PositionInvalideException

class Vehicule:
    def __init__(self, identifiant, route, position=0.0, vitesse=0.0):
        # Validation de la vitesse
        if vitesse < 0:
            raise VitesseNegativeException(vitesse, str(identifiant))

        # Validation de la position
        if position < 0:
            raise PositionInvalideException(position, vehicule_id=str(identifiant))

        self.id = identifiant
        self.vitesse = vitesse
        self.position = position
```

### Exemple 2: Gestion dans Route

```python
from exceptions import RoutePleineException, VehiculeDejaPresent

class Route:
    def ajouter_vehicule(self, vehicule):
        # Vérifier capacité
        if len(self.vehicules) >= self.capacite_max:
            raise RoutePleineException(self.nom, self.capacite_max)

        # Vérifier doublon
        if vehicule.id in [v.id for v in self.vehicules]:
            raise VehiculeDejaPresent(str(vehicule.id), self.nom)

        self.vehicules.append(vehicule)
```

### Exemple 3: Try/Except dans le code appelant

```python
from exceptions import (
    SimulateurException,
    VitesseNegativeException,
    FichierConfigurationException
)

try:
    # Charger la configuration
    sim = Simulateur("data/config_reseau.json")

    # Lancer la simulation
    sim.lancer_simulation(n_tours=100, delta_t=1.0)

except FichierConfigurationException as e:
    print(f"❌ Erreur de configuration: {e}")
    print(f"   Code d'erreur: {e.code}")

except VitesseNegativeException as e:
    print(f"❌ Erreur de vitesse: {e}")
    print(f"   Véhicule: {e.vehicule_id}, Vitesse: {e.vitesse}")

except SimulateurException as e:
    # Capturer toutes les exceptions du simulateur
    print(f"❌ Erreur du simulateur [{e.code}]: {e}")

except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
```

## 🔍 Codes d'Erreur

Les exceptions incluent un code d'erreur pour faciliter le débogage :

- **VEH0xx** : Erreurs véhicule
- **RTE0xx** : Erreurs route/réseau
- **SIM0xx** : Erreurs simulateur
- **ANA0xx** : Erreurs analyseur

## 🎨 Attributs Personnalisés

Chaque exception fournit des attributs spécifiques pour faciliter le traitement :

```python
try:
    vehicule = Vehicule("V1", route, position=-10, vitesse=50)
except PositionInvalideException as e:
    print(f"Position invalide: {e.position}")
    print(f"Position max: {e.position_max}")
    print(f"Véhicule: {e.vehicule_id}")
    print(f"Message: {e.message}")
    print(f"Code: {e.code}")
```

## 🧪 Tests des Exceptions

Les tests unitaires doivent vérifier que les exceptions sont levées correctement :

```python
import pytest
from exceptions import VitesseNegativeException
from models import Vehicule, Route

def test_vitesse_negative_leve_exception():
    route = Route("R1", longueur=1000, limite_vitesse=50)

    with pytest.raises(VitesseNegativeException) as exc_info:
        vehicule = Vehicule("V1", route, position=0, vitesse=-10)

    assert exc_info.value.vitesse == -10
    assert exc_info.value.code == "VEH001"
```

## 📊 Hiérarchie des Exceptions

```
Exception (Python built-in)
    └── SimulateurException (base)
        ├── VehiculeException
        │   ├── VitesseNegativeException
        │   └── PositionInvalideException
        ├── RouteException
        │   ├── RoutePleineException
        │   ├── VehiculeDejaPresent
        │   ├── RouteInexistanteException
        │   └── LongueurRouteInvalideException
        ├── ConfigurationException
        │   ├── FichierConfigurationException
        │   └── IterationsInvalidesException
        └── AnalyseurException
            ├── DivisionParZeroException
            ├── DonneesMaquantesException
            └── RouteVideException
```

## ✅ Bonnes Pratiques

1. **Lever des exceptions spécifiques** plutôt que génériques
2. **Inclure du contexte** (IDs, valeurs, limites) dans les exceptions
3. **Capturer et re-lever** les exceptions avec `raise ... from e` pour préserver la trace
4. **Documenter** les exceptions dans les docstrings avec `Raises:`
5. **Logger** les erreurs avant de les lever si nécessaire
6. **Utiliser try/except** aux bons endroits (frontières de l'application)

## 🔗 Intégration

Ces exceptions sont intégrées dans :

- ✅ `models/vehicule.py` - Validation vitesse/position
- ✅ `models/route.py` - Validation capacité/doublons
- ✅ `models/reseau.py` - Validation existence routes
- ✅ `core/simulateur.py` - Validation configuration/itérations
- ✅ `core/analyseur.py` - Validation données/calculs

---

## 📚 **Génération de Documentation (Sphinx)**

1. Installer Sphinx :

```powershell
python -m pip install -U sphinx sphinx-rtd-theme
```

2. Construire la doc :

```powershell
python -m sphinx -b html docs docs/_build/html
```

Si la construction échoue car Sphinx ne peut pas importer des modules, vérifiez que vous exécutez la commande depuis la racine du projet et que toutes les dépendances d'import sont installées.

## 📦 **Installation du package (préparation PyPI/TestPyPI)**

Le projet est maintenant préparé pour être distribué sur PyPI/TestPyPI. Vous trouverez les fichiers de packaging (`pyproject.toml`, `setup.cfg`, `setup.py`, `MANIFEST.in`) à la racine du dépôt.

Pour construire et tester l'installation localement (recommandé via TestPyPI) :

```powershell
# Installer les outils de build et twine
python -m pip install --upgrade build twine

# Construire les distributions
python -m build

# (Optionnel) Publier sur TestPyPI pour tester
python -m twine upload --repository testpypi dist/*

# Installer depuis TestPyPI pour vérifier
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps simulateur-trafic==0.1.0
```

Consultez `PUBLISH.md` pour des instructions détaillées et un exemple de `.pypirc`.

---

**Auteur :** Moatez Tilouche
