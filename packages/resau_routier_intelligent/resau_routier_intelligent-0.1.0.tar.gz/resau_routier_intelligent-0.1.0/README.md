# 🚳️ Réseau Routier Intelligent

**Réseau Routier Intelligent** est un simulateur Python orienté objet permettant de modéliser et de simuler un réseau routier intelligent.
Ce projet vise à offrir une architecture modulaire, extensible et testable, adaptée à la recherche ou à l’expérimentation dans le domaine de la mobilité intelligente.

---

## 🎯 Objectifs

* Concevoir une application orientée objet complète.
* Simuler un réseau routier avec plusieurs routes, intersections et véhicules.
* Mettre en œuvre des techniques avancées de programmation objet.
* Créer une architecture modulaire et testable.
* Visualiser les résultats sous forme graphique ou cartographique.

---

## 🧠 Contexte

Une start-up spécialisée dans la **mobilité intelligente** souhaite développer un **simulateur modulaire du trafic routier**, capable de :

* 🚳️ **Modéliser un réseau routier** (routes, intersections).
* 🚗 **Simuler la circulation de véhicules** avec des comportements variés.
* 📊 **Fournir des statistiques** sur les embouteillages, vitesses moyennes et temps de parcours.
* 🞺 **Générer des rapports** sous forme de logs, fichiers CSV ou visualisations cartographiques.

---

## 🌇️ Architecture

Le projet suit une approche **orientée objet** et une structure **modulaire** :

```
resau_routier_intelligent/
├── data/             #Fichier de configuration au format Json
├── core/             # Classes principales : Route, Intersection, Véhicule
├── simulation/       # Gestion du cycle de simulation et du moteur d’événements
├── models/            # Les modèles utilisés (route,vehicule,reseau)
|── ios/       # Génération et affichage des visualisations et des statistiques
|── exceptions/       # Exceptions personnalisées
└── tests/       # Tests unitaire
```

---

## ⚙️ Installation

Depuis **PyPI** (après publication) :

```bash
pip install resau_routier_intelligent
```

Ou depuis le dépôt GitHub :

```bash
git clone https://github.com/BenLazregAhmed/resau_routier_intelligent.git
cd resau_routier_intelligent
poetry install
```

---

## 🚀 Exemple d’utilisation

