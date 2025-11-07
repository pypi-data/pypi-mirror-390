"""
Ce module contient la définition de la classe Export qui fournit des méthodes pour
exporter les résultats d'une simulation de trafic au format CSV et JSON.
"""

import csv
import json
import re


class Export:
    """
    Classe responsable de l'export des résultats d'une simulation.
    """

    def exporter_resultats_csv(self, historique: dict[int, dict[str, list[str]]]):
        """
        Exporte l'historique d'une simulation au format CSV.

        Args:
            historique (dict[int, dict[str, list[str]]]): état de chaque véhicule
            par route pour chaque tour.
        """
        fichier_csv = "resultats.csv"
        with open(fichier_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Tour", "Route", "ID_Vehicule", "Position", "Vitesse"])

            for tour, etat in historique.items():
                for route, vehicules in etat.items():
                    for v_str in vehicules:
                        v_info = self.parse_vehicule_info(v_str)
                        if v_info:
                            writer.writerow([
                                tour,
                                route,
                                v_info["id"],
                                v_info["position"],
                                v_info["vitesse"]
                            ])
        print(f"Résultats exportés avec succès dans {fichier_csv}.")

    def exporter_resultats_json(self, historique: dict[int, dict[str, list[str]]]):
        """
        Exporte l'historique d'une simulation au format JSON.

        Args:
            historique (dict[int, dict[str, list[str]]]): état de chaque véhicule
            par route pour chaque tour.
        """
        fichier_json = "historique.json"
        historique_modifie = {f"Tour {tour}": etat for tour, etat in historique.items()}
        with open(fichier_json, "w", encoding="utf-8") as f:
            json.dump(historique_modifie, f, indent=4, ensure_ascii=False)
        print(f"Résultats exportés avec succès dans {fichier_json}.")

    def parse_vehicule_info(self, s: str) -> dict | None:
        """
        Extrait ID, position et vitesse d'un véhicule à partir d'une chaîne.

        Args:
            s (str): chaîne de caractères au format "(ID:x, Pos:y, Vit:z)"

        Returns:
            dict | None: informations du véhicule {'id': int, 'position': float, 'vitesse': float}
        """
        match = re.match(r"\(ID:(\d+), Pos:(\d+), Vit:(\d+)\)", s.strip())
        if match:
            return {
                "id": int(match.group(1)),
                "position": float(match.group(2)),
                "vitesse": float(match.group(3))
            }
        return None
