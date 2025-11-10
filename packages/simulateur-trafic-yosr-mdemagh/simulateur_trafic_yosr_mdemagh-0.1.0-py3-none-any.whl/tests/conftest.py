import pytest
import tempfile
import json
import os

@pytest.fixture
def fichier_config_temporaire():
    """Crée un fichier JSON temporaire représentant une configuration de simulation."""
    config = {
        "routes": [
            {"nom": "Route1", "longueur": 100.0, "limite_vitesse": 20.0},
            {"nom": "Route2", "longueur": 200.0, "limite_vitesse": 30.0}
        ],
        "vehicules": [
            {"id": "V1", "route": "Route1", "position": 0.0, "vitesse": 10.0},
            {"id": "V2", "route": "Route2", "position": 50.0, "vitesse": 15.0}
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        json.dump(config, tmp)
        tmp_path = tmp.name

    yield tmp_path  # On retourne le chemin pour le test
    os.remove(tmp_path)  # Nettoyage après le test
