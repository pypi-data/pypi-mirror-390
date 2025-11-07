"""
Module d'affichage - Affiche les résultats de la simulation.
"""

from typing import Dict
from ..models.reseau import ReseauRoutier
from ..core.analyseur import Analyseur


class Afficheur:
    """Gère l'affichage des résultats de la simulation."""
    
    def afficher_etat_initial(self, reseau: ReseauRoutier):
        """Affiche l'état initial du réseau."""
        print("\n" + "="*60)
        print("SIMULATEUR DE TRAFIC ROUTIER - ÉTAT INITIAL")
        print("="*60)
        print(f"Réseau: {reseau}")
        print(f"Nombre de routes: {len(reseau.get_toutes_les_routes())}")
        print(f"Nombre total de véhicules: {reseau.get_nombre_total_vehicules()}")
        print("="*60 + "\n")
    
    def afficher_tour(self, tour: int, reseau: ReseauRoutier, analyseur: Analyseur):
        """
        Affiche les statistiques d'un tour de simulation.
        
        Args:
            tour: Numéro du tour
            reseau: Réseau routier
            analyseur: Analyseur pour calculer les statistiques
        """
        print(f"\n--- Tour {tour} ---")
        print(f"Véhicules dans le réseau: {reseau.get_nombre_total_vehicules()}")
        
        vitesse_moyenne = analyseur.calculer_vitesse_moyenne_globale()
        print(f"Vitesse moyenne globale: {vitesse_moyenne:.2f} m/s ({vitesse_moyenne * 3.6:.2f} km/h)")
        
        zones_congestion = analyseur.identifier_zones_congestion()
        if zones_congestion:
            print(f"Routes en congestion: {', '.join(zones_congestion)}")
        else:
            print("Aucune route en congestion")
    
    def afficher_rapport_final(self, rapport: Dict):
        """
        Affiche le rapport final de la simulation.
        
        Args:
            rapport: Dictionnaire contenant les statistiques
        """
        print("\n" + "="*60)
        print("RAPPORT FINAL DE LA SIMULATION")
        print("="*60)
        print(f"Vitesse moyenne globale: {rapport['vitesse_moyenne_globale']:.2f} m/s")
        print(f"Nombre total de véhicules: {rapport['nombre_total_vehicules']}")
        print(f"Nombre de routes: {rapport['nombre_routes']}")
        
        print("\nVitesses moyennes par route:")
        for route, vitesse in rapport['vitesse_moyenne_par_route'].items():
            print(f"  - {route}: {vitesse:.2f} m/s ({vitesse * 3.6:.2f} km/h)")
        
        if rapport['zones_congestion']:
            print(f"\nRoutes en congestion: {', '.join(rapport['zones_congestion'])}")
        else:
            print("\nAucune route en congestion")
        
        print("="*60 + "\n")

