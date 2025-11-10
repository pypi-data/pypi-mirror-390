import pytest
from models.reseau import ReseauRoutier
from models.route import Route
from models.vehicule import Vehicule


def test_ajout_route():
    """Vérifie qu'une route peut être ajoutée au réseau et retrouvée."""
    reseau = ReseauRoutier()
    route = Route("Route1", 100.0,limV=10)  # nom et longueur
    reseau.ajouter_route(route)
    assert "Route1" in reseau.routes
    assert reseau.get_route("Route1") == route


def test_mettre_a_jour_routes():
    """Vérifie que la mise à jour du réseau appelle bien la méthode sur chaque route."""
    reseau = ReseauRoutier()

    # Création de deux routes
    route1 = Route("R1", 100.0,limV=10)
    route2 = Route("R2", 200.0,limV=20)

    # Création de véhicules pour vérifier leur mouvement après mise à jour
    v1 = Vehicule("V1", route1, position=0.0, vitesse=10.0)
    v2 = Vehicule("V2", route2, position=50.0, vitesse=20.0)

    route1.ajouter_vehicule(v1)
    route2.ajouter_vehicule(v2)

    reseau.ajouter_route(route1)
    reseau.ajouter_route(route2)

    # On met à jour le réseau sur 1 seconde
    reseau.mettre_a_jour(1.0)

    # Vérifie que la position des véhicules a bien changé
    assert v1.position == 10.0  # 0 + 10*1
    assert v2.position == 70.0  # 50 + 20*1

    # Vérifie que les routes sont bien dans le réseau
    assert "R1" in reseau.routes
    assert "R2" in reseau.routes
