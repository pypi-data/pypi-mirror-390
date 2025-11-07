"""
Module d'exceptions personnalisées pour le simulateur de trafic.

Ce module définit toutes les exceptions personnalisées utilisées dans le projet
pour gérer les erreurs spécifiques au domaine du simulateur de trafic routier.
"""

from .base_exceptions import SimulateurException
from .vehicule_exceptions import (
    VehiculeException,
    VitesseNegativeException,
    PositionInvalideException
)
from .route_exceptions import (
    RouteException,
    RoutePleineException,
    VehiculeDejaPresent,
    RouteInexistanteException,
    LongueurRouteInvalideException
)
from .simulateur_exceptions import (
    ConfigurationException,
    FichierConfigurationException,
    IterationsInvalidesException
)
from .analyseur_exceptions import (
    AnalyseurException,
    DivisionParZeroException,
    DonneesMaquantesException,
    RouteVideException
)

__all__ = [
    # Base
    'SimulateurException',
    
    # Véhicule
    'VehiculeException',
    'VitesseNegativeException',
    'PositionInvalideException',
    
    # Route
    'RouteException',
    'RoutePleineException',
    'VehiculeDejaPresent',
    'RouteInexistanteException',
    'LongueurRouteInvalideException',
    
    # Simulateur
    'ConfigurationException',
    'FichierConfigurationException',
    'IterationsInvalidesException',
    
    # Analyseur
    'AnalyseurException',
    'DivisionParZeroException',
    'DonneesMaquantesException',
    'RouteVideException',
]
