import os
import json
from simulateur_trafic.models.reseau import Reseau
from simulateur_trafic.models.route import Route
from simulateur_trafic.models.vehicule import Vehicule
from simulateur_trafic.core.analyseur import Analyseur

class Simulateur:
    def __init__(self, fichier_config=None):
        """
        Initialise le simulateur à partir d'un fichier de configuration JSON.
        Gère les erreurs liées à la lecture du fichier ou à son contenu.
        """
        if fichier_config is None:
            # Configuration par défaut incluse dans le package
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(script_dir, "data", "config_reseau.json")
        elif os.path.isabs(fichier_config):
            config_path = fichier_config
        else:
            config_path = os.path.abspath(fichier_config)

        print(f"Recherche du fichier de configuration: {config_path}")

        try:
            # Lecture du fichier de configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Validation du contenu
            if not Simulateur.valider_configuration(config):
                raise ValueError("Erreur : la configuration du réseau est invalide.")

            # Création du réseau
            reseau = Reseau(nom=config.get('nom_reseau', 'Reseau_Par_Defaut'))

            # Chargement des routes
            for route_config in config.get("routes", []):
                route = Route(
                    nom=route_config['nom'],
                    longueur=route_config['longueur'],
                    limite_vitesse=route_config['limite_vitesse']
                )
                reseau.ajouter_route(route)

            # Connexions entre routes
            for connexion in config.get('connexions', []):
                reseau.connecter_routes(connexion['route1'], connexion['route2'])

            # Véhicules initiaux
            for vehicule_config in config.get('vehicules_initiaux', []):
                route = reseau.routes.get(vehicule_config['route'])
                if route:
                    vehicule = Vehicule(
                        identifiant=vehicule_config['identifiant'],
                        position=vehicule_config.get('position', 0),
                        vitesse=vehicule_config.get('vitesse', 0),
                        route_actuelle=route
                    )
                    route.ajouter_vehicule(vehicule)

            self.reseau = reseau
            print(f"✅ Réseau chargé : {self.reseau.nom}")
            print(f"Nombre de routes : {len(self.reseau.routes)}")

        except FileNotFoundError:
            print(f"❌ Erreur : Fichier de configuration '{config_path}' non trouvé.")
            self.reseau = None

        except json.JSONDecodeError as e:
            print(f"❌ Erreur : Format JSON invalide dans '{config_path}' : {e}")
            self.reseau = None

        except ValueError as e:
            print(f"❌ {e}")
            self.reseau = None


    @staticmethod
    def valider_configuration(config):
        """Valide la structure du fichier de configuration."""
        champs_requis = ['routes', 'connexions']

        for champ in champs_requis:
            if champ not in config:
                print(f"Erreur : Champ '{champ}' manquant dans la configuration.")
                return False

        for route in config['routes']:
            if not all(key in route for key in ['nom', 'longueur', 'limite_vitesse']):
                print(f"Erreur : Route invalide : {route}")
                return False

        return True


    def lancer_simulation(self, n_tours, delta_t):
        """
        Lance la simulation pour n_tours pas de temps.
        Gère les erreurs si les paramètres sont invalides.
        """
        try:
            if n_tours <= 0 or delta_t <= 0:
                raise ValueError("Le nombre d’itérations et le delta_t doivent être positifs.")

            if not self.reseau:
                raise ValueError("Aucun réseau n’a été chargé, la simulation ne peut pas démarrer.")

            print("\n=== État initial du réseau ===")
            for nom_route, route in self.reseau.routes.items():
                print(f"\nRoute {nom_route} (longueur: {route.longueur}):")
                for vehicule in route.vehicules:
                    print(f"  {vehicule.identifiant} - Position: {vehicule.position}, Vitesse: {vehicule.vitesse}")

            print("\n=== Simulation en cours ===")
            for pas in range(n_tours):
                print(f"\n{'='*50}")
                print(f"--- Pas de temps {pas + 1} ---")

                # État avant mise à jour
                for nom_route, route in self.reseau.routes.items():
                    if route.vehicules:
                        vehicules_info = [f"{v.identifiant}({v.position:.1f})" for v in route.vehicules]
                        print(f"  {nom_route}: {vehicules_info}")

                # Mise à jour
                self.reseau.mettre_a_jour_reseau()

                # État après mise à jour
                for nom_route, route in self.reseau.routes.items():
                    if route.vehicules:
                        vehicules_info = [f"{v.identifiant}({v.position:.1f})" for v in route.vehicules]
                        print(f"  {nom_route}: {vehicules_info}")

                stats = Analyseur.obtenir_statistiques(self.reseau)
                print(f"Véhicules actifs: {stats['total_vehicules_actifs']}, Véhicules sortis: {stats['vehicules_sortis']}")

                if stats['total_vehicules_actifs'] == 0:
                    print("\n🏁 Tous les véhicules ont quitté le réseau!")
                    break


            # Statistiques finales
            print(f"\n{'='*50}")
            print("=== Statistiques finales ===")
            stats = Analyseur.obtenir_statistiques(self.reseau)
            for key, value in stats.items():
                print(f"{key}: {value}")
            
            # Statistiques des véhicules sortis
            if self.reseau.vehicules_sortis:
                print("\n=== Véhicules qui ont quitté le réseau ===")
                for vehicule in self.reseau.vehicules_sortis:
                    vehicule_stats = vehicule.obtenir_statistiques()
                    print(f"{vehicule.identifiant}:")
                    print(f"  - Distance totale: {vehicule_stats['distance_totale_parcourue']}")
                    print(f"  - Routes visitées: {vehicule_stats['routes_visitees']}")
                    print(f"  - Historique: {vehicule_stats['historique_routes']}")

        except ValueError as e:
            print(f"❌ Erreur : {e}")

        except Exception as e:
            print(f"⚠️ Une erreur inattendue est survenue pendant la simulation : {e}")

