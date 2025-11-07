from exceptions import (
    LongueurRouteInvalideException,
    RoutePleineException,
    VehiculeDejaPresent
)


class Route:
    """Représente une route du réseau.

    Attributs principaux:
        nom (str): nom de la route
        longueur (float): longueur en mètres
        limite_vitesse (float): limite de vitesse
        vehicules (list): véhicules présents sur la route
    """

    def __init__(self, nom, longueur, limite_vitesse, capacite_max=100):
        """Crée une nouvelle route.

        Args:
            nom (str): nom de la route.
            longueur (float): longueur de la route en mètres.
            limite_vitesse (float): vitesse maximale autorisée.
            capacite_max (int): capacité maximale de véhicules (défaut: 100).
            
        Raises:
            LongueurRouteInvalideException: Si la longueur est <= 0.
            ValueError: Si la limite de vitesse est négative.
        """
        # Validation de la longueur
        if longueur <= 0:
            raise LongueurRouteInvalideException(longueur, nom)
        
        # Validation de la limite de vitesse
        if limite_vitesse < 0:
            raise ValueError(f"La limite de vitesse doit être >= 0 pour la route '{nom}'")
        
        self.nom = nom
        self.longueur = longueur
        self.limite_vitesse = limite_vitesse
        self.capacite_max = capacite_max
        self.vehicules = []

    def ajouter_vehicule(self, vehicule):
        """Ajoute un véhicule à la route.
        
        Args:
            vehicule (Vehicule): Le véhicule à ajouter.
            
        Raises:
            RoutePleineException: Si la route a atteint sa capacité maximale.
            VehiculeDejaPresent: Si le véhicule est déjà sur cette route.
        """
        # Vérifier si la route est pleine
        if len(self.vehicules) >= self.capacite_max:
            raise RoutePleineException(self.nom, self.capacite_max)
        
        # Vérifier si le véhicule est déjà présent
        for v in self.vehicules:
            if v.id == vehicule.id:
                raise VehiculeDejaPresent(str(vehicule.id), self.nom)
        
        # Ajouter le véhicule
        self.vehicules.append(vehicule)

    def mettre_a_jour_vehicules(self, delta_t):
        """Met à jour la position de chaque véhicule pour un pas `delta_t`.
        
        Args:
            delta_t (float): Intervalle de temps en secondes.
        """
        try:
            for v in self.vehicules:
                v.avancer(delta_t)
        except Exception as e:
            # Log l'erreur mais continue avec les autres véhicules
            print(f"Erreur lors de la mise à jour du véhicule {v.id} sur la route {self.nom}: {e}")
            # Re-lever l'exception si nécessaire
            raise
