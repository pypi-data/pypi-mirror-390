"""
Simulateur de Trafic Routier

Un simulateur de trafic routier avec gestion d'exceptions complète,
tests unitaires et documentation Sphinx.

Auteur: Moatez Tilouche
"""

__version__ = "1.0.0"
__author__ = "Moatez Tilouche"
__email__ = "moateztilouch@gmail.com"

# Import des classes principales pour faciliter l'utilisation
from .core.simulateur import Simulateur
from .core.analyseur import Analyseur
from .models.vehicule import Vehicule
from .models.route import Route
from .models.reseau import ReseauRoutier

__all__ = [
    "Simulateur",
    "Analyseur", 
    "Vehicule",
    "Route",
    "ReseauRoutier",
]