class SimulationError(Exception):
    """Exception de base pour le simulateur."""
    pass


class VehiculeInvalideError(SimulationError):
    """Erreur quand un véhicule est invalide."""
    pass


class VehiculePresentsError(SimulationError):
    """Erreur quand on souhaite ajouter un véhicule à une route, qui est déjà existant dans cette route."""
    pass


class VitesseInvalideError(SimulationError):
    """Erreur quand la vitesse d'un véhicule est négative."""
    pass


class PositionInvalideError(SimulationError):
    """Erreur quand la position d'un véhicule est invalide."""
    pass
