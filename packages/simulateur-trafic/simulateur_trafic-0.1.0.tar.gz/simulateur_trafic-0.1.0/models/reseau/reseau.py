"""Entités et logique associées au réseau routier simulé."""

from __future__ import annotations

from typing import Any, Dict, List

from core.exceptions import RouteNotFoundError, VehicleAlreadyPresentError


class ReseauRoutier:
    """Représente le réseau routier composé de routes, intersections et véhicules."""

    def __init__(self) -> None:
        """Initialise les collections représentant l'état du réseau."""
        self.routes: List["Route"] = []
        self.intersections: List[Any] = []
        self.vehicules: List["Vehicule"] = []

    def ajouter_route(self, route: "Route") -> None:
        """Ajoute une route au réseau."""
        self.routes.append(route)

    def ajouter_intersection(self, intersection: Any) -> None:
        """Ajoute une intersection au réseau."""
        self.intersections.append(intersection)

    def ajouter_vehicule(self, vehicule: "Vehicule") -> None:
        """Référence un véhicule dans le réseau et la route associée."""
        if vehicule in self.vehicules:
            raise VehicleAlreadyPresentError(
                f"Le véhicule {vehicule.identifiant} est déjà enregistré dans le réseau."
            )
        route = vehicule.route_actuelle
        if route is None or route not in self.routes:
            raise RouteNotFoundError(
                "Impossible d'ajouter un véhicule sur une route inexistante dans le réseau."
            )
        route.ajouter_vehicule(vehicule)
        self.vehicules.append(vehicule)

    def mettre_a_jour_reseau(self) -> None:
        """Met à jour la position de tous les véhicules présents sur les routes."""
        for route in self.routes:
            route.mettre_a_jour_vehicules()

    def obtenir_etat_reseau(self) -> Dict[str, int]:
        """Retourne un instantané des éléments suivis dans le réseau."""
        return {
            "nombre_routes": len(self.routes),
            "nombre_intersections": len(self.intersections),
            "nombre_vehicules": len(self.vehicules),
        }
