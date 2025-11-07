from typing import Dict, List

from exception import *


class Analyseur:
    """La classe Analyseur est une classe utilitaire qui regroupe des méthodes statiques pour effectuer des analyses de trafic"""
    @staticmethod
    def vitesses_moyennes(reseau) -> Dict[str, float]:
        """Cette méthode calcule la vitesse moyenne des véhicules pour chaque route du réseau."""
        if reseau is None or not hasattr(reseau, "routes"):
            raise DonneesManquantesError("réseau ou attribut 'routes'")

        res = {}
        for nom, route in reseau.routes.items():
            if route is None or not hasattr(route, "vehicules"):
                raise DonneesManquantesError(f"route '{nom}'")
            if not route.vehicules:
                res[nom] = 0.0
            else:
                total_vitesse = sum(v.vitesse for v in route.vehicules)
                res[nom] = total_vitesse / len(route.vehicules)
        return res

    @staticmethod
    def zones_congestion(reseau, seuil_vitesse: float = 2.0) -> List[str]:
        """Cette méthode identifie les routes considérées comme congestionnées."""
        vm = Analyseur.vitesses_moyennes(reseau)
        return [r for r, v in vm.items() if v <= seuil_vitesse]

    @staticmethod
    def temps_parcours_estime(route, vitesse_moyenne: float = None) -> float | None:
        """Cette méthode calcule le temps de parcours estimé pour une seule route"""
        if route is None or not hasattr(route, "longueur"):
            raise DonneesManquantesError("objet route")

        if vitesse_moyenne is None:
            if not hasattr(route, "vehicules") or not route.vehicules:
                raise DonneesManquantesError("véhicules sur la route")
            vitesse_moyenne = sum(v.vitesse for v in route.vehicules) / len(route.vehicules)

        if vitesse_moyenne == 0:
            raise DivisionParZeroError("Vitesse moyenne égale à zéro : impossible de calculer le temps de parcours.")

        if vitesse_moyenne < 0:
            raise DonneesManquantesError("vitesse moyenne négative")

        return route.longueur / vitesse_moyenne
