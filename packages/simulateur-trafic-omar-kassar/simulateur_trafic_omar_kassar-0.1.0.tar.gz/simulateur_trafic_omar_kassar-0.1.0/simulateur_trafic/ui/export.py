"""
Module `export`
===============

Ce module définit la classe :class:`Exporteur`, responsable de l’enregistrement
des résultats et états de simulation dans différents formats (`JSON`, `CSV`).

Les exports produits peuvent être utilisés pour l’analyse, la visualisation,
ou la reprise de simulation.  
Chaque étape (snapshot) du réseau routier peut être sauvegardée sous forme
de fichier JSON, et un résumé global (vitesse moyenne, densité, etc.)
peut être exporté en CSV.
"""

import csv
import json
import os
from typing import Dict
from ..models.reseau import ReseauRoutier


class Exporteur:
    """
    Classe gérant l’export des données de simulation vers des fichiers JSON et CSV.

    Parameters
    ----------
    dossier : str, optional
        Dossier de sortie où seront enregistrés les fichiers d’export.
        Par défaut : ``"output"``.
    """

    def __init__(self, dossier: str = "output"):
        """Initialise l’exporteur et crée le dossier de sortie s’il n’existe pas."""
        os.makedirs(dossier, exist_ok=True)
        self.dossier = dossier

    def export_step(self, step: int, reseau: ReseauRoutier, snapshot: Dict) -> None:
        """
        Exporte l’état complet du réseau pour une étape donnée au format JSON.

        Crée un fichier nommé ``snapshot_XXXX.json`` (avec numéro d’étape à 4 chiffres)
        contenant les informations des routes et véhicules, ainsi que le snapshot
        de simulation associé.

        Parameters
        ----------
        step : int
            Numéro de l’étape (tour de simulation).
        reseau : ReseauRoutier
            Instance du réseau routier à exporter.
        snapshot : dict
            Données spécifiques à cette étape (statistiques, mesures, etc.).
        """
        path = os.path.join(self.dossier, f"snapshot_{step:04d}.json")
        serial = {
            "step": step,
            "routes": {
                nom: {
                    "longueur": r.longueur,
                    "limite_vitesse": r.limite_vitesse,
                    "vehicules": [
                        {"id": v.id, "position": v.position, "vitesse": v.vitesse}
                        for v in r.vehicules
                    ],
                } for nom, r in reseau.routes.items()
            },
            "snapshot": snapshot
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serial, f, indent=2)

    def export_csv_summary(self, historique: list, filename: str = "summary.csv") -> None:
        """
        Exporte un résumé global de la simulation au format CSV.

        Chaque ligne du fichier correspond à un tour de simulation et inclut :
        - la vitesse moyenne par route,
        - la densité de circulation par route.

        Parameters
        ----------
        historique : list of dict
            Liste des snapshots de simulation, chacun contenant au moins
            les clés ``"vitesses_moyennes"`` et ``"densites"``.
        filename : str, optional
            Nom du fichier CSV de sortie.  
            Par défaut : ``"summary.csv"``.
        """
        csv_path = os.path.join(self.dossier, filename)
        all_rows = []
        for step_idx, snap in enumerate(historique):
            row = {"step": step_idx}
            for route, vm in snap["vitesses_moyennes"].items():
                row[f"vm_{route}"] = vm
            for route, dens in snap["densites"].items():
                row[f"dens_{route}"] = dens
            all_rows.append(row)

        if not all_rows:
            return

        headers = sorted(set().union(*(r.keys() for r in all_rows)))
        with open(csv_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in all_rows:
                writer.writerow(r)

    @staticmethod
    def exporter_json(stats: dict, chemin: str) -> None:
        """
        Exporte un dictionnaire de statistiques au format JSON.

        Parameters
        ----------
        stats : dict
            Données statistiques (ex. vitesses moyennes, taux d’embouteillage...).
        chemin : str
            Chemin du fichier de sortie JSON.
        """
        with open(chemin, "w") as f:
            json.dump(stats, f, indent=4)

    @staticmethod
    def exporter_csv(stats: dict, chemin: str) -> None:
        """
        Exporte un ensemble de statistiques au format CSV.

        Le fichier contiendra les colonnes :
        ``tour``, ``vitesse_moyenne`` et ``embouteillage``.

        Parameters
        ----------
        stats : dict
            Dictionnaire contenant les clés :
            - ``"tours"`` : liste des indices de tours (int)
            - ``"vitesses"`` : vitesses moyennes (float)
            - ``"embouteillages"`` : taux ou indicateurs de congestion
        chemin : str
            Chemin du fichier CSV de sortie.
        """
        with open(chemin, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tour", "vitesse_moyenne", "embouteillage"])
            for t, v, e in zip(stats["tours"], stats["vitesses"], stats["embouteillages"]):
                writer.writerow([t, v, e])
