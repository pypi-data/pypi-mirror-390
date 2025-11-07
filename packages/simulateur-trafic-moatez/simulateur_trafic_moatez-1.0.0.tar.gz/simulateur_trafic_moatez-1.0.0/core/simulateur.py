from models import ReseauRoutier, Route, Vehicule
from core.analyseur import Analyseur
from io_pkg import Affichage, Export
from exceptions import (
    FichierConfigurationException,
    IterationsInvalidesException,
    RouteInexistanteException
)
import json
import csv
import os

class Simulateur:
    """Simulateur principal.

    Gère le réseau routier, l'avancement du temps, l'analyse et l'export des
    résultats. Charge une configuration JSON décrivant les routes et
    véhicules.
    """

    def __init__(self, fichier_config):
        """Initialise le simulateur à partir d'un fichier de configuration.

        Args:
            fichier_config (str): chemin vers un fichier JSON contenant
                les routes et véhicules à instancier.
                
        Raises:
            FichierConfigurationException: Si le fichier est manquant ou invalide.
            RouteInexistanteException: Si un véhicule référence une route inexistante.
        """
        self.reseau = ReseauRoutier()
        self.temps = 0
        self.analyseur = Analyseur()
        self.affichage = Affichage()
        self.exporteur = Export()
        self.historique = []

        # Charger configuration avec gestion des erreurs
        try:
            # Vérifier que le fichier existe
            if not os.path.exists(fichier_config):
                raise FileNotFoundError(f"Le fichier '{fichier_config}' n'existe pas")
            
            with open(fichier_config, "r", encoding="utf-8") as f:
                config = json.load(f)
                
        except FileNotFoundError as e:
            raise FichierConfigurationException(fichier_config, str(e)) from e
        except json.JSONDecodeError as e:
            raise FichierConfigurationException(
                fichier_config, 
                f"Format JSON invalide: {str(e)}"
            ) from e
        except Exception as e:
            raise FichierConfigurationException(
                fichier_config, 
                f"Erreur lors de la lecture: {str(e)}"
            ) from e

        # Charger les routes
        try:
            if "routes" not in config:
                raise FichierConfigurationException(
                    fichier_config,
                    "La clé 'routes' est manquante dans la configuration"
                )
            
            for r in config["routes"]:
                route = Route(r["nom"], r["longueur"], r["limite_vitesse"])
                self.reseau.ajouter_route(route)
                
        except KeyError as e:
            raise FichierConfigurationException(
                fichier_config,
                f"Clé manquante dans la définition d'une route: {str(e)}"
            ) from e
        except Exception as e:
            raise FichierConfigurationException(
                fichier_config,
                f"Erreur lors de la création des routes: {str(e)}"
            ) from e

        # Charger les véhicules
        try:
            if "vehicules" not in config:
                raise FichierConfigurationException(
                    fichier_config,
                    "La clé 'vehicules' est manquante dans la configuration"
                )
            
            for v in config["vehicules"]:
                try:
                    route = self.reseau.get_route(v["route"])
                    vehicule = Vehicule(v["id"], route, v["position"], v["vitesse"])
                    route.ajouter_vehicule(vehicule)
                except RouteInexistanteException:
                    raise
                except KeyError as e:
                    raise FichierConfigurationException(
                        fichier_config,
                        f"Clé manquante dans la définition du véhicule {v.get('id', '?')}: {str(e)}"
                    ) from e
                    
        except RouteInexistanteException:
            raise
        except FichierConfigurationException:
            raise
        except Exception as e:
            raise FichierConfigurationException(
                fichier_config,
                f"Erreur lors de la création des véhicules: {str(e)}"
            ) from e

    def lancer_simulation(self, n_tours, delta_t):
        """Exécute la simulation pendant `n_tours` incréments de `delta_t`.

        À chaque tour:
        - avance le temps
        - met à jour les véhicules sur chaque route
        - calcule des statistiques via l'analyseur
        - affiche l'état
        - enregistre un snapshot des positions dans l'historique

        Args:
            n_tours (int): nombre de pas de simulation à exécuter.
            delta_t (float): durée (en secondes) d'un pas de simulation.
            
        Raises:
            IterationsInvalidesException: Si n_tours est invalide (<= 0).
            ValueError: Si delta_t est invalide (<= 0).
        """
        # Validation des paramètres
        if not isinstance(n_tours, int) or n_tours <= 0:
            raise IterationsInvalidesException(n_tours)
        
        if not isinstance(delta_t, (int, float)) or delta_t <= 0:
            raise ValueError(f"delta_t doit être un nombre strictement positif, reçu: {delta_t}")
        
        try:
            for tour in range(n_tours):
                self.temps += delta_t
                
                # Mise à jour des véhicules sur chaque route
                for route in self.reseau.routes.values():
                    try:
                        route.mettre_a_jour_vehicules(delta_t)
                    except Exception as e:
                        print(f"⚠️  Avertissement au tour {tour + 1}: Erreur sur la route {route.nom}: {e}")
                        # On continue la simulation malgré l'erreur sur une route

                # Analyse et affichage
                try:
                    stats = self.analyseur.analyser(self.reseau)
                    self.affichage.afficher_etat(self.temps, self.reseau, stats)
                except Exception as e:
                    print(f"⚠️  Avertissement: Erreur lors de l'analyse au temps {self.temps}s: {e}")
                    stats = {"nb_vehicules": 0, "vitesses": [], "moyenne_vitesse": 0}

                # Enregistrement de l'historique
                snapshot = {"temps": self.temps, "positions": {}}
                for route in self.reseau.routes.values():
                    for v in route.vehicules:
                        snapshot["positions"][v.id] = v.position
                self.historique.append(snapshot)

            # Export des résultats finaux
            try:
                self.exporteur.exporter_resultats(stats, "data/resultats.json")
            except Exception as e:
                print(f"⚠️  Avertissement: Impossible d'exporter les résultats: {e}")
                
        except (IterationsInvalidesException, ValueError):
            # Re-lever les exceptions de validation
            raise
        except KeyboardInterrupt:
            print("\n⚠️  Simulation interrompue par l'utilisateur")
            raise
        except Exception as e:
            print(f"❌ Erreur critique lors de la simulation: {e}")
            raise
            for route in self.reseau.routes.values():
                route.mettre_a_jour_vehicules(delta_t)

            stats = self.analyseur.analyser(self.reseau)
            self.affichage.afficher_etat(self.temps, self.reseau, stats)

            snapshot = {"temps": self.temps, "positions": {}}
            for route in self.reseau.routes.values():
                for v in route.vehicules:
                    snapshot["positions"][v.id] = v.position
            self.historique.append(snapshot)

        self.exporteur.exporter_resultats(stats, "data/resultats.json")

    def tracer_positions(self):
        """Exporte les positions des véhicules au format CSV.

        Le fichier produit contient une colonne 'temps' suivie d'une colonne par
        véhicule (identifiée par son id). Ce jeu de données peut ensuite être
        visualisé avec l'outil de votre choix.
        """
        # Export position time-series to CSV using the standard library so plotting
        # is optional and doesn't require matplotlib.
        if not self.historique:
            print("Aucun historique disponible pour tracer les positions.")
            return

        # Collect all vehicle ids and sorted time steps
        temps = [s["temps"] for s in self.historique]
        vehicules_ids = []
        seen = set()
        for s in self.historique:
            for vid in s["positions"].keys():
                if vid not in seen:
                    seen.add(vid)
                    vehicules_ids.append(vid)

        out_path = "data/positions.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # Header: time + vehicle ids
            writer.writerow(["temps"] + list(vehicules_ids))
            for s in self.historique:
                row = [s["temps"]]
                for vid in vehicules_ids:
                    row.append(s["positions"].get(vid, ""))
                writer.writerow(row)

        print(f"Positions exportées vers {out_path} (CSV). Use your preferred plotting tool to visualize it.")
