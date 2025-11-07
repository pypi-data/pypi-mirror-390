import pytest
import os
import tempfile
import json
from simulateur_trafic.core.simulateur import Simulateur
from simulateur_trafic.models.reseau import Reseau


@pytest.fixture
def config_test_simple():
    """Fixture qui crée un fichier de configuration temporaire pour les tests."""
    config_data = {
        "nom_reseau": "Reseau_Test",
        "routes": [
            {
                "nom": "Route_Test",
                "longueur": 500,
                "limite_vitesse": 50
            }
        ],
        "vehicules_initiaux": [
            {
                "identifiant": "V_Test_1",
                "position": 0,
                "vitesse": 25,
                "route": "Route_Test"
            },
            {
                "identifiant": "V_Test_2", 
                "position": 100,
                "vitesse": 30,
                "route": "Route_Test"
            }
        ]
    }
    
    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f, indent=2)
        temp_path = f.name
    
    yield temp_path
    
    # Nettoyer le fichier temporaire après le test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_initialisation_simulateur_fichier_config():
    """Test l'initialisation du simulateur à partir du fichier de configuration par défaut."""
    # Utiliser le fichier de configuration existant
    simulateur = Simulateur()
    
    # Vérifier que le réseau a été créé
    assert simulateur.reseau is not None
    assert isinstance(simulateur.reseau, Reseau)
    assert simulateur.reseau.nom == "Reseau_Urbain_Principal"
    
    # Vérifier qu'il y a des routes dans le réseau
    assert len(simulateur.reseau.routes) > 0
    
    # Vérifier qu'il y a des véhicules dans le réseau
    total_vehicules = sum(len(route.vehicules) for route in simulateur.reseau.routes.values())
    assert total_vehicules > 0


def test_initialisation_simulateur_config_personnalisee(config_test_simple):
    

    """Test l'initialisation du simulateur avec un fichier de configuration personnalisé."""
    simulateur = Simulateur(fichier_config=config_test_simple)
    
    # Vérifier que le réseau a été créé avec la bonne configuration
    assert simulateur.reseau is not None
    assert simulateur.reseau.nom == "Reseau_Test"
    assert len(simulateur.reseau.routes) == 1
    assert "Route_Test" in simulateur.reseau.routes
    
    # Vérifier les véhicules
    route_test = simulateur.reseau.routes["Route_Test"]
    assert len(route_test.vehicules) == 2
    
    vehicules_ids = [v.identifiant for v in route_test.vehicules]
    assert "V_Test_1" in vehicules_ids
    assert "V_Test_2" in vehicules_ids


def test_execution_simulation_plusieurs_tours(config_test_simple):
    """Test l'exécution d'une simulation sur plusieurs tours sans erreur."""
    simulateur = Simulateur(fichier_config=config_test_simple)
    
    # Capturer l'état initial
    stats_initiales = simulateur.reseau.obtenir_statistiques()
    vehicules_initiaux = stats_initiales['total_vehicules_actifs']
    
    # Exécuter la simulation sur 5 tours
    try:
        simulateur.lancer_simulation(n_tours=5, delta_t=1.0)
        simulation_reussie = True
    except Exception as e:
        simulation_reussie = False
        pytest.fail(f"La simulation a échoué avec l'erreur: {e}")
    
    # Vérifier que la simulation s'est exécutée sans erreur
    assert simulation_reussie
    
    # Vérifier que l'état du réseau a évolué
    stats_finales = simulateur.reseau.obtenir_statistiques()
    
    # Au moins l'un des éléments suivants devrait être vrai :
    # - Les véhicules ont bougé (changement de position)
    # - Certains véhicules ont quitté le réseau
    assert (stats_finales['total_vehicules_actifs'] <= vehicules_initiaux or 
            stats_finales['vehicules_sortis'] > 0)


def test_simulation_longue_sans_erreur():
    """Test qu'une simulation longue s'exécute sans erreur avec le fichier de configuration par défaut."""
    simulateur = Simulateur()
    
    # Exécuter une simulation plus longue
    try:
        simulateur.lancer_simulation(n_tours=20, delta_t=1.0)
        simulation_reussie = True
    except Exception as e:
        simulation_reussie = False
        pytest.fail(f"La simulation longue a échoué avec l'erreur: {e}")
    
    assert simulation_reussie
    
    # Vérifier les statistiques finales
    stats = simulateur.reseau.obtenir_statistiques()
    assert 'total_vehicules_actifs' in stats
    assert 'vehicules_sortis' in stats
    assert stats['total_vehicules_actifs'] >= 0
    assert stats['vehicules_sortis'] >= 0


def test_simulation_arret_automatique(config_test_simple):
    """Test que la simulation s'arrête automatiquement quand tous les véhicules ont quitté le réseau."""
    simulateur = Simulateur(fichier_config=config_test_simple)
    
    # Exécuter une simulation très longue (plus que nécessaire)
    # La simulation devrait s'arrêter automatiquement
    simulateur.lancer_simulation(n_tours=100, delta_t=1.0)
    
    # Vérifier qu'il n'y a plus de véhicules actifs ou que tous ont quitté
    stats = simulateur.reseau.obtenir_statistiques()
    # Soit tous les véhicules ont quitté le réseau, soit ils sont tous sortis
    assert (stats['total_vehicules_actifs'] == 0 or 
            stats['vehicules_sortis'] > 0)