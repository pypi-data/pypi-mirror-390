from typing import List, Dict
from .simulateur import Simulateur
from ..exceptions.StatisticsCalculationException import StatisticsCalculationException
class Analyseur:
    """Classe pour analyser les résultats de simulation."""
    
    def __init__(self, simulateur: Simulateur):
        self.simulateur = simulateur
        self.donnees_analyse = {}
    
    def analyser_performances_globales(self) -> Dict:
        """Analyse les performances globales du réseau."""
        if not self.simulateur.historique_stats:
            return {}
        
        # Calculs sur l'historique complet
        vitesses_moyennes = []
        densites_moyennes = []
        nb_vehicules_evolution = []
        
        for snapshot in self.simulateur.historique_stats:
            vitesses_routes = []
            densites_routes = []
            
            for stats_route in snapshot['routes'].values():
                if stats_route['vitesse_moyenne'] > 0:
                    vitesses_routes.append(stats_route['vitesse_moyenne'])
                densites_routes.append(stats_route['densite_trafic'])
            
            if vitesses_routes:
                vitesses_moyennes.append(sum(vitesses_routes) / len(vitesses_routes))
            if densites_routes:
                densites_moyennes.append(sum(densites_routes) / len(densites_routes))
            
            nb_vehicules_evolution.append(snapshot['nombre_vehicules'])
        
        self.donnees_analyse = {
            'vitesse_moyenne_globale': sum(vitesses_moyennes) / len(vitesses_moyennes) if vitesses_moyennes else 0,
            'densite_moyenne_globale': sum(densites_moyennes) / len(densites_moyennes) if densites_moyennes else 0,
            'pic_vehicules': max(nb_vehicules_evolution) if nb_vehicules_evolution else 0,
            'evolution_trafic': nb_vehicules_evolution,
            'evolution_vitesse': vitesses_moyennes,
            'evolution_densite': densites_moyennes
        }
        
        return self.donnees_analyse
    
    def identifier_zones_congestion(self) -> List[Dict]:
        """Identifie les zones de congestion dans le réseau."""
        zones_congestion = []
        
        if not self.simulateur.historique_stats:
            return zones_congestion
        
        # Analyser la dernière snapshot
        derniere_stats = self.simulateur.historique_stats[-1]
        
        for nom_route, stats_route in derniere_stats['routes'].items():
            densite = stats_route['densite_trafic']
            vitesse_moy = stats_route['vitesse_moyenne']
            limite_vitesse = stats_route['limite_vitesse']
            
            # Critères de congestion
            if densite > 15 or (vitesse_moy < limite_vitesse * 0.5 and vitesse_moy > 0):
                niveau_congestion = "CRITIQUE" if densite > 20 else "ÉLEVÉ" if densite > 15 else "MODÉRÉ"
                
                zones_congestion.append({
                    'route': nom_route,
                    'densite': densite,
                    'vitesse_moyenne': vitesse_moy,
                    'limite_vitesse': limite_vitesse,
                    'niveau': niveau_congestion,
                    'reduction_vitesse': ((limite_vitesse - vitesse_moy) / limite_vitesse * 100) if vitesse_moy > 0 else 100
                })
        
        # Trier par niveau de congestion
        zones_congestion.sort(key=lambda x: x['densite'], reverse=True)
        return zones_congestion
    
    def calculer_temps_parcours_moyens(self) -> Dict[str, float]:
        """Calcule les temps de parcours moyens par route."""
        temps_parcours = {}
        
        for nom_route, route in self.simulateur.reseau.routes.items():
            if route.vehicules:
                # Temps théorique à vitesse limite
                temps_theorique = (route.longueur / route.limite_vitesse) * 60  # minutes
                
                # Temps réel basé sur la vitesse moyenne actuelle
                if route.vitesse_moyenne > 0:
                    temps_reel = (route.longueur / route.vitesse_moyenne) * 60
                    temps_parcours[nom_route] = {
                        'temps_theorique': temps_theorique,
                        'temps_reel': temps_reel,
                        'retard': temps_reel - temps_theorique
                    }
                else:
                    raise StatisticsCalculationException('la vitesse moyenne ne doit pas etre négative ou nulle' )
        
        return temps_parcours