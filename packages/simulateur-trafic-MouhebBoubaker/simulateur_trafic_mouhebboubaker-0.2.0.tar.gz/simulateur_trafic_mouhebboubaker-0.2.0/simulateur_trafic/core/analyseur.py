class Analyseur: 

    @staticmethod
    def calculeVitesseMoyen(reseau):
        try:
            vitesse=0
            nb=0

            for route in reseau.routes.values():
                for vehicule in route.vehicules:
                    vitesse+=vehicule.vitesse
                    nb+=1

            vitesseMoyen=vitesse/nb 
            return vitesseMoyen
        except ZeroDivisionError:
            print("Aucun véhicule dans le réseau pour calculer la vitesse moyenne.")
            return 0
    
    @staticmethod
    def obtenir_statistiques(reseau):
        """Retourne les statistiques complètes du réseau"""
        total_vehicules_actifs = sum(len(route.vehicules) for route in reseau.routes.values())
        total_longueur = sum(route.longueur for route in reseau.routes.values())
        
        return {
            "nombre_routes": len(reseau.routes),
            "total_vehicules_actifs": total_vehicules_actifs,
            "vehicules_sortis": len(reseau.vehicules_sortis),
            "total_longueur": total_longueur,
            "routes": {nom: len(route.vehicules) for nom, route in reseau.routes.items()},
            "connexions": reseau.connections
        }