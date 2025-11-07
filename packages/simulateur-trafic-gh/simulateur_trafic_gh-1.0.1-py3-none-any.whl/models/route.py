from typing import List

from exception import *
from .vehicule import Vehicule


class Route:
    def __init__(self, nom: str, longueur: float, limite_vitesse: float , maxV : int = 10):
        self.nom = nom
        self.longueur = float(longueur)
        self.limite_vitesse = float(limite_vitesse)
        self.vehicules: List[Vehicule] = []
        self.maxV = maxV


    def ajouter_vehicule(self, vehicule: Vehicule):
        """ajoute un véhicule à la liste de la route (s'il n'est pas déjà présent) et établit la référence bidirectionnelle en assignant la route au véhicule"""
        if len(self.vehicules) >= self.maxV:
            raise RoutePleineError(self.nom)

        if vehicule in self.vehicules:
            raise VehiculeDejaPresentError(vehicule.id, self.nom)

        self.vehicules.append(vehicule)
        vehicule.route = self


    def retirer_vehicule(self, vehicule: Vehicule):
        """Retire un véhicule de la liste de la route et supprime la référence de la route dans l'objet véhicule (défini à None)."""

        if vehicule not in self.vehicules:
            raise VehiculePasPresentError(vehicule.id, self.nom)
        
        self.vehicules.remove(vehicule)
        vehicule.route = None


    def mettre_a_jour_vehicules(self, delta_t: float):
        # Trier par position (du plus proche au plus éloigné)
        self.vehicules.sort(key=lambda v: v.position)

        for i, veh in enumerate(self.vehicules):
            # Limiter la vitesse à la limite de la route
            if veh.vitesse > self.limite_vitesse:
                veh.vitesse = self.limite_vitesse

            # Gestion de la distance de sécurité
            if i < len(self.vehicules) - 1:
                vehicule_devant = self.vehicules[i + 1]
                distance = vehicule_devant.position - veh.position

                # Si trop proche du véhicule de devant → ralentir
                if distance < 5:  # 5 mètres de sécurité
                    veh.vitesse = max(0, veh.vitesse - 1)
                else:
                    # Sinon, accélération progressive (jusqu’à la limite)
                    veh.vitesse = min(self.limite_vitesse, veh.vitesse + 0.5)

            # Mettre à jour la position selon la vitesse
            veh.avancer(delta_t)

        # Supprimer les véhicules sortis de la route
        for veh in list(self.vehicules):
            if veh.position >= self.longueur:
                self.retirer_vehicule(veh)
