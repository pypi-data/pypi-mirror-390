import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Rectangle, Circle
import matplotlib.patches as mpatches

def simuler_graphique(route):
    """Simulation graphique d'une route simple avec améliorations visuelles"""
    fig, (ax_main, ax_stats) = plt.subplots(2, 1, figsize=(14, 8), 
                                           gridspec_kw={'height_ratios': [3, 1]})
    
    # Configuration de l'axe principal
    ax_main.set_xlim(-50, route.longueur + 50)
    ax_main.set_ylim(-1.5, 1.5)
    
    # Dessiner la route avec des bandes
    route_width = 0.4
    ax_main.add_patch(Rectangle((0, -route_width/2), route.longueur, route_width, 
                               facecolor='gray', alpha=0.7, label='Route'))
    
    # Lignes de démarcation
    ax_main.plot([0, route.longueur], [0, 0], 'w--', linewidth=2, alpha=0.8)
    
    # Marqueurs de distance
    for i in range(0, int(route.longueur), 100):
        ax_main.axvline(x=i, color='yellow', linestyle=':', alpha=0.5)
        ax_main.text(i, -1.2, f'{i}m', ha='center', fontsize=8)
    
    # Véhicules
    vehicle_circles = []
    vehicle_texts = []
    
    def init():
        for circle in vehicle_circles:
            circle.remove()
        for text in vehicle_texts:
            text.remove()
        vehicle_circles.clear()
        vehicle_texts.clear()
        return []
    
    def update(frame):
        # Nettoyer les anciens éléments
        for circle in vehicle_circles:
            circle.remove()
        for text in vehicle_texts:
            text.remove()
        vehicle_circles.clear()
        vehicle_texts.clear()
        
        # Mettre à jour la route
        route.mettre_a_jour_vehicules()
        
        # Dessiner les véhicules
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        for i, vehicule in enumerate(route.vehicules):
            color = colors[i % len(colors)]
            
            # Cercle pour le véhicule
            circle = Circle((vehicule.position, 0), 15, color=color, zorder=5)
            ax_main.add_patch(circle)
            vehicle_circles.append(circle)
            
            # Texte avec l'identifiant
            text = ax_main.text(vehicule.position, 0.6, vehicule.identifiant, 
                               ha='center', va='center', fontweight='bold', 
                               fontsize=10, color='white',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.8))
            vehicle_texts.append(text)
            
            # Vitesse affichée
            speed_text = ax_main.text(vehicule.position, -0.8, f'{vehicule.vitesse:.0f} km/h', 
                                     ha='center', fontsize=8, color=color)
            vehicle_texts.append(speed_text)
        
        # Mise à jour des statistiques
        ax_stats.clear()
        ax_stats.set_xlim(0, 10)
        ax_stats.set_ylim(0, len(route.vehicules) + 1)
        
        for i, vehicule in enumerate(route.vehicules):
            y_pos = len(route.vehicules) - i
            ax_stats.text(0.5, y_pos, f"{vehicule.identifiant}:", fontweight='bold')
            ax_stats.text(2, y_pos, f"Pos: {vehicule.position:.1f}m")
            ax_stats.text(4.5, y_pos, f"Vitesse: {vehicule.vitesse:.0f} km/h")
            ax_stats.text(7, y_pos, f"Distance: {vehicule.distance_totale_parcourue:.0f}m")
        
        ax_stats.set_title("Statistiques des véhicules", fontweight='bold')
        ax_stats.axis('off')
        
        print(f"\n=== Frame {frame + 1} ===")
        for v in route.vehicules:
            print(f"  {v.identifiant} - Position: {v.position:.2f}m, Vitesse: {v.vitesse}km/h")
        
        return vehicle_circles + vehicle_texts
    
    # Configuration des axes
    ax_main.set_title(f"Simulation de trafic - Route {route.nom} (Longueur: {route.longueur}m, Limite: {route.limite_vitesse} km/h)", 
                     fontweight='bold', fontsize=12)
    ax_main.set_xlabel("Distance (mètres)", fontweight='bold')
    ax_main.set_ylabel("Voies", fontweight='bold')
    ax_main.grid(True, alpha=0.3)
    
    # Animation
    ani = animation.FuncAnimation(fig, update, frames=20, init_func=init, 
                                 interval=500, repeat=True, blit=False)
    
    plt.tight_layout()
    plt.show()
    return ani

