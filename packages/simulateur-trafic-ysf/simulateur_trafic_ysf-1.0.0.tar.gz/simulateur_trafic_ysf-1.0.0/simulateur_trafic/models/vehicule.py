"""
Classe Vehicule - Représente un véhicule dans le simulateur de trafic.
"""


class Vehicule:
    """Représente un véhicule circulant sur une route."""
    
    def __init__(self, identifiant: str, route=None, position: float = 0.0, vitesse: float = 0.0):
        """
        Initialise un véhicule.
        
        Args:
            identifiant: Identifiant unique du véhicule
            route: Route sur laquelle se trouve le véhicule
            position: Position initiale sur la route (en mètres)
            vitesse: Vitesse initiale (en m/s)
        """
        if vitesse < 0:
            raise ValueError(f"La vitesse ne peut pas être négative: {vitesse}")
        if position < 0:
            raise ValueError(f"La position ne peut pas être négative: {position}")
        
        self.identifiant = identifiant
        self.route = route
        self.position = position
        self.vitesse = vitesse
        
    def avancer(self, delta_t: float):
        """
        Fait avancer le véhicule selon sa vitesse et le temps écoulé.
        
        Args:
            delta_t: Temps écoulé en secondes
        """
        if delta_t < 0:
            raise ValueError(f"Le temps delta_t ne peut pas être négatif: {delta_t}")
        if self.vitesse < 0:
            raise ValueError(f"La vitesse ne peut pas être négative: {self.vitesse}")
        
        if self.route is None:
            raise ValueError("Le véhicule doit être sur une route pour avancer")
        
        nouvelle_position = self.position + self.vitesse * delta_t
        
        # Le véhicule ne dépasse pas la longueur de la route
        if nouvelle_position > self.route.longueur:
            self.position = self.route.longueur
        else:
            self.position = nouvelle_position
    
    def changer_de_route(self, nouvelle_route):
        """
        Change le véhicule de route.
        
        Args:
            nouvelle_route: Nouvelle route sur laquelle placer le véhicule
        """
        if nouvelle_route is None:
            raise ValueError("La nouvelle route ne peut pas être None")
        
        # Retirer le véhicule de l'ancienne route si elle existe
        if self.route is not None:
            self.route.retirer_vehicule(self)
        
        # Changer de route et remettre la position à zéro
        self.route = nouvelle_route
        self.position = 0.0
        
        # Ajouter le véhicule à la nouvelle route
        nouvelle_route.ajouter_vehicule(self)
    
    def __repr__(self):
        route_nom = self.route.nom if self.route else "Aucune"
        return f"Vehicule({self.identifiant}, route={route_nom}, pos={self.position:.1f}m, v={self.vitesse:.1f}m/s)"

