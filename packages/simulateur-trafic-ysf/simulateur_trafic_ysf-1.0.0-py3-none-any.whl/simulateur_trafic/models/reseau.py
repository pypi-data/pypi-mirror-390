"""
Classe ReseauRoutier - Gère l'ensemble du réseau routier.
"""

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.route import Route


class ReseauRoutier:
    """Gère l'ensemble des routes et intersections du réseau."""
    
    def __init__(self):
        """Initialise un réseau routier vide."""
        self.routes: Dict[str, 'Route'] = {}  # Dictionnaire nom_route -> Route
    
    def ajouter_route(self, route: 'Route'):
        """
        Ajoute une route au réseau.
        
        Args:
            route: Route à ajouter
        """
        if route is None:
            raise ValueError("La route ne peut pas être None")
        
        if route.nom in self.routes:
            raise ValueError(f"Une route avec le nom '{route.nom}' existe déjà")
        
        self.routes[route.nom] = route
    
    def get_route(self, nom: str) -> Optional['Route']:
        """
        Récupère une route par son nom.
        
        Args:
            nom: Nom de la route
            
        Returns:
            La route si trouvée, None sinon
        """
        return self.routes.get(nom)
    
    def mettre_a_jour(self, delta_t: float):
        """
        Met à jour toutes les routes du réseau.
        
        Args:
            delta_t: Temps écoulé en secondes
        """
        for route in self.routes.values():
            route.mettre_a_jour_vehicules(delta_t)
    
    def get_toutes_les_routes(self) -> List['Route']:
        """Retourne la liste de toutes les routes."""
        return list(self.routes.values())
    
    def get_nombre_total_vehicules(self) -> int:
        """Retourne le nombre total de véhicules dans le réseau."""
        return sum(route.get_nombre_vehicules() for route in self.routes.values())
    
    def __repr__(self):
        nb_routes = len(self.routes)
        nb_vehicules = self.get_nombre_total_vehicules()
        return f"ReseauRoutier({nb_routes} routes, {nb_vehicules} véhicules)"

