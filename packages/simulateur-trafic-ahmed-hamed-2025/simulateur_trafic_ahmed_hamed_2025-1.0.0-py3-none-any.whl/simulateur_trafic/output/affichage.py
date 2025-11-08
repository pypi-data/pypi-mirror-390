import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulateur_trafic.exceptions import StatistiqueCalculError

def afficher_etat_reseau(statistiques):
    """Affiche l'état actuel du réseau routier"""
    try:
        print(f"Réseau: {statistiques['nb_routes']} routes, {statistiques['nb_vehicules_total']} véhicules")
        
        for nom_route, route_data in statistiques["routes"].items():
            print(f"  {nom_route}: {route_data['nb_vehicules']} véhicules")
            # Afficher les détails des véhicules si demandé
            # for vehicule_str in route_data["vehicules"]:
            #     print(f"    {vehicule_str}")
    except KeyError as e:
        raise StatistiqueCalculError(f"Données de statistiques manquantes: {e}")
    except Exception as e:
        raise StatistiqueCalculError(f"Erreur lors de l'affichage de l'état du réseau: {e}")

def afficher_statistiques_finales(analyse_resultats):
    """Affiche les statistiques finales de la simulation"""
    try:
        print("\n=== Statistiques finales ===")
        print(f"Vitesse moyenne: {analyse_resultats.get('vitesse_moyenne', 0):.2f}")
        print(f"Zones de congestion: {analyse_resultats.get('zones_congestion', [])}")
        print(f"Durée de la simulation: {analyse_resultats.get('duree_simulation', 0)} tours")
    except Exception as e:
        raise StatistiqueCalculError(f"Erreur lors de l'affichage des statistiques finales: {e}")