class Analyseur:
    def __init__(self):
        pass
    
    def calculer_statistiques(self, historique):
        """Calcule les statistiques de la simulation"""
        if not historique:
            print("Aucune donnée à analyser")
            return
        
        vitesses_moyennes = []
        congestion_zones = {}
        temps_parcours = {}
        
        try:
            for tour_data in historique:
                nb_vehicules = tour_data["nb_vehicules_total"]
                try : 
                   vitesse_moyenne = sum(len(route_data["vehicules"]) for route_data in tour_data["routes"].values()) / nb_vehicules
                except ZeroDivisionError:
                    vitesse_moyenne = 0
                vitesses_moyennes.append(vitesse_moyenne)
                
                for nom_route, route_data in tour_data["routes"].items():
                    if route_data["nb_vehicules"] > 3:
                        if nom_route not in congestion_zones:
                            congestion_zones[nom_route] = 0
                        congestion_zones[nom_route] += 1
            
            vitesse_moyenne_globale = 0
            if vitesses_moyennes:
                vitesse_moyenne_globale = sum(vitesses_moyennes) / len(vitesses_moyennes)
            
            print(f"Vitesse moyenne globale: {vitesse_moyenne_globale:.2f}")
            print(f"Zones de congestion identifiées: {list(congestion_zones.keys())}")
            
            print(f"Nombre total de tours: {len(historique)}")
            
            return {
                "vitesse_moyenne": vitesse_moyenne_globale,
                "zones_congestion": list(congestion_zones.keys()),
                "duree_simulation": len(historique)
            }
        except ZeroDivisionError as e:
            print(f"Erreur de division par zéro dans le calcul des statistiques: {e}")
            raise
