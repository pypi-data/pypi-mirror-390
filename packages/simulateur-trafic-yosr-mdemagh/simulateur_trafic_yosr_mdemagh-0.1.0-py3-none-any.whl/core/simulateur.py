# core/simulateur.py
import json
from models.reseau import ReseauRoutier
from models.route import Route
from models.vehicule import Vehicule
from core.analyseur import Analyseur
#from core.analyseur_cy import Analyseur


from io_utils.affichage import Affichage
from io_utils.export import Export
from exceptions.exceptions import SimulationError

class Simulateur:
    def __init__(self, fichier_config):
        self.reseau = ReseauRoutier()
        self.analyseur = Analyseur()
        self.tours = 0
        self._charger_config(fichier_config)

    def _charger_config(self, fichier_config):
        """Lit le fichier JSON et construit les routes et véhicules"""
        try:
            with open(fichier_config, "r") as f:
                config = json.load(f)

            # Vérifier le contenu minimal du fichier
            if "routes" not in config or "vehicules" not in config:
                raise ValueError("Le fichier de configuration est incomplet.")

        except FileNotFoundError:
            raise SimulationError(f"Le fichier {fichier_config} est introuvable.")
        except ValueError as e:
            raise SimulationError(f"Erreur de données dans le fichier : {e}")

        # Créer les routes et véhicules si tout va bien
        for r in config["routes"]:
            route = Route(r["nom"], r["longueur"], r["limite_vitesse"])
            self.reseau.ajouter_route(route)

        for v in config["vehicules"]:
            route = self.reseau.get_route(v["route"])
            veh = Vehicule(v["id"], route, v["position"], v["vitesse"])
            route.ajouter_vehicule(veh)

    def lancer_simulation(self, n_tours, delta_t):
        try:
            if n_tours <= 0 or delta_t <= 0:
                raise ValueError("Le nombre d’itérations et le pas de temps doivent être positifs.")

            vitesses_moyennes = []
            for t in range(n_tours):
                print(f"--- Tour {t+1} ---")
                self.reseau.mettre_a_jour(delta_t)
                stats = self.analyseur.analyser_reseau(self.reseau)
                Affichage.afficher_console(stats)
                vitesses_moyennes.append(stats["vitesse_moyenne"])

            Affichage.afficher_graphique(vitesses_moyennes)
            Export.exporter_json(stats, "resultats.json")
            Export.exporter_csv(stats, "resultats.csv")

        except ValueError as e:
            print(f"[ERREUR] Paramètre de simulation invalide : {e}")
        except FileNotFoundError as e:
            print(f"[ERREUR] Fichier manquant : {e}")
        except ZeroDivisionError:
            print("[ERREUR] Division par zéro lors de l'analyse des vitesses moyennes.")
        except SimulationError as e:
            print(f"[ERREUR] {e}")
        except Exception as e:
            print(f"[ERREUR INATTENDUE] {e}")