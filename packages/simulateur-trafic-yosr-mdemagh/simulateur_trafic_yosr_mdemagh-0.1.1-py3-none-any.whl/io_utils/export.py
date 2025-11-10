"""
Module `export`
---------------
Fournit des utilitaires pour exporter des statistiques dans différents formats
(JSON et CSV). Ce module est utile pour sauvegarder les résultats d'une simulation
ou d'un traitement afin de pouvoir les analyser ou partager.
"""

import json
import csv


class Export:
    """
    Classe utilitaire pour l'exportation des statistiques.

    Fournit des méthodes statiques permettant de sauvegarder les résultats
    sous forme de fichiers JSON ou CSV.
    """

    @staticmethod
    def exporter_json(stats: dict, filename: str = "resultats.json") -> None:
        """
        Exporte les statistiques au format JSON.

        Args:
            stats (dict): Dictionnaire contenant les statistiques à exporter.
            filename (str, optional): Nom du fichier de sortie.
                Par défaut "resultats.json".
        """
        with open(filename, "w") as f:
            json.dump(stats, f, indent=4)

    @staticmethod
    def exporter_csv(stats: dict, filename: str = "resultats.csv") -> None:
        """
        Exporte les statistiques au format CSV.

        Chaque ligne contient une paire clé-valeur du dictionnaire.

        Args:
            stats (dict): Dictionnaire contenant les statistiques à exporter.
            filename (str, optional): Nom du fichier de sortie.
                Par défaut "resultats.csv".
        """
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            for k, v in stats.items():
                writer.writerow([k, v])
