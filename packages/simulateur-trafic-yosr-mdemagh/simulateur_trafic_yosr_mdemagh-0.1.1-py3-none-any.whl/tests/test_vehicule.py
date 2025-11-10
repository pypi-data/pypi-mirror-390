import pytest
from models.route import Route
from models.vehicule import Vehicule


def test_avancement_modifie_correctement_la_position():
    """L’avancement modifie correctement la position."""
    route = Route("R1", longueur=100, limV=50)
    vehicule = Vehicule(identifiant="V1", route=route, position=0, vitesse=10)

    vehicule.avancer(delta_t=2)  # avance de 10 * 2 = 20
    assert vehicule.position == 20, "La position du véhicule doit être 20 après 2 secondes à 10 m/s."


def test_vehicule_ne_depasse_pas_la_longueur_de_la_route():
    """Le véhicule ne dépasse pas la longueur de la route."""
    route = Route("R2", longueur=50, limV=30)
    vehicule = Vehicule(identifiant="V2", route=route, position=45, vitesse=10)

    vehicule.avancer(delta_t=1)  # devrait atteindre 55, mais limité à 50
    assert vehicule.position == 50, "La position ne doit pas dépasser la longueur de la route."


def test_changement_de_route_remet_position_a_zero():
    """Le changement de route remet la position à zéro."""
    route1 = Route("R1", longueur=100, limV=50)
    route2 = Route("R2", longueur=200, limV=80)
    vehicule = Vehicule(identifiant="V3", route=route1, position=80, vitesse=10)

    vehicule.changer_de_route(route2)
    assert vehicule.route == route2, "Le véhicule doit être sur la nouvelle route."
    assert vehicule.position == 0, "La position doit être remise à 0 après changement de route."
