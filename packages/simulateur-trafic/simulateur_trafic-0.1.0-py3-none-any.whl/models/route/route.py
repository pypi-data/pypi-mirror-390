"""Définition d'une route utilisée dans le réseau simulé."""

from __future__ import annotations

from typing import List, Optional

from core.exceptions import RouteCapacityError, VehicleAlreadyPresentError


class Route:
    """Représente un tronçon de route sur lequel circulent des véhicules."""

    def __init__(
        self,
        nom: str,
        longueur: float,
        limite_vitesse: float,
        capacite_max: Optional[int] = None,
    ) -> None:
        """Construit une route avec ses caractéristiques principales."""
        self.nom = nom
        self.longueur = longueur
        self.limite_vitesse = limite_vitesse
        self.capacite_max = capacite_max
        self.vehicules_presents: List["Vehicule"] = []

    def ajouter_vehicule(self, vehicule: "Vehicule") -> None:
        """Ajoute un véhicule à la route si celui-ci n'est pas déjà présent."""
        if vehicule in self.vehicules_presents:
            raise VehicleAlreadyPresentError(
                f"Le véhicule {vehicule.identifiant} est déjà sur la route {self.nom}."
            )
        if self.capacite_max is not None and len(self.vehicules_presents) >= self.capacite_max:
            raise RouteCapacityError(
                f"La route {self.nom} a atteint sa capacité maximale ({self.capacite_max})."
            )
        self.vehicules_presents.append(vehicule)
        vehicule.route_actuelle = self

    def mettre_a_jour_vehicules(self) -> None:
        """Demande à chaque véhicule présent de mettre à jour sa position."""
        for vehicule in self.vehicules_presents:
            vehicule.avancer()
