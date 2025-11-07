"""
Ce module contient la définition de la classe ReseauRoutier pour le simulateur de trafic.
"""

from simulateur_trafic.models.route import Route

class ReseauRoutier:
    """
    Représente un réseau de rues dans le simulateur.

    Attributes:
        routes (list[Route]): liste des routes dans le réseau.
        intersections (dict[str, list[Route]]): dictionnaire des intersections,
            clé = nom de l'intersection, valeur = liste des routes connectées.
    """

    def __init__(self):
        """
        Initialise un nouveau réseau.

        Attributes:
            routes (list[Route]): initialisé comme liste vide.
            intersections (dict[str, list[Route]]): initialisé comme dictionnaire vide.
        """
        self.routes: list[Route] = []
        self.intersections: dict[str, list[Route]] = {}

    @classmethod
    def from_json(cls, config: dict) -> "ReseauRoutier":
        """
        Crée une instance de ReseauRoutier à partir d'une configuration JSON.

        Args:
            config (dict): dictionnaire contenant deux clés :
                - "routes": liste de dictionnaires représentant chaque route.
                - "intersections": liste de dictionnaires représentant chaque intersection.

        Returns:
            ReseauRoutier: instance construite à partir de la configuration.
        """
        reseau = cls()
        for r in config.get("routes", []):
            route = Route(
                r["nom"], r["longueur"], r["start"], r["end"],
                r["limite_vitesse"], r["vehicules"]
            )
            reseau.ajouter_route(route)

        for inter in config.get("intersections", []):
            routes_obj = [r for r in reseau.routes if r.nom in inter["connecte"]]
            reseau.ajouter_intersection(inter["nom"], routes_obj)

        return reseau

    def ajouter_route(self, route: Route):
        """
        Ajoute une nouvelle route dans le réseau.

        Args:
            route (Route): objet Route à ajouter.
        """
        self.routes.append(route)

    def ajouter_intersection(self, nom: str, routes: list[Route]):
        """
        Ajoute une intersection dans le réseau.

        Args:
            nom (str): nom de l'intersection.
            routes (list[Route]): liste des routes qui composent cette intersection.
        """
        self.intersections[nom] = routes

    def simuler(self, temps: float):
        """
        Met à jour les positions des véhicules sur chaque route.

        Args:
            temps (float): durée de la simulation pour mettre à jour les véhicules.
        """
        for route in self.routes:
            route.mettre_a_jour_vehicules(temps)

    def etat_reseau(self) -> dict[str, list[int]]:
        """
        Retourne l'état actuel du réseau.

        Returns:
            dict[str, list[int]]: clé = nom de la route, valeur = liste des identifiants des véhicules.
        """
        etat = {}
        for route in self.routes:
            etat[route.nom] = [vehicule.identifiant for vehicule in route.vehicules]
        return etat
