import json

class Export:
    """Export simple de résultats au format JSON.

    Méthode `exporter_resultats` écrit les statistiques fournies dans un
    fichier JSON indenté.
    """

    def exporter_resultats(self, stats, fichier):
        """Écrit `stats` dans `fichier` au format JSON.

        Args:
            stats (dict): dictionnaire de statistiques à sauvegarder.
            fichier (str): chemin du fichier de sortie.
        """
        with open(fichier, "w") as f:
            json.dump(stats, f, indent=4)
        print(f"\nR\u00e9sultats export\u00e9s dans {fichier}")
