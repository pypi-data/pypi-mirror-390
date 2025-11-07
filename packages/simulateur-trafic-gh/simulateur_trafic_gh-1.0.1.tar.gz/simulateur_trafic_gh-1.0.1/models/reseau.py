from typing import Dict
from .route import Route
from .vehicule import Vehicule


class ReseauRoutier:
    def __init__(self):
        self.routes: Dict[str, Route] = {}
        self.intersections = {}


    def ajouter_route(self, route: Route):
        """Enregistre un objet Route dans le réseau en utilisant son nom comme clé d'accès rapide"""
        self.routes[route.nom] = route


    def ajouter_vehicule(self, vehicule: Vehicule, nom_route: str):
        """érifie l'existence de la route, puis délègue à l'objet Route l'ajout du véhicule à sa liste interne, assurant l'intégrité de la relation"""
        route = self.routes.get(nom_route)
        if not route:
            raise ValueError(f"Route {nom_route} inconnue")
        route.ajouter_vehicule(vehicule)


    def etat(self):
        """Fournit un instantané sérialisable de l'état actuel du réseau (ID, position, vitesse des véhicules) pour l'analyse et la journalisation des données"""
        return {
        r.nom: [{"id": v.id, "pos": v.position, "vitesse": v.vitesse} for v in r.vehicules]
        for r in self.routes.values()
        }