def simuler_reseau_graphique(reseau):
    """Simulation graphique d'un réseau de routes avec améliorations visuelles"""
    fig = plt.figure(figsize=(16, 10))
    
    # Créer une grille pour l'affichage
    gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], width_ratios=[3, 1])
    ax_main = fig.add_subplot(gs[0, :])
    ax_stats = fig.add_subplot(gs[1, 0])
    ax_network = fig.add_subplot(gs[1, 1])
    ax_history = fig.add_subplot(gs[2, :])
    
    # Configuration des positions des routes pour l'affichage
    positions_routes = {}
    colors_routes = {}
    route_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    # Organiser les routes en réseau 2D
    if len(reseau.routes) <= 4:
        positions = [(0, 0), (800, 0), (0, -400), (800, -400)]
    else:
        # Disposition circulaire pour plus de routes
        angles = np.linspace(0, 2*np.pi, len(reseau.routes), endpoint=False)
        radius = 300
        positions = [(radius * np.cos(angle), radius * np.sin(angle)) for angle in angles]
    
    for i, (nom_route, route) in enumerate(reseau.routes.items()):
        positions_routes[nom_route] = positions[i % len(positions)]
        colors_routes[nom_route] = route_colors[i % len(route_colors)]
    
    # Dessiner les routes comme des segments
    route_lines = {}
    route_patches = {}
    
    for nom_route, route in reseau.routes.items():
        x, y = positions_routes[nom_route]
        color = colors_routes[nom_route]
        
        # Route horizontale
        route_patch = Rectangle((x, y-20), route.longueur/5, 40, 
                               facecolor=color, alpha=0.6, 
                               edgecolor='black', linewidth=2)
        ax_main.add_patch(route_patch)
        route_patches[nom_route] = route_patch
        
        # Étiquette de la route
        ax_main.text(x + route.longueur/10, y, nom_route, 
                    ha='center', va='center', fontweight='bold', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # Afficher la longueur et la vitesse limite
        ax_main.text(x + route.longueur/10, y-60, 
                    f'{route.longueur}m\n{route.limite_vitesse} km/h', 
                    ha='center', va='center', fontsize=8)
    
    # Dessiner les connexions
    for route1_nom, routes_connectees in reseau.connections.items():
        x1, y1 = positions_routes[route1_nom]
        x1 += reseau.routes[route1_nom].longueur/10  # Centre de la route
        
        for route2_nom in routes_connectees:
            if route1_nom < route2_nom:  # Éviter les doublons
                x2, y2 = positions_routes[route2_nom]
                x2 += reseau.routes[route2_nom].longueur/10
                
                ax_main.plot([x1, x2], [y1, y2], 'k--', alpha=0.5, linewidth=2)
                
                # Flèche pour indiquer la direction
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                ax_main.scatter(mid_x, mid_y, c='black', s=50, marker='o', alpha=0.7)
    
    # Variables pour l'animation
    vehicle_objects = {}
    vehicle_texts = {}
    frame_data = []  # Pour l'historique
    
    def init():
        for obj in vehicle_objects.values():
            if hasattr(obj, 'remove'):
                obj.remove()
        for text in vehicle_texts.values():
            text.remove()
        vehicle_objects.clear()
        vehicle_texts.clear()
        return []
    
    def update(frame):
        # Sauvegarder l'état actuel pour l'historique
        current_state = {}
        for route_nom, route in reseau.routes.items():
            current_state[route_nom] = [(v.identifiant, v.position, v.vitesse) for v in route.vehicules]
        frame_data.append(current_state)
        
        # Nettoyer les anciens objets
        for obj in vehicle_objects.values():
            if hasattr(obj, 'remove'):
                obj.remove()
        for text in vehicle_texts.values():
            text.remove()
        vehicle_objects.clear()
        vehicle_texts.clear()
        
        # Mettre à jour le réseau
        reseau.mettre_a_jour_reseau()
        
        # Dessiner les véhicules
        vehicle_colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink']
        all_vehicles = []
        
        for route_nom, route in reseau.routes.items():
            route_x, route_y = positions_routes[route_nom]
            
            for i, vehicule in enumerate(route.vehicules):
                # Position du véhicule sur la route visuelle
                progress = vehicule.position / route.longueur
                vehicle_x = route_x + progress * (route.longueur / 5)
                vehicle_y = route_y + (i - len(route.vehicules)/2) * 15  # Décaler verticalement
                
                color = vehicle_colors[hash(vehicule.identifiant) % len(vehicle_colors)]
                
                # Cercle pour le véhicule
                circle = Circle((vehicle_x, vehicle_y), 8, color=color, zorder=10)
                ax_main.add_patch(circle)
                vehicle_objects[vehicule.identifiant] = circle
                
                # Texte avec l'identifiant
                text = ax_main.text(vehicle_x, vehicle_y + 20, vehicule.identifiant, 
                                   ha='center', va='center', fontsize=8, fontweight='bold')
                vehicle_texts[vehicule.identifiant] = text
                
                all_vehicles.append(vehicule)
        
        # Mise à jour des statistiques
        ax_stats.clear()
        stats = reseau.obtenir_statistiques()
        
        stats_text = f"""STATISTIQUES DU RÉSEAU
        
Routes: {stats['nombre_routes']}
Véhicules actifs: {stats['total_vehicules_actifs']}
Véhicules sortis: {stats['vehicules_sortis']}
Longueur totale: {stats['total_longueur']}m

VÉHICULES PAR ROUTE:"""
        
        for route_nom, nb_vehicules in stats['routes'].items():
            if nb_vehicules > 0:
                stats_text += f"\n{route_nom}: {nb_vehicules}"
        
        ax_stats.text(0.05, 0.95, stats_text, transform=ax_stats.transAxes, 
                     verticalalignment='top', fontsize=10, fontfamily='monospace')
        ax_stats.set_title("Statistiques", fontweight='bold')
        ax_stats.axis('off')
        
        # Graphique du réseau (diagramme de connexions)
        ax_network.clear()
        ax_network.set_title("Connexions du réseau", fontweight='bold')
        
        # Créer un graphique simple des connexions
        pos_net = {}
        for i, nom in enumerate(reseau.routes.keys()):
            angle = 2 * np.pi * i / len(reseau.routes)
            pos_net[nom] = (np.cos(angle), np.sin(angle))
        
        # Dessiner les nœuds
        for nom, (x, y) in pos_net.items():
            nb_vehicules = len(reseau.routes[nom].vehicules)
            size = 100 + nb_vehicules * 50
            ax_network.scatter(x, y, s=size, c=colors_routes[nom], alpha=0.7)
            ax_network.text(x, y, nom, ha='center', va='center', fontsize=8, fontweight='bold')
        
        # Dessiner les connexions
        for route1, routes_conn in reseau.connections.items():
            x1, y1 = pos_net[route1]
            for route2 in routes_conn:
                if route1 < route2:
                    x2, y2 = pos_net[route2]
                    ax_network.plot([x1, x2], [y1, y2], 'k-', alpha=0.5, linewidth=2)
        
        ax_network.set_xlim(-1.5, 1.5)
        ax_network.set_ylim(-1.5, 1.5)
        ax_network.axis('off')
        
        # Historique des mouvements
        ax_history.clear()
        if len(frame_data) > 1:
            # Graphique simple du nombre de véhicules par route au fil du temps
            frames = range(len(frame_data))
            for route_nom in reseau.routes.keys():
                counts = [len(frame_data[f].get(route_nom, [])) for f in frames]
                ax_history.plot(frames, counts, marker='o', label=route_nom, 
                               color=colors_routes[route_nom])
            
            ax_history.set_title("Évolution du nombre de véhicules par route", fontweight='bold')
            ax_history.set_xlabel("Temps (frames)")
            ax_history.set_ylabel("Nombre de véhicules")
            ax_history.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax_history.grid(True, alpha=0.3)
        
        # Configuration de l'axe principal
        ax_main.set_xlim(-100, max(pos[0] + reseau.routes[nom].longueur/5 + 100 
                                  for nom, pos in positions_routes.items()))
        ax_main.set_ylim(min(pos[1] for pos in positions_routes.values()) - 150,
                        max(pos[1] for pos in positions_routes.values()) + 150)
        ax_main.set_title(f"Simulation du réseau {reseau.nom} - Frame {frame + 1}", 
                         fontweight='bold', fontsize=14)
        ax_main.set_xlabel("Distance (mètres)", fontweight='bold')
        ax_main.set_ylabel("Position Y", fontweight='bold')
        ax_main.grid(True, alpha=0.3)
        
        # Log dans la console
        print(f"\n{'='*60}")
        print(f"=== Frame {frame + 1} - {reseau.nom} ===")
        for route_nom, route in reseau.routes.items():
            if route.vehicules:
                print(f"\n🛣️  Route {route_nom}:")
                for v in route.vehicules:
                    progress = (v.position / route.longueur) * 100
                    print(f"   🚗 {v.identifiant}: {v.position:.1f}m ({progress:.1f}%) - {v.vitesse} km/h")
        
        if reseau.vehicules_sortis:
            print(f"\n🚪 Véhicules sortis: {[v.identifiant for v in reseau.vehicules_sortis]}")
        
        return list(vehicle_objects.values()) + list(vehicle_texts.values())
    
    # Animation
    ani = animation.FuncAnimation(fig, update, frames=30, init_func=init, 
                                 interval=1000, repeat=True, blit=False)
    
    plt.tight_layout()
    plt.show()
    return ani

def creer_animation_sauvegardee(reseau, nom_fichier="simulation_reseau.gif"):
    """Crée et sauvegarde une animation du réseau"""
    ani = simuler_reseau_graphique(reseau)
    
    try:
        # Sauvegarder l'animation (nécessite pillow: pip install pillow)
        ani.save(nom_fichier, writer='pillow', fps=1)
        print(f"Animation sauvegardée: {nom_fichier}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
    
    return ani

def afficher_statistiques_finales(reseau):
    """Affiche un résumé visuel des statistiques finales"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    stats = reseau.obtenir_statistiques()
    
    # Graphique 1: Véhicules par route
    routes = list(stats['routes'].keys())
    vehicules_count = list(stats['routes'].values())
    
    ax1.bar(routes, vehicules_count, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax1.set_title("Véhicules par route", fontweight='bold')
    ax1.set_ylabel("Nombre de véhicules")
    ax1.tick_params(axis='x', rotation=45)
    
    # Graphique 2: Répartition des véhicules
    labels = ['Véhicules actifs', 'Véhicules sortis']
    sizes = [stats['total_vehicules_actifs'], stats['vehicules_sortis']]
    colors = ['#FF9999', '#66B2FF']
    
    ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title("Répartition des véhicules", fontweight='bold')
    
    # Graphique 3: Informations sur les routes
    route_lengths = [reseau.routes[nom].longueur for nom in routes]
    speed_limits = [reseau.routes[nom].limite_vitesse for nom in routes]
    
    x = np.arange(len(routes))
    width = 0.35
    
    ax3.bar(x - width/2, route_lengths, width, label='Longueur (m)', color='skyblue')
    ax3_twin = ax3.twinx()
    ax3_twin.bar(x + width/2, speed_limits, width, label='Limite vitesse (km/h)', color='orange')
    
    ax3.set_xlabel('Routes')
    ax3.set_ylabel('Longueur (m)', color='skyblue')
    ax3_twin.set_ylabel('Vitesse (km/h)', color='orange')
    ax3.set_title('Caractéristiques des routes', fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(routes)
    ax3.legend(loc='upper left')
    ax3_twin.legend(loc='upper right')
    
    # Graphique 4: Statistiques des véhicules sortis
    if reseau.vehicules_sortis:
        vehicules_sortis_noms = [v.identifiant for v in reseau.vehicules_sortis]
        distances_parcourues = [v.distance_totale_parcourue for v in reseau.vehicules_sortis]
        
        ax4.barh(vehicules_sortis_noms, distances_parcourues, color='lightgreen')
        ax4.set_title("Distance parcourue par véhicule sorti", fontweight='bold')
        ax4.set_xlabel("Distance (m)")
    else:
        ax4.text(0.5, 0.5, "Aucun véhicule\nn'a encore quitté\nle réseau", 
                ha='center', va='center', transform=ax4.transAxes, fontsize=14)
        ax4.set_title("Véhicules sortis", fontweight='bold')
    
    plt.tight_layout()
    plt.show()