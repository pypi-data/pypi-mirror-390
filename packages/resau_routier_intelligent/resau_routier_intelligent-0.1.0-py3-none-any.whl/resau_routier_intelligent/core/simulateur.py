import json
import random
from typing import Dict
from ..models.reseau import ReseauRoutier
from ..models.route import Route
from ..models.vehicule import Vehicule
from ..exceptions.ConfigFileException import ConfigFileException

class Simulateur:
    """Classe principale de simulation du trafic routier."""
    
    def __init__(self, fichier_config: str = None):
        self.reseau = ReseauRoutier()
        self.temps_simulation = 0.0  # minutes
        self.historique_stats = []
        self.configuration = {}
        
        if fichier_config:
            self.charger_configuration(fichier_config)
            self.initialiser_reseau()
    
    def charger_configuration(self, fichier_config: str) -> None:
        """Charge la configuration depuis un fichier JSON."""
        try:
            with open(fichier_config, 'r', encoding='utf-8') as f:
                self.configuration = json.load(f)
        except FileNotFoundError:
            raise ConfigFileException(f"Fichier de configuration introuvable: {fichier_config}")
        except json.JSONDecodeError as e:
            raise ConfigFileException(f"Format JSON invalide: {e}")
    
    def initialiser_reseau(self) -> None:
        """Initialise le réseau routier selon la configuration."""
        # Créer les routes
        for route_config in self.configuration.get('routes', []):
            route = Route(
                nom=route_config['nom'],
                longueur=route_config['longueur'],
                limite_vitesse=route_config.get('limite_vitesse', 50)
            )
            self.reseau.ajouter_route(route)
        
        # Connecter les routes
        for connexion in self.configuration.get('connexions', []):
            self.reseau.connecter_routes(
                connexion['route1'],
                connexion['route2'],
                connexion.get('intersection')
            )
        
        # Ajouter les véhicules initiaux
        for vehicule_config in self.configuration.get('vehicules', []):
            vehicule = Vehicule(
                identifiant=vehicule_config['id'],
                vitesse_max=vehicule_config.get('vitesse_max', 90)
            )
            self.reseau.ajouter_vehicule(vehicule, vehicule_config['route_depart'])
    
    def lancer_simulation(self, n_tours: int, delta_t: float = 1.0) -> None:
        """Lance la simulation pendant n_tours avec un pas de temps delta_t."""
        print(f"🚗 Démarrage de la simulation ({n_tours} tours, Δt={delta_t}min)")
        print("=" * 60)
        
        for tour in range(n_tours):
            # Mise à jour du réseau
            self.reseau.mettre_a_jour_reseau(delta_t)
            self.temps_simulation += delta_t
            
            # Ajout aléatoire de nouveaux véhicules
            if tour % 5 == 0:  # Tous les 5 tours
                self._generer_nouveaux_vehicules()
            
            # Collecte des statistiques
            stats_actuelles = self.reseau.obtenir_statistiques_globales()
            stats_actuelles['temps'] = self.temps_simulation
            self.historique_stats.append(stats_actuelles)
            
            # Affichage périodique
            if tour % 10 == 0:
                self._afficher_etat_simulation(tour, n_tours)
        
        print("\n✅ Simulation terminée!")
        self._afficher_resume_final()
    
    def _generer_nouveaux_vehicules(self) -> None:
        """Génère de nouveaux véhicules aléatoirement."""
        if len(self.reseau.vehicules) < 50:  # Limite le nombre total
            nb_nouveaux = random.randint(1, 3)
            for i in range(nb_nouveaux):
                vehicule_id = f"V{len(self.reseau.vehicules) + i + 1:03d}"
                vehicule = Vehicule(
                    identifiant=vehicule_id,
                    vitesse_max=random.uniform(70, 110)
                )
                # Route de départ aléatoire
                route_depart = random.choice(list(self.reseau.routes.keys()))
                self.reseau.ajouter_vehicule(vehicule, route_depart)
    
    def _afficher_etat_simulation(self, tour_actuel: int, total_tours: int) -> None:
        """Affiche l'état actuel de la simulation."""
        pourcentage = (tour_actuel / total_tours) * 100
        nb_vehicules = len(self.reseau.vehicules)
        
        print(f"Tour {tour_actuel:3d}/{total_tours} ({pourcentage:5.1f}%) | "
              f"Véhicules: {nb_vehicules:3d} | Temps: {self.temps_simulation:6.1f}min")
    
    def _afficher_resume_final(self) -> None:
        """Affiche le résumé final de la simulation."""
        stats_finales = self.reseau.obtenir_statistiques_globales()
        
        print("\n📊 RÉSUMÉ DE LA SIMULATION")
        print("=" * 40)
        print(f"Durée totale: {self.temps_simulation:.1f} minutes")
        print(f"Nombre de véhicules: {stats_finales['nombre_vehicules']}")
        print(f"Nombre de routes: {stats_finales['nombre_routes']}")
        
        print("\n🛣️  ÉTAT DES ROUTES:")
        for nom_route, stats_route in stats_finales['routes'].items():
            densite = stats_route['densite_trafic']
            vitesse_moy = stats_route['vitesse_moyenne']
            etat_trafic = self._evaluer_etat_trafic(densite)
            
            print(f"  {nom_route:15s} | {stats_route['vehicules_actuels']:2d} véh. | "
                  f"Vitesse: {vitesse_moy:5.1f} km/h | {etat_trafic}")
    
    def _evaluer_etat_trafic(self, densite: float) -> str:
        """Évalue l'état du trafic selon la densité."""
        if densite > 20:
            return "🔴 Embouteillé"
        elif densite > 15:
            return "🟠 Dense"
        elif densite > 10:
            return "🟡 Modéré"
        else:
            return "🟢 Fluide"
    
    def _configuration_par_defaut(self) -> Dict:
        """Retourne une configuration par défaut."""
        return {
            "routes": [
                {"nom": "Avenue Principale", "longueur": 5.0, "limite_vitesse": 70},
                {"nom": "Route Nationale", "longueur": 8.0, "limite_vitesse": 90},
                {"nom": "Boulevard Urbain", "longueur": 3.5, "limite_vitesse": 50},
                {"nom": "Autoroute A1", "longueur": 15.0, "limite_vitesse": 130},
                {"nom": "Rue Résidentielle", "longueur": 2.0, "limite_vitesse": 30}
            ],
            "connexions": [
                {"route1": "Avenue Principale", "route2": "Route Nationale", "intersection": "Carrefour Central"},
                {"route1": "Boulevard Urbain", "route2": "Avenue Principale", "intersection": "Place de la Ville"},
                {"route1": "Route Nationale", "route2": "Autoroute A1", "intersection": "Échangeur Nord"},
                {"route1": "Rue Résidentielle", "route2": "Boulevard Urbain", "intersection": "Rond-Point Sud"}
            ],
            "vehicules": [
                {"id": "V001", "route_depart": "Avenue Principale", "vitesse_max": 85},
                {"id": "V002", "route_depart": "Route Nationale", "vitesse_max": 95},
                {"id": "V003", "route_depart": "Boulevard Urbain", "vitesse_max": 75},
                {"id": "V004", "route_depart": "Autoroute A1", "vitesse_max": 120},
                {"id": "V005", "route_depart": "Rue Résidentielle", "vitesse_max": 60}
            ]
        }
    
    def _sauvegarder_configuration_defaut(self, fichier: str) -> None:
        """Sauvegarde la configuration par défaut."""
        import os
        os.makedirs(os.path.dirname(fichier), exist_ok=True)
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(self.configuration, f, indent=2, ensure_ascii=False)
