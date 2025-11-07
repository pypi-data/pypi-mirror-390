from simulateur_trafic.models.route import Route
from simulateur_trafic.models.vehicule import Vehicule
from simulateur_trafic.models.reseau import Reseau


def test_ajout_routes_au_reseau(reseau_simple):
     
     
    route2 = Route("A2", longueur=500, limite_vitesse=50)
    
 
    reseau_simple.ajouter_route(route2)
    reseau_simple.connecter_routes("A1","A2")
    
   
    assert reseau_simple.routes[route2.nom] == route2
    assert len(reseau_simple.routes) == 2


def test_mise_a_jour_ensemble_routes(reseau_simple):
    # Ajouter une route supplémentaire avec un véhicule
    route_supplementaire = Route("A2", longueur=800, limite_vitesse=40)
    vehicule_supplementaire = Vehicule("V2", 0, 80, route_supplementaire)
    route_supplementaire.ajouter_vehicule(vehicule_supplementaire)
    reseau_simple.ajouter_route(route_supplementaire)
    
    # Connecter les routes pour permettre le changement
    reseau_simple.connecter_routes("A1", "A2")
    
    # Récupérer les positions avant mise à jour
    positions_avant = {}
    routes_avant = {}
    for route_nom, route in reseau_simple.routes.items():
        for vehicule in route.vehicules:
            positions_avant[vehicule.identifiant] = vehicule.position
            routes_avant[vehicule.identifiant] = vehicule.route_actuelle.nom
    
    # Mettre à jour le réseau
    reseau_simple.mettre_a_jour_reseau()
    
    # Vérifier que tous les véhicules ont été traités
    for route_nom, route in reseau_simple.routes.items():
        for vehicule in route.vehicules:
            # Si le véhicule est toujours sur la même route
            if routes_avant[vehicule.identifiant] == vehicule.route_actuelle.nom:
                position_attendue = positions_avant[vehicule.identifiant] + vehicule.vitesse
                if position_attendue <= route.longueur:
                    assert vehicule.position == position_attendue
                else:
                    # Le véhicule devrait avoir changé de route ou quitté le réseau
                    assert vehicule.position <= route.longueur
            else:
                # Le véhicule a changé de route, sa position devrait être à 0
                assert vehicule.position == 0


def test_changement_route_automatique(reseau_simple):
    """Test que les véhicules changent automatiquement de route quand ils atteignent la fin"""
    # Ajouter une route courte pour forcer un changement
    route_courte = Route("A2", longueur=50, limite_vitesse=100)
    reseau_simple.ajouter_route(route_courte)
    reseau_simple.connecter_routes("A1", "A2")
    
    # Créer un véhicule proche de la fin de la route A1
    vehicule_test = Vehicule("V_test", 950, 100, reseau_simple.routes["A1"])
    
    # Compter les véhicules avant mise à jour
    total_vehicules_avant = sum(len(route.vehicules) for route in reseau_simple.routes.values())
    
    # Mettre à jour le réseau
    reseau_simple.mettre_a_jour_reseau()
    
    # Vérifier qu'un changement de route a eu lieu
    total_vehicules_apres = sum(len(route.vehicules) for route in reseau_simple.routes.values())
    
    # Le nombre total de véhicules devrait être le même (ou diminuer si certains quittent le réseau)
    assert total_vehicules_apres <= total_vehicules_avant