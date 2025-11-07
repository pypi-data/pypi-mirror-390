"""
Module `simulateur`
===================

Ce module définit la classe :class:`Simulateur`, responsable de
l’exécution d’une simulation de trafic sur un réseau routier donné.

Le simulateur orchestre la mise à jour des véhicules, la collecte
de statistiques via l’analyseur, et l’affichage ou l’exportation
éventuelle des résultats à chaque étape.
"""

from __future__ import annotations
from typing import Optional
import logging

from ..models.reseau import ReseauRoutier
from ..ui.affichage import Affichage
from ..ui.export import Exporteur
from ..core.analyseur import Analyseur

logger = logging.getLogger(__name__)


class Simulateur:
    """
    Classe principale gérant la simulation du trafic routier.

    Cette classe contrôle la boucle de simulation : mise à jour
    des véhicules, détection de fin de route, collecte de statistiques
    et visualisation/exportation facultative.

    Attributes
    ----------
    reseau : ReseauRoutier
        Le réseau routier simulé.
    afficher : Affichage or None
        Gestionnaire d’affichage de l’état du réseau à chaque étape,
        ou ``None`` si l’affichage est désactivé.
    exporter : Exporteur or None
        Objet responsable de l’exportation des données de simulation,
        ou ``None`` si non utilisé.
    analyseur : Analyseur
        Instance utilisée pour extraire les statistiques du réseau.
    """

    def __init__(self, reseau: ReseauRoutier, afficher: bool = True, exporter: Optional[Exporteur] = None):
        """
        Initialise le simulateur avec un réseau routier donné.

        Parameters
        ----------
        reseau : ReseauRoutier
            Le réseau routier sur lequel exécuter la simulation.
        afficher : bool, optional
            Si ``True``, active l’affichage graphique à chaque étape
            de simulation. Par défaut ``True``.
        exporter : Exporteur, optional
            Composant optionnel permettant d’enregistrer les données
            de simulation sur disque.
        """
        self.reseau = reseau
        self.afficher = Affichage() if afficher else None
        self.exporter = exporter
        self.analyseur = Analyseur(reseau)

    def lancer_simulation(self, n_tours: int, delta_t: float, unit: str = "s", afficher_intermediaire: bool = True):
        """
        Exécute la boucle principale de simulation du trafic.

        Parameters
        ----------
        n_tours : int
            Nombre total d’étapes (tours de simulation) à exécuter.
        delta_t : float
            Pas de temps entre deux étapes (en secondes ou minutes selon `unit`).
        unit : {"s", "min"}, optional
            Unité du pas de temps. Si `"min"`, le pas est converti en secondes.
        afficher_intermediaire : bool, optional
            Si ``True``, affiche l’état du réseau à chaque étape si un affichage
            est disponible. Par défaut ``True``.

        Returns
        -------
        list[dict]
            Liste d’instantanés statistiques collectés par l’analyseur
            à chaque tour de simulation. Chaque dictionnaire contient
            les clés ``"vitesses_moyennes"`` et ``"densites"``.

        Notes
        -----
        À chaque étape :
            - les véhicules de chaque route sont mis à jour,
            - les véhicules arrivés en fin de route sont traités,
            - un instantané des statistiques est collecté et stocké,
            - un affichage et/ou exportation peut être effectué.
        """
        if unit == "min":
            delta_t = delta_t * 60.0
        logging.info("Démarrage simulation: tours=%s, delta_t=%ss", n_tours, delta_t)
        results = []
        for t in range(n_tours):
            # Mise à jour des véhicules sur chaque route
            for r in self.reseau.routes.values():
                r.mettre_a_jour_vehicules(delta_t)

            # Gestion des véhicules arrivés en fin de route
            for r in list(self.reseau.routes.values()):
                for v in list(r.vehicules):
                    self.reseau.etape_fin_route(v)

            # Collecte des statistiques
            snap = self.analyseur.snapshot()
            results.append(snap)

            # Affichage ou exportation
            if afficher_intermediaire and self.afficher:
                self.afficher.afficher_etat(self.reseau, t, snap)
            if self.exporter:
                self.exporter.export_step(t, self.reseau, snap)

        return results
