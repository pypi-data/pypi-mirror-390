class Affichage:
    """Composant d'affichage minimal pour la simulation.

    Fournit une méthode `afficher_etat` qui affiche sur la sortie standard
    une représentation textuelle de l'état du réseau et des statistiques.
    """

    def afficher_etat(self, temps, reseau, stats):
        """Affiche l'état courant de la simulation.

        Args:
            temps (float): temps simulé (s).
            reseau (ReseauRoutier): instance contenant les routes et véhicules.
            stats (dict): statistiques calculées par l'analyseur.
        """
        print(f"\n--- Temps: {temps} s ---")
        for nom, etat in reseau.etat_reseau().items():
            print(f"Route {nom} : {etat}")
        print(f"Statistiques: {stats}")
