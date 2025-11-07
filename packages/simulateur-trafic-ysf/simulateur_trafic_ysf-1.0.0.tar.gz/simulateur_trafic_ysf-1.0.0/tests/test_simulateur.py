"""
Tests d'intégration pour le simulateur complet.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from simulateur_trafic.core.simulateur import Simulateur


def test_simulateur_initialisation_fichier_config():
    """Test l'initialisation du simulateur à partir d'un fichier de configuration."""
    # Créer un fichier de configuration temporaire
    config = {
        "routes": [
            {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
        ],
        "vehicules": [
            {"identifiant": "V1", "route": "A1", "position": 0, "vitesse": 10}
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_config = f.name
    
    try:
        simu = Simulateur(fichier_config=temp_config)
        assert simu.reseau is not None
        assert len(simu.reseau.get_toutes_les_routes()) == 1
        assert simu.reseau.get_nombre_total_vehicules() == 1
    finally:
        os.unlink(temp_config)


def test_simulateur_fichier_config_inexistant():
    """Test qu'un fichier de configuration inexistant lève une exception."""
    with pytest.raises(FileNotFoundError):
        Simulateur(fichier_config="fichier_inexistant.json")


def test_simulateur_lancer_simulation_plusieurs_tours():
    """Test l'exécution d'une simulation sur plusieurs tours sans erreur."""
    # Créer un fichier de configuration temporaire
    config = {
        "routes": [
            {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
        ],
        "vehicules": [
            {"identifiant": "V1", "route": "A1", "position": 0, "vitesse": 10}
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_config = f.name
    
    try:
        simu = Simulateur(fichier_config=temp_config)
        rapport = simu.lancer_simulation(n_tours=10, delta_t=60, afficher=False, exporter=False)
        
        assert rapport is not None
        assert 'vitesse_moyenne_globale' in rapport
        assert 'nombre_total_vehicules' in rapport
    finally:
        os.unlink(temp_config)


def test_simulateur_n_tours_invalide():
    """Test qu'un nombre de tours invalide lève une exception."""
    config = {
        "routes": [
            {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_config = f.name
    
    try:
        simu = Simulateur(fichier_config=temp_config)
        with pytest.raises(ValueError, match="tours doit être positif"):
            simu.lancer_simulation(n_tours=0, delta_t=60, afficher=False)
    finally:
        os.unlink(temp_config)

