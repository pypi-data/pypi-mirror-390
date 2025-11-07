"""
Classe Analyseur - Calcule les statistiques du réseau routier.
"""

from typing import Dict, List
from ..models.reseau import ReseauRoutier
from ..models.route import Route


class Analyseur:
    """Calcule et analyse les statistiques du trafic routier."""
    
    def __init__(self, reseau: ReseauRoutier):
        """
        Initialise l'analyseur avec un réseau.
        
        Args:
            reseau: Réseau routier à analyser
        """
        if reseau is None:
            raise ValueError("Le réseau ne peut pas être None")
        self.reseau = reseau
    
    def calculer_vitesse_moyenne_globale(self) -> float:
        """
        Calcule la vitesse moyenne de tous les véhicules du réseau.
        
        Returns:
            Vitesse moyenne en m/s
        """
        total_vitesse = 0.0
        total_vehicules = 0
        
        for route in self.reseau.get_toutes_les_routes():
            nb_vehicules = route.get_nombre_vehicules()
            if nb_vehicules > 0:
                total_vitesse += route.get_vitesse_moyenne() * nb_vehicules
                total_vehicules += nb_vehicules
        
        if total_vehicules == 0:
            return 0.0
        
        return total_vitesse / total_vehicules
    
    def calculer_vitesse_moyenne_par_route(self) -> Dict[str, float]:
        """
        Calcule la vitesse moyenne pour chaque route.
        
        Returns:
            Dictionnaire {nom_route: vitesse_moyenne}
        """
        resultats = {}
        for route in self.reseau.get_toutes_les_routes():
            resultats[route.nom] = route.get_vitesse_moyenne()
        return resultats
    
    def identifier_zones_congestion(self, seuil_congestion: float = 5.0) -> List[str]:
        """
        Identifie les routes en congestion (vitesse moyenne < seuil).
        
        Args:
            seuil_congestion: Seuil de vitesse en m/s en dessous duquel on considère une congestion
            
        Returns:
            Liste des noms de routes en congestion
        """
        routes_congestionnees = []
        for route in self.reseau.get_toutes_les_routes():
            vitesse_moyenne = route.get_vitesse_moyenne()
            if vitesse_moyenne > 0 and vitesse_moyenne < seuil_congestion:
                routes_congestionnees.append(route.nom)
        return routes_congestionnees
    
    def calculer_temps_parcours_estime(self, route: Route) -> float:
        """
        Calcule le temps de parcours estimé pour une route.
        
        Args:
            route: Route pour laquelle calculer le temps de parcours
            
        Returns:
            Temps estimé en secondes, ou 0 si aucun véhicule
        """
        if route is None:
            raise ValueError("La route ne peut pas être None")
        
        vitesse_moyenne = route.get_vitesse_moyenne()
        if vitesse_moyenne == 0:
            return 0.0
        
        try:
            return route.longueur / vitesse_moyenne
        except ZeroDivisionError:
            return 0.0
    
    def generer_rapport_statistiques(self) -> Dict:
        """
        Génère un rapport complet des statistiques.
        
        Returns:
            Dictionnaire contenant toutes les statistiques
        """
        return {
            'vitesse_moyenne_globale': self.calculer_vitesse_moyenne_globale(),
            'vitesse_moyenne_par_route': self.calculer_vitesse_moyenne_par_route(),
            'zones_congestion': self.identifier_zones_congestion(),
            'nombre_total_vehicules': self.reseau.get_nombre_total_vehicules(),
            'nombre_routes': len(self.reseau.get_toutes_les_routes())
        }

