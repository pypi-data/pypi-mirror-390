import pytest
from models.route import Route
from models.vehicule import Vehicule
from models.reseau import ReseauRoutier


@pytest.fixture
def route_simple():
    """Fixture pour créer une route simple de test"""
    return Route("A1", longueur=1000, limite_vitesse=30)


@pytest.fixture
def route_courte():
    """Fixture pour créer une route courte pour tester les sorties"""
    return Route("R1", longueur=50, limite_vitesse=20)


@pytest.fixture
def vehicule_exemple(route_simple):
    """Fixture pour créer un véhicule de test"""
    return Vehicule("V1", route=route_simple, position=0, vitesse=10)


@pytest.fixture
def vehicule_rapide():
    """Fixture pour créer un véhicule rapide sans route"""
    return Vehicule("V2", position=0, vitesse=50)


@pytest.fixture
def reseau_simple(route_simple, vehicule_exemple):
    """Fixture pour créer un réseau simple avec une route et un véhicule"""
    reseau = ReseauRoutier()
    reseau.ajouter_route(route_simple)
    route_simple.ajouter_vehicule(vehicule_exemple)
    return reseau


@pytest.fixture
def reseau_multi_routes():
    """Fixture pour créer un réseau avec plusieurs routes"""
    reseau = ReseauRoutier()
    
    route1 = Route("A-B", longueur=100, limite_vitesse=20)
    route2 = Route("B-C", longueur=80, limite_vitesse=15)
    route3 = Route("C-D", longueur=200, limite_vitesse=35)
    
    reseau.ajouter_route(route1)
    reseau.ajouter_route(route2)
    reseau.ajouter_route(route3)
    
    return reseau