import json
import random
from typing import Optional
from exception import *
from models.reseau import ReseauRoutier
from models.route import Route
from models.vehicule import Vehicule
from core.analyseur import Analyseur
from IO.affichage import Affichage
from IO.export import Export

class Simulateur:
    def __init__(self, fichier_config: Optional[str] = None):
        self.reseau = ReseauRoutier()
        self.analyseur = Analyseur()
        self.affichage = Affichage()
        self.export = Export()
        self.stats = {
            'vitesses_moyennes': [],
            'etat_par_tour': []
        }

        if fichier_config:
            self._charger_config(fichier_config)

    def _charger_config(self, path: str):
        """Lit un fichier JSON pour instancier les objets modèles (Route, Vehicule)."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        except FileNotFoundError:
            raise FichierConfigError(path, "Fichier de configuration introuvable")
        except json.JSONDecodeError:
            raise FichierConfigError(path, "Format JSON invalide")

        # Charger les routes
        for r in cfg.get('routes', []):
            route = Route(r['nom'], r['longueur'], r['limite_vitesse'])
            self.reseau.ajouter_route(route)

        # Charger les véhicules
        for v in cfg.get('vehicules', []):
            veh = Vehicule(
                id=v['id'],
                position=v.get('position', 0.0),
                vitesse=v.get('vitesse', 0.0)
            )
            self.reseau.ajouter_vehicule(veh, v['route'])

    def lancer_simulation(
        self,
        n_tours: int,
        delta_t: float,
        afficher: bool = True,
        export_path: Optional[str] = None
    ):
        """Exécute la boucle de simulation pour un nombre défini de tours"""
        if not isinstance(n_tours, int) or n_tours <= 0:
            raise IterationInvalideError(n_tours)
        
        for t in range(n_tours):
            # --- Mise à jour de chaque route ---
            for route in self.reseau.routes.values():
                route.mettre_a_jour_vehicules(delta_t)

            # --- Calculs analytiques ---
            vm = self.analyseur.vitesses_moyennes(self.reseau)
            self.stats['vitesses_moyennes'].append({'tour': t, 'vm': vm})
            etat = self.reseau.etat()
            self.stats['etat_par_tour'].append({'tour': t, 'etat': etat})

            # --- AFFICHAGE ---
            if afficher:
                self.affichage.afficher_console(t, self.reseau, vm)

            # --- AJOUT ALÉATOIRE DE NOUVEAUX VÉHICULES ---
            # (Place this AFTER the route updates but BEFORE export)
            if random.random() < 0.3:  # 30% de chance à chaque tour
                new_id = f"Auto_{t}"
                route = random.choice(list(self.reseau.routes.values()))
                try:
                    v = Vehicule(new_id, position=0, vitesse=random.uniform(5, 15))
                    route.ajouter_vehicule(v)
                    print(f"→ Nouveau véhicule ajouté : {new_id} sur {route.nom}")
                except Exception as e:
                    print(f"Impossible d'ajouter {new_id} sur {route.nom}: {e}")
