"""
Module `vehicule`
=================

Ce module définit la classe :class:`Vehicule`, représentant un véhicule
circulant dans le réseau routier. Chaque véhicule possède une position,
une vitesse, et une vitesse désirée, et peut se déplacer ou changer
de route au cours de la simulation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Vehicule:
    """
    Représente un véhicule dans le réseau routier.

    Un véhicule est caractérisé par sa position le long d'une route,
    sa vitesse actuelle et sa vitesse de croisière désirée. Il peut
    se déplacer sur une route et en changer selon la logique du réseau.

    Attributes
    ----------
    id : str
        Identifiant unique du véhicule (UUID4).
    position : float
        Position actuelle du véhicule sur la route (en mètres depuis le départ).
    vitesse : float
        Vitesse instantanée du véhicule (en m/s).
    vitesse_desiree : float
        Vitesse cible ou de croisière du véhicule (en m/s).
    route : Route | None
        Référence à la route actuelle sur laquelle se trouve le véhicule.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position: float = 0.0
    vitesse: float = 0.0
    vitesse_desiree: float = 15.0
    route: Optional["Route"] = None

    def avancer(self, delta_t: float) -> None:
        """
        Fait avancer le véhicule le long de sa route.

        La vitesse effective est la plus faible entre la vitesse désirée
        et la limite de vitesse de la route. Si le véhicule atteint la fin
        de la route, sa position est bornée à la longueur maximale.

        Parameters
        ----------
        delta_t : float
            Pas de temps (en secondes) utilisé pour le déplacement.
        """
        if self.route is None:
            return

        # Détermination de la vitesse effective
        limite = self.route.limite_vitesse
        v_effective = min(self.vitesse_desiree, limite)

        # Mise à jour de la vitesse et de la position
        self.vitesse = v_effective
        nouvelle_position = self.position + self.vitesse * delta_t

        if nouvelle_position > self.route.longueur:
            # Véhicule arrivé en fin de route
            self.position = self.route.longueur
        else:
            self.position = nouvelle_position

    def changer_de_route(self, nouvelle_route: "Route", position: float = 0.0) -> None:
        """
        Déplace le véhicule vers une autre route du réseau.

        La suppression et l’ajout du véhicule sont gérés par les méthodes
        de la classe :class:`Route`.

        Parameters
        ----------
        nouvelle_route : Route
            Nouvelle route sur laquelle transférer le véhicule.
        position : float, optional
            Position initiale sur la nouvelle route (en mètres),
            par défaut 0.0.
        """
        if self.route:
            self.route.retirer_vehicule(self)

        self.route = nouvelle_route
        self.position = max(0.0, min(position, nouvelle_route.longueur))
        nouvelle_route.ajouter_vehicule(self)
