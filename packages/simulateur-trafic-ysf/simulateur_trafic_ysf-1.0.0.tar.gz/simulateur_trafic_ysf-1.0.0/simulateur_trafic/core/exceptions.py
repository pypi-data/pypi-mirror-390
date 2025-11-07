"""
Exceptions personnalisées pour le simulateur de trafic.
"""


class SimulateurException(Exception):
    """Exception de base pour le simulateur."""
    pass


class VehiculeException(SimulateurException):
    """Exception liée aux véhicules."""
    pass


class RouteException(SimulateurException):
    """Exception liée aux routes."""
    pass


class ReseauException(SimulateurException):
    """Exception liée au réseau routier."""
    pass


class ConfigurationException(SimulateurException):
    """Exception liée à la configuration."""
    pass

