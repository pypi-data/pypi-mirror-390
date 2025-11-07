import pytest
from models.route import Route
from models.vehicule import Vehicule


class TestRoute:
    """Tests unitaires pour la classe Route"""
    
    def test_creation_route(self):
        """Test de la création d'une route"""
        route = Route("A1", longueur=1000, limite_vitesse=30)
        assert route.nom == "A1"
        assert route.longueur == 1000.0
        assert route.limite_vitesse == 30.0
        assert len(route.vehicules) == 0
    
    def test_ajout_vehicule_simple(self, route_simple):
        """Test de l'ajout d'un véhicule à une route"""
        v = Vehicule("V1", position=0, vitesse=10)
        route_simple.ajouter_vehicule(v)
        
        assert v in route_simple.vehicules
        assert v.route == route_simple
        assert len(route_simple.vehicules) == 1
    
    def test_ajout_vehicule_double(self, route_simple):
        """Test qu'un véhicule ne peut pas être ajouté deux fois"""
        v = Vehicule("V1", position=0, vitesse=10)
        route_simple.ajouter_vehicule(v)
        route_simple.ajouter_vehicule(v)
        
        assert len(route_simple.vehicules) == 1
    
    def test_ajout_plusieurs_vehicules(self, route_simple):
        """Test de l'ajout de plusieurs véhicules"""
        v1 = Vehicule("V1", position=0, vitesse=10)
        v2 = Vehicule("V2", position=10, vitesse=15)
        v3 = Vehicule("V3", position=20, vitesse=20)
        
        route_simple.ajouter_vehicule(v1)
        route_simple.ajouter_vehicule(v2)
        route_simple.ajouter_vehicule(v3)
        
        assert len(route_simple.vehicules) == 3
        assert v1 in route_simple.vehicules
        assert v2 in route_simple.vehicules
        assert v3 in route_simple.vehicules
    
    def test_retirer_vehicule(self, route_simple):
        """Test du retrait d'un véhicule d'une route"""
        v = Vehicule("V1", position=0, vitesse=10)
        route_simple.ajouter_vehicule(v)
        
        assert v in route_simple.vehicules
        
        route_simple.retirer_vehicule(v)
        
        assert v not in route_simple.vehicules
        assert v.route is None
    
    def test_retirer_vehicule_inexistant(self, route_simple):
        """Test du retrait d'un véhicule qui n'est pas sur la route"""
        v = Vehicule("V1", position=0, vitesse=10)
        
        # Ne devrait pas lever d'erreur
        route_simple.retirer_vehicule(v)
        assert len(route_simple.vehicules) == 0
    
    def test_mise_a_jour_avance_vehicules(self, route_simple):
        """Test que la mise à jour avance les véhicules"""
        v1 = Vehicule("V1", position=0, vitesse=10)
        v2 = Vehicule("V2", position=0, vitesse=20)
        
        route_simple.ajouter_vehicule(v1)
        route_simple.ajouter_vehicule(v2)
        
        route_simple.mettre_a_jour_vehicules(delta_t=1.0)
        
        assert v1.position == pytest.approx(10.0)
        assert v2.position == pytest.approx(20.0)
    
    def test_mise_a_jour_applique_limite_vitesse(self, route_simple):
        """Test que la mise à jour applique la limite de vitesse"""
        # route_simple a une limite de 30 m/s
        v = Vehicule("V1", position=0, vitesse=50)
        route_simple.ajouter_vehicule(v)
        
        route_simple.mettre_a_jour_vehicules(delta_t=1.0)
        
        assert v.vitesse == route_simple.limite_vitesse
        # La position devrait être basée sur la vitesse limitée
        assert v.position == pytest.approx(30.0)
    
    def test_mise_a_jour_retire_vehicules_sortis(self, route_courte):
        """Test que les véhicules sortis de la route sont retirés"""
        # route_courte a une longueur de 50 m
        v = Vehicule("V1", position=45, vitesse=10)
        route_courte.ajouter_vehicule(v)
        
        assert len(route_courte.vehicules) == 1
        
        # Après 1 seconde, le véhicule sera à position 55 > 50
        route_courte.mettre_a_jour_vehicules(delta_t=1.0)
        
        assert len(route_courte.vehicules) == 0
        assert v.route is None
    
    def test_mise_a_jour_trie_vehicules(self, route_simple):
        """Test que les véhicules sont triés par position"""
        v1 = Vehicule("V1", position=50, vitesse=5)
        v2 = Vehicule("V2", position=10, vitesse=5)
        v3 = Vehicule("V3", position=30, vitesse=5)
        
        # Ajouter dans le désordre
        route_simple.ajouter_vehicule(v1)
        route_simple.ajouter_vehicule(v2)
        route_simple.ajouter_vehicule(v3)
        
        route_simple.mettre_a_jour_vehicules(delta_t=1.0)
        
        # Vérifier l'ordre après mise à jour
        assert route_simple.vehicules[0] == v2
        assert route_simple.vehicules[1] == v3
        assert route_simple.vehicules[2] == v1
    
    def test_mise_a_jour_plusieurs_tours(self, route_simple):
        """Test de plusieurs mises à jour successives"""
        v = Vehicule("V1", position=0, vitesse=10)
        route_simple.ajouter_vehicule(v)
        
        for i in range(5):
            route_simple.mettre_a_jour_vehicules(delta_t=1.0)
        
        assert v.position == pytest.approx(50.0)
    
    def test_vehicule_reste_sur_route(self, route_simple):
        """Test qu'un véhicule reste sur la route s'il ne dépasse pas"""
        v = Vehicule("V1", position=980, vitesse=10)
        route_simple.ajouter_vehicule(v)
        
        route_simple.mettre_a_jour_vehicules(delta_t=1.0)
        
        assert v in route_simple.vehicules
        assert v.position == pytest.approx(990.0)
    
    def test_vehicule_exactement_a_la_limite(self, route_simple):
        """Test d'un véhicule qui arrive exactement à la fin de la route"""
        v = Vehicule("V1", position=990, vitesse=10)
        route_simple.ajouter_vehicule(v)
        
        route_simple.mettre_a_jour_vehicules(delta_t=1.0)
        
        # Position = 1000, ne dépasse pas la longueur
        assert v in route_simple.vehicules
        assert v.position == pytest.approx(1000.0)