```python
"""
Point d'entrée principal du simulateur de trafic routier intelligent
Auteur: Simulateur IA
Date: 2025
"""
import cProfile
import pstats
import io
import os
import sys
import argparse
from pathlib import Path

# Ajout du répertoire racine au path pour les imports
sys.path.append(str(Path(__file__).parent))

from core.simulateur import Simulateur
from core.analyseur import Analyseur
from ios.affichage import AffichageConsole
from ios.export import ExportDonnees

def main():
    """Fonction principale du simulateur."""
    
    # Configuration des arguments en ligne de commande
    parser = argparse.ArgumentParser(description='Simulateur de Trafic Routier Intelligent')
    parser.add_argument('--config', '-c', 
                       default='../data/config_reseau.json',
                       help='Fichier de configuration du réseau (défaut: ../data/config_reseau.json)')
    parser.add_argument('--tours', '-t', 
                       type=int, default=60,
                       help='Nombre de tours de simulation (défaut: 60)')
    parser.add_argument('--delta', '-d', 
                       type=float, default=1.0,
                       help='Pas de temps en minutes (défaut: 1.0)')
    parser.add_argument('--export-csv', 
                       action='store_true',
                       help='Exporter les résultats en CSV')
    parser.add_argument('--export-json', 
                       action='store_true',
                       help='Exporter les résultats en JSON')
    parser.add_argument('--graphiques', '-g', 
                       action='store_true',
                       help='Générer des graphiques de visualisation')
    parser.add_argument('--silencieux', '-s', 
                       action='store_true',
                       help='Mode silencieux (pas d\'affichage détaillé)')
    parser.add_argument('--demo', 
                       action='store_true',
                       help='Lancer une démonstration rapide')
    
    args = parser.parse_args()
    
    # Mode démonstration
    if args.demo:
        lancer_demonstration()
        return
    
    try:
        print("🚗 SIMULATEUR DE TRAFIC ROUTIER INTELLIGENT")
        print("=" * 50)
        print(f"Configuration: {args.config}")
        print(f"Simulation: {args.tours} tours × {args.delta}min")
        print()
        
        # Initialisation du simulateur
        if not args.silencieux:
            print("🔧 Initialisation du simulateur...")
        
        simulateur = Simulateur(fichier_config=args.config)
        
        if not args.silencieux:
            afficher_configuration_reseau(simulateur)
        
        # Lancement de la simulation
        simulateur.lancer_simulation(n_tours=args.tours, delta_t=args.delta)
        
        # Analyse des résultats
        if not args.silencieux:
            print("\n🔍 Analyse des résultats...")
        
        analyseur = Analyseur(simulateur)
        
        # Affichage du rapport détaillé
        if not args.silencieux:
            AffichageConsole.afficher_rapport_detaille(analyseur)
        
        # Exports demandés
        exporteur = ExportDonnees(simulateur)
        
        if args.export_csv:
            nom_csv = f"resultats_{args.tours}tours_{args.delta}min.csv"
            exporteur.exporter_csv(nom_csv)
        
        if args.export_json:
            nom_json = f"resultats_{args.tours}tours_{args.delta}min.json"
            exporteur.exporter_json(nom_json)
        
        if args.graphiques:
            print("📊 Génération des graphiques...")
            exporteur.generer_graphiques()
        
        print("\n✅ Simulation terminée avec succès!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Simulation interrompue par l'utilisateur")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ Erreur: Fichier non trouvé - {e}")
        print("💡 Astuce: Utilisez --demo pour une démonstration avec configuration par défaut")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

def afficher_configuration_reseau(simulateur):
    """Affiche la configuration du réseau chargée."""
    reseau = simulateur.reseau
    config = simulateur.configuration
    
    print("🗺️  CONFIGURATION DU RÉSEAU:")
    print(f"   Routes: {len(reseau.routes)}")
    print(f"   Intersections: {len(reseau.intersections)}")
    print(f"   Véhicules initiaux: {len(reseau.vehicules)}")
    
    print("\n🛣️  ROUTES CONFIGURÉES:")
    for nom_route, route in reseau.routes.items():
        connexions = len(route.routes_connectees)
        print(f"   {nom_route:20s} | {route.longueur:4.1f}km | "
              f"{route.limite_vitesse:3.0f}km/h | {connexions} connexion(s)")
    
    if reseau.intersections:
        print(f"\n🚦 INTERSECTIONS:")
        for nom_intersection, routes_connectees in reseau.intersections.items():
            routes_str = ", ".join(routes_connectees)
            print(f"   {nom_intersection:15s} -> {routes_str}")
    
    print()

def lancer_demonstration():
    """Lance une démonstration rapide du simulateur."""
    print("🎯 MODE DÉMONSTRATION")
    print("=" * 40)
    
    # Configuration simplifiée pour la démo
    print("Création d'un réseau de démonstration...")
    
    simulateur = Simulateur()  # Configuration par défaut
    
    print("Configuration automatique terminée!")
    afficher_configuration_reseau(simulateur)
    
    # Simulation courte
    print("🚀 Lancement d'une simulation de 30 tours...")
    simulateur.lancer_simulation(n_tours=60, delta_t=1.0)
    
    # Analyse rapide
    analyseur = Analyseur(simulateur)
    AffichageConsole.afficher_rapport_detaille(analyseur)
    
    # Export JSON automatique
    exporteur = ExportDonnees(simulateur)
    exporteur.exporter_json("demo_resultats.json")
    
    print("\n🎉 Démonstration terminée!")
    print("💡 Pour une simulation personnalisée, utilisez: python main.py --config votre_config.json")

def verifier_dependances():
    """Vérifie que toutes les dépendances sont installées."""
    dependances_manquantes = []
    
    try:
        import matplotlib
    except ImportError:
        dependances_manquantes.append("matplotlib")
    
    try:
        import pandas
    except ImportError:
        dependances_manquantes.append("pandas")
    
    try:
        import numpy
    except ImportError:
        dependances_manquantes.append("numpy")
    
    if dependances_manquantes:
        print("❌ Dépendances manquantes:")
        for dep in dependances_manquantes:
            print(f"   - {dep}")
        print("\n💡 Installez avec: pip install " + " ".join(dependances_manquantes))
        return False
    
    return True

if __name__ == "__main__":
    if not verifier_dependances():
        print("\n⚠️  Certaines fonctionnalités peuvent être limitées.")
        input("Appuyez sur Entrée pour continuer quand même...")

    print("\n📈 Démarrage du profilage de la simulation...\n")

    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()
    print("\n📊 Profilage terminé. Analyse des résultats...\n")

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumtime")
    ps.print_stats(30)  # affiche les 30 fonctions les plus coûteuses
    print(s.getvalue())

python main.py --config <path to your config file or leave empty to use the default one> --tours 60 --export-csv --export-json
```

