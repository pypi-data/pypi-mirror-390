"""
Module d'export - Exporte les résultats de la simulation.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class Exporteur:
    """Gère l'export des résultats de la simulation."""
    
    def exporter_rapport(self, rapport: Dict, nom_fichier: str = None):
        """
        Exporte le rapport au format JSON.
        
        Args:
            rapport: Dictionnaire contenant les statistiques
            nom_fichier: Nom du fichier de sortie (optionnel)
        """
        if nom_fichier is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier = f"rapport_simulation_{timestamp}.json"
        
        # Créer le dossier data s'il n'existe pas
        output_dir = Path("data")
        output_dir.mkdir(exist_ok=True)
        
        fichier_path = output_dir / nom_fichier
        
        with open(fichier_path, 'w', encoding='utf-8') as f:
            json.dump(rapport, f, indent=2, ensure_ascii=False)
        
        print(f"Rapport exporté vers: {fichier_path}")
    
    def exporter_csv(self, donnees: List[Dict], nom_fichier: str = None):
        """
        Exporte des données au format CSV.
        
        Args:
            donnees: Liste de dictionnaires à exporter
            nom_fichier: Nom du fichier de sortie (optionnel)
        """
        if nom_fichier is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier = f"donnees_simulation_{timestamp}.csv"
        
        if not donnees:
            raise ValueError("Aucune donnée à exporter")
        
        output_dir = Path("data")
        output_dir.mkdir(exist_ok=True)
        
        fichier_path = output_dir / nom_fichier
        
        with open(fichier_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = donnees[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(donnees)
        
        print(f"Données exportées vers: {fichier_path}")

