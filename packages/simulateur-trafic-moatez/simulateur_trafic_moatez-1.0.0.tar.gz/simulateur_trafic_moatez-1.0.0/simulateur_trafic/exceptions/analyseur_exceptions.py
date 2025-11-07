"""
Module d'exceptions liées à l'analyseur.

Contient toutes les exceptions spécifiques aux opérations
d'analyse statistique.
"""

from .base_exceptions import SimulateurException


class AnalyseurException(SimulateurException):
    """
    Exception de base pour toutes les erreurs liées à l'analyseur.
    """
    pass


class DivisionParZeroException(AnalyseurException):
    """
    Exception levée lors d'une tentative de division par zéro dans les calculs.
    
    Attributes:
        operation (str): Description de l'opération qui a causé l'erreur.
    """
    
    def __init__(self, operation: str = None):
        """
        Initialise l'exception pour une division par zéro.
        
        Args:
            operation (str, optional): Description de l'opération en cours.
        """
        self.operation = operation
        
        if operation:
            message = f"Division par zéro détectée lors de l'opération: {operation}"
        else:
            message = "Division par zéro détectée dans les calculs statistiques"
        
        super().__init__(message, code="ANA001")


class DonneesMaquantesException(AnalyseurException):
    """
    Exception levée lorsque des données nécessaires sont manquantes pour l'analyse.
    
    Attributes:
        donnees_manquantes (str): Description des données manquantes.
    """
    
    def __init__(self, donnees_manquantes: str):
        """
        Initialise l'exception pour des données manquantes.
        
        Args:
            donnees_manquantes (str): Description des données manquantes.
        """
        self.donnees_manquantes = donnees_manquantes
        
        message = f"Données manquantes pour l'analyse: {donnees_manquantes}"
        
        super().__init__(message, code="ANA002")


class RouteVideException(AnalyseurException):
    """
    Exception levée lors d'une tentative de calcul sur une route vide.
    
    Certains calculs (comme la vitesse moyenne) nécessitent au moins un véhicule.
    
    Attributes:
        route_id (str): Identifiant de la route vide.
        operation (str): Opération tentée sur la route vide.
    """
    
    def __init__(self, route_id: str = None, operation: str = None):
        """
        Initialise l'exception pour une route vide.
        
        Args:
            route_id (str, optional): Identifiant de la route.
            operation (str, optional): Opération tentée.
        """
        self.route_id = route_id
        self.operation = operation
        
        if route_id and operation:
            message = (f"Impossible d'effectuer l'opération '{operation}' "
                      f"sur la route '{route_id}': aucun véhicule présent")
        elif route_id:
            message = f"La route '{route_id}' ne contient aucun véhicule"
        else:
            message = "Impossible de calculer des statistiques: aucun véhicule présent"
        
        super().__init__(message, code="ANA003")
