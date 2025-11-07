#  simulateur_trafic_gh — Simulateur de Trafic Routier

Un simulateur Python modulaire pour modéliser et analyser le trafic routier à travers des **routes**, **véhicules**, et **réseaux routiers**.  
Ce projet est conçu pour des fins pédagogiques et expérimentales — facile à étendre et à intégrer dans d’autres applications.

---

##  Installation

```bash
pip install simulateur_trafic_gh
```

Ou depuis le code source :

```bash
git clone https://github.com/YosraGhanmi/simulateur_trafic_gh.git
cd simulateur_trafic_gh
pip install .
```

---

## 🧩 Structure du package

```
simulateur_trafic_gh/
├── core/
│   ├── simulateur.py       # Boucle principale de simulation
│   ├── analyseur.py        # Calculs de statistiques (vitesses moyennes, congestion)
├── models/
│   ├── vehicule.py         # Classe représentant un véhicule
│   ├── route.py            # Classe représentant une route
│   ├── reseau.py           # Ensemble de routes et de véhicules
├── IO/
│   ├── affichage.py        # Affichage console et visualisation
│   ├── export.py           # Exportation des résultats JSON
├── data/
│   ├── config_reseau.json  # Exemple de configuration
├── exception.py            # Gestion des erreurs personnalisées
└── main.py                 # Exemple d'exécution
```

---

## 🧠 Exemple d’utilisation

```python
from simulateur_trafic_gh.core.simulateur import Simulateur

# Charger un réseau depuis un fichier JSON
simu = Simulateur(fichier_config='data/config_reseau.json')

# Lancer la simulation pendant 60 tours (delta_t = 60 secondes)
simu.lancer_simulation(n_tours=60, delta_t=60, afficher=True, export_path='resultats.json')

print("Simulation terminée ! Résultats enregistrés dans resultats.json")
```

---

## ⚙️ Fonctionnalités principales

✅ Chargement automatique du réseau routier via un fichier JSON  
✅ Mise à jour dynamique de la position et vitesse des véhicules  
✅ Analyse statistique des vitesses moyennes et zones congestionnées  
✅ Export des résultats en JSON  
✅ Gestion d’erreurs robustes (fichier manquant, route pleine, etc.)  

---

## 🧪 Exemple de configuration JSON

```json
{
  "routes": [
    {"nom": "Route1", "longueur": 500, "limite_vitesse": 15},
    {"nom": "Route2", "longueur": 300, "limite_vitesse": 12}
  ],
  "vehicules": [
    {"id": "V1", "route": "Route1", "vitesse": 10, "position": 0},
    {"id": "V2", "route": "Route2", "vitesse": 12, "position": 0}
  ]
}
```

---

## 📈 Optimisation et Performance

Le projet peut être optimisé grâce à :
- **Profilage (cProfile)** pour identifier les goulots d’étranglement
- **Numba** pour accélérer les boucles critiques
- **Cython** pour compiler certaines classes Python en C

---

## 👩‍💻 Auteur

**Yosra Ghanmi**  
📧 yosraghanmi23@gmail.com  
💻 [GitHub : YosraGhanmi](https://github.com/YosraGhanmi)

---

## 🪪 Licence

Distribué sous licence **MIT** — libre d’utilisation, de modification et de distribution.
