# core/analyseur.py
from exceptions.exceptions import SimulationError
import numpy as np
from numba import njit

# Fonction Numba pour calculer la vitesse moyenne et la position maximale
@njit
def calcul_stats_num(vitesses, positions):
    n = len(vitesses)
    if n == 0:
        return 0.0, 0.0

    vitesse_moy = 0.0
    max_pos = 0.0
    for i in range(n):
        vitesse_moy += vitesses[i]
        if positions[i] > max_pos:
            max_pos = positions[i]
    vitesse_moy /= n
    return vitesse_moy, max_pos


class Analyseur:
    def __init__(self):
        pass

    def analyser_reseau(self, reseau):
        """Retourne des statistiques globales avec gestion d'erreurs"""
        try:
            # 2️ Extraire les vitesses et positions dans des arrays NumPy
            vitesses = np.array([v.vitesse for r in reseau.routes.values() for v in r.vehicules])
            positions = np.array([v.position for r in reseau.routes.values() for v in r.vehicules])

            nb_routes = len(reseau.routes)
            nb_vehicules = len(vitesses)  # plus rapide que sum(len(r.vehicules))

            if nb_vehicules == 0:
                raise ZeroDivisionError("Aucun véhicule dans le réseau.")

            #  Appeler la fonction Numba pour calculer vitesse moyenne et max position
            vitesse_moyenne, max_position = calcul_stats_num(vitesses, positions)

            stats = {
                "nb_routes": nb_routes,
                "nb_vehicules": nb_vehicules,
                "vitesse_moyenne": vitesse_moyenne,
                "max_position": max_position
            }

            return stats

        except ZeroDivisionError as e:
            print(f"[ERREUR] {e}")
            # On renvoie des valeurs neutres pour ne pas bloquer la simulation
            return {
                "nb_routes": len(reseau.routes),
                "nb_vehicules": 0,
                "vitesse_moyenne": 0,
                "max_position": 0
            }

        except Exception as e:
            raise SimulationError(f"Erreur inattendue lors de l'analyse du réseau : {e}")
