"""
Module d'exceptions liées au simulateur.

Contient toutes les exceptions spécifiques aux opérations
du Simulateur principal.
"""

from .base_exceptions import SimulateurException


class ConfigurationException(SimulateurException):
    """
    Exception de base pour toutes les erreurs de configuration.
    """
    pass


class FichierConfigurationException(ConfigurationException):
    """
    Exception levée lorsqu'un problème survient avec le fichier de configuration.
    
    Cela peut être dû à un fichier manquant, un format JSON invalide,
    ou des données manquantes dans la configuration.
    
    Attributes:
        fichier (str): Chemin du fichier de configuration.
        raison (str): Raison de l'erreur.
    """
    
    def __init__(self, fichier: str, raison: str = None):
        """
        Initialise l'exception pour un problème de fichier de configuration.
        
        Args:
            fichier (str): Chemin du fichier de configuration.
            raison (str, optional): Raison détaillée de l'erreur.
        """
        self.fichier = fichier
        self.raison = raison
        
        if raison:
            message = f"Erreur avec le fichier de configuration '{fichier}': {raison}"
        else:
            message = f"Impossible de charger le fichier de configuration '{fichier}'"
        
        super().__init__(message, code="SIM001")


class IterationsInvalidesException(ConfigurationException):
    """
    Exception levée lorsque le nombre d'itérations de simulation est invalide.
    
    Le nombre d'itérations doit être un entier strictement positif.
    
    Attributes:
        iterations (int): Le nombre d'itérations invalide.
    """
    
    def __init__(self, iterations):
        """
        Initialise l'exception pour un nombre d'itérations invalide.
        
        Args:
            iterations: Le nombre d'itérations invalide (peut être de n'importe quel type).
        """
        self.iterations = iterations
        
        if not isinstance(iterations, (int, float)):
            message = (f"Nombre d'itérations invalide: '{iterations}' (type: {type(iterations).__name__}). "
                      f"Doit être un entier positif")
        elif iterations <= 0:
            message = (f"Nombre d'itérations invalide: {iterations}. "
                      f"Doit être un entier strictement positif (> 0)")
        else:
            message = f"Nombre d'itérations invalide: {iterations}"
        
        super().__init__(message, code="SIM002")
