"""
Ce module contient la définition de la classe Simulateur qui permet de gérer la simulation
du trafic sur un réseau routier.
"""

import json
from simulateur_trafic.models.reseau import ReseauRoutier
from simulateur_trafic.core.analyseur import Analyseur
from simulateur_trafic.inout.export import Export
from simulateur_trafic.inout.affichage import Affichage


class Simulateur:
    """
    Représente un simulateur d'un réseau routier.

    Attributes:
        reseau (ReseauRoutier): le réseau routier à simuler
        stats (dict): dictionnaire contenant des statistiques de simulation
            - "tours_effectues" (int): nombre de tours effectués
            - "historique" (dict[int, dict[str, list[str]]]): états des rues par tour
        analyseur (Analyseur): objet pour analyser le réseau
        export (Export): objet pour l'exportation des données
        affichage (Affichage): objet pour afficher les résultats dans la console et graphiques
    """

    def __init__(self, fichier_config: str):
        """
        Initialise le simulateur avec un fichier de configuration JSON.

        Args:
            fichier_config (str): chemin vers le fichier JSON contenant la configuration
                du réseau routier (routes et intersections)
        """
        try:
            with open(fichier_config, "r", encoding="utf-8") as f:
                config = json.load(f)

            self.reseau = ReseauRoutier.from_json(config)
            self.stats = {
                "tours_effectues": 0,
                "historique": {}
            }
            self.analyseur = Analyseur(self.reseau)
            self.export = Export()
            self.affichage = Affichage()

        except FileNotFoundError:
            print("Erreur : fichier de configuration manquant.")
            return
        except json.JSONDecodeError:
            print("Erreur : fichier de configuration invalide.")
            return

    def lancer_simulation(self, n_tours: int, delta_t: float, afficher: bool = True, exporter: bool = True):
        """
        Lance la simulation du réseau routier pour un nombre de tours donné.

        Pour chaque tour, la méthode :
        - Fait évoluer les véhicules sur chaque route
        - Met à jour les statistiques ("tours_effectues","historique")
        - Met à jour les attributs de l'objet Analyseur
        - Affiche les résultats intermédiaires

        Args:
            n_tours (int): nombre total de tours à simuler
            delta_t (float): durée d'un tour en unité de temps
            afficher (bool, optional): si True, affiche les statistiques et visualisations
            exporter (bool, optional): si True, exporte les résultats en CSV et JSON
        """
        try:
            if n_tours <= 0:
                raise ValueError("Le nombre de tours doit être strictement positif.")
            if delta_t <= 0:
                raise ValueError("Le delta_t doit être strictement positif.")

            for tour in range(1, n_tours + 1):
                self.reseau.simuler(delta_t)

                self.stats["tours_effectues"] += 1
                etat = {}
                for route in self.reseau.routes:
                    etat[route.nom] = [
                        f"(ID:{v.identifiant}, Pos:{v.position}, Vit:{v.vitesse})"
                        for v in route.vehicules
                    ]
                self.stats["historique"][tour] = etat
                self.analyseur.update_stats(tour)

            if afficher:
                self.affichage.afficher_stats(self.analyseur)
                self.affichage.visualiser_resultats(self.analyseur.vitesse_moyenne)
                self.affichage.animer_traffic(self.reseau, self.stats["historique"])

            if exporter:
                self.export.exporter_resultats_csv(self.stats["historique"])
                self.export.exporter_resultats_json(self.stats["historique"])
        except ValueError as e:
            print(f"Erreur de paramètres : {e}")