---

## 📊 Fonctionnalités prévues

| Fonctionnalité                                | Statut              |
| --------------------------------------------- | ------------------- |
| Modélisation des routes et intersections      | ✅                   |
| Simulation de circulation de véhicules        | ✅                   |
| Calcul de statistiques (vitesses, congestion) | ✅                   |
| Génération de rapports (console / CSV)        | ✅                   |
| Visualisation graphique du réseau             | 🔄 En développement |

---
## Exemple d'exécution

📈 Démarrage du profilage de la simulation...

🚗 SIMULATEUR DE TRAFIC ROUTIER INTELLIGENT
==================================================
Configuration: C:\Users\21656\Desktop\ING3\python\tp\tp1\resau_routier_intelligent\data\config_reseau.json
Simulation: 60 tours × 1.0min

🔧 Initialisation du simulateur...
🗺️  CONFIGURATION DU RÉSEAU:
   Routes: 2
   Intersections: 0
   Véhicules initiaux: 0

🛣️  ROUTES CONFIGURÉES:
   A1                   | 5000.0km |  90km/h | 0 connexion(s)
   B1                   | 3000.0km |  50km/h | 0 connexion(s)

🚗 Démarrage de la simulation (60 tours, Δt=1.0min)
============================================================
Tour   0/60 (  0.0%) | Véhicules:   1 | Temps:    1.0min
Tour  10/60 ( 16.7%) | Véhicules:   5 | Temps:   11.0min
Tour  20/60 ( 33.3%) | Véhicules:   8 | Temps:   21.0min
Tour  30/60 ( 50.0%) | Véhicules:  12 | Temps:   31.0min
Tour  40/60 ( 66.7%) | Véhicules:  16 | Temps:   41.0min
Tour  50/60 ( 83.3%) | Véhicules:  18 | Temps:   51.0min

✅ Simulation terminée!

📊 RÉSUMÉ DE LA SIMULATION
========================================
Durée totale: 60.0 minutes
Nombre de véhicules: 19
Nombre de routes: 2

🛣️  ÉTAT DES ROUTES:
  A1              | 12 véh. | Vitesse:  78.8 km/h | 🟢 Fluide
  B1              |  7 véh. | Vitesse:  50.0 km/h | 🟢 Fluide

🔍 Analyse des résultats...

================================================================================

📈 RAPPORT DÉTAILLÉ DE SIMULATION

================================================================================

🌐 PERFORMANCES GLOBALES:
   Vitesse moyenne du réseau: 55.4 km/h
   Densité moyenne du trafic: 0.0 véh/km
   Pic de véhicules simultanés: 19

🟢 TRAFIC FLUIDE: Aucune zone de congestion détectée

⏱️  TEMPS DE PARCOURS:
   A1                   | Théorique: 3333.3min | Réel: 3807.2min | 🔴 +473.8min
   B1                   | Théorique: 3600.0min | Réel: 3600.0min | 🟢  +0.0min

✅ Simulation terminée avec succès!

📊 Profilage terminé. Analyse des résultats...

---

## 🧩 Dépendances

Aucune dépendance externe obligatoire.
Optionnellement, certaines extensions pourront utiliser :

* `matplotlib` ou `folium` pour la visualisation
* `pandas` pour l’analyse de données

---

## 🧪 Tests

Pour exécuter les tests unitaires :

```bash
poetry run pytest
```

---

## 📄 Licence

Distribué sous la licence **MIT**.
Voir le fichier [LICENSE](./LICENSE) pour plus d’informations.

---

## 👤 Auteur

**Ahmed BenLazreg**
📧 [benlazregahmed328@gmail.com](mailto:benlazregahmed328@gmail.com)
🔗 [GitHub – BenLazregAhmed](https://github.com/BenLazregAhmed)
🔗 [LinkedIn – Ahmed BenLazreg](https://www.linkedin.com/in/ahmed-benlazreg-9b34a6261/)

---

## 🌟 Contributions

Les contributions sont les bienvenues !
N’hésitez pas à ouvrir une **issue** ou à proposer une **pull request** pour améliorer le simulateur.
