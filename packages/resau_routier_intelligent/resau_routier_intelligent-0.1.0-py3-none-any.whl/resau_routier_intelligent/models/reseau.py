from typing import List, Dict
from .route import Route
from .vehicule import Vehicule
class ReseauRoutier:
    """Classe représentant l'ensemble du réseau routier."""
    
    def __init__(self, nom: str = "Réseau Principal"):
        self.nom = nom
        self.routes: Dict[str, Route] = {}
        self.vehicules: List[Vehicule] = []
        self.intersections: Dict[str, List[str]] = {} 
        
    def ajouter_route(self, route: Route) -> None:
        """Ajoute une route au réseau."""
        self.routes[route.nom] = route
        route.reseau = self
        
    def connecter_routes(self, nom_route1: str, nom_route2: str, intersection: str = None) -> None:
        """Connecte deux routes, éventuellement via une intersection."""
        if nom_route1 in self.routes and nom_route2 in self.routes:
            route1 = self.routes[nom_route1]
            route2 = self.routes[nom_route2]
            route1.connecter_route(route2)
            
            if intersection:
                if intersection not in self.intersections:
                    self.intersections[intersection] = []
                if nom_route1 not in self.intersections[intersection]:
                    self.intersections[intersection].append(nom_route1)
                if nom_route2 not in self.intersections[intersection]:
                    self.intersections[intersection].append(nom_route2)
    
    def ajouter_vehicule(self, vehicule: Vehicule, nom_route_depart: str) -> None:
        """Ajoute un véhicule au réseau sur une route donnée."""
        if nom_route_depart in self.routes:
            self.vehicules.append(vehicule)
            route_depart = self.routes[nom_route_depart]
            vehicule.changer_de_route(route_depart)
    
    def obtenir_routes_sortie(self, route_actuelle: Route) -> List[Route]:
        """Retourne les routes de sortie possibles depuis une route donnée."""
        return route_actuelle.routes_connectees
    
    def mettre_a_jour_reseau(self, delta_t: float) -> None:
        """Met à jour l'état de tout le réseau."""
        for route in self.routes.values():
            route.mettre_a_jour_vehicules(delta_t)
    
    def obtenir_statistiques_globales(self) -> Dict:
        """Retourne les statistiques globales du réseau."""
        stats = {
            'nombre_routes': len(self.routes),
            'nombre_vehicules': len(self.vehicules),
            'nombre_intersections': len(self.intersections),
            'routes': {}
        }
        
        for nom_route, route in self.routes.items():
            stats['routes'][nom_route] = route.obtenir_statistiques()
            
        return stats