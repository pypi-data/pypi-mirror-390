"""
Ce module contient la définition de la classe Affichage qui fournit des méthodes pour
afficher et visualiser les statistiques et l'animation d'un réseau routier.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import re
import random
from numba import njit
from simulateur_trafic.inout.affichage_cython import calculer_position


class Affichage:
    """
    Représente une classe responsable de l'affichage et de la visualisation.
    """

    def afficher_stats(self, analyseur):
        """
        Affiche les statistiques enregistrées dans l'analyseur dans la console.

        Args:
            analyseur (Analyseur): objet qui contient les statistiques à afficher
        """
        for tour in sorted(analyseur.vitesse_moyenne.keys()):
            print(f"\n--- Statistiques Tour {tour} ---")
            print("Vitesses moyennes par route :")
            for route, vm in analyseur.vitesse_moyenne[tour].items():
                print(f"  {route} : {vm:.2f} unités/t")

            if analyseur.zones_congestion.get(tour):
                print("Zones de congestion détectées :")
                for route, infos in analyseur.zones_congestion[tour].items():
                    print(f"  {route} : {infos['vehicules']} véhicules (capacité {infos['capacite']:.1f})")
            else:
                print("Aucune congestion détectée.")

            print("Temps de parcours estimés (par véhicule) :")
            for route, temps in analyseur.temps_parcours[tour].items():
                for veh_id, tps in temps.items():
                    print(f"  {route} - Veh {veh_id} : {tps:.2f} unités de temps")

    def visualiser_resultats(self, historique_vitesse_moyenne):
        """
        Affiche l'évolution des vitesses moyennes de toutes les routes pour tous les tours.

        Args:
            historique_vitesse_moyenne (dict[int, dict[str, float]]): vitesses moyennes par route et par tour
        """
        plt.figure(figsize=(10, 6))
        routes = set()
        for stats in historique_vitesse_moyenne.values():
            routes.update(stats.keys())
        routes = sorted(routes)
        tours = sorted(historique_vitesse_moyenne.keys())

        for route in routes:
            evolution = [historique_vitesse_moyenne[tour].get(route, 0) for tour in tours]
            plt.plot(tours, evolution, marker="o", label=f"Route {route}")

        plt.title("Évolution des vitesses moyennes par route")
        plt.xlabel("Tours de simulation")
        plt.ylabel("Vitesse moyenne")
        plt.xticks(tours)
        plt.legend()
        plt.grid(True)
        plt.show()

    def parse_vehicule_info(self, s: str) -> dict | None:
        """
        Extrait ID, position et vitesse d'un véhicule à partir d'une chaîne.

        Args:
            s (str): chaîne au format "(ID:x, Pos:y, Vit:z)"

        Returns:
            dict ou None: informations du véhicule {'id': int, 'position': float, 'vitesse': float}
        """
        match = re.match(r"\(ID:(\d+), Pos:(\d+), Vit:(\d+)\)", s.strip())
        if match:
            return {
                "id": int(match.group(1)),
                "position": float(match.group(2)),
                "vitesse": float(match.group(3))
            }
        return None

    @staticmethod
    @njit
    def calculer_position_numba(x1, y1, x2, y2, L, pos):
        ratio = min(max(pos / L, 0.0), 1.0)
        x = x1 + ratio * (x2 - x1)
        y = y1 + ratio * (y2 - y1)
        return x, y
    def get_position(self, route_name: str, pos: float) -> tuple[float, float]:
        """
        Calcule la position (x, y) d'un véhicule sur la route en fonction de la distance parcourue.

        Args:
            route_name (str): nom de la route
            pos (float): distance parcourue

        Returns:
            tuple[float, float]: coordonnées (x, y) du véhicule
        """
        r = self.routes[route_name]
        """
        avec numba on fait :
        return Affichage.calculer_position_numba(r["start"][0], r["start"][1],
                                   r["end"][0], r["end"][1],
                                   r["longueur"], pos)
        """
        """return calculer_position(r["start"][0], r["start"][1],
                                    r["end"][0], r["end"][1],
                                    r["longueur"],pos)"""
        ratio = min(max(pos / r["longueur"], 0.0), 1.0)
        x = r["start"][0] + ratio * (r["start"][1] - r["start"][0])
        y = r["end"][0] + ratio * (r["end"][1]- r["end"][0])
        return x, y

    def animer_traffic(self, reseau, historique):
        """
        Affiche une animation du trafic à partir de l'historique donné.

        Args:
            reseau (ReseauRoutier): réseau à animer
            historique (dict[int, dict[str, list[str]]]): état des véhicules par route et par tour
        """
        self.routes = {
            route.nom: {"start": route.start, "end": route.end, "longueur": route.longueur}
            for route in reseau.routes
        }

        couleurs_possibles = ["red", "blue", "green", "orange", "purple", "cyan",
                              "magenta", "brown", "gray", "pink"]
        random.shuffle(couleurs_possibles)
        for i, name in enumerate(self.routes.keys()):
            self.routes[name]["color"] = couleurs_possibles[i % len(couleurs_possibles)]

        fig, ax = plt.subplots()
        for name, r in self.routes.items():
            xs, ys = zip(r["start"], r["end"])
            ax.plot(xs, ys, '-', linewidth=2, color=r["color"], label=name)
        ax.legend()
        veh_scatter = ax.scatter([], [], c=[], s=80)
        ax.set_title("Simulation du trafic (Historique des tours)")
        ax.axis('off')

        def init():
            veh_scatter.set_offsets(np.empty((0, 2)))
            return veh_scatter,

        def update(tour):
            data = historique[tour]
            coords, colors = [], []

            for route_name, veh_list in data.items():
                for v_str in veh_list:
                    v = self.parse_vehicule_info(v_str)
                    if v:
                        coords.append(self.get_position(route_name, v["position"]))
                        colors.append(self.routes[route_name]["color"])

            veh_scatter.set_offsets(coords)
            veh_scatter.set_color(colors)
            ax.set_title(f"Tour {tour}")
            return veh_scatter,

        ani = animation.FuncAnimation(
            fig, update, frames=sorted(historique.keys()),
            init_func=init, interval=1000, blit=True, repeat=False
        )

        plt.show()
