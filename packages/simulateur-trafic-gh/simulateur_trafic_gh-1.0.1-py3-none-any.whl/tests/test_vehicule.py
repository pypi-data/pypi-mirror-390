import pytest
from models.vehicule import Vehicule
from models.route import Route


class TestVehicule:
    """Tests unitaires pour la classe Vehicule"""
    
    def test_creation_vehicule(self):
        """Test de la création d'un véhicule avec valeurs par défaut"""
        v = Vehicule("V1")
        assert v.id == "V1"
        assert v.position == 0.0
        assert v.vitesse == 0.0
        assert v.longueur == 4.0
        assert v.route is None
    
    def test_creation_vehicule_avec_parametres(self):
        """Test de la création d'un véhicule avec paramètres personnalisés"""
        v = Vehicule("V2", position=10.0, vitesse=20.0, longueur=5.0)
        assert v.id == "V2"
        assert v.position == 10.0
        assert v.vitesse == 20.0
        assert v.longueur == 5.0
    
    def test_avancer_modifie_position(self, vehicule_exemple):
        """Test que l'avancement modifie correctement la position"""
        position_initiale = vehicule_exemple.position
        vitesse = vehicule_exemple.vitesse
        delta_t = 2.0
        
        vehicule_exemple.avancer(delta_t)
        
        position_attendue = position_initiale + vitesse * delta_t
        assert vehicule_exemple.position == pytest.approx(position_attendue)
    
    def test_avancer_plusieurs_fois(self):
        """Test de plusieurs avancements successifs"""
        v = Vehicule("V1", position=0, vitesse=10)
        
        v.avancer(1.0)
        assert v.position == pytest.approx(10.0)
        
        v.avancer(1.0)
        assert v.position == pytest.approx(20.0)
        
        v.avancer(0.5)
        assert v.position == pytest.approx(25.0)
    
    def test_avancer_avec_vitesse_nulle(self):
        """Test qu'un véhicule à l'arrêt ne bouge pas"""
        v = Vehicule("V1", position=10, vitesse=0)
        v.avancer(5.0)
        assert v.position == 10.0
    
    def test_changement_de_route(self, route_simple):
        """Test du changement de route d'un véhicule"""
        v = Vehicule("V1", position=50, vitesse=10)
        route_ancienne = Route("R1", longueur=100, limite_vitesse=20)
        route_ancienne.ajouter_vehicule(v)
        
        # Vérification initiale
        assert v.route == route_ancienne
        assert v in route_ancienne.vehicules
        
        # Changement de route
        v.changer_de_route(route_simple, nouvelle_position=0.0)
        
        # Vérifications après changement
        assert v.route == route_simple
        assert v.position == 0.0
        assert v in route_simple.vehicules
        assert v not in route_ancienne.vehicules
    
    def test_changement_de_route_remet_position_zero(self):
        """Test que le changement de route remet la position à zéro"""
        route1 = Route("R1", longueur=100, limite_vitesse=20)
        route2 = Route("R2", longueur=200, limite_vitesse=30)
        
        v = Vehicule("V1", position=80, vitesse=15)
        route1.ajouter_vehicule(v)
        
        v.changer_de_route(route2, nouvelle_position=0.0)
        
        assert v.position == 0.0
        assert v.route == route2
    
    def test_changement_de_route_avec_position_personnalisee(self):
        """Test du changement de route avec une position personnalisée"""
        route1 = Route("R1", longueur=100, limite_vitesse=20)
        route2 = Route("R2", longueur=200, limite_vitesse=30)
        
        v = Vehicule("V1", position=80, vitesse=15)
        route1.ajouter_vehicule(v)
        
        v.changer_de_route(route2, nouvelle_position=25.0)
        
        assert v.position == 25.0
        assert v.route == route2
    
    def test_vehicule_sans_route_initiale(self):
        """Test du changement de route pour un véhicule sans route initiale"""
        route = Route("R1", longueur=100, limite_vitesse=20)
        v = Vehicule("V1", position=0, vitesse=10)
        
        assert v.route is None
        
        v.changer_de_route(route, nouvelle_position=10.0)
        
        assert v.route == route
        assert v.position == 10.0
        assert v in route.vehicules