"""
Module d'exceptions liées aux routes.

Contient toutes les exceptions spécifiques aux opérations
sur les objets Route et ReseauRoutier.
"""

from .base_exceptions import SimulateurException


class RouteException(SimulateurException):
    """
    Exception de base pour toutes les erreurs liées aux routes.
    """
    pass


class RoutePleineException(RouteException):
    """
    Exception levée lorsqu'on tente d'ajouter un véhicule sur une route pleine.
    
    Attributes:
        route_id (str): Identifiant de la route.
        capacite_max (int): Capacité maximale de la route.
    """
    
    def __init__(self, route_id: str, capacite_max: int = None):
        """
        Initialise l'exception pour une route pleine.
        
        Args:
            route_id (str): Identifiant de la route pleine.
            capacite_max (int, optional): Capacité maximale de la route.
        """
        self.route_id = route_id
        self.capacite_max = capacite_max
        
        if capacite_max:
            message = (f"La route '{route_id}' est pleine. "
                      f"Capacité maximale atteinte: {capacite_max} véhicules")
        else:
            message = f"La route '{route_id}' est pleine. Impossible d'ajouter un véhicule"
        
        super().__init__(message, code="RTE001")


class VehiculeDejaPresent(RouteException):
    """
    Exception levée lorsqu'on tente d'ajouter un véhicule déjà présent sur la route.
    
    Attributes:
        vehicule_id (str): Identifiant du véhicule.
        route_id (str): Identifiant de la route.
    """
    
    def __init__(self, vehicule_id: str, route_id: str):
        """
        Initialise l'exception pour un véhicule déjà présent.
        
        Args:
            vehicule_id (str): Identifiant du véhicule.
            route_id (str): Identifiant de la route.
        """
        self.vehicule_id = vehicule_id
        self.route_id = route_id
        
        message = (f"Le véhicule '{vehicule_id}' est déjà présent sur la route '{route_id}'. "
                  f"Impossible de l'ajouter deux fois")
        
        super().__init__(message, code="RTE002")


class RouteInexistanteException(RouteException):
    """
    Exception levée lorsqu'on tente d'accéder à une route qui n'existe pas.
    
    Attributes:
        route_id (str): Identifiant de la route inexistante.
    """
    
    def __init__(self, route_id: str, routes_disponibles: list = None):
        """
        Initialise l'exception pour une route inexistante.
        
        Args:
            route_id (str): Identifiant de la route inexistante.
            routes_disponibles (list, optional): Liste des routes disponibles.
        """
        self.route_id = route_id
        self.routes_disponibles = routes_disponibles
        
        if routes_disponibles:
            routes_str = ", ".join(routes_disponibles)
            message = (f"La route '{route_id}' n'existe pas dans le réseau. "
                      f"Routes disponibles: {routes_str}")
        else:
            message = f"La route '{route_id}' n'existe pas dans le réseau routier"
        
        super().__init__(message, code="RTE003")


class LongueurRouteInvalideException(RouteException):
    """
    Exception levée lorsqu'une longueur de route invalide est détectée.
    
    La longueur d'une route doit être strictement positive.
    
    Attributes:
        longueur (float): La longueur invalide.
        route_id (str): Identifiant de la route.
    """
    
    def __init__(self, longueur: float, route_id: str = None):
        """
        Initialise l'exception pour une longueur invalide.
        
        Args:
            longueur (float): La longueur invalide.
            route_id (str, optional): Identifiant de la route.
        """
        self.longueur = longueur
        self.route_id = route_id
        
        if route_id:
            message = (f"Longueur invalide pour la route '{route_id}': {longueur} m. "
                      f"La longueur doit être > 0")
        else:
            message = f"Longueur de route invalide: {longueur} m. Doit être > 0"
        
        super().__init__(message, code="RTE004")
