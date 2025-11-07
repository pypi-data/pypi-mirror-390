from exceptions import VitesseNegativeException, PositionInvalideException


class Vehicule:
    """Représente un véhicule dans la simulation.

    Attributs:
        id (str): identifiant unique du véhicule
        route (Route): route sur laquelle il circule
        position (float): position actuelle en mètres
        vitesse (float): vitesse actuelle en mètres/seconde
    """

    def __init__(self, identifiant, route, position=0.0, vitesse=0.0):
        """Initialise un véhicule.

        Args:
            identifiant: identifiant unique (str ou int).
            route: instance de `Route` où le véhicule est placé.
            position (float): position initiale (m).
            vitesse (float): vitesse initiale (m/s).
            
        Raises:
            VitesseNegativeException: Si la vitesse est négative.
            PositionInvalideException: Si la position est négative ou dépasse la longueur de la route.
        """
        # Validation de la vitesse
        if vitesse < 0:
            raise VitesseNegativeException(vitesse, str(identifiant))
        
        # Validation de la position
        if position < 0:
            raise PositionInvalideException(position, vehicule_id=str(identifiant))
        
        if route and position > route.longueur:
            raise PositionInvalideException(position, route.longueur, str(identifiant))
        
        self.id = identifiant
        self.route = route
        self.position = position
        self.vitesse = vitesse

    def avancer(self, delta_t):
        """Fait avancer le véhicule en fonction de sa vitesse pendant `delta_t`.

        La position est bornée par la longueur de la route.
        
        Args:
            delta_t (float): Intervalle de temps en secondes.
            
        Raises:
            VitesseNegativeException: Si la vitesse devient négative.
            PositionInvalideException: Si la position devient invalide.
        """
        try:
            # Vérification de la vitesse avant le calcul
            if self.vitesse < 0:
                raise VitesseNegativeException(self.vitesse, str(self.id))
            
            # Calcul de la nouvelle position
            nouvelle_position = self.position + self.vitesse * delta_t
            
            # Vérification que la position ne devient pas négative
            if nouvelle_position < 0:
                raise PositionInvalideException(nouvelle_position, self.route.longueur, str(self.id))
            
            # Mise à jour de la position (bornée par la longueur de la route)
            self.position = min(nouvelle_position, self.route.longueur)
            
        except (VitesseNegativeException, PositionInvalideException):
            # Re-lever les exceptions personnalisées
            raise
        except Exception as e:
            # Capturer toute autre erreur inattendue
            raise PositionInvalideException(
                self.position, 
                self.route.longueur if self.route else None, 
                str(self.id)
            ) from e

    def changer_de_route(self, nouvelle_route):
        """Change la route du véhicule et réinitialise sa position à 0."""
        self.route = nouvelle_route
        self.position = 0
