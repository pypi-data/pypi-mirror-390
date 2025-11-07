"""
Classe Route - Représente une route dans le réseau routier.
"""


class Route:
    """Représente une route avec ses caractéristiques et ses véhicules."""
    
    def __init__(self, nom: str, longueur: float, limite_vitesse: float):
        """
        Initialise une route.
        
        Args:
            nom: Nom de la route
            longueur: Longueur de la route en mètres
            limite_vitesse: Limite de vitesse en m/s
        """
        if longueur <= 0:
            raise ValueError(f"La longueur de la route doit être positive: {longueur}")
        if limite_vitesse <= 0:
            raise ValueError(f"La limite de vitesse doit être positive: {limite_vitesse}")
        
        self.nom = nom
        self.longueur = longueur
        self.limite_vitesse = limite_vitesse
        self.vehicules = []  # Liste des véhicules sur cette route
    
    def ajouter_vehicule(self, vehicule):
        """
        Ajoute un véhicule à la route.
        
        Args:
            vehicule: Véhicule à ajouter
        """
        if vehicule is None:
            raise ValueError("Le véhicule ne peut pas être None")
        
        if vehicule in self.vehicules:
            raise ValueError(f"Le véhicule {vehicule.identifiant} est déjà sur cette route")
        
        self.vehicules.append(vehicule)
        vehicule.route = self
    
    def retirer_vehicule(self, vehicule):
        """
        Retire un véhicule de la route.
        
        Args:
            vehicule: Véhicule à retirer
        """
        if vehicule in self.vehicules:
            self.vehicules.remove(vehicule)
            vehicule.route = None
    
    def mettre_a_jour_vehicules(self, delta_t: float):
        """
        Met à jour la position de tous les véhicules sur la route.
        
        Args:
            delta_t: Temps écoulé en secondes
        """
        for vehicule in self.vehicules:
            vehicule.avancer(delta_t)
    
    def get_vitesse_moyenne(self) -> float:
        """
        Calcule la vitesse moyenne des véhicules sur la route.
        
        Returns:
            Vitesse moyenne en m/s, ou 0 si aucun véhicule
        """
        if len(self.vehicules) == 0:
            return 0.0
        
        somme_vitesses = sum(v.vitesse for v in self.vehicules)
        return somme_vitesses / len(self.vehicules)
    
    def get_nombre_vehicules(self) -> int:
        """Retourne le nombre de véhicules sur la route."""
        return len(self.vehicules)
    
    def __repr__(self):
        return f"Route({self.nom}, longueur={self.longueur}m, limite={self.limite_vitesse}m/s, {len(self.vehicules)} véhicules)"

