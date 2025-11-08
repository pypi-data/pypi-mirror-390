import json
import os
from simulateur_trafic.models.route import Route
from simulateur_trafic.models.reseau import ReseauRoutier
from simulateur_trafic.output.affichage import afficher_etat_reseau
from simulateur_trafic.output.export import exporter_vers_csv, exporter_vers_json
from simulateur_trafic.core.analyseur import Analyseur
from simulateur_trafic.models.vehicule import Vehicule
class Simulateur:
    """
    Gère l'ensemble de la simulation de trafic routier.
    
    Attributes:
        reseau (ReseauRoutier): Le réseau routier simulé
        analyseur (Analyseur): L'analyseur des résultats de simulation
        historique (list): Historique des statistiques de chaque tour de simulation
    """
    
    def __init__(self, fichier_config=None):
        """
        Constructeur de la classe Simulateur.
        
        Args:
            fichier_config (str, optional): Chemin vers le fichier de configuration JSON. Défaut à None.
        """
        self.reseau = ReseauRoutier()
        self.analyseur = Analyseur()
        self.historique = []
        
        if fichier_config:
            self.charger_configuration(fichier_config)
    
    def charger_configuration(self, chemin_fichier):
        """
        Charge la configuration du réseau à partir d'un fichier JSON.
        
        Le fichier de configuration doit contenir:
        - Une liste de routes avec leur nom, longueur et limite de vitesse
        - Une liste de véhicules avec leur ID, position initiale, vitesse et route assignée
        
        Args:
            chemin_fichier (str): Chemin vers le fichier de configuration JSON
        """
        try:
            with open(chemin_fichier, 'r') as f:
                config = json.load(f)
            
            for route_data in config.get("routes", []):
                route = Route(
                    nom=route_data["nom"],
                    longueur=route_data["longueur"],
                    limite_vitesse=route_data["limite_vitesse"]
                )
                self.reseau.ajouter_route(route)
            
            for vehicule_data in config.get("vehicules", []):
                vehicule = Vehicule(
                    id=vehicule_data["id"],
                    position=vehicule_data["position"],
                    vitesse=vehicule_data["vitesse"],
                    route_actuelle=None
                )
                
                nom_route = vehicule_data["route_actuelle"]
                route = self.reseau.obtenir_route(nom_route)
                if route:
                    vehicule.changer_de_route(route)
        except FileNotFoundError:
            print(f"Erreur: Fichier de configuration '{chemin_fichier}' non trouvé.")

    
    def lancer_simulation(self, n_tours, delta_t):
        """
        Lance la simulation pour un nombre donné de tours.
       
        Args:
            n_tours (int): Nombre de tours de simulation à exécuter
            delta_t (float): Intervalle de temps entre chaque tour (en secondes)
        """
        try:
            if n_tours <= 0 :
               raise ValueError("Le nombre de tours doit être supérieur à zéro")

            
            print(f"Lancement de la simulation: {n_tours} tours, {delta_t} secondes par tour")
            
            for tour in range(n_tours):
                print(f"\n--- Tour {tour + 1} ---")
                
                self.reseau.mettre_a_jour(delta_t)
                
                stats = self.reseau.obtenir_statistiques()
                stats["tour"] = tour + 1
                self.historique.append(stats)
                
                afficher_etat_reseau(stats)
                
                for route in self.reseau.routes.values():
                    vehicules_a_retirer = []
                    for vehicule in route.vehicules:
                        if vehicule.position >= route.longueur:
                            vehicules_a_retirer.append(vehicule)
                    
                    for vehicule in vehicules_a_retirer:
                        print(f"Véhicule {vehicule.id} a terminé son trajet sur {route.nom}")
                        route.retirer_vehicule(vehicule)
            
            print("\n=== Résultats de la simulation ===")
            self.analyseur.calculer_statistiques(self.historique)
            
            print("\n=== Export des résultats ===")
            exporter_vers_csv(self.historique, "resultats_simulation.csv")
            exporter_vers_json(self.historique, "resultats_simulation.json")
            print("Résultats exportés vers resultats_simulation.csv et resultats_simulation.json")
        except ValueError as e:
            print(f"Erreur de valeur dans la simulation: {e}")
