from core.analyseur import Analyseur
class AffichageConsole:
    """Classe pour l'affichage console des résultats."""
    
    @staticmethod
    def afficher_rapport_detaille(analyseur: Analyseur):
        """Affiche un rapport détaillé de la simulation."""
        print("\n" + "="*80)
        print("📈 RAPPORT DÉTAILLÉ DE SIMULATION")
        print("="*80)
        
        # Performances globales
        perf = analyseur.analyser_performances_globales()
        print(f"\n🌐 PERFORMANCES GLOBALES:")
        print(f"   Vitesse moyenne du réseau: {perf.get('vitesse_moyenne_globale', 0):.1f} km/h")
        print(f"   Densité moyenne du trafic: {perf.get('densite_moyenne_globale', 0):.1f} véh/km")
        print(f"   Pic de véhicules simultanés: {perf.get('pic_vehicules', 0)}")
        
        # Zones de congestion
        zones = analyseur.identifier_zones_congestion()
        if zones:
            print(f"\n🚨 ZONES DE CONGESTION ({len(zones)} détectées):")
            for zone in zones[:5]:  # Top 5
                print(f"   {zone['route']:20s} | {zone['niveau']:8s} | "
                      f"Densité: {zone['densite']:5.1f} | "
                      f"Vitesse: {zone['vitesse_moyenne']:5.1f} km/h "
                      f"(-{zone['reduction_vitesse']:4.1f}%)")
        else:
            print(f"\n🟢 TRAFIC FLUIDE: Aucune zone de congestion détectée")
        
        # Temps de parcours
        temps_parcours = analyseur.calculer_temps_parcours_moyens()
        if temps_parcours:
            print(f"\n⏱️  TEMPS DE PARCOURS:")
            for route, temps in temps_parcours.items():
                retard = temps['retard']
                statut = "🔴" if retard > 5 else "🟡" if retard > 2 else "🟢"
                print(f"   {route:20s} | Théorique: {temps['temps_theorique']:5.1f}min | "
                      f"Réel: {temps['temps_reel']:5.1f}min | {statut} {retard:+5.1f}min")
