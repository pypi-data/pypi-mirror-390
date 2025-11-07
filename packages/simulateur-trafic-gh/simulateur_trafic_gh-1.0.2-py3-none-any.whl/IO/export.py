import json
import csv


class Export:
    def export_json(self, data, path: str):
        """Sérialise la totalité des données de simulation au format JSON"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Données exportées en JSON vers : {path}")

    def export_csv_etat(self, stats, path: str):
        """Transforme les données d'état du réseau d'une structure hiérarchique en une liste plate d'enregistrements, puis écrit cette liste dans un fichier CSV structuré"""
        rows = []

        for s in stats['etat_par_tour']:
            t = s['tour']
            for r, vehs in s['etat'].items():
                for v in vehs:
                    rows.append({
                        'tour': t,
                        'route': r,
                        'id': v['id'],
                        'pos': v['pos'],
                        'vitesse': v['vitesse']
                    })

        keys = ['tour', 'route', 'id', 'pos', 'vitesse']

        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

        print(f"Données exportées en CSV vers : {path}")
