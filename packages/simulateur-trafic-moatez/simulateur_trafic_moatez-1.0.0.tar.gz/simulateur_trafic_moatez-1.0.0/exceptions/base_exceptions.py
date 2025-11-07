"""
Module contenant l'exception de base pour le simulateur de trafic.

Toutes les exceptions personnalisées du projet héritent de cette classe.
"""


class SimulateurException(Exception):
    """
    Exception de base pour toutes les exceptions du simulateur de trafic.
    
    Cette classe sert de parent à toutes les exceptions personnalisées
    du projet, permettant de capturer toutes les erreurs du simulateur
    avec un seul type d'exception si nécessaire.
    
    Attributes:
        message (str): Message décrivant l'erreur.
        code (str): Code d'erreur optionnel pour identifier le type d'erreur.
    """
    
    def __init__(self, message: str, code: str = None):
        """
        Initialise l'exception avec un message et un code optionnel.
        
        Args:
            message (str): Message décrivant l'erreur.
            code (str, optional): Code d'erreur pour identifier le type d'erreur.
        """
        self.message = message
        self.code = code
        super().__init__(self.message)
    
    def __str__(self):
        """Retourne une représentation textuelle de l'exception."""
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message
