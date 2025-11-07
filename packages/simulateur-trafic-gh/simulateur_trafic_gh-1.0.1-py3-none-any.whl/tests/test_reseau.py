import pytest
from models.reseau import ReseauRoutier
from models.route import Route
from models.vehicule import Vehicule


class TestReseauRoutier:
    """Tests unitaires pour la classe ReseauRoutier"""
    
    def test_creation_reseau(self):
        """Test de la création d'un réseau vide"""
        reseau = ReseauRoutier()
        assert len(reseau.routes) == 0
        assert isinstance(reseau.routes, dict)
    
    def test_ajouter_route(self):
        """Test de l'ajout d'une route au réseau"""
        reseau = ReseauRoutier()
        route = Route("A1", longueur=1000, limite_vitesse=30)
        
        reseau.ajouter_route(route)
        
        assert "A1" in reseau.routes
        assert reseau.routes["A1"] == route
        assert len(reseau.routes) == 1
    
    def test_ajouter_plusieurs_routes(self, reseau_multi_routes):
        """Test de l'ajout de plusieurs routes"""
        assert len(reseau_multi_routes.routes) == 3
        assert "A-B" in reseau_multi_routes.routes
        assert "B-C" in reseau_multi_routes.routes
        assert "C-D" in reseau_multi_routes.routes
    
    def test_ajouter_vehicule_route_existante(self):
        """Test de l'ajout d'un véhicule sur une route existante"""
        reseau = ReseauRoutier()
        route = Route("A1", longueur=1000, limite_vitesse=30)
        reseau.ajouter_route(route)
        
        v = Vehicule("V1", position=0, vitesse=10)
        reseau.ajouter_vehicule(v, "A1")
        
        assert v in route.vehicules
        assert v.route == route
    
    def test_ajouter_vehicule_route_inexistante(self):
        """Test de l'ajout d'un véhicule sur une route inexistante"""
        reseau = ReseauRoutier()
        v = Vehicule("V1", position=0, vitesse=10)
        
        with pytest.raises(ValueError, match="Route .* inconnue"):
            reseau.ajouter_vehicule(v, "RouteInexistante")
    
    def test_ajouter_vehicules_routes_differentes(self, reseau_multi_routes):
        """Test de l'ajout de véhicules sur différentes routes"""
        v1 = Vehicule("V1", position=0, vitesse=10)
        v2 = Vehicule("V2", position=0, vitesse=15)
        v3 = Vehicule("V3", position=0, vitesse=20)
        
        reseau_multi_routes.ajouter_vehicule(v1, "A-B")
        reseau_multi_routes.ajouter_vehicule(v2, "B-C")
        reseau_multi_routes.ajouter_vehicule(v3, "C-D")
        
        assert len(reseau_multi_routes.routes["A-B"].vehicules) == 1
        assert len(reseau_multi_routes.routes["B-C"].vehicules) == 1
        assert len(reseau_multi_routes.routes["C-D"].vehicules) == 1
    
    def test_etat_reseau_vide(self):
        """Test de l'état d'un réseau sans véhicules"""
        reseau = ReseauRoutier()
        route = Route("A1", longueur=1000, limite_vitesse=30)
        reseau.ajouter_route(route)
        
        etat = reseau.etat()
        
        assert "A1" in etat
        assert etat["A1"] == []
    
    def test_etat_reseau_avec_vehicules(self, reseau_simple):
        """Test de l'état d'un réseau avec des véhicules"""
        etat = reseau_simple.etat()
        
        assert "A1" in etat
        assert len(etat["A1"]) == 1
        
        vehicule_info = etat["A1"][0]
        assert "id" in vehicule_info
        assert "pos" in vehicule_info
        assert "vitesse" in vehicule_info
        assert vehicule_info["id"] == "V1"
    
    def test_etat_structure_correcte(self, reseau_multi_routes):
        """Test de la structure de l'état du réseau"""
        v1 = Vehicule("V1", position=10, vitesse=15)
        v2 = Vehicule("V2", position=20, vitesse=25)
        
        reseau_multi_routes.ajouter_vehicule(v1, "A-B")
        reseau_multi_routes.ajouter_vehicule(v2, "A-B")
        
        etat = reseau_multi_routes.etat()
        
        assert len(etat["A-B"]) == 2
        assert etat["A-B"][0]["id"] == "V1"
        assert etat["A-B"][0]["pos"] == 10
        assert etat["A-B"][0]["vitesse"] == 15
        assert etat["A-B"][1]["id"] == "V2"
        assert etat["A-B"][1]["pos"] == 20
        assert etat["A-B"][1]["vitesse"] == 25
    
    def test_etat_plusieurs_routes_avec_vehicules(self, reseau_multi_routes):
        """Test de l'état avec plusieurs routes contenant des véhicules"""
        v1 = Vehicule("V1", position=10, vitesse=15)
        v2 = Vehicule("V2", position=20, vitesse=25)
        v3 = Vehicule("V3", position=30, vitesse=30)
        
        reseau_multi_routes.ajouter_vehicule(v1, "A-B")
        reseau_multi_routes.ajouter_vehicule(v2, "B-C")
        reseau_multi_routes.ajouter_vehicule(v3, "C-D")
        
        etat = reseau_multi_routes.etat()
        
        assert len(etat) == 3
        assert len(etat["A-B"]) == 1
        assert len(etat["B-C"]) == 1
        assert len(etat["C-D"]) == 1
    
    def test_mise_a_jour_toutes_routes(self, reseau_multi_routes):
        """Test de la mise à jour de toutes les routes du réseau"""
        v1 = Vehicule("V1", position=0, vitesse=10)
        v2 = Vehicule("V2", position=0, vitesse=15)
        v3 = Vehicule("V3", position=0, vitesse=20)
        
        reseau_multi_routes.ajouter_vehicule(v1, "A-B")
        reseau_multi_routes.ajouter_vehicule(v2, "B-C")
        reseau_multi_routes.ajouter_vehicule(v3, "C-D")
        
        # Simuler une mise à jour manuelle de toutes les routes
        for route in reseau_multi_routes.routes.values():
            route.mettre_a_jour_vehicules(delta_t=1.0)
        
        assert v1.position == pytest.approx(10.0)
        assert v2.position == pytest.approx(15.0)
        assert v3.position == pytest.approx(20.0)
    
    def test_acces_route_par_nom(self):
        """Test de l'accès à une route par son nom"""
        reseau = ReseauRoutier()
        route = Route("A1", longueur=1000, limite_vitesse=30)
        reseau.ajouter_route(route)
        
        route_recuperee = reseau.routes.get("A1")
        
        assert route_recuperee is not None
        assert route_recuperee == route
        assert route_recuperee.nom == "A1"
    
    def test_route_inexistante_retourne_none(self):
        """Test que l'accès à une route inexistante retourne None"""
        reseau = ReseauRoutier()
        route_recuperee = reseau.routes.get("RouteInexistante")
        
        assert route_recuperee is None