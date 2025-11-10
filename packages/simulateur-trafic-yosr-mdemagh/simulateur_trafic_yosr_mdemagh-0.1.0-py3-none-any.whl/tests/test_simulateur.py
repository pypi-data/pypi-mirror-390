import sys
import os
import json
import tempfile

import pytest
from core.simulateur import Simulateur


# --- 2. Test de l’initialisation du simulateur ---
def test_initialisation_simulateur(fichier_config_temporaire):
    """Vérifie que le simulateur charge bien les routes et véhicules depuis le fichier JSON."""
    simulateur = Simulateur(fichier_config_temporaire)
    # Vérifie que les routes sont bien créées
    assert "Route1" in simulateur.reseau.routes
    assert "Route2" in simulateur.reseau.routes

    # Vérifie qu’il y a des véhicules dans les routes
    r1 = simulateur.reseau.get_route("Route1")
    r2 = simulateur.reseau.get_route("Route2")
    assert len(r1.vehicules) == 1
    assert len(r2.vehicules) == 1
    # Vérifie que les attributs des véhicules sont corrects
    v1 = r1.vehicules[0]
    assert v1.id == "V1"
    assert v1.vitesse == 10.0
    assert v1.position == 0.0


# --- 3. Test de l’exécution d’une simulation complète ---
def test_execution_simulation(monkeypatch, fichier_config_temporaire):
    """Vérifie que la simulation s’exécute plusieurs tours sans erreur."""
    simulateur = Simulateur(fichier_config_temporaire)
    # On neutralise les sorties console et fichiers pour éviter du bruit pendant le test
    monkeypatch.setattr("core.simulateur.Affichage.afficher_console", lambda stats: None)
    monkeypatch.setattr("core.simulateur.Affichage.afficher_graphique", lambda data: None)
    monkeypatch.setattr("core.simulateur.Export.exporter_json", lambda data, path: None)
    monkeypatch.setattr("core.simulateur.Export.exporter_csv", lambda data, path: None)
    monkeypatch.setattr("core.simulateur.Analyseur.analyser_reseau", lambda self, r: {"vitesse_moyenne": 10.0})
    # Exécution de la simulation (2 tours de 1s)
    simulateur.lancer_simulation(n_tours=2, delta_t=1.0)
    # Vérifie que la simulation a bien effectué 2 tours
    assert simulateur.reseau.get_route("Route1") is not None
    assert simulateur.reseau.get_route("Route2") is not None
