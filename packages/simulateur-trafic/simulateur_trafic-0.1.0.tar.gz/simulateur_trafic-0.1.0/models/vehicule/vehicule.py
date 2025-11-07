"""Spécifie le comportement d'un véhicule dans le réseau simulé."""

from __future__ import annotations

from typing import Optional

from core.exceptions import InvalidVehicleStateError


class Vehicule:
    """Modélise un véhicule se déplaçant sur une route."""

    def __init__(
        self,
        identifiant: str,
        position: float = 0,
        vitesse: float = 50,
        route_actuelle: Optional["Route"] = None,
    ) -> None:
        """Initialise un véhicule avec son état courant."""
        if vitesse < 0:
            raise InvalidVehicleStateError(
                f"La vitesse doit être positive pour le véhicule {identifiant}."
            )
        if position < 0:
            raise InvalidVehicleStateError(
                f"La position doit être positive pour le véhicule {identifiant}."
            )
        self.identifiant = identifiant
        self.position = position
        self.vitesse = vitesse
        self.route_actuelle = route_actuelle

    def avancer(self) -> None:
        """Fait progresser le véhicule le long de sa route actuelle."""
        if self.route_actuelle is not None:
            self.position += self.vitesse

    def changer_de_route(self, nouvelle_route: "Route") -> None:
        """Positionne le véhicule sur une nouvelle route et réinitialise la position."""
        if nouvelle_route is None:
            raise InvalidVehicleStateError(
                f"Le véhicule {self.identifiant} doit être associé à une route valide."
            )
        self.route_actuelle = nouvelle_route
        self.position = 0
