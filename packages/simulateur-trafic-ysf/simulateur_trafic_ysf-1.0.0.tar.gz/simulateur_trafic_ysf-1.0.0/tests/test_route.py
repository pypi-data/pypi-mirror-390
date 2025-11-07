"""
Tests unitaires pour la classe Route.
"""

import pytest
from simulateur_trafic.models.route import Route
from simulateur_trafic.models.vehicule import Vehicule


def test_route_creation():
    """Test la création d'une route."""
    route = Route("A1", longueur=1000, limite_vitesse=30)
    assert route.nom == "A1"
    assert route.longueur == 1000
    assert route.limite_vitesse == 30
    assert len(route.vehicules) == 0


def test_route_ajouter_vehicule(route_simple):
    """Test l'ajout d'un véhicule à une route."""
    vehicule = Vehicule("V1", route=None, position=0, vitesse=10)
    route_simple.ajouter_vehicule(vehicule)
    assert vehicule in route_simple.vehicules
    assert vehicule.route == route_simple


def test_route_mise_a_jour_avance_vehicules(route_simple):
    """Test que la mise à jour avance les véhicules."""
    vehicule1 = Vehicule("V1", route=route_simple, position=0, vitesse=10)
    vehicule2 = Vehicule("V2", route=route_simple, position=100, vitesse=15)
    route_simple.ajouter_vehicule(vehicule1)
    route_simple.ajouter_vehicule(vehicule2)
    
    position1_initiale = vehicule1.position
    position2_initiale = vehicule2.position
    
    route_simple.mettre_a_jour_vehicules(delta_t=10)
    
    assert vehicule1.position > position1_initiale
    assert vehicule2.position > position2_initiale


def test_route_vitesse_moyenne(route_simple):
    """Test le calcul de la vitesse moyenne."""
    vehicule1 = Vehicule("V1", route=route_simple, position=0, vitesse=10)
    vehicule2 = Vehicule("V2", route=route_simple, position=100, vitesse=20)
    route_simple.ajouter_vehicule(vehicule1)
    route_simple.ajouter_vehicule(vehicule2)
    
    vitesse_moyenne = route_simple.get_vitesse_moyenne()
    assert vitesse_moyenne == 15.0  # (10 + 20) / 2


def test_route_vitesse_moyenne_route_vide(route_simple):
    """Test que la vitesse moyenne d'une route vide est 0."""
    assert route_simple.get_vitesse_moyenne() == 0.0


def test_route_longueur_nulle_raise_error():
    """Test qu'une longueur nulle lève une exception."""
    with pytest.raises(ValueError, match="longueur.*positive"):
        Route("A1", longueur=0, limite_vitesse=30)


def test_route_ajouter_vehicule_deja_present(route_simple):
    """Test qu'ajouter un véhicule déjà présent lève une exception."""
    vehicule = Vehicule("V1", route=route_simple, position=0, vitesse=10)
    route_simple.ajouter_vehicule(vehicule)
    
    with pytest.raises(ValueError, match="déjà sur cette route"):
        route_simple.ajouter_vehicule(vehicule)

