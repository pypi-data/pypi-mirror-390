from exceptions import (
    RouteVideException,
    DivisionParZeroException,
    DonneesMaquantesException
)


class Analyseur:
    """Classe simple d'analyse du réseau.

    Fournit des méthodes pour calculer des statistiques basiques sur le réseau
    (nombre de véhicules, liste des vitesses et vitesse moyenne).
    """

    def analyser(self, reseau):
        """Analyse l'état du `reseau` et renvoie des statistiques.

        Args:
            reseau: instance de `ReseauRoutier` contenant les routes et véhicules.

        Returns:
            dict: clés: 'nb_vehicules', 'vitesses', 'moyenne_vitesse'.
            
        Raises:
            DonneesMaquantesException: Si le réseau n'a pas de routes.
            DivisionParZeroException: Si une erreur de calcul survient.
        """
        try:
            # Vérifier que le réseau contient des routes
            if not reseau or not hasattr(reseau, 'routes'):
                raise DonneesMaquantesException("Le réseau ne contient pas de routes")
            
            if not reseau.routes:
                raise DonneesMaquantesException("Le réseau ne contient aucune route")
            
            stats = {"nb_vehicules": 0, "vitesses": [], "moyenne_vitesse": 0}

            for route in reseau.routes.values():
                for v in route.vehicules:
                    stats["nb_vehicules"] += 1
                    stats["vitesses"].append(v.vitesse)

            # Calcul de la moyenne avec gestion de la division par zéro
            if stats["vitesses"]:
                try:
                    stats["moyenne_vitesse"] = sum(stats["vitesses"]) / len(stats["vitesses"])
                except ZeroDivisionError as e:
                    raise DivisionParZeroException("calcul de la vitesse moyenne") from e
            
            return stats
            
        except (DonneesMaquantesException, DivisionParZeroException):
            # Re-lever les exceptions personnalisées
            raise
        except Exception as e:
            # Capturer toute autre erreur inattendue
            raise DonneesMaquantesException(f"Erreur lors de l'analyse: {str(e)}") from e
