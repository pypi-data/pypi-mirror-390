"""Simulation logic for loading a traffic network and running it."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from core.exceptions import (
    ConfigurationError,
    ConfigurationFileNotFoundError,
    ConfigurationFormatError,
    InvalidSimulationParameterError,
)
from models.reseau import ReseauRoutier
from models.route import Route
from models.vehicule import Vehicule


class Simulateur:
    """Pilote la simulation d'un réseau routier et centralise les statistiques."""

    def __init__(self, fichier_config: Optional[str] = None) -> None:
        """Crée un simulateur et charge éventuellement une configuration initiale.

        Parameters
        ----------
        fichier_config: Optional[str]
            Chemin vers un fichier JSON décrivant les routes et les véhicules
            à instancier avant de démarrer la simulation. Si ``None`` est
            fourni, le réseau reste vide.
        """
        self.reseau = ReseauRoutier()
        self.statistiques: list[Dict[str, Any]] = []
        self.tour_actuel = 0

        if fichier_config:
            self.charger_config(fichier_config)

    def charger_config(self, fichier_config: str) -> None:
        """Initialise le réseau routier à partir d'un fichier de configuration.

        Le fichier doit contenir deux listes ``routes`` et ``vehicules`` décrivant
        respectivement les tronçons routiers et les véhicules à ajouter.
        """
        try:
            with open(fichier_config, "r", encoding="utf-8") as fichier:
                config: Dict[str, Any] = json.load(fichier)
        except FileNotFoundError as exc:
            raise ConfigurationFileNotFoundError(
                f"Fichier de configuration introuvable: {fichier_config}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise ConfigurationFormatError(
                f"Format JSON invalide dans {fichier_config}: {exc}"
            ) from exc

        try:
            routes_config = config["routes"]
            vehicules_config = config["vehicules"]
        except KeyError as exc:
            raise ConfigurationFormatError(
                "Le fichier de configuration doit contenir les clés 'routes' et 'vehicules'."
            ) from exc

        if not isinstance(routes_config, list) or not isinstance(
            vehicules_config, list
        ):
            raise ConfigurationFormatError(
                "Les sections 'routes' et 'vehicules' doivent être des listes."
            )

        for route_data in routes_config:
            try:
                nom = route_data["nom"]
                longueur = route_data["longueur"]
                limite_vitesse = route_data["limite_vitesse"]
            except KeyError as exc:
                raise ConfigurationFormatError(
                    "Chaque route doit définir 'nom', 'longueur' et 'limite_vitesse'."
                ) from exc
            route = Route(nom, longueur, limite_vitesse)
            self.reseau.ajouter_route(route)

        for vehicule_data in vehicules_config:
            try:
                identifiant = vehicule_data["identifiant"]
                position = vehicule_data["position"]
                vitesse = vehicule_data["vitesse"]
                route_nom = vehicule_data["route"]
            except KeyError as exc:
                raise ConfigurationFormatError(
                    "Chaque véhicule doit définir 'identifiant', 'position', 'vitesse' et 'route'."
                ) from exc

            vehicule = Vehicule(identifiant, position, vitesse)
            try:
                route = next(
                    troncon
                    for troncon in self.reseau.routes
                    if troncon.nom == route_nom
                )
            except StopIteration as exc:
                raise ConfigurationFormatError(
                    f"Route {route_nom} introuvable pour le véhicule {identifiant}."
                ) from exc
            vehicule.changer_de_route(route)
            self.reseau.ajouter_vehicule(vehicule)

    def lancer_simulation(self, n_tours: int, delta_t: int) -> None:
        """Exécute la simulation sur un nombre de tours fixé.

        Parameters
        ----------
        n_tours: int
            Nombre d'itérations à exécuter.
        delta_t: int
            Pas de temps utilisé pour chaque itération (réservé pour de
            potentielles évolutions du modèle).
        """
        if n_tours <= 0 or delta_t <= 0:
            raise InvalidSimulationParameterError(
                "Le nombre de tours et le pas de temps doivent être strictement positifs."
            )

        for tour in range(n_tours):
            self.tour_actuel = tour

            self.reseau.mettre_a_jour_reseau()

            statistiques_tour = {"tour": tour, "vehicules": len(self.reseau.vehicules)}
            self.statistiques.append(statistiques_tour)

            print(f"Tour {tour}: {len(self.reseau.vehicules)} véhicules")
