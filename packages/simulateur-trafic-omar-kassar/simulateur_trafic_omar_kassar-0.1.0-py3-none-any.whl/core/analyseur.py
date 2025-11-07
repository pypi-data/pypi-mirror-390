# core/analyseur.py
from __future__ import annotations
from typing import Dict, List
import statistics

from models.reseau import ReseauRoutier


class Analyseur:
    """
    Classe responsable de l'analyse du trafic dans le réseau routier.

    Cette classe extrait des statistiques à partir de l'état courant du
    réseau routier, telles que les vitesses moyennes, les densités
    de véhicules, et les zones de congestion.

    Attributes
    ----------
    reseau : ReseauRoutier
        Le réseau routier sur lequel les analyses sont effectuées.
    historique : list[dict]
        Liste d'historiques des statistiques collectées à chaque étape
        de la simulation.
    """

    def __init__(self, reseau: ReseauRoutier):
        """
        Initialise un analyseur pour un réseau donné.

        Parameters
        ----------
        reseau : ReseauRoutier
            Instance du réseau routier à analyser.
        """
        self.reseau = reseau
        self.historique = []  # snapshots if needed

    def vitesses_moyennes_par_route(self) -> Dict[str, float]:
        """
        Calcule la vitesse moyenne sur chaque route du réseau.

        Returns
        -------
        dict[str, float]
            Dictionnaire associant à chaque nom de route sa vitesse
            moyenne (en m/s). Si une route ne contient aucun véhicule,
            la vitesse moyenne vaut 0.0.
        """
        res = {}
        for nom, route in self.reseau.routes.items():
            vitesses = [v.vitesse for v in route.vehicules if v is not None]
            res[nom] = statistics.mean(vitesses) if vitesses else 0.0
        return res

    def densites_par_route(self) -> Dict[str, float]:
        """
        Calcule la densité de véhicules pour chaque route.

        Returns
        -------
        dict[str, float]
            Dictionnaire associant à chaque nom de route la densité
            exprimée en véhicules par kilomètre.
        """
        res = {}
        for nom, route in self.reseau.routes.items():
            # véhicules / longueur (en km)
            km = route.longueur / 1000.0 if route.longueur > 0 else 1.0
            res[nom] = len(route.vehicules) / km
        return res

    def zones_congestion(self, seuil_vitesse: float = 5.0) -> List[str]:
        """
        Identifie les routes en situation de congestion.

        Parameters
        ----------
        seuil_vitesse : float, optional
            Vitesse moyenne seuil (en m/s) en dessous de laquelle une
            route est considérée comme congestionnée. Par défaut 5.0.

        Returns
        -------
        list[str]
            Liste des noms de routes dont la vitesse moyenne est
            inférieure au seuil spécifié.
        """
        res = []
        vms = self.vitesses_moyennes_par_route()
        for nom, vm in vms.items():
            if vm < seuil_vitesse:
                res.append(nom)
        return res

    def snapshot(self) -> Dict:
        """
        Capture un instantané des statistiques du réseau.

        L’instantané inclut les vitesses moyennes et les densités
        actuelles des routes. Chaque capture est stockée dans
        l’attribut ``historique``.

        Returns
        -------
        dict
            Un dictionnaire contenant :
                - ``vitesses_moyennes`` : dict[str, float]
                - ``densites`` : dict[str, float]
        """
        s = {
            "vitesses_moyennes": self.vitesses_moyennes_par_route(),
            "densites": self.densites_par_route(),
        }
        self.historique.append(s)
        return s
