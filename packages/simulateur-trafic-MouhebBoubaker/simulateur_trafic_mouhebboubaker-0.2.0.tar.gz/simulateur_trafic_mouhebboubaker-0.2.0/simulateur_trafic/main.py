from core.simulateur import Simulateur

sim=Simulateur(fichier_config="./data/config_reseau.json")
sim.lancer_simulation(n_tours=60,delta_t=60) #60 minutes ,pas de 1 min

