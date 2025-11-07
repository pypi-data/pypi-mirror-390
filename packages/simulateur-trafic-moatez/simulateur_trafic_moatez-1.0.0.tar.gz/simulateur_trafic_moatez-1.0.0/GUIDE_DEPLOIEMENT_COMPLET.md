# 🚀 GUIDE COMPLET DE DÉPLOIEMENT PYPI
# Auteur: Moatez Tilouche
# Package: simulateur-trafic

## ❌ PROBLÈME IDENTIFIÉ

**Erreur rencontrée:**
```
HTTPError: 403 Forbidden from https://upload.pypi.org/legacy/
The user 'MoatezTilouche' isn't allowed to upload to project 'simulateur-trafic'.
```

**Cause:** Le nom `simulateur-trafic` existe déjà sur PyPI et appartient à quelqu'un d'autre.

## ✅ SOLUTIONS DISPONIBLES

### SOLUTION 1: Changer le nom du package (RECOMMANDÉ)

#### 1.1 Modifier setup.py
```python
name="simulateur-trafic-moatez",  # Nom unique
# ou
name="simulateur-trafic-tilouche", 
# ou  
name="traffic-simulator-mt",
```

#### 1.2 Rebuild le package
```powershell
# Nettoyer les anciens builds
Remove-Item -Recurse -Force dist, build, *.egg-info

# Rebuild avec nouveau nom
python setup.py sdist bdist_wheel

# Vérifier
python -m twine check dist/*
```

#### 1.3 Upload
```powershell
python -m twine upload dist/* --config-file .pypirc
```

### SOLUTION 2: Utiliser TestPyPI avec token TestPyPI

#### 2.1 Créer token TestPyPI
1. Aller sur: https://test.pypi.org
2. Account Settings → API tokens → Add API token
3. Copier le token TestPyPI

#### 2.2 Mettre à jour .pypirc
```ini
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = votre-token-testpypi-ici

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJGM1M2VkMjZiLTE3MzktNGYzNi04ZDgxLTgzZDk5NzUzM2YxYgACKlszLCJjMzNiNzAyYS0wYjgxLTQxNTgtODQ5OC03NjIwYTVmODc2YTEiXQAABiBVfk6yOB0ZAL86zypoUKrK5WvuSxlabsjfO-zY2RlfKw
```

#### 2.3 Upload vers TestPyPI
```powershell
python -m twine upload --repository testpypi dist/* --config-file .pypirc
```

## 🎯 SOLUTION RECOMMANDÉE: Nouveau nom

### Étape 1: Choisir un nom unique
```
simulateur-trafic-moatez
simulateur-trafic-tilouche  
traffic-simulator-mt
simulateur-routier-mt
```

### Étape 2: Script de déploiement complet

```powershell
# ===== SCRIPT DE DÉPLOIEMENT COMPLET =====

# 1. Nettoyer les anciens builds
Write-Host "🧹 Nettoyage des anciens builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force dist }
if (Test-Path "build") { Remove-Item -Recurse -Force build }
if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force *.egg-info }

# 2. Modifier le nom dans setup.py (à faire manuellement)
Write-Host "✏️  Modifiez le nom dans setup.py en : simulateur-trafic-moatez" -ForegroundColor Cyan
Read-Host "Appuyez sur Entrée quand c'est fait..."

# 3. Rebuild le package
Write-Host "📦 Construction du package..." -ForegroundColor Green
python setup.py sdist bdist_wheel

# 4. Vérifier la validité
Write-Host "🔍 Vérification..." -ForegroundColor Blue
python -m twine check dist/*

# 5. Upload vers PyPI
Write-Host "🚀 Upload vers PyPI..." -ForegroundColor Magenta
python -m twine upload dist/* --config-file .pypirc

# 6. Vérification finale
Write-Host "✅ Test d'installation..." -ForegroundColor Green
pip install simulateur-trafic-moatez

Write-Host "🎉 DÉPLOIEMENT TERMINÉ !" -ForegroundColor Green
```

### Étape 3: Commandes manuelles une par une

```powershell
# 1. Nettoyer
Remove-Item -Recurse -Force dist, build, simulateur_trafic.egg-info -ErrorAction SilentlyContinue

# 2. Modifier setup.py (voir section suivante)

# 3. Rebuild
python setup.py sdist bdist_wheel

# 4. Vérifier
python -m twine check dist/*

# 5. Upload
python -m twine upload dist/* --config-file .pypirc

# 6. Installer et tester
pip install simulateur-trafic-moatez
simulateur-trafic-moatez
```

## 📝 MODIFICATION SETUP.PY REQUISE

Modifier dans setup.py ligne ~20:
```python
# AVANT
name="simulateur-trafic",

# APRÈS
name="simulateur-trafic-moatez",
```

Et optionnellement dans setup.cfg:
```ini
# AVANT
name = simulateur-trafic

# APRÈS  
name = simulateur-trafic-moatez
```

## 🔧 FICHIER .pypirc COMPLET

```ini
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = votre-token-testpypi-si-vous-en-avez-un

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJGM1M2VkMjZiLTE3MzktNGYzNi04ZDgxLTgzZDk5NzUzM2YxYgACKlszLCJjMzNiNzAyYS0wYjgxLTQxNTgtODQ5OC03NjIwYTVmODc2YTEiXQAABiBVfk6yOB0ZAL86zypoUKrK5WvuSxlabsjfO-zY2RlfKw
```

## 🎉 RÉSULTAT ATTENDU

Après déploiement réussi:

### Installation utilisateur:
```bash
pip install simulateur-trafic-moatez
```

### Usage:
```bash
# Console script (à configurer dans setup.py)
simulateur-trafic-moatez

# Ou module
python -c "import simulateur_trafic; print('✅ Package installé!')"
```

### Page PyPI:
```
https://pypi.org/project/simulateur-trafic-moatez/
```

## ⚠️ CHECKLIST AVANT DÉPLOIEMENT

- [ ] Nom du package unique vérifié
- [ ] setup.py modifié avec nouveau nom
- [ ] Token PyPI valide dans .pypirc
- [ ] Tests locaux passent
- [ ] Package rebuild avec nouveau nom
- [ ] twine check PASSED

## 🚀 COMMANDE FINALE

```powershell
python -m twine upload dist/* --config-file .pypirc --verbose
```

---

**💡 TIP:** Commencez par changer le nom dans setup.py en "simulateur-trafic-moatez" puis relancez le build !

**🎯 PROCHAINE ÉTAPE:** Modifier setup.py et relancer le déploiement !