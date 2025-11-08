"""
Point d'entrée principal du simulateur de trafic.
Permet d'exécuter une simulation en ligne de commande avec des paramètres personnalisés.
"""

import argparse
from simulateur_trafic.core.simulateur import Simulateur


def main():
    # --- Argument parser setup ---
    parser = argparse.ArgumentParser(
        description="Simulateur de trafic routier - exécution d'une simulation personnalisée."
    )
    parser.add_argument(
        "--n_tours",
        type=int,
        default=5,
        help="Nombre de tours de simulation (par défaut : 5)"
    )
    parser.add_argument(
        "--delta_t",
        type=int,
        default=60,
        help="Durée d'un pas de simulation en secondes (par défaut : 60)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="simulateur_trafic/data/config_reseau.json",
        help="Chemin du fichier de configuration JSON (par défaut : simulateur_trafic/data/config_reseau.json)"
    )

    args = parser.parse_args()

    # --- Lancement de la simulation ---
    print("🚦 Lancement du simulateur de trafic...")
    print(f"📁 Fichier de configuration : {args.config}")
    print(f"🔁 Nombre de tours : {args.n_tours}")
    print(f"⏱️ Pas de temps : {args.delta_t} secondes\n")

    simu = Simulateur(fichier_config=args.config)
    simu.lancer_simulation(n_tours=args.n_tours, delta_t=args.delta_t)


if __name__ == "__main__":
    main()
