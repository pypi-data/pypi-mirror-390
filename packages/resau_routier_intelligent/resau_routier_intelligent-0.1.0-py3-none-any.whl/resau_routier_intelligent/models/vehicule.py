import random
from typing import  Optional
from enum import Enum
from ..exceptions.NegativeDeltaTException import NegativeDeltaTException
class StatutVehicule(Enum):
    EN_MOUVEMENT = "en_mouvement"
    ARRETE = "arrete"
    EN_ATTENTE = "en_attente"

class Vehicule:
    """Classe représentant une véhicule."""
    def __init__(self, identifiant: str, vitesse_max: float = 90, position: float = 0):
        self.identifiant = identifiant
        self.position = position  # Position sur la route actuelle (en km)
        self.vitesse_actuelle = 0.0  # km/h
        self.vitesse_max = vitesse_max  # km/h
        self.route_actuelle: Optional['Route'] = None
        self.statut = StatutVehicule.EN_MOUVEMENT
        self.temps_total_parcours = 0.0  # minutes
        self.distance_totale = 0.0  # km
        self.historique_positions = []
        
    def avancer(self, delta_t: float) -> None:
        if self.statut == StatutVehicule.ARRETE:
            return
        if delta_t <0:
            raise NegativeDeltaTException("Le delta_t ne peut pas être négatif.")
        if self.route_actuelle:
            # Calcul de la vitesse en fonction du trafic et des limites
            vitesse_cible = min(
                self.vitesse_max,
                self.route_actuelle.limite_vitesse,
                self._calculer_vitesse_trafic()
            )
            
            # Ajustement progressif de la vitesse
            if self.vitesse_actuelle < vitesse_cible:
                self.vitesse_actuelle = min(vitesse_cible, self.vitesse_actuelle + 10)
            elif self.vitesse_actuelle > vitesse_cible:
                self.vitesse_actuelle = max(vitesse_cible, self.vitesse_actuelle - 15)
            
            # Déplacement
            distance = (self.vitesse_actuelle * delta_t) / 60  # conversion min->h
            self.position += distance
            self.distance_totale += distance
            self.temps_total_parcours += delta_t
            
            # Enregistrement de l'historique
            self.historique_positions.append({
                'temps': self.temps_total_parcours,
                'position': self.position,
                'vitesse': self.vitesse_actuelle,
                'route': self.route_actuelle.nom if self.route_actuelle else None
            })
            
            # Vérifier si le véhicule a atteint la fin de la route
            if self.position >= self.route_actuelle.longueur:
                self._gerer_fin_de_route()
    
    def changer_de_route(self, nouvelle_route: 'Route') -> None:
        """Change le véhicule de route."""
        if self.route_actuelle:
            self.route_actuelle.retirer_vehicule(self)
        
        self.route_actuelle = nouvelle_route
        self.position = 0.0
        nouvelle_route.ajouter_vehicule(self)
    
    def _calculer_vitesse_trafic(self) -> float:
        """Calcule la vitesse en fonction de la densité du trafic."""
        if not self.route_actuelle:
            return self.vitesse_max
            
        densite = self.route_actuelle.calculer_densite_trafic()
        
        # Réduction de vitesse selon la densité
        if densite > 20:  # Très dense
            return self.route_actuelle.limite_vitesse * 0.3
        elif densite > 15:  # Dense
            return self.route_actuelle.limite_vitesse * 0.5
        elif densite > 10:  # Modéré
            return self.route_actuelle.limite_vitesse * 0.7
        else:  # Fluide
            return self.route_actuelle.limite_vitesse
    
    def _gerer_fin_de_route(self) -> None:
        """Gère le comportement quand le véhicule atteint la fin d'une route."""
        if self.route_actuelle and hasattr(self.route_actuelle, 'reseau'):
            # Chercher une route de sortie aléatoire
            routes_sortie = self.route_actuelle.reseau.obtenir_routes_sortie(self.route_actuelle)
            if routes_sortie:
                nouvelle_route = random.choice(routes_sortie)
                self.changer_de_route(nouvelle_route)
            else:
                # Pas de sortie disponible, le véhicule s'arrête
                self.statut = StatutVehicule.ARRETE
