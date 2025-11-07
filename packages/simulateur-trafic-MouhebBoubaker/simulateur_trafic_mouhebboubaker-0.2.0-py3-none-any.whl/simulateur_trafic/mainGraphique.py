from ioo.affichage import simuler_reseau_graphique
from models.vehicule import Vehicule
from models.route import Route
from core.simulateur import Simulateur
import os



def simulation_reseau():

    """Simulation graphique d'un réseau complet"""
  
    try:
        sim=Simulateur(fichier_config="./data/config_reseau.json")
        reseau=sim.reseau
        simuler_reseau_graphique(reseau)
    except Exception as e:
        print(f"Erreur lors du chargement du réseau: {e}")
        print("Utilisation de la simulation simple...")
         

if __name__=="__main__":
 
    simulation_reseau()