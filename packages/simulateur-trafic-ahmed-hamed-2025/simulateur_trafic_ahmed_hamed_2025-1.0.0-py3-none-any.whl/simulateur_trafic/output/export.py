import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import json
from simulateur_trafic.exceptions import ExportError

def exporter_vers_csv(donnees, nom_fichier):
    """Exporte les données de simulation vers un fichier CSV"""
    try:
        with open(nom_fichier, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['tour', 'nb_routes', 'nb_vehicules_total']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for tour_data in donnees:
                row = {
                    'tour': tour_data['tour'],
                    'nb_routes': tour_data['nb_routes'],
                    'nb_vehicules_total': tour_data['nb_vehicules_total']
                }
                writer.writerow(row)
        print(f"Données exportées vers {nom_fichier}")
    except Exception as e:
        raise ExportError(f"Erreur lors de l'export CSV vers {nom_fichier}: {e}")

def exporter_vers_json(donnees, nom_fichier):
    """Exporte les données de simulation vers un fichier JSON"""
    try:
        with open(nom_fichier, 'w', encoding='utf-8') as jsonfile:
            json.dump(donnees, jsonfile, indent=2, ensure_ascii=False)
        print(f"Données exportées vers {nom_fichier}")
    except Exception as e:
        raise ExportError(f"Erreur lors de l'export JSON vers {nom_fichier}: {e}")

def exporter_donnees_detaillees_vers_csv(historique, nom_fichier):
    """Exporte des données détaillées vers un fichier CSV"""
    try:
        with open(nom_fichier, 'w', newline='', encoding='utf-8') as csvfile:
            # En-têtes pour les données détaillées
            fieldnames = ['tour', 'route', 'nb_vehicules']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for tour_data in historique:
                for nom_route, route_data in tour_data["routes"].items():
                    row = {
                        'tour': tour_data['tour'],
                        'route': nom_route,
                        'nb_vehicules': route_data['nb_vehicules']
                    }
                    writer.writerow(row)
        print(f"Données détaillées exportées vers {nom_fichier}")
    except Exception as e:
        raise ExportError(f"Erreur lors de l'export détaillé CSV vers {nom_fichier}: {e}")