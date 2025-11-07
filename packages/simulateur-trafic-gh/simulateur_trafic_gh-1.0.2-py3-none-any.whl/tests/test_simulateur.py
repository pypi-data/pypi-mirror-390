import pytest
import json
from core.simulateur import Simulateur
from models.route import Route
from models.vehicule import Vehicule


class TestSimulateur:
    """Tests d'intégration pour la classe Simulateur"""
    
    def test_creation_simulateur_sans_config(self):
        """Test de la création d'un simulateur sans fichier de configuration"""
        simu = Simulateur()
        
        assert simu.reseau is not None
        assert len(simu.reseau.routes) == 0
        assert simu.analyseur is not None
        assert simu.affichage is not None
        assert simu.export is not None
    
    def test_creation_simulateur_avec_config(self, tmp_path):
        """Test de la création d'un simulateur avec un fichier de configuration"""
        cfg = tmp_path / 'config.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
            ],
            "vehicules": [
                {"id": "V1", "route": "A1", "position": 0, "vitesse": 10}
            ]
        }))
        
        simu = Simulateur(fichier_config=str(cfg))
        
        assert len(simu.reseau.routes) == 1
        assert "A1" in simu.reseau.routes
        assert len(simu.reseau.routes["A1"].vehicules) == 1
    
    def test_lancer_simulation_minimale(self, tmp_path):
        """Test minimal pour vérifier le bon fonctionnement de la simulation"""
        cfg = tmp_path / 'cfg.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "R1", "longueur": 200, "limite_vitesse": 10}
            ],
            "vehicules": [
                {"id": "T1", "route": "R1", "position": 0, "vitesse": 5}
            ]
        }))
        
        simu = Simulateur(fichier_config=str(cfg))
        simu.lancer_simulation(n_tours=2, delta_t=1, afficher=False)
        
        route = simu.reseau.routes['R1']
        assert any(v.id == 'T1' for v in route.vehicules)
        
        v = route.vehicules[0]
        assert v.position >= 9.9
    
    def test_simulation_plusieurs_tours(self, tmp_path):
        """Test d'une simulation sur plusieurs tours"""
        cfg = tmp_path / 'config.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
            ],
            "vehicules": [
                {"id": "V1", "route": "A1", "position": 0, "vitesse": 10}
            ]
        }))
        
        simu = Simulateur(fichier_config=str(cfg))
        simu.lancer_simulation(n_tours=5, delta_t=1.0, afficher=False)
        
        v = simu.reseau.routes["A1"].vehicules[0]
        assert v.position == pytest.approx(50.0)
    
    def test_simulation_collecte_statistiques(self, tmp_path):
        """Test que la simulation collecte correctement les statistiques"""
        cfg = tmp_path / 'config.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
            ],
            "vehicules": [
                {"id": "V1", "route": "A1", "position": 0, "vitesse": 10}
            ]
        }))
        
        simu = Simulateur(fichier_config=str(cfg))
        simu.lancer_simulation(n_tours=3, delta_t=1.0, afficher=False)
        
        assert len(simu.stats['vitesses_moyennes']) == 3
        assert len(simu.stats['etat_par_tour']) == 3
        
        # Vérifier la structure des stats
        assert 'tour' in simu.stats['vitesses_moyennes'][0]
        assert 'vm' in simu.stats['vitesses_moyennes'][0]
        assert 'tour' in simu.stats['etat_par_tour'][0]
        assert 'etat' in simu.stats['etat_par_tour'][0]
    
    def test_simulation_limite_vitesse_appliquee(self, tmp_path):
        """Test que la limite de vitesse est appliquée pendant la simulation"""
        cfg = tmp_path / 'config.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "A1", "longueur": 1000, "limite_vitesse": 20}
            ],
            "vehicules": [
                {"id": "V1", "route": "A1", "position": 0, "vitesse": 50}
            ]
        }))
        
        simu = Simulateur(fichier_config=str(cfg))
        simu.lancer_simulation(n_tours=1, delta_t=1.0, afficher=False)
        
        v = simu.reseau.routes["A1"].vehicules[0]
        assert v.vitesse == 20.0
        assert v.position == pytest.approx(20.0)
    
    def test_simulation_vehicule_sort_de_route(self, tmp_path):
        """Test qu'un véhicule sort correctement de la route"""
        cfg = tmp_path / 'config.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "R1", "longueur": 50, "limite_vitesse": 30}
            ],
            "vehicules": [
                {"id": "V1", "route": "R1", "position": 40, "vitesse": 20}
            ]
        }))
        
        simu = Simulateur(fichier_config=str(cfg))
        
        assert len(simu.reseau.routes["R1"].vehicules) == 1
        
        simu.lancer_simulation(n_tours=1, delta_t=1.0, afficher=False)
        
        # Le véhicule devrait être sorti (40 + 20 = 60 > 50)
        assert len(simu.reseau.routes["R1"].vehicules) == 0
    
    def test_simulation_plusieurs_vehicules(self, tmp_path):
        """Test d'une simulation avec plusieurs véhicules"""
        cfg = tmp_path / 'config.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
            ],
            "vehicules": [
                {"id": "V1", "route": "A1", "position": 0, "vitesse": 10},
                {"id": "V2", "route": "A1", "position": 50, "vitesse": 15},
                {"id": "V3", "route": "A1", "position": 100, "vitesse": 20}
            ]
        }))
        
        simu = Simulateur(fichier_config=str(cfg))
        simu.lancer_simulation(n_tours=2, delta_t=1.0, afficher=False)
        
        route = simu.reseau.routes["A1"]
        assert len(route.vehicules) == 3
        
        vehicules_dict = {v.id: v for v in route.vehicules}
        assert vehicules_dict["V1"].position == pytest.approx(20.0)
        assert vehicules_dict["V2"].position == pytest.approx(80.0)
        assert vehicules_dict["V3"].position == pytest.approx(140.0)
    
    def test_simulation_plusieurs_routes(self, tmp_path):
        """Test d'une simulation avec plusieurs routes"""
        cfg = tmp_path / 'config.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "A-B", "longueur": 100, "limite_vitesse": 20},
                {"nom": "B-C", "longueur": 80, "limite_vitesse": 15}
            ],
            "vehicules": [
                {"id": "V1", "route": "A-B", "position": 0, "vitesse": 10},
                {"id": "V2", "route": "B-C", "position": 0, "vitesse": 12}
            ]
        }))
        
        simu = Simulateur(fichier_config=str(cfg))
        simu.lancer_simulation(n_tours=3, delta_t=1.0, afficher=False)
        
        assert len(simu.reseau.routes["A-B"].vehicules) == 1
        assert len(simu.reseau.routes["B-C"].vehicules) == 1
        
        v1 = simu.reseau.routes["A-B"].vehicules[0]
        v2 = simu.reseau.routes["B-C"].vehicules[0]
        
        assert v1.position == pytest.approx(30.0)
        assert v2.position == pytest.approx(36.0)
    
    def test_simulation_export_json(self, tmp_path):
        """Test de l'export des résultats en JSON"""
        cfg = tmp_path / 'config.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
            ],
            "vehicules": [
                {"id": "V1", "route": "A1", "position": 0, "vitesse": 10}
            ]
        }))
        
        export_path = tmp_path / 'resultats.json'
        
        simu = Simulateur(fichier_config=str(cfg))
        simu.lancer_simulation(
            n_tours=2, 
            delta_t=1.0, 
            afficher=False, 
            export_path=str(export_path)
        )
        
        assert export_path.exists()
        
        with open(export_path, 'r') as f:
            data = json.load(f)
        
        assert 'vitesses_moyennes' in data
        assert 'etat_par_tour' in data
        assert len(data['vitesses_moyennes']) == 2
    
    def test_simulation_sans_vehicules(self, tmp_path):
        """Test d'une simulation avec des routes mais sans véhicules"""
        cfg = tmp_path / 'config.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "A1", "longueur": 1000, "limite_vitesse": 30}
            ],
            "vehicules": []
        }))
        
        simu = Simulateur(fichier_config=str(cfg))
        
        # Ne devrait pas lever d'erreur
        simu.lancer_simulation(n_tours=5, delta_t=1.0, afficher=False)
        
        assert len(simu.stats['vitesses_moyennes']) == 5
    
    def test_simulation_integration_complete(self, tmp_path):
        """Test d'intégration complet du simulateur"""
        cfg = tmp_path / 'config_complete.json'
        cfg.write_text(json.dumps({
            "routes": [
                {"nom": "A-B", "longueur": 100, "limite_vitesse": 20},
                {"nom": "B-C", "longueur": 80, "limite_vitesse": 15},
                {"nom": "C-D", "longueur": 200, "limite_vitesse": 35}
            ],
            "vehicules": [
                {"id": "V1", "route": "A-B", "position": 0, "vitesse": 16},
                {"id": "V2", "route": "A-B", "position": 0, "vitesse": 11},
                {"id": "V3", "route": "B-C", "position": 0, "vitesse": 9},
                {"id": "V4", "route": "C-D", "position": 0, "vitesse": 20}
            ]
        }))
        
        export_path = tmp_path / 'resultats_complet.json'
        
        simu = Simulateur(fichier_config=str(cfg))
        simu.lancer_simulation(
            n_tours=10, 
            delta_t=1.0, 
            afficher=False, 
            export_path=str(export_path)
        )
        
        # Vérifications
        assert len(simu.reseau.routes) == 3
        assert len(simu.stats['vitesses_moyennes']) == 10
        assert export_path.exists()
        
        # Vérifier que les vitesses moyennes sont calculées
        vm = simu.stats['vitesses_moyennes'][0]['vm']
        assert 'A-B' in vm
        assert 'B-C' in vm
        assert 'C-D' in vm