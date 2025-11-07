from simulateur_trafic.models.vehicule import Vehicule
 

def test_ajout_vehicule(route_simple):
    vehicule = Vehicule("V1", 0, 100, None)
    route_simple.ajouter_vehicule(vehicule)
    assert vehicule in route_simple.vehicules



def test_mise_a_jour_avance_vehicules(route_simple):
     
    vehicule1 = Vehicule("V1", 0, 100, route_simple)
    vehicule2 = Vehicule("V2", 0, 150, route_simple)
    route_simple.ajouter_vehicule(vehicule1)
    route_simple.ajouter_vehicule(vehicule2)

    positions_avant = [v.position for v in route_simple.vehicules]
    route_simple.mettre_a_jour_vehicules()

    positions_apres = [v.position for v in route_simple.vehicules]
    for avant, apres, v in zip(positions_avant, positions_apres, route_simple.vehicules):
        assert apres == avant + v.vitesse