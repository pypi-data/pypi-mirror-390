# models/vehicule.py
from exceptions.exceptions import VitesseInvalideError, PositionInvalideError
class Vehicule:
    """
    Représente un véhicule circulant sur une route.

    Un véhicule est défini par un identifiant, une route sur laquelle il se déplace,
    une position (distance parcourue sur la route) et une vitesse. Il peut avancer
    en fonction du temps écoulé et changer de route.

    Attributes:
        id (str | int): Identifiant unique du véhicule.
        route (Route): Référence à l'objet `Route` sur lequel le véhicule circule.
        position (float): Position actuelle du véhicule sur la route
            (comprise entre 0 et `route.longueur`).
        vitesse (float): Vitesse actuelle du véhicule.

    Methods:
        avancer(delta_t: float) -> None:
            Fait avancer le véhicule en fonction de sa vitesse et du temps écoulé.
            Si la position dépasse la longueur de la route, elle est limitée à la fin.
        changer_de_route(nouvelle_route: Route) -> None:
            Change le véhicule de route et réinitialise sa position au début.
    """

    def __init__(self, identifiant, route, position=0.0, vitesse=0.0):
        self.id = identifiant
        self.route = route      # référence à un objet Route
        self.position = position  # position sur la route (0 <= position <= route.longueur)
        self.vitesse = vitesse

    def avancer(self, delta_t):
        try:
            if self.vitesse < 0:
                raise VitesseInvalideError(self.id, self.vitesse)

            self.position += self.vitesse * delta_t

            if self.position < 0 or self.position > self.route.longueur:
                raise PositionInvalideError(self.id, self.position, self.route.longueur)

        except (VitesseInvalideError, PositionInvalideError) as e:
            print(e)  # 🔹 Le message clair défini dans l’exception sera affiché
            self.position = max(0, min(self.position, self.route.longueur))

    def changer_de_route(self, nouvelle_route):
        """Changer de route"""
        self.route = nouvelle_route
        self.position = 0  # il recommence au début de la nouvelle route
