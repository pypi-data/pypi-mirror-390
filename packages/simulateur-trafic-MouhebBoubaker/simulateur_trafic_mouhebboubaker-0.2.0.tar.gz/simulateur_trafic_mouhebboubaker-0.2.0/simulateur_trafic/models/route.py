class Route:
    def __init__(self, nom, longueur, limite_vitesse):
        self.nom = nom
        self.longueur = longueur
        self.limite_vitesse = limite_vitesse
        self.vehicules = []

    def ajouter_vehicule(self, vehicule):

        try:
            # Vérifier si le véhicule est déjà sur la route
            if vehicule in self.vehicules:
                raise ValueError(f"Erreur : le véhicule {vehicule.identifiant} est déjà présent sur la route {self.nom}.")
            
            # Ajouter le véhicule
            self.vehicules.append(vehicule)
            vehicule.route_actuelle = self
            
        except ValueError as e:
            # Afficher un message clair sans faire planter le programme
            print(e)           
        
    def retirer_vehicule(self, vehicule):
        """Retire un véhicule de cette route"""
        if vehicule in self.vehicules:
            self.vehicules.remove(vehicule)

    def mettre_a_jour_vehicules(self):
        """Met à jour tous les véhicules de cette route"""
        vehicules_a_retirer = []
        
        for vehicule in self.vehicules:
            print(f"Mise à jour véhicule -> {vehicule.identifiant} sur route {self.nom}")
            
            # Limiter la vitesse selon la limite de la route
            vehicule.vitesse = min(vehicule.vitesse, self.limite_vitesse)
            
            # Faire avancer le véhicule
            fin_de_route = vehicule.avancer()
            
            # Si le véhicule a atteint la fin, le marquer pour changement de route
            if fin_de_route:
                vehicules_a_retirer.append(vehicule)
        
        return vehicules_a_retirer  # Retourner les véhicules qui doivent changer de route