# Simulateur de Trafic Routier Intelligent

[![CI](https://github.com/yourusername/simulateur_trafic/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/simulateur_trafic/actions/workflows/ci.yml)
[![Tests](https://github.com/yourusername/simulateur_trafic/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/simulateur_trafic/actions/workflows/tests.yml)

Un simulateur modulaire pour modéliser et analyser le trafic routier, développé dans le cadre d'un projet Python orienté objet.

## Structure du Projet

```
simulateur_trafic/
├── main.py                 # Point d'entrée principal
├── models/                 # Modèles de base
│   ├── vehicule.py        # Classe Vehicule
│   ├── route.py           # Classe Route
│   └── reseau.py          # Classe ReseauRoutier
├── core/                  # Modules core
│   ├── simulateur.py     # Classe Simulateur principale
│   ├── analyseur.py      # Classe Analyseur pour les statistiques
│   └── exceptions.py     # Exceptions personnalisées
├── io/                    # Modules d'entrée/sortie
│   ├── affichage.py      # Affichage console
│   └── export.py         # Export JSON/CSV
├── tests/                 # Tests unitaires et d'intégration
│   ├── conftest.py       # Fixtures pytest
│   ├── test_vehicule.py
│   ├── test_route.py
│   ├── test_reseau.py
│   └── test_simulateur.py
└── data/                  # Données de configuration
    └── config_reseau.json
```

## Installation

1. Créer et activer l'environnement virtuel :
```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
# Sur macOS/Linux :
source venv/bin/activate

# Sur Windows :
# venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer la simulation

```bash
python main.py
```

Ou depuis Python :
```python
from core.simulateur import Simulateur

simu = Simulateur(fichier_config="data/config_reseau.json")
simu.lancer_simulation(n_tours=60, delta_t=60)
```

### Exécuter les tests

```bash
pytest tests/
```

Avec couverture de code :
```bash
pytest tests/ --cov=simulateur_trafic --cov-report=html
```

## CI/CD

Le projet utilise GitHub Actions pour l'intégration continue :

- **CI** : Tests automatiques sur chaque push/PR
- **Tests** : Matrice de tests sur plusieurs OS (Ubuntu, macOS, Windows) et versions Python (3.9-3.12)
- **Lint** : Vérification du code avec flake8 et pylint

Les workflows sont définis dans `.github/workflows/`.

## Fonctionnalités

- **Modélisation** : Routes, véhicules, réseau routier
- **Simulation** : Évolution temporelle du trafic
- **Statistiques** : Vitesses moyennes, zones de congestion, temps de parcours
- **Export** : Rapports JSON et CSV
- **Tests** : Suite complète de tests unitaires et d'intégration
- **Gestion d'erreurs** : Exceptions personnalisées et validation des données

## Configuration

Le fichier `data/config_reseau.json` permet de configurer :
- Les routes (nom, longueur, limite de vitesse)
- Les véhicules (identifiant, route, position initiale, vitesse)

## Auteurs

Projet développé dans le cadre d'un TP Python.

