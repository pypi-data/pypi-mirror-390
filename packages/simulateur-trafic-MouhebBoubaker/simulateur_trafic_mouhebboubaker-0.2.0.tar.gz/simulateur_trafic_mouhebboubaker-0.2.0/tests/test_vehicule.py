
def test_verefie_avance(vehicule_exemple):
    assert vehicule_exemple.position==0
    nouveau_position=vehicule_exemple.position+vehicule_exemple.vitesse
    vehicule_exemple.avancer() 
    assert vehicule_exemple.position==nouveau_position

def test_verifie_longuer(vehicule_exemple):

    for i in range(20) :
        vehicule_exemple.avancer()
    assert vehicule_exemple.position<=vehicule_exemple.route_actuelle.longueur

def test_changement_route_remet_position_zero(vehicule_exemple, route_simple):
    # Création d'une nouvelle route
    from simulateur_trafic.models.route import Route
    nouvelle_route = Route("A2", 500, 20)
    vehicule_exemple.avancer()
    assert vehicule_exemple.position > 0
    vehicule_exemple.changer_de_route(nouvelle_route)
    assert vehicule_exemple.position == 0
    assert vehicule_exemple.route_actuelle == nouvelle_route
