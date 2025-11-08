import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulateur_trafic.exceptions import ReseauMiseAJourError, ReseauStatistiqueError

class ReseauRoutier:
    """
    Représente un réseau routier composé de plusieurs routes interconnectées.
    
    Attributes:
        routes (dict): Dictionnaire des routes du réseau avec leur nom comme clé
        intersections (dict): Dictionnaire des intersections du réseau (à implémenter)
    """
    
    def __init__(self):
        """Initialise un nouveau réseau routier vide."""
        self.routes = {}
        self.intersections = {}
    
    def ajouter_route(self, route):
        """
        Ajoute une route au réseau.
        
        Args:
            route (Route): La route à ajouter au réseau
        """
        try:
            self.routes[route.nom] = route
        except Exception as e:
            raise ReseauMiseAJourError(f"Erreur lors de l'ajout de la route {route.nom}: {e}")
    
    def retirer_route(self, nom_route):
        """
        Retire une route du réseau.
        
        Args:
            nom_route (str): Le nom de la route à retirer du réseau
        """
        try:
            if nom_route in self.routes:
                del self.routes[nom_route]
        except Exception as e:
            raise ReseauMiseAJourError(f"Erreur lors du retrait de la route {nom_route}: {e}")
    
    def obtenir_route(self, nom):
        """
        Retourne une route par son nom.
        
        Args:
            nom (str): Le nom de la route recherchée
            
        Returns:
            Route or None: La route correspondante ou None si elle n'existe pas
        """
        try:
            return self.routes.get(nom)
        except Exception as e:
            raise ReseauMiseAJourError(f"Erreur lors de l'obtention de la route {nom}: {e}")
    
    def mettre_a_jour(self, delta_t):
        """
        Met à jour toutes les routes du réseau.
        
        Appelle la méthode mettre_a_jour_vehicules pour chaque route du réseau.
        
        Args:
            delta_t (float): Intervalle de temps écoulé depuis la dernière mise à jour (en secondes)
        """
        try:
            for route in self.routes.values():
                route.mettre_a_jour_vehicules(delta_t)
        except Exception as e:
            raise ReseauMiseAJourError(f"Erreur lors de la mise à jour du réseau: {e}")
    
    def obtenir_statistiques(self):
        """
        Retourne des statistiques sur l'état actuel du réseau.
        
        Returns:
            dict: Dictionnaire contenant les statistiques du réseau:
                - nb_routes: Nombre total de routes
                - nb_vehicules_total: Nombre total de véhicules sur le réseau
                - routes: Détails pour chaque route (nom, nb_vehicules, vehicules)
        """
        try:
            stats = {
                "nb_routes": len(self.routes),
                "nb_vehicules_total": sum(len(route.vehicules) for route in self.routes.values()),
                "routes": {}
            }
            
            for nom, route in self.routes.items():
                stats["routes"][nom] = {
                    "nb_vehicules": len(route.vehicules),
                    "vehicules": [str(v) for v in route.vehicules]
                }
            
            return stats
        except Exception as e:
            raise ReseauStatistiqueError(f"Erreur lors de l'obtention des statistiques du réseau: {e}")