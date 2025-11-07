"""
Classe Simulateur - Gère la simulation du trafic routier.
"""

import json
from pathlib import Path
from typing import Optional
from ..models.reseau import ReseauRoutier
from ..models.route import Route
from ..models.vehicule import Vehicule
from .analyseur import Analyseur
from ..io.affichage import Afficheur
from ..io.export import Exporteur


class Simulateur:
    """Gère la simulation complète du trafic routier."""
    
    def __init__(self, fichier_config: str = "data/config_reseau.json"):
        """
        Initialise le simulateur à partir d'un fichier de configuration.
        
        Args:
            fichier_config: Chemin vers le fichier de configuration JSON
        """
        self.reseau = ReseauRoutier()
        self.analyseur = Analyseur(self.reseau)
        self.afficheur = Afficheur()
        self.exporteur = Exporteur()
        self.tour_actuel = 0
        
        try:
            self._charger_configuration(fichier_config)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Fichier de configuration introuvable: {fichier_config}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Erreur de format JSON dans le fichier de configuration: {e}") from e
    
    def _charger_configuration(self, fichier_config: str):
        """
        Charge la configuration depuis un fichier JSON.
        
        Args:
            fichier_config: Chemin vers le fichier de configuration
        """
        config_path = Path(fichier_config)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Le fichier de configuration n'existe pas: {fichier_config}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Charger les routes
        if 'routes' not in config:
            raise ValueError("Le fichier de configuration doit contenir une clé 'routes'")
        
        for route_config in config['routes']:
            route = Route(
                nom=route_config['nom'],
                longueur=route_config['longueur'],
                limite_vitesse=route_config['limite_vitesse']
            )
            self.reseau.ajouter_route(route)
        
        # Charger les véhicules
        if 'vehicules' in config:
            for vehicule_config in config['vehicules']:
                route_nom = vehicule_config.get('route')
                route = self.reseau.get_route(route_nom)
                
                if route is None:
                    raise ValueError(f"La route '{route_nom}' n'existe pas pour le véhicule {vehicule_config.get('identifiant')}")
                
                vehicule = Vehicule(
                    identifiant=vehicule_config['identifiant'],
                    route=route,
                    position=vehicule_config.get('position', 0.0),
                    vitesse=vehicule_config.get('vitesse', 10.0)
                )
                route.ajouter_vehicule(vehicule)
    
    def lancer_simulation(self, n_tours: int, delta_t: float = 60.0, afficher: bool = True, exporter: bool = False):
        """
        Lance la simulation sur plusieurs tours.
        
        Args:
            n_tours: Nombre de tours de simulation
            delta_t: Temps écoulé par tour en secondes
            afficher: Si True, affiche les statistiques à chaque tour
            exporter: Si True, exporte les résultats à la fin
        """
        if n_tours <= 0:
            raise ValueError(f"Le nombre de tours doit être positif: {n_tours}")
        if delta_t <= 0:
            raise ValueError(f"Le delta_t doit être positif: {delta_t}")
        
        self.tour_actuel = 0
        
        if afficher:
            self.afficheur.afficher_etat_initial(self.reseau)
        
        for tour in range(1, n_tours + 1):
            self.tour_actuel = tour
            
            # Mettre à jour le réseau
            self.reseau.mettre_a_jour(delta_t)
            
            # Afficher les statistiques si demandé
            if afficher:
                self.afficheur.afficher_tour(tour, self.reseau, self.analyseur)
        
        # Générer le rapport final
        rapport = self.analyseur.generer_rapport_statistiques()
        
        if afficher:
            self.afficheur.afficher_rapport_final(rapport)
        
        if exporter:
            self.exporteur.exporter_rapport(rapport, f"rapport_simulation_tour_{n_tours}.json")
        
        return rapport

