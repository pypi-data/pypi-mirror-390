"""
Module `affichage`
-------------------
Contient la classe `Affichage`, qui regroupe des méthodes utilitaires
pour afficher des statistiques dans la console ou sous forme de graphiques.
"""

import matplotlib
matplotlib.use('Agg')  # backend non interactif
import matplotlib.pyplot as plt


class Affichage:
    """
    Classe utilitaire pour l'affichage des résultats.

    Fournit des méthodes statiques permettant d'afficher des statistiques
    soit dans la console, soit sous forme de graphiques enregistrés en fichier.
    """

    @staticmethod
    def afficher_console(stats: dict) -> None:
        """
        Affiche les statistiques dans la console.

        Args:
            stats (dict): Dictionnaire contenant les statistiques à afficher,
                où les clés sont des libellés et les valeurs des résultats.
        """
        print("=== Statistiques ===")
        for k, v in stats.items():
            print(f"{k}: {v}")

    @staticmethod
    def afficher_graphique(vitesses: list[float], filename: str = "vitesses_moyennes.png") -> None:
        """
        Génère et sauvegarde un graphique représentant l'évolution des vitesses moyennes.

        Args:
            vitesses (list[float]): Liste des vitesses moyennes à tracer.
            filename (str, optional): Nom du fichier image de sortie.
                Par défaut "vitesses_moyennes.png".
        """
        plt.plot(vitesses)
        plt.title("Évolution de la vitesse moyenne")
        plt.xlabel("Temps")
        plt.ylabel("Vitesse")
        plt.savefig(filename)  # sauvegarde le graphique
        plt.close()  # ferme la figure pour libérer la mémoire
