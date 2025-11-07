import random

class Vehicule:
    def __init__(self, identifiant, position=0, vitesse=0, route_actuelle=None):
        self.identifiant = identifiant
        self.position = position
        self.vitesse = vitesse
        self.route_actuelle = route_actuelle
        if(route_actuelle!=None):
            route_actuelle.vehicules.append(self)
        self.historique_routes = []  # Pour suivre le chemin parcouru
        self.distance_totale_parcourue = 0
    
    def avancer(self):


        if self.vitesse < 0:
            raise ValueError("Erreur : la vitesse ne peut pas être négative.")

        """Avance le véhicule selon sa vitesse"""
        if self.route_actuelle:
            ancienne_position = self.position
            self.position += self.vitesse
            
            # Calculer la distance parcourue
            distance_parcourue = self.vitesse
            self.distance_totale_parcourue += distance_parcourue
            
            # Vérifier si le véhicule a atteint la fin de la route
            if self.position >= self.route_actuelle.longueur:
                self.position = self.route_actuelle.longueur
                return True  # Indique qu'il faut changer de route
            
            return False  # Le véhicule continue sur la même route
    
    def changer_de_route(self, nouvelle_route):
        """Change le véhicule vers une nouvelle route"""
        # Retirer le véhicule de l'ancienne route
    
        self.route_actuelle.vehicules.remove(self)
        # Ajouter l'ancienne route à l'historique
        self.historique_routes.append(self.route_actuelle.nom)
        # Ajouter à la nouvelle route
        self.route_actuelle = nouvelle_route
        self.position = 0  # Commencer au début de la nouvelle route
        nouvelle_route.ajouter_vehicule(self)
    
    
    def obtenir_statistiques(self):
        """Retourne les statistiques du véhicule"""
        return {
            "identifiant": self.identifiant,
            "position": self.position,
            "vitesse": self.vitesse,
            "route_actuelle": self.route_actuelle.nom if self.route_actuelle else None,
            "distance_totale_parcourue": self.distance_totale_parcourue,
            "routes_visitees": len(self.historique_routes),
            "historique_routes": self.historique_routes
        }