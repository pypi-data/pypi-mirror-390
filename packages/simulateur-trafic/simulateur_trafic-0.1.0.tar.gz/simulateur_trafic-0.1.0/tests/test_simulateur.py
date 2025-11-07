import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.exceptions import (
    ConfigurationFileNotFoundError,
    DivisionByZeroAnalysisError,
    InvalidSimulationParameterError,
    InvalidVehicleStateError,
    MissingDataError,
    RouteCapacityError,
    RouteNotFoundError,
    VehicleAlreadyPresentError,
)
from core.analyseur import Analyseur
from core.simulateur import Simulateur
from models.reseau import ReseauRoutier
from models.route import Route
from models.vehicule import Vehicule


@pytest.fixture
def route_simple():
    return Route("A1", longueur=1000, limite_vitesse=30, capacite_max=2)


@pytest.fixture
def vehicule_exemple(route_simple):
    vehicule = Vehicule("V1", vitesse=10, route_actuelle=route_simple)
    route_simple.ajouter_vehicule(vehicule)
    return vehicule


@pytest.fixture
def reseau_simple(route_simple, vehicule_exemple):
    reseau = ReseauRoutier()
    reseau.ajouter_route(route_simple)
    reseau.ajouter_vehicule(vehicule_exemple)
    return reseau


def test_route_ajout_vehicule_duplique_leve_exception(route_simple, vehicule_exemple):
    with pytest.raises(VehicleAlreadyPresentError):
        route_simple.ajouter_vehicule(vehicule_exemple)


def test_route_capacite_max_leve_exception(route_simple):
    route_simple.ajouter_vehicule(Vehicule("V2", vitesse=20, route_actuelle=route_simple))
    route_simple.ajouter_vehicule(Vehicule("V3", vitesse=25, route_actuelle=route_simple))
    with pytest.raises(RouteCapacityError):
        route_simple.ajouter_vehicule(Vehicule("V4", vitesse=30, route_actuelle=route_simple))


def test_route_met_a_jour_vehicules(route_simple, vehicule_exemple):
    position_initiale = vehicule_exemple.position

    route_simple.mettre_a_jour_vehicules()

    assert vehicule_exemple.position == position_initiale + vehicule_exemple.vitesse


def test_vehicule_negative_speed_leve_exception(route_simple):
    with pytest.raises(InvalidVehicleStateError):
        Vehicule("V4", vitesse=-10, route_actuelle=route_simple)


def test_vehicule_avancer_depasse_longueur_leve_exception(route_simple):
    vehicule = Vehicule("V5", position=995, vitesse=10, route_actuelle=route_simple)
    route_simple.ajouter_vehicule(vehicule)
    with pytest.raises(InvalidVehicleStateError):
        vehicule.avancer()


def test_vehicule_ne_bouge_pas_sans_route():
    vehicule = Vehicule("V6", vitesse=15)
    vehicule.avancer()

    assert vehicule.position == 0


def test_changer_de_route_reinitialise_position(route_simple):
    nouvelle_route = Route("B1", longueur=500, limite_vitesse=50)
    vehicule = Vehicule("V7", position=100, vitesse=25, route_actuelle=route_simple)

    vehicule.changer_de_route(nouvelle_route)

    assert vehicule.route_actuelle is nouvelle_route
    assert vehicule.position == 0


def test_reseau_met_a_jour_reseau(reseau_simple, vehicule_exemple):
    position_initiale = vehicule_exemple.position

    reseau_simple.mettre_a_jour_reseau()

    assert vehicule_exemple.position == position_initiale + vehicule_exemple.vitesse


def test_reseau_etat_compte_elements(reseau_simple):
    reseau_simple.ajouter_intersection({"id": "I1"})

    etat = reseau_simple.obtenir_etat_reseau()

    assert etat["nombre_routes"] == 1
    assert etat["nombre_intersections"] == 1
    assert etat["nombre_vehicules"] == 1


def test_analyseur_vitesse_moyenne_sans_donnees(reseau_simple):
    reseau_simple.vehicules.clear()
    analyseur = Analyseur(reseau_simple)
    with pytest.raises(MissingDataError):
        analyseur.calculer_vitesses_moyennes()


def test_analyseur_temps_parcours_zero_limite(route_simple):
    route_simple.limite_vitesse = 0
    analyseur = Analyseur(ReseauRoutier())
    analyseur.reseau.routes.append(route_simple)
    with pytest.raises(DivisionByZeroAnalysisError):
        analyseur.calculer_temps_parcours(route_simple)


def test_simulateur_config_introuvable():
    with pytest.raises(ConfigurationFileNotFoundError):
        Simulateur(fichier_config="fichier_inexistant.json")


def test_simulateur_lancer_simulation_param_invalide(reseau_simple):
    simulateur = Simulateur()
    simulateur.reseau = reseau_simple
    with pytest.raises(InvalidSimulationParameterError):
        simulateur.lancer_simulation(n_tours=0, delta_t=60)


def test_simulateur_charger_config_route_inexistante(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """{
            "routes": [],
            "vehicules": [
                {"identifiant": "V8", "position": 0, "vitesse": 10, "route": "Inconnue"}
            ]
        }""",
        encoding="utf-8",
    )

    simulateur = Simulateur()
    with pytest.raises(RouteNotFoundError):
        simulateur.charger_config(str(config_path))


def test_simulateur_charger_config_route_valide(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """{
            "routes": [
                {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
            ],
            "vehicules": [
                {"identifiant": "V9", "position": 0, "vitesse": 10, "route": "A1"}
            ]
        }""",
        encoding="utf-8",
    )

    simulateur = Simulateur()
    simulateur.charger_config(str(config_path))
    assert len(simulateur.reseau.vehicules) == 1
