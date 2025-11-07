#!/usr/bin/env python3
"""
Module simple pour profiler le simulateur de trafic avec cProfile
"""

import cProfile
import pstats
import os
import sys

def profiler_simulation():
    """Lance une simulation simple et profile les performances"""
    
    # Ajouter le répertoire parent au path pour importer les modules
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from simulateur_trafic.core.simulateur import Simulateur
        from simulateur_trafic.models.reseau import Reseau
        from simulateur_trafic.models.route import Route
        from simulateur_trafic.models.vehicule import Vehicule
        
        def simulation_simple():
            """Simulation simple à profiler"""
            # Créer le simulateur avec la configuration par défaut
            simulateur = Simulateur()  # Utilise la config par défaut
            
            if simulateur.reseau is None:
                print("Erreur: Impossible de charger le réseau")
                return None
            
            # Ajouter quelques véhicules pour tester
            routes = list(simulateur.reseau.routes.values())
            if routes:
                route_principale = routes[0]
                for i in range(10):  # 10 véhicules pour tester
                    vehicule = Vehicule(f"Test_V{i}", vitesse=25 + i % 15)
                    route_principale.ajouter_vehicule(vehicule)
            
            # Lancer la simulation
            simulateur.lancer_simulation(n_tours=20, delta_t=1)  # 20 tours
                
            return simulateur
        
        # Lancer le profiling
        print("Démarrage du profiling...")
        profiler = cProfile.Profile()
        profiler.enable()
        
        # Exécuter la simulation
        resultat = simulation_simple()
        
        profiler.disable()
        
        # Sauvegarder les résultats
        profiler.dump_stats('simulation_profile.prof')
        
        # Afficher les résultats
        print("\n" + "="*60)
        print("RÉSULTATS DU PROFILING")
        print("="*60)
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 des fonctions les plus coûteuses
        
        print("\n" + "="*60)
        print("Fichier 'simulation_profile.prof' créé.")
        print("Utilisez 'snakeviz simulation_profile.prof' pour une visualisation graphique")
        print("="*60)
        
        return resultat
        
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        print("Assurez-vous que tous les modules sont présents")
    except Exception as e:
        print(f"Erreur lors du profiling: {e}")

if __name__ == "__main__":
    profiler_simulation()