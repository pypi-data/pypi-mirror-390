# Simulateur de Trafic

Un simulateur de trafic routier en Python permettant de modéliser et analyser le flux de véhicules sur un réseau de routes.

## Installation

```bash
pip install simulateur_trafic_MouhebBoubaker
```

## Utilisation rapide

```python
from simulateur_trafic.models.vehicule import Vehicule
from simulateur_trafic.models.route import Route

# Créer une route
route = Route("Route A", longueur=1000, limite_vitesse=50)

# Créer un véhicule
vehicule = Vehicule("V001", position=0, vitesse=30)

# Ajouter le véhicule à la route
route.ajouter_vehicule(vehicule)
```

## Fonctionnalités

- Simulation de véhicules avec positions et vitesses
- Gestion de réseaux de routes
- Suivi des statistiques de trafic
- Visualisation graphique

## Licence

MIT License
