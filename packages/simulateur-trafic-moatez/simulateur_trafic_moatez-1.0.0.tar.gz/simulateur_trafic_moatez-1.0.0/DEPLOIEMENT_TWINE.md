# 🚀 DÉPLOIEMENT PRATIQUE AVEC TWINE

## 📋 Prérequis

✅ Package construit et vérifié :

```powershell
python -m twine check dist/*
# PASSED pour simulateur_trafic-1.0.0-py3-none-any.whl
# PASSED pour simulateur_trafic-1.0.0.tar.gz
```

## 🧪 ÉTAPE 1: Déploiement TestPyPI

### 1. Créer compte TestPyPI

1. Aller sur https://test.pypi.org/account/register/
2. Créer compte et vérifier email
3. Aller dans Account Settings → API tokens
4. Generate token avec scope "Entire account"
5. **COPIER LE TOKEN** (commence par `pypi-`)

### 2. Upload vers TestPyPI

**Méthode recommandée avec token :**

```powershell
twine upload --repository-url https://test.pypi.org/legacy/ dist/* -u __token__ -p your-token-here
```

**Méthode interactive :**

```powershell
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# Username: __token__
# Password: [votre-token-ici]
```

### 3. Vérifier sur TestPyPI

- Page package : https://test.pypi.org/project/simulateur-trafic/
- Vérifier métadonnées, description, fichiers

### 4. Test installation depuis TestPyPI

```powershell
# Nouvelle session PowerShell
pip install --index-url https://test.pypi.org/simple/ simulateur-trafic

# Tester
simulateur-trafic
python -c "import simulateur_trafic; print(simulateur_trafic.__version__)"
```

## 🌟 ÉTAPE 2: Déploiement PyPI Production

### 1. Créer compte PyPI

1. Aller sur https://pypi.org/account/register/
2. Créer compte et vérifier email
3. Générer token API (scope "Entire account")

### 2. Vérifier nom unique

- Chercher "simulateur-trafic" sur https://pypi.org
- Si existe, changer nom dans setup.py

### 3. Upload vers PyPI

**Commande de production :**

```powershell
twine upload dist/* -u __token__ -p your-pypi-token
```

**Ou avec URL explicite :**

```powershell
twine upload --repository-url https://upload.pypi.org/legacy/ dist/* -u __token__ -p your-pypi-token
```

### 4. Vérification finale

```powershell
# Installation normale
pip install simulateur-trafic

# Test complet
simulateur-trafic
python -m simulateur_trafic
python -c "from simulateur_trafic import Simulateur; print('✅ Package déployé !')"
```

## 🔐 Authentification Sécurisée

### Configuration ~/.pypirc (optionnel)

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-token-for-testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-token-for-production
```

Puis simplement :

```powershell
twine upload --repository testpypi dist/*
twine upload --repository pypi dist/*
```

## ⚡ Commandes Rapides

### TestPyPI

```powershell
# Upload
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ simulateur-trafic
```

### PyPI Production

```powershell
# Upload
twine upload dist/*

# Install normal
pip install simulateur-trafic
```

## 🔍 Vérifications Post-Déploiement

### Page PyPI

- https://pypi.org/project/simulateur-trafic/
- Métadonnées correctes
- README affiché
- Fichiers disponibles (.whl + .tar.gz)

### Installation utilisateur

```powershell
pip install simulateur-trafic
simulateur-trafic --help  # Si help implémenté
simulateur-trafic         # Exécution normale
```

### Import développeur

```python
from simulateur_trafic import Simulateur, Vehicule, Route, ReseauRoutier
from simulateur_trafic.core import Analyseur

sim = Simulateur()
print(f"Version: {simulateur_trafic.__version__}")
```

## 🎯 Résultat Final

Après déploiement réussi :

1. **Page PyPI** : https://pypi.org/project/simulateur-trafic/
2. **Installation** : `pip install simulateur-trafic`
3. **Usage** : `simulateur-trafic` ou `python -m simulateur_trafic`
4. **Import** : `from simulateur_trafic import Simulateur`

---

**🎉 PACKAGE PUBLIÉ ! Votre simulateur est maintenant disponible pour toute la communauté Python !**
