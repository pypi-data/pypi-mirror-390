# 📦 Guide de Déploiement PyPI avec setuptools

Ce guide explique comment déployer le package `simulateur-trafic` sur TestPyPI puis PyPI en utilisant setuptools.

## 🏗️ Structure du Package

Le projet a été restructuré pour le déploiement PyPI :

```
simulateur_trafic/
├── setup.py                    # Configuration setuptools principale
├── setup.cfg                   # Configuration setuptools (format INI)
├── pyproject.toml              # Configuration build system
├── MANIFEST.in                 # Fichiers à inclure dans la distribution
├── LICENSE                     # Licence MIT
├── README.md                   # Documentation principale
├── requirements.txt            # Dépendances (vide dans ce cas)
├── simulateur_trafic/          # Package Python principal
│   ├── __init__.py            # Point d'entrée avec imports
│   ├── __main__.py            # Support pour python -m simulateur_trafic
│   ├── main.py                # Fonction main() pour console script
│   ├── core/                  # Modules core
│   ├── models/                # Modules models
│   ├── exceptions/            # Modules exceptions
│   ├── io_pkg/                # Modules io_pkg
│   └── data/                  # Fichiers de données
├── dist/                      # Distributions générées
├── build/                     # Fichiers de build temporaires
└── simulateur_trafic.egg-info/  # Métadonnées egg
```

## 🔧 Configuration setuptools

### setup.py

Configuration principale avec tous les métadonnées, dépendances, et points d'entrée.

### setup.cfg

Configuration format INI pour setuptools (alternative déclarative).

### pyproject.toml

Spécifie le système de build (setuptools) et les requirements.

## 📦 Construire le Package

### Méthode 1: setuptools classique

```powershell
# Créer source distribution et wheel
python setup.py sdist bdist_wheel

# Vérifier la version
python setup.py --version

# Informations sur le package
python setup.py --name --version --author
```

### Méthode 2: build moderne (optionnel)

```powershell
# Installer build
pip install build

# Construire avec build
python -m build
```

## 📋 Contenu des Distributions

**Source Distribution (tar.gz)** :

- Code source complet
- setup.py, setup.cfg, pyproject.toml
- README.md, LICENSE, MANIFEST.in
- Tous les modules Python

**Wheel (.whl)** :

- Package compilé prêt à installer
- Plus rapide à installer
- Compatible toutes plateformes (pure Python)

## 🧪 Test en Local

### Installation en mode développement

```powershell
# Installation éditable (liens vers le code source)
pip install -e .

# Avec dépendances de développement
pip install -e .[dev]
```

### Installation depuis wheel

```powershell
# Installer directement le wheel généré
pip install dist/simulateur_trafic-1.0.0-py3-none-any.whl
```

### Test du script console

```powershell
# Après installation, tester la commande
simulateur-trafic

# Ou via module
python -m simulateur_trafic
```

### Test d'import

```python
# Test des imports dans Python
import simulateur_trafic
from simulateur_trafic import Simulateur, Vehicule, Route

# Vérifier version
print(simulateur_trafic.__version__)
```

## 🚀 Déploiement sur TestPyPI

### 1. Préparer les outils

```powershell
# Installer twine pour upload
pip install twine

# Vérifier les distributions
twine check dist/*
```

### 2. Créer compte TestPyPI

- Aller sur https://test.pypi.org
- Créer un compte
- Vérifier l'email

### 3. Configurer credentials

Créer `~/.pypirc` :

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-token-here

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-token-here
```

### 4. Upload vers TestPyPI

```powershell
# Upload
twine upload --repository testpypi dist/*

# Ou sans ~/.pypirc
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

### 5. Test installation depuis TestPyPI

```powershell
# Installer depuis TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps simulateur-trafic

# Tester
simulateur-trafic
python -c "import simulateur_trafic; print(simulateur_trafic.__version__)"
```

## 🌟 Déploiement sur PyPI

### 1. Vérifications finales

```powershell
# Tests complets
python -m pytest

# Vérification métadonnées
python setup.py check --metadata --strict

# Vérification distributions
twine check dist/*
```

### 2. Upload vers PyPI

```powershell
# Upload vers PyPI officiel
twine upload dist/*
```

### 3. Installation publique

```powershell
# Installation normale
pip install simulateur-trafic

# Test
simulateur-trafic
```

## 🔍 Vérifications Avant Publication

### Checklist

- [ ] Tests passent tous (pytest)
- [ ] README.md bien formaté
- [ ] LICENSE inclus
- [ ] Version correcte dans **init**.py
- [ ] setup.py/setup.cfg complets
- [ ] MANIFEST.in inclut tous fichiers nécessaires
- [ ] Nom package unique sur PyPI
- [ ] Wheel construit sans erreur
- [ ] Installation locale fonctionne
- [ ] Console script fonctionne
- [ ] Imports fonctionnent

### Commandes de vérification

```powershell
# Structure package
python setup.py --name --version --description

# Contenu wheel
python -c "import zipfile; print(zipfile.ZipFile('dist/simulateur_trafic-1.0.0-py3-none-any.whl').namelist())"

# Test installation propre
pip uninstall simulateur-trafic
pip install dist/simulateur_trafic-1.0.0-py3-none-any.whl
simulateur-trafic
```

## 📊 Métadonnées Package

- **Nom**: simulateur-trafic
- **Version**: 1.0.0
- **Auteur**: Moatez Tilouche
- **Licence**: MIT
- **Python**: >=3.8
- **Type**: Pure Python
- **Console Script**: simulateur-trafic

## ⚠️ Notes Importantes

1. **Nom unique** : Vérifier que `simulateur-trafic` n'existe pas sur PyPI
2. **Version** : Incrémenter pour chaque release
3. **TestPyPI** : Toujours tester avant PyPI
4. **Sécurité** : Utiliser tokens API, pas mots de passe
5. **Documentation** : README visible sur PyPI

## 🎯 Prochaines Étapes

1. Tester installation locale
2. Upload vers TestPyPI
3. Vérifier page TestPyPI
4. Test installation depuis TestPyPI
5. Si OK, upload vers PyPI
6. Promouvoir le package !

---

**Auteur**: Moatez Tilouche  
**Package**: simulateur-trafic v1.0.0
