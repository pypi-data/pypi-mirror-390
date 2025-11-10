import pytest
from models.route import Route
from models.vehicule import Vehicule


def test_ajouter_vehicule():
    """Un véhicule ajouté à la route doit apparaître dans la liste des véhicules."""
    route = Route("R1", longueur=100, limV=50)
    vehicule = Vehicule(identifiant="V1", route=route, position=0, vitesse=10)

    route.ajouter_vehicule(vehicule)

    assert vehicule in route.vehicules, "Le véhicule doit être présent dans la liste des véhicules de la route."
    assert len(route.vehicules) == 1, "La route doit contenir exactement un véhicule après l'ajout."


def test_mettre_a_jour_vehicules_limite_vitesse():
    """La mise à jour des véhicules doit limiter leur vitesse à la vitesse maximale de la route."""
    route = Route("R2", longueur=200, limV=50)
    vehicule = Vehicule(identifiant="V2", route=route, position=0, vitesse=80)  # vitesse trop élevée
    route.ajouter_vehicule(vehicule)
    route.mettre_a_jour_vehicules(delta_t=1)
    assert vehicule.vitesse == 50, "La vitesse du véhicule doit être limitée à la vitesse maximale de la route."


def test_mettre_a_jour_vehicules_fait_avancer():
    """La mise à jour des véhicules doit faire avancer chaque véhicule."""
    route = Route("R3", longueur=100, limV=60)
    vehicule = Vehicule(identifiant="V3", route=route, position=10, vitesse=30)
    route.ajouter_vehicule(vehicule)
    route.mettre_a_jour_vehicules(delta_t=2)  # avance de 30 * 2 = 60
    assert vehicule.position == 70, "Le véhicule doit avoir avancé de 60 unités après la mise à jour."


def test_mettre_a_jour_vehicules_limite_longueur_route():
    """Un véhicule ne doit pas dépasser la longueur maximale de la route après mise à jour."""
    route = Route("R4", longueur=100, limV=60)
    vehicule = Vehicule(identifiant="V4", route=route, position=90, vitesse=20)
    route.ajouter_vehicule(vehicule)
    route.mettre_a_jour_vehicules(delta_t=1)  # essaie d'aller à 110
    assert vehicule.position == 100, "La position du véhicule doit être limitée à la fin de la route."
