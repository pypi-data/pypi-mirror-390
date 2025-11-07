from exceptions import RouteInexistanteException


class ReseauRoutier:
    """Représente l'ensemble des routes composant le réseau.

    Fournit des méthodes pour ajouter des routes, récupérer une route par nom
    et obtenir un état synthétique du réseau.
    """

    def __init__(self):
        """Initialise un réseau vide (sans routes)."""
        self.routes = {}

    def ajouter_route(self, route):
        """Ajoute une instance `Route` au réseau.

        Args:
            route (Route): instance à ajouter.
        """
        self.routes[route.nom] = route

    def get_route(self, nom):
        """Retourne la route nommée `nom` ou lève une exception si elle n'existe pas.
        
        Args:
            nom (str): Nom de la route recherchée.
            
        Returns:
            Route: La route correspondante.
            
        Raises:
            RouteInexistanteException: Si la route n'existe pas dans le réseau.
        """
        route = self.routes.get(nom)
        if route is None:
            routes_disponibles = list(self.routes.keys())
            raise RouteInexistanteException(nom, routes_disponibles)
        return route

    def etat_reseau(self):
        """Retourne un dictionnaire résumant la position des véhicules par route.

        Format:
            { nom_route: [(vehicule_id, position_approchee), ...], ... }
        """
        etat = {}
        for nom, route in self.routes.items():
            etat[nom] = [(v.id, round(v.position, 2)) for v in route.vehicules]
        return etat
