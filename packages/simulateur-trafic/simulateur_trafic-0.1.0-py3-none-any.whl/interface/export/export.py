"""Fonctionnalités d'export des données issues de la simulation."""

from __future__ import annotations

import csv
import json
from typing import Sequence


class Export:
    """Gère la sérialisation des données du réseau simulé vers différents formats."""

    def __init__(self, reseau) -> None:
        """Enregistre le réseau dont les données seront exportées."""
        self.reseau = reseau

    def exporter_json(self, nom_fichier: str) -> None:
        """Exporte les routes et les véhicules du réseau dans un fichier JSON."""
        data = {
            "routes": [
                {"nom": route.nom, "longueur": route.longueur, "limite_vitesse": route.limite_vitesse}
                for route in self.reseau.routes
            ],
            "vehicules": [
                {"id": vehicule.identifiant, "vitesse": vehicule.vitesse, "position": vehicule.position}
                for vehicule in self.reseau.vehicules
            ],
        }

        with open(nom_fichier, "w", encoding="utf-8") as fichier:
            json.dump(data, fichier, indent=2)
        print(f"Données exportées vers {nom_fichier}")

    def exporter_csv(self, nom_fichier: str) -> None:
        """Exporte la liste des véhicules dans un fichier CSV."""
        with open(nom_fichier, "w", encoding="utf-8", newline="") as fichier:
            writer = csv.writer(fichier)
            writer.writerow(["ID", "Vitesse", "Position", "Route"])

            for vehicule in self.reseau.vehicules:
                route_nom = vehicule.route_actuelle.nom if vehicule.route_actuelle else "Aucune"
                writer.writerow([vehicule.identifiant, vehicule.vitesse, vehicule.position, route_nom])

        print(f"Véhicules exportés vers {nom_fichier}")

    def exporter_statistiques(self, statistiques: Sequence[dict], nom_fichier: str) -> None:
        """Sérialise la liste des statistiques calculées pendant la simulation."""
        with open(nom_fichier, "w", encoding="utf-8") as fichier:
            json.dump(statistiques, fichier, indent=2)
        print(f"Statistiques exportées vers {nom_fichier}")
