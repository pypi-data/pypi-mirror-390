"""
Tests unitaires pour la classe Vehicule.
"""

import pytest
from simulateur_trafic.models.vehicule import Vehicule
from simulateur_trafic.models.route import Route


def test_vehicule_creation(route_simple):
    """Test la création d'un véhicule."""
    vehicule = Vehicule("V1", route=route_simple, position=0, vitesse=10)
    assert vehicule.identifiant == "V1"
    assert vehicule.position == 0
    assert vehicule.vitesse == 10
    assert vehicule.route == route_simple


def test_vehicule_avancement_modifie_position(vehicule_exemple):
    """Test que l'avancement modifie correctement la position."""
    position_initiale = vehicule_exemple.position
    vehicule_exemple.avancer(delta_t=10)  # 10 secondes
    assert vehicule_exemple.position > position_initiale
    assert vehicule_exemple.position == 100  # 10 m/s * 10 s = 100 m


def test_vehicule_ne_depasse_pas_longueur_route(route_simple):
    """Test que le véhicule ne dépasse pas la longueur de la route."""
    vehicule = Vehicule("V1", route=route_simple, position=0, vitesse=100)
    vehicule.avancer(delta_t=20)  # Devrait dépasser la route de 1000m
    assert vehicule.position == route_simple.longueur
    assert vehicule.position <= route_simple.longueur


def test_vehicule_changement_route_remet_position_zero(vehicule_exemple, route_simple):
    """Test que le changement de route remet la position à zéro."""
    vehicule_exemple.position = 500
    nouvelle_route = Route("A2", longueur=2000, limite_vitesse=25)
    vehicule_exemple.changer_de_route(nouvelle_route)
    assert vehicule_exemple.position == 0
    assert vehicule_exemple.route == nouvelle_route


def test_vehicule_vitesse_negative_raise_error(route_simple):
    """Test qu'une vitesse négative lève une exception."""
    with pytest.raises(ValueError, match="vitesse ne peut pas être négative"):
        Vehicule("V1", route=route_simple, position=0, vitesse=-10)


def test_vehicule_position_negative_raise_error(route_simple):
    """Test qu'une position négative lève une exception."""
    with pytest.raises(ValueError, match="position ne peut pas être négative"):
        Vehicule("V1", route=route_simple, position=-10, vitesse=10)


def test_vehicule_avancer_sans_route_raise_error():
    """Test qu'avancer sans route lève une exception."""
    vehicule = Vehicule("V1", route=None, position=0, vitesse=10)
    with pytest.raises(ValueError, match="doit être sur une route"):
        vehicule.avancer(delta_t=10)

