"""
Point d'entrée principal pour le simulateur de trafic.

Ce module peut être exécuté directement ou importé pour utiliser
les classes du simulateur dans d'autres projets.
"""

import os
import sys
from pathlib import Path

from .core.simulateur import Simulateur
from .exceptions import (
    SimulateurException,
    FichierConfigurationException,
    IterationsInvalidesException
)


def get_default_config_path():
    """Retourne le chemin vers le fichier de configuration par défaut."""
    package_dir = Path(__file__).parent
    config_path = package_dir / "data" / "config_reseau.json"
    return str(config_path)


def main():
    """
    Fonction principale pour exécuter le simulateur.
    
    Peut être appelée depuis la ligne de commande:
    python -m simulateur_trafic
    ou
    simulateur-trafic
    """
    try:
        print("=" * 60)
        print("🚦 SIMULATEUR DE TRAFIC ROUTIER")
        print("=" * 60)
        print()
        
        # Utiliser la configuration par défaut
        config_path = get_default_config_path()
        
        # Initialisation du simulateur
        print("📂 Chargement de la configuration...")
        print(f"   Fichier: {config_path}")
        simu = Simulateur(config_path)
        print("✅ Configuration chargée avec succès\n")
        
        # Lancement de la simulation
        print("▶️  Démarrage de la simulation...")
        print("-" * 60)
        simu.lancer_simulation(n_tours=10, delta_t=1.0)
        print("-" * 60)
        print("✅ Simulation terminée avec succès\n")
        
        # Export des positions
        print("📊 Export des positions en CSV...")
        simu.tracer_positions()
        
        print()
        print("=" * 60)
        print("✨ Simulation complète !")
        print("=" * 60)
        
    except FichierConfigurationException as e:
        print(f"\n❌ ERREUR DE CONFIGURATION [{e.code}]")
        print(f"   Fichier: {e.fichier}")
        print(f"   Raison: {e.raison}")
        print("\n💡 Vérifiez que le fichier de configuration existe et est valide.")
        sys.exit(1)
        
    except IterationsInvalidesException as e:
        print(f"\n❌ ERREUR DE PARAMÈTRES [{e.code}]")
        print(f"   Nombre d'itérations invalide: {e.iterations}")
        print("\n💡 Le nombre d'itérations doit être un entier > 0.")
        sys.exit(1)
        
    except SimulateurException as e:
        print(f"\n❌ ERREUR DU SIMULATEUR [{e.code}]")
        print(f"   {e.message}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrompue par l'utilisateur.")
        print("   Les données partielles ont été sauvegardées.")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {type(e).__name__}")
        print(f"   {str(e)}")
        print("\n💡 Contactez le support technique si le problème persiste.")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()