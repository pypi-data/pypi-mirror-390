import matplotlib.pyplot as plt
from typing import Any
import pandas as pd


class Affichage:
    def afficher_console(self, tour: int, reseau: Any, vitesses_moyennes: dict):
        """Affiche l'état succinct de la simulation dans la console pour un tour donné"""
        print(f"--- Tour {tour} ---")
        for nom, v in vitesses_moyennes.items():
            nb_vehicules = len(reseau.routes[nom].vehicules)
            print(f"Route {nom}: vm = {v:.2f} m/s, #véhicules = {nb_vehicules}")

    def tracer_vitesse_moyenne(self, stats):
        """convertit les statistiques brutes en un DataFrame Pandas"""
        df = pd.DataFrame([
            {'tour': s['tour'], **s['vm']}
            for s in stats['vitesses_moyennes']
        ])
        for col in df.columns:
            if col == 'tour':
                continue
            plt.figure()
            plt.plot(df['tour'], df[col], marker='o')
            plt.title(f"Vitesse moyenne - Route {col}")
            plt.xlabel('Tour')
            plt.ylabel('Vitesse (m/s)')
            plt.grid(True)
            plt.show()
