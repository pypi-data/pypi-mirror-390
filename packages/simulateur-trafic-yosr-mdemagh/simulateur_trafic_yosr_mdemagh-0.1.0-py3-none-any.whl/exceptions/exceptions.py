class VehiculeError(Exception):
    """Exception de base pour les erreurs liées aux véhicules."""
    def __init__(self, message="Erreur liée au véhicule."):
        super().__init__(message)


class VitesseInvalideError(VehiculeError):
    """Levée quand la vitesse d'un véhicule est négative."""
    def __init__(self, vehicule_id, vitesse):
        message = f" Vitesse invalide ({vitesse}) pour le véhicule '{vehicule_id}'. La vitesse ne peut pas être négative."
        super().__init__(message)


class PositionInvalideError(VehiculeError):
    """Levée quand la position d'un véhicule devient invalide."""
    def __init__(self, vehicule_id, position, longueur):
        message = (
            f"Position invalide ({position}) pour le véhicule '{vehicule_id}'. "
            f"La position doit être comprise entre 0 et {longueur}."
        )
        super().__init__(message)


class RouteError(Exception):
    """Exception de base pour les erreurs de route."""
    def __init__(self, message="Erreur liée à la route."):
        super().__init__(message)


class VehiculeDejaPresentError(RouteError):
    """Levée quand un véhicule est déjà présent sur la route."""
    def __init__(self, vehicule_id, nom_route):
        message = f" Le véhicule '{vehicule_id}' est déjà présent sur la route '{nom_route}'."
        super().__init__(message)


class RoutePleineError(RouteError):
    """Levée quand on tente d’ajouter un véhicule alors que la route est pleine."""
    def __init__(self, nom_route, capacite_max):
        message = f" La route '{nom_route}' est pleine (capacité maximale : {capacite_max} véhicules)."
        super().__init__(message)


class SimulationError(Exception):
    """Exception générale pour les erreurs du simulateur."""
    def __init__(self, message="Erreur de simulation."):
        super().__init__(message)
