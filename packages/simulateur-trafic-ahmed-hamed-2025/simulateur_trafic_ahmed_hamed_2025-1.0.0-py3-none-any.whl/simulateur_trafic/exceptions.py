class SimulationError(Exception):
    """Exception de base pour toutes les erreurs liées à la simulation de trafic."""
    pass

class VehiculeError(SimulationError):
    """Exception levée pour les erreurs liées aux véhicules."""
    pass

class RouteError(SimulationError):
    """Exception levée pour les erreurs liées aux routes."""
    pass



class StatistiqueError(SimulationError):
    """Exception levée pour les erreurs liées aux calculs statistiques."""
    pass



class ExportError(SimulationError):
    """Exception levée lors des erreurs d'export des données."""
    pass

class ReseauError(SimulationError):
    """Exception levée pour les erreurs liées au réseau routier."""
    pass

class ChangementRouteError(VehiculeError):
    """Exception levée lors des erreurs de changement de route."""
    pass

class MiseAJourRouteError(RouteError):
    """Exception levée lors des erreurs de mise à jour des routes."""
    pass

class StatistiqueCalculError(StatistiqueError):
    """Exception levée lors des erreurs dans les calculs statistiques."""
    pass

class ReseauMiseAJourError(ReseauError):
    """Exception levée lors des erreurs de mise à jour du réseau."""
    pass

class ReseauStatistiqueError(ReseauError):
    """Exception levée lors des erreurs dans les statistiques du réseau."""
    pass