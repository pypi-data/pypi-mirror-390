import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulateur_trafic.exceptions import  MiseAJourRouteError

class Route:
    """
    Représente une route dans le simulateur de trafic.
    
    Attributes:
        nom (str): Nom de la route
        longueur (float): Longueur de la route en mètres
        limite_vitesse (float): Limite de vitesse sur la route en m/s
        vehicules (list): Liste des véhicules présents sur la route
    """
    
    def __init__(self, nom, longueur, limite_vitesse):
        """
        Initialise une nouvelle route.
        
        Args:
            nom (str): Nom de la route
            longueur (float): Longueur de la route en mètres
            limite_vitesse (float): Limite de vitesse sur la route en m/s
        """
        self.nom = nom
        self.longueur = longueur
        self.limite_vitesse = limite_vitesse
        self.vehicules = []
    
    def ajouter_vehicule(self, vehicule):
        """
        Ajoute un véhicule à la route.
        
        Args:
            vehicule (Vehicule): Le véhicule à ajouter à la route
        """
        try:
            if len(self.vehicules) >= self.longueur / 3:
                raise ValueError("La route est pleine")
            if vehicule in self.vehicules:
                raise ValueError("Le véhicule est déjà sur la route")
            if vehicule not in self.vehicules:
                self.vehicules.append(vehicule)
        except ValueError as e:
            print(f"Erreur dans la méthode ajouter_vehicule: {e}")
            raise
        except Exception as e:
            print(f"Erreur inattendue dans la méthode ajouter_vehicule: {e}")
            raise
        
    
    def retirer_vehicule(self, vehicule):
        """
        Retire un véhicule de la route.
        
        Args:
            vehicule (Vehicule): Le véhicule à retirer de la route
        """
        if vehicule in self.vehicules:
            self.vehicules.remove(vehicule)
    
    def mettre_a_jour_vehicules(self, delta_t):
        """
        Met à jour la position de tous les véhicules sur la route.
        
        Pour chaque véhicule sur la route:
        1. Appelle la méthode avancer du véhicule
        2. Limite la vitesse du véhicule à la limite de vitesse de la route
        
        Args:
            delta_t (float): Intervalle de temps écoulé depuis la dernière mise à jour (en secondes)
        """
        try:
            for vehicule in self.vehicules:
                vehicule.avancer(delta_t)
                if vehicule.vitesse > self.limite_vitesse:
                    vehicule.vitesse = self.limite_vitesse
        except Exception as e:
            raise MiseAJourRouteError(f"Erreur lors de la mise à jour des véhicules sur la route {self.nom}: {e}")
    
    def __str__(self):
        """
        Retourne une représentation textuelle de la route.
        
        Returns:
            str: Description de la route avec son nom, longueur, limite de vitesse et nombre de véhicules
        """
        return f"Route(nom={self.nom}, longueur={self.longueur}, limite_vitesse={self.limite_vitesse}, nb_vehicules={len(self.vehicules)})"