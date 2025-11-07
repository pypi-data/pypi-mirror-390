"""
Module `reseau`
===============

Ce module définit la classe :class:`ReseauRoutier`, représentant un ensemble
de routes connectées formant un réseau de circulation.

Le réseau gère les relations de connectivité entre routes (avec
probabilités de bifurcation) et le déplacement des véhicules à travers
ces routes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .route import Route
from .vehicule import Vehicule


@dataclass
class ReseauRoutier:
    """
    Représente un réseau routier composé de plusieurs routes connectées.

    Le réseau permet d’ajouter des routes, de définir des connexions
    probabilistes entre elles, et de gérer le passage des véhicules
    d’une route à une autre.

    Attributes
    ----------
    routes : dict[str, Route]
        Dictionnaire associant le nom de chaque route à son objet
        :class:`Route`.
    adjacency : dict[str, list[tuple[str, float]]]
        Dictionnaire de connectivité indiquant, pour chaque route source,
        la liste des routes suivantes accessibles avec leurs probabilités
        de transition.
    """

    routes: Dict[str, Route] = field(default_factory=dict)
    adjacency: Dict[str, List[Tuple[str, float]]] = field(default_factory=dict)

    def ajouter_route(self, route: Route) -> None:
        """
        Ajoute une route au réseau.

        Parameters
        ----------
        route : Route
            Instance de la route à ajouter.
        """
        self.routes[route.nom] = route
        self.adjacency.setdefault(route.nom, [])

    def connecter(self, de: str, vers: str, proba: float = 1.0) -> None:
        """
        Connecte deux routes du réseau.

        Un véhicule atteignant la fin de la route ``de`` pourra être
        redirigé vers la route ``vers`` selon une probabilité donnée.

        Parameters
        ----------
        de : str
            Nom de la route de départ.
        vers : str
            Nom de la route d’arrivée.
        proba : float, optional
            Probabilité que le véhicule emprunte cette connexion
            (par défaut 1.0).

        Raises
        ------
        KeyError
            Si l’une des routes spécifiées n’existe pas dans le réseau.
        """
        if de not in self.routes or vers not in self.routes:
            raise KeyError("Route inconnue")
        self.adjacency.setdefault(de, []).append((vers, proba))

    def ajouter_vehicule_sur_route(self, veh: Vehicule, nom_route: str, position: float = 0.0) -> None:
        """
        Place un véhicule sur une route spécifique du réseau.

        Parameters
        ----------
        veh : Vehicule
            Le véhicule à insérer dans le réseau.
        nom_route : str
            Nom de la route sur laquelle placer le véhicule.
        position : float, optional
            Position initiale du véhicule (en mètres) le long de la route.
            Par défaut 0.0.
        """
        r = self.routes[nom_route]
        veh.position = max(0.0, min(position, r.longueur))
        r.ajouter_vehicule(veh)

    def etape_fin_route(self, veh: Vehicule) -> None:
        """
        Gère le comportement d’un véhicule ayant atteint la fin de sa route.

        Si une connexion sortante existe, le véhicule est transféré sur
        la prochaine route choisie aléatoirement selon les probabilités
        définies. Sinon, il est retiré du réseau (considéré arrivé).

        Parameters
        ----------
        veh : Vehicule
            Véhicule à traiter en fin de route.
        """
        r = veh.route
        if r is None:
            return
        if veh.position < r.longueur - 1e-6:
            return

        # Choix de la prochaine route selon les probabilités de bifurcation
        succ = self.adjacency.get(r.nom, [])
        if not succ:
            r.retirer_vehicule(veh)
            return

        import random
        noms = [s[0] for s in succ]
        probs = [s[1] for s in succ]

        # Normalisation des probabilités
        total = sum(probs)
        if total <= 0:
            r.retirer_vehicule(veh)
            return
        probs = [p / total for p in probs]

        # Sélection aléatoire de la route suivante
        next_nom = random.choices(noms, probs)[0]
        new_route = self.routes[next_nom]

        # Réinitialiser la position du véhicule et le transférer
        veh.position = 0.0
        r.retirer_vehicule(veh)
        new_route.ajouter_vehicule(veh)
