"""
Module `affichage`
==================

Ce module fournit la classe :class:`Affichage`, responsable de l’affichage
visuel et textuel de l’état du réseau routier.  
Il permet d’observer la simulation à travers deux formes de rendu :
une évolution de la vitesse moyenne dans le temps, et une représentation
graphique de la position des véhicules sur leurs routes.
"""

from __future__ import annotations
import matplotlib.pyplot as plt
import math
from ..models.reseau import ReseauRoutier


class Affichage:
    """
    Classe utilitaire pour l'affichage du réseau routier et des résultats de simulation.

    La classe fournit des méthodes pour tracer la vitesse moyenne au cours
    du temps et pour visualiser l’état instantané du réseau routier
    (positions des véhicules sur chaque route).

    Notes
    -----
    Cette classe est purement visuelle : elle ne modifie pas l’état du réseau.
    """

    def __init__(self):
        """Initialise une instance d'Affichage (aucun état interne)."""
        pass

    @staticmethod
    def afficher_vitesse_moyenne(results: list[dict]) -> None:
        """
        Affiche l’évolution de la vitesse moyenne au cours du temps.

        Trace un graphique (via Matplotlib) représentant la vitesse moyenne
        des véhicules sur le réseau à chaque tour de simulation.

        Parameters
        ----------
        results : list of dict
            Liste de snapshots contenant pour chaque tour :
            - ``"t"`` : indice du tour (int)
            - ``"vitesse_moyenne"`` : vitesse moyenne (float, en km/h)

        Raises
        ------
        KeyError
            Si les clés ``"t"`` ou ``"vitesse_moyenne"`` sont absentes
            d’un des dictionnaires de `results`.
        """
        tours = [snap["t"] for snap in results]
        vitesses = [snap["vitesse_moyenne"] for snap in results]

        plt.plot(tours, vitesses)
        plt.xlabel("Temps (tours)")
        plt.ylabel("Vitesse moyenne (km/h)")
        plt.title("Évolution de la vitesse moyenne")
        plt.show()

    def afficher_etat(self, reseau: ReseauRoutier, tour: int, snapshot: dict) -> None:
        """
        Affiche l’état du réseau routier à un instant donné.

        Montre en console les positions des véhicules par route,
        puis génère une visualisation graphique simple :
        chaque route est représentée comme une ligne horizontale,
        et les véhicules sont placés en fonction de leur position.

        Parameters
        ----------
        reseau : ReseauRoutier
            Instance du réseau routier contenant les routes et véhicules.
        tour : int
            Numéro du tour actuel (itération de la simulation).
        snapshot : dict
            Données du tour courant (non utilisées ici mais passées pour compatibilité).
        """
        print(f"--- Tour {tour} ---")
        for nom, route in reseau.routes.items():
            positions = [v.position for v in route.vehicules]
            print(f"{nom}: {len(route.vehicules)} véhicules, positions={['{:.1f}'.format(p) for p in positions]}")

        fig, ax = plt.subplots(figsize=(8, 1 + 0.8 * len(reseau.routes)))
        y = 0
        yticks = []
        ylabels = []
        for nom, route in reseau.routes.items():
            xs = [v.position for v in route.vehicules]
            ax.scatter(xs, [y] * len(xs))
            ax.hlines(y, 0, route.longueur, linewidth=2)
            yticks.append(y)
            ylabels.append(f"{nom} ({route.longueur} m)")
            y += 1

        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels)
        ax.set_xlabel("Position (m)")
        ax.set_title(f"État du réseau - tour {tour}")
        plt.tight_layout()
        plt.show()
