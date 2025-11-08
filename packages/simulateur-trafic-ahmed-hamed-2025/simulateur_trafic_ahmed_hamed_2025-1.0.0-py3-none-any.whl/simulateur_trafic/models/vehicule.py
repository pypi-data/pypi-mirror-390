import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulateur_trafic.exceptions import  ChangementRouteError

class Vehicule:
    """
    Représente un véhicule dans le simulateur de trafic.
    
    Attributes:
        id (str): Identifiant unique du véhicule
        position (float): Position actuelle du véhicule sur la route (en mètres)
        vitesse (float): Vitesse actuelle du véhicule (en m/s)
        route_actuelle (Route): Route sur laquelle le véhicule se trouve actuellement
    """
    
    def __init__(self, id, position=0, vitesse=0, route_actuelle=None):
        """
        Initialise un nouveau véhicule.
        
        Args:
            id (str): Identifiant unique du véhicule
            position (float, optional): Position initiale sur la route. Défaut à 0.
            vitesse (float, optional): Vitesse initiale du véhicule. Défaut à 0.
            route_actuelle (Route, optional): Route initiale du véhicule. Défaut à None.
        """
        self.id = id
        self.position = position
        self.vitesse = vitesse
        self.route_actuelle = route_actuelle
    
    def avancer(self, delta_t):
        """
        Fait avancer le véhicule en fonction de sa vitesse et du temps écoulé. 
        La position du véhicule est mise à jour selon la formule: nouvelle_position = position + vitesse * delta_t
        Si le véhicule dépasse la longueur de la route, sa position est limitée à la longueur de la route.
        Args:
            delta_t (float): Intervalle de temps écoulé depuis le dernier déplacement (en secondes)
        """
        try:
            self.position += self.vitesse * delta_t
            if self.vitesse<0 :
                raise ValueError("La vitesse ne peut pas être négative")
            if self.position <0:
                raise ValueError("La position ne peut pas être inférieure à zéro")
            
            if self.route_actuelle and self.position > self.route_actuelle.longueur:
                self.position = self.route_actuelle.longueur
        except ValueError as e:
            print(f"Erreur dans la méthode avancer: {e}")
            raise

    
    def changer_de_route(self, nouvelle_route):
        """
        Change la route actuelle du véhicule.
        
        Retire le véhicule de sa route actuelle (si elle existe) et l'ajoute à la nouvelle route.
        
        Args:
            nouvelle_route (Route): La nouvelle route sur laquelle le véhicule doit se déplacer
        """
        try:
            if self.route_actuelle:
                self.route_actuelle.retirer_vehicule(self)
            
            self.route_actuelle = nouvelle_route
            if nouvelle_route:
                nouvelle_route.ajouter_vehicule(self)
        except Exception as e:
            raise ChangementRouteError(f"Erreur lors du changement de route pour le véhicule {self.id}: {e}")
    
    def __str__(self):
        """
        Retourne une représentation textuelle du véhicule.
        
        Returns:
            str: Description du véhicule avec son ID, position, vitesse et route actuelle
        """
        return f"Vehicule(id={self.id}, position={self.position}, vitesse={self.vitesse}, route={self.route_actuelle.nom if self.route_actuelle else 'Aucune'})"