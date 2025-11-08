from typing import List, Dict, Optional
from .vehicule import Vehicule
class Route:
    """Classe représentant une route dans le réseau."""
    
    def __init__(self, nom: str, longueur: float, limite_vitesse: float = 50):
        self.nom = nom
        self.longueur = longueur  # km
        self.limite_vitesse = limite_vitesse  # km/h
        self.vehicules: List[Vehicule] = []
        self.routes_connectees: List['Route'] = []
        self.reseau: Optional['ReseauRoutier'] = None
        
        # Statistiques
        self.nb_vehicules_passes = 0
        self.temps_moyen_parcours = 0.0
        self.vitesse_moyenne = 0.0
        
    def ajouter_vehicule(self, vehicule: Vehicule) -> None:
        """Ajoute un véhicule à la route."""
        if vehicule in self.vehicules:
            raise ValueError
        self.vehicules.append(vehicule)
        vehicule.route_actuelle = self
        self.nb_vehicules_passes += 1
        
        
    def retirer_vehicule(self, vehicule: Vehicule) -> None:
        """Retire un véhicule de la route."""
        if vehicule in self.vehicules:
            self.vehicules.remove(vehicule)
            
    def mettre_a_jour_vehicules(self, delta_t: float) -> None:
        """Met à jour tous les véhicules présents sur la route."""
        for vehicule in self.vehicules[:]:  # Copie pour éviter les modifications concurrentes
            vehicule.avancer(delta_t)
            
        self._mettre_a_jour_statistiques()
    
    def calculer_densite_trafic(self) -> float:
        """Calcule la densité de trafic (véhicules par km)."""
        return len(self.vehicules) / max(self.longueur, 0.1)
    
    def connecter_route(self, route: 'Route') -> None:
        """Connecte cette route à une autre route."""
        if route not in self.routes_connectees:
            self.routes_connectees.append(route)
        if self not in route.routes_connectees:
            route.routes_connectees.append(self)
    
    def _mettre_a_jour_statistiques(self) -> None:
        """Met à jour les statistiques de la route."""
        if self.vehicules:
            self.vitesse_moyenne = sum(v.vitesse_actuelle for v in self.vehicules) / len(self.vehicules)
        else:
            self.vitesse_moyenne = 0.0
    
    def obtenir_statistiques(self) -> Dict:
        """Retourne les statistiques de la route."""
        return {
            'nom': self.nom,
            'vehicules_actuels': len(self.vehicules),
            'vehicules_passes': self.nb_vehicules_passes,
            'densite_trafic': self.calculer_densite_trafic(),
            'vitesse_moyenne': self.vitesse_moyenne,
            'limite_vitesse': self.limite_vitesse,
            'longueur': self.longueur
        }
