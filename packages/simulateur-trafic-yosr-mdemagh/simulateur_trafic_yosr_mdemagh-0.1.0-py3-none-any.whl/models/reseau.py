# models/reseau.py
from models.route import Route

class ReseauRoutier:
    """
    Représente un réseau routier composé de routes et, éventuellement, d'intersections.

    Cette classe permet de gérer un ensemble de routes connectées,
    d'y ajouter de nouvelles routes, de récupérer une route par son nom
    et de mettre à jour l'état des routes (et donc des véhicules qui y circulent).

    Attributes:
        routes (dict[str, Route]): Dictionnaire des routes du réseau,
            où la clé est le nom de la route et la valeur est une instance de `Route`.
        intersections (dict): Dictionnaire des intersections du réseau.
            (Actuellement non utilisé, prévu pour de futures extensions).

    Methods:
        ajouter_route(route: Route) -> None:
            Ajoute une route au réseau.
        get_route(nom: str) -> Route | None:
            Récupère une route par son nom, ou None si elle n'existe pas.
        mettre_a_jour(delta_t: float) -> None:
            Met à jour toutes les routes et les véhicules qu'elles contiennent,
            en fonction du pas de temps fourni.
    """

    def __init__(self):
        self.routes = {}
        self.intersections = {}

    def ajouter_route(self, route):
        """Ajoute une route au réseau"""
        self.routes[route.nom] = route

    def get_route(self, nom):
        """Récupère une route par son nom"""
        return self.routes.get(nom, None)

    def mettre_a_jour(self, delta_t):
        """Met à jour toutes les routes et donc tous les véhicules"""
        for route in self.routes.values():
            route.mettre_a_jour_vehicules(delta_t)
