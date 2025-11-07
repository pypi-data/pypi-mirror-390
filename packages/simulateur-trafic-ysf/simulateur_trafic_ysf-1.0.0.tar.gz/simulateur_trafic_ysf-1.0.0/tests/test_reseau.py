"""
Tests unitaires pour la classe ReseauRoutier.
"""

import pytest
from simulateur_trafic.models.reseau import ReseauRoutier
from simulateur_trafic.models.route import Route
from simulateur_trafic.models.vehicule import Vehicule


def test_reseau_creation():
    """Test la création d'un réseau."""
    reseau = ReseauRoutier()
    assert len(reseau.routes) == 0


def test_reseau_ajouter_route(reseau_simple, route_simple):
    """Test l'ajout d'une route au réseau."""
    assert route_simple.nom in reseau_simple.routes
    assert reseau_simple.get_route(route_simple.nom) == route_simple


def test_reseau_mise_a_jour_ensemble_routes(reseau_simple):
    """Test la mise à jour de l'ensemble des routes."""
    route = reseau_simple.get_route("A1")
    vehicule = route.vehicules[0]
    position_initiale = vehicule.position
    
    reseau_simple.mettre_a_jour(delta_t=10)
    
    assert vehicule.position > position_initiale


def test_reseau_get_route_inexistante():
    """Test la récupération d'une route inexistante."""
    reseau = ReseauRoutier()
    assert reseau.get_route("Inexistante") is None


def test_reseau_nombre_total_vehicules(reseau_simple):
    """Test le calcul du nombre total de véhicules."""
    assert reseau_simple.get_nombre_total_vehicules() == 1


def test_reseau_ajouter_route_dupliquee():
    """Test qu'ajouter une route dupliquée lève une exception."""
    reseau = ReseauRoutier()
    route1 = Route("A1", longueur=1000, limite_vitesse=30)
    route2 = Route("A1", longueur=2000, limite_vitesse=25)
    
    reseau.ajouter_route(route1)
    
    with pytest.raises(ValueError, match="existe déjà"):
        reseau.ajouter_route(route2)

