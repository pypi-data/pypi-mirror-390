# models/route.py
from exceptions.exceptions import VehiculeDejaPresentError, RoutePleineError
class Route:
    """
    Représente une route dans le réseau routier.

    Une route possède un nom, une longueur, une limitation de vitesse
    et une liste de véhicules qui y circulent. Elle permet d'ajouter
    des véhicules et de mettre à jour leur état au fil du temps.

    Attributes:
        nom (str): Nom unique de la route.
        longueur (float): Longueur de la route (par ex. en kilomètres ou en mètres).
        limV (float): Limite de vitesse autorisée sur la route.
        vehicules (list): Liste des véhicules circulant sur la route.

    Methods:
        ajouter_vehicule(vehicule) -> None:
            Ajoute un véhicule sur la route.
        mettre_a_jour_vehicules(delta_t: float) -> None:
            Met à jour la position et la vitesse de tous les véhicules présents
            sur la route en tenant compte de la limitation de vitesse.
    """

    def __init__(self, nom, longueur, limV):
        self.nom = nom
        self.longueur = longueur
        self.limV = limV
        self.vehicules = []  # toujours initialiser une liste vide ici

    def ajouter_vehicule(self, vehicule):
        try:
            if vehicule in self.vehicules:
                raise VehiculeDejaPresentError(vehicule.id, self.nom)
            if len(self.vehicules) >= 10:
                raise RoutePleineError(self.nom, 10)

            self.vehicules.append(vehicule)

        except (VehiculeDejaPresentError, RoutePleineError) as e:
            print(e)  # 🔹 Affiche le message clair

    def mettre_a_jour_vehicules(self, delta_t):
        """Mettre à jour tous les véhicules présents sur la route"""
        for v in self.vehicules:
            # si la vitesse du véhicule dépasse la limite → on la réduit
            if v.vitesse > self.limV:
                v.vitesse = self.limV

            # avancer le véhicule
            v.avancer(delta_t)
