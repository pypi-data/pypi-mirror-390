from exception import *


class Vehicule:

    def __init__(self, id, position=0.0, vitesse=0.0, longueur=4.0, route=None):
        self.id = id
        self.position = position
        self.vitesse = vitesse
        self.longueur = longueur
        self.route = route

    def avancer(self, delta_t: float):
        """Met à jour la position du véhicule en appliquant la formule simple de la cinématique"""
        if self.vitesse < 0:
            raise VitesseNegativeError(self.vitesse)
        nouvelle_position = self.position + self.vitesse * delta_t
        if nouvelle_position < 0:
            raise PositionInvalideError(nouvelle_position)

        self.position = nouvelle_position

    def changer_de_route(self, nouvelle_route, nouvelle_position=0.0):
        """gère la transition du véhicule d'une route à une autre en mettant à jour sa référence de route"""
        # Retirer de l'ancienne route si elle existe
        if self.route is not None:
            self.route.retirer_vehicule(self)
        
        # Ajouter à la nouvelle route
        if nouvelle_route is not None:
            nouvelle_route.ajouter_vehicule(self)
        
        # Mettre à jour la position
        self.position = nouvelle_position