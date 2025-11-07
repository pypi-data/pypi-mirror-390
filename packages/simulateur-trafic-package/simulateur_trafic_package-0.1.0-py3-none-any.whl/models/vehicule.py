"""
Ce module contient la définition de la classe Vehicule pour le simulateur de trafic.
"""
from simulateur_trafic.exceptions.exceptions import VitesseInvalideError


class Vehicule:
    """
    Représente un véhicule dans le simulateur.

    Attributes:
        identifiant (int): identifiant unique du véhicule.
        position (float): position actuelle du véhicule sur sa route.
        vitesse (float): vitesse actuelle du véhicule.
        route_actuelle (Route, optional): route sur laquelle se trouve le véhicule.
    """

    def __init__(self, identifiant: int, position: float, vitesse: float):
        """
        Initialise un nouveau véhicule dans le simulateur.

        Args:
            identifiant (int): identifiant unique du véhicule.
            position (float): position initiale du véhicule sur la route.
            vitesse (float): vitesse initiale du véhicule.
        """
        self.identifiant = identifiant
        self.position = position
        self.vitesse = vitesse
        self.route_actuelle = None

    def avancer(self, temps: float):
        """
        Met à jour la position du véhicule en fonction du temps écoulé.

        Args:
            temps (float): durée pendant laquelle le véhicule avance.
        """
        try:
            if self.vitesse < 0:
                raise VitesseInvalideError("La vitesse ne peut pas être négative.")
            self.position += self.vitesse * temps
        except VitesseInvalideError as e:
            print(f"Erreur dans avancer(): {e}")

    def changer_de_route(self, nouvelle_route):
        """
        Assigne une nouvelle route au véhicule.

        Args:
            nouvelle_route (Route): objet Route correspondant à la nouvelle route.
        """
        self.route_actuelle = nouvelle_route
        self.position = 0
