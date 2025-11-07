"""
Module d'exceptions liées aux véhicules.

Contient toutes les exceptions spécifiques aux opérations
sur les objets Vehicule.
"""

from .base_exceptions import SimulateurException


class VehiculeException(SimulateurException):
    """
    Exception de base pour toutes les erreurs liées aux véhicules.
    """
    pass


class VitesseNegativeException(VehiculeException):
    """
    Exception levée lorsqu'une vitesse négative est détectée.
    
    La vitesse d'un véhicule ne peut pas être négative dans le simulateur.
    
    Attributes:
        vitesse (float): La vitesse invalide qui a causé l'exception.
        vehicule_id (str): Identifiant du véhicule concerné.
    """
    
    def __init__(self, vitesse: float, vehicule_id: str = None):
        """
        Initialise l'exception pour une vitesse négative.
        
        Args:
            vitesse (float): La vitesse négative détectée.
            vehicule_id (str, optional): Identifiant du véhicule.
        """
        self.vitesse = vitesse
        self.vehicule_id = vehicule_id
        
        if vehicule_id:
            message = f"Vitesse négative détectée pour le véhicule '{vehicule_id}': {vitesse} m/s"
        else:
            message = f"Vitesse négative détectée: {vitesse} m/s. La vitesse doit être >= 0"
        
        super().__init__(message, code="VEH001")


class PositionInvalideException(VehiculeException):
    """
    Exception levée lorsqu'une position invalide est détectée.
    
    La position d'un véhicule doit être comprise entre 0 et la longueur de la route.
    
    Attributes:
        position (float): La position invalide.
        position_max (float): Position maximale autorisée.
        vehicule_id (str): Identifiant du véhicule concerné.
    """
    
    def __init__(self, position: float, position_max: float = None, vehicule_id: str = None):
        """
        Initialise l'exception pour une position invalide.
        
        Args:
            position (float): La position invalide détectée.
            position_max (float, optional): Position maximale autorisée.
            vehicule_id (str, optional): Identifiant du véhicule.
        """
        self.position = position
        self.position_max = position_max
        self.vehicule_id = vehicule_id
        
        if vehicule_id and position_max is not None:
            message = (f"Position invalide pour le véhicule '{vehicule_id}': {position} m. "
                      f"La position doit être entre 0 et {position_max} m")
        elif position_max is not None:
            message = f"Position invalide: {position} m. Doit être entre 0 et {position_max} m"
        else:
            message = f"Position invalide: {position} m. La position doit être >= 0"
        
        super().__init__(message, code="VEH002")
