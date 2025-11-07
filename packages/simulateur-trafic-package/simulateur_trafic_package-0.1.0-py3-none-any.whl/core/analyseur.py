"""
Ce module contient la définition de la classe Analyseur qui permet d'analyser un ReseauRoutier.
"""

from simulateur_trafic.models.reseau import ReseauRoutier


class Analyseur:
    """
    Représente un analyseur d'un réseau routier.

    Attributes:
        reseau (ReseauRoutier): le réseau routier à analyser
        vitesse_moyenne (dict[int, dict[str, float]]): vitesse moyenne pour chaque route
        zones_congestion (dict[int, dict[str, dict]]): zones de congestion détectées par tour
        temps_parcours (dict[int, dict[str, dict]]): temps de parcours pour chaque véhicule
            sur chaque route et par tour
    """

    def __init__(self, reseau: ReseauRoutier):
        """
        Initialise un nouvel analyseur pour un réseau routier donné.

        Args:
            reseau (ReseauRoutier): le réseau à analyser
        """
        self.reseau = reseau
        self.vitesse_moyenne = {}
        self.zones_congestion = {}
        self.temps_parcours = {}

    def update_stats(self, tour: int):
        """
        Ajoute les statistiques pour un tour donné.

        Args:
            tour (int): numéro du tour à analyser
        """
        self.vitesse_moyenne[tour] = self._calculer_vitesse_moyenne()
        self.zones_congestion[tour] = self._calculer_zones_congestion()
        self.temps_parcours[tour] = self._calculer_temps_parcours()

    def _calculer_vitesse_moyenne(self) -> dict:
        """
        Calcule la vitesse moyenne de chaque route du réseau.

        Returns:
            dict[str, float]: clé = nom de route, valeur = vitesse moyenne
        """
        vitesses_moyenne = {}
        for route in self.reseau.routes:
            if route.vehicules:
                vitesses_moyenne[route.nom] = sum(v.vitesse for v in route.vehicules) / len(route.vehicules)
            else:
                vitesses_moyenne[route.nom] = 0
                print(f"Aucun véhicule sur la route {route.nom}.")
        return vitesses_moyenne

    def _calculer_zones_congestion(self) -> dict:
        """
        Recherche les zones de congestion pour chaque route.

        Returns:
            dict[str, dict[int, float]]: clé = nom de route, valeur = dict avec
                'vehicules' et 'capacite'
        """
        congestion = {}
        for route in self.reseau.routes:
            capacite_max = route.longueur / 10  # 1 véhicule / 10 unités de longueur
            n_vehicules = len(route.vehicules)
            if n_vehicules > capacite_max:
                congestion[route.nom] = {"vehicules": n_vehicules, "capacite": capacite_max}
        return congestion

    def _calculer_temps_parcours(self) -> dict:
        """
        Calcule le temps de parcours pour chaque véhicule sur chaque route.

        Returns:
            dict[str, dict[int, float]]: clé = nom de route, valeur = dict
                {id_vehicule: temps_parcours}
        """
        temps_routes = {}
        for route in self.reseau.routes:
            temps_vehicules = {}
            for v in route.vehicules:
                if v.vitesse > 0:
                    temps_vehicules[v.identifiant] = route.longueur / v.vitesse
                else:
                    temps_vehicules[v.identifiant] = 0
            temps_routes[route.nom] = temps_vehicules
        return temps_routes
