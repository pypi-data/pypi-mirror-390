import csv
import json
from core.simulateur import Simulateur
class ExportDonnees:
    """Classe pour l'export des données de simulation."""
    
    def __init__(self, simulateur: Simulateur):
        self.simulateur = simulateur
    
    def exporter_csv(self, nom_fichier: str = "resultats_simulation.csv"):
        """Exporte les résultats en format CSV."""
        donnees_csv = []
        
        for i, snapshot in enumerate(self.simulateur.historique_stats):
            ligne_base = {
                'temps': snapshot['temps'],
                'iteration': i,
                'nb_vehicules_total': snapshot['nombre_vehicules']
            }
            
            for nom_route, stats_route in snapshot['routes'].items():
                ligne = ligne_base.copy()
                ligne.update({
                    'route': nom_route,
                    'vehicules_sur_route': stats_route['vehicules_actuels'],
                    'vehicules_passes': stats_route['vehicules_passes'],
                    'densite_trafic': stats_route['densite_trafic'],
                    'vitesse_moyenne': stats_route['vitesse_moyenne'],
                    'limite_vitesse': stats_route['limite_vitesse'],
                    'longueur_route': stats_route['longueur']
                })
                donnees_csv.append(ligne)
        
        # Écriture du fichier CSV
        if donnees_csv:
            with open(nom_fichier, 'w', newline='', encoding='utf-8') as fichier_csv:
                champs = donnees_csv[0].keys()
                writer = csv.DictWriter(fichier_csv, fieldnames=champs)
                writer.writeheader()
                writer.writerows(donnees_csv)
            
            print(f"📁 Données exportées vers: {nom_fichier}")
    
    def exporter_json(self, nom_fichier: str = "resultats_simulation.json"):
        """Exporte les résultats en format JSON."""
        donnees_export = {
            'configuration': self.simulateur.configuration,
            'duree_simulation': self.simulateur.temps_simulation,
            'historique_complet': self.simulateur.historique_stats,
            'resume_final': self.simulateur.reseau.obtenir_statistiques_globales()
        }
        
        with open(nom_fichier, 'w', encoding='utf-8') as fichier_json:
            json.dump(donnees_export, fichier_json, indent=2, ensure_ascii=False)
        
        print(f"📁 Données JSON exportées vers: {nom_fichier}")
    
    def generer_graphiques(self):
        """Génère des graphiques de visualisation."""
        if not self.simulateur.historique_stats:
            print("❌ Pas de données pour générer les graphiques")
            return
        
        # Préparation des données
        temps = [s['temps'] for s in self.simulateur.historique_stats]
        nb_vehicules = [s['nombre_vehicules'] for s in self.simulateur.historique_stats]
        
        # Vitesses moyennes par route
        routes_principales = list(self.simulateur.reseau.routes.keys())[:4]  # Top 4 routes
        vitesses_routes = {route: [] for route in routes_principales}
        