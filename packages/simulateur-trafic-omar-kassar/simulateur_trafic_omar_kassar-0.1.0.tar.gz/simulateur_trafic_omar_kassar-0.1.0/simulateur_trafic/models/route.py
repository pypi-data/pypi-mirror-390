"""
Module `route`
==============

Ce module définit la classe :class:`Route`, représentant une route
du réseau routier. Chaque route contient une liste de véhicules et
gère leur déplacement localement, selon un pas de temps donné.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from .vehicule import Vehicule


@dataclass
class Route:
    """
    Représente une route du réseau routier.

    Une route est caractérisée par sa longueur, sa limite de vitesse,
    et la liste des véhicules qui s’y trouvent. Elle fournit des méthodes
    pour ajouter, retirer et mettre à jour les véhicules.

    Attributes
    ----------
    nom : str
        Nom unique de la route.
    longueur : float
        Longueur de la route en mètres.
    limite_vitesse : float
        Limite de vitesse sur cette route (en m/s).
    vehicules : list[Vehicule]
        Liste des véhicules actuellement présents sur la route.
    """

    nom: str
    longueur: float
    limite_vitesse: float
    vehicules: List[Vehicule] = field(default_factory=list)

    def ajouter_vehicule(self, v: Vehicule) -> None:
        """
        Ajoute un véhicule sur la route s’il n’y est pas déjà.

        Parameters
        ----------
        v : Vehicule
            Le véhicule à ajouter à la route.
        """
        if v not in self.vehicules:
            self.vehicules.append(v)
            v.route = self

    def retirer_vehicule(self, v: Vehicule) -> None:
        """
        Retire un véhicule de la route.

        Parameters
        ----------
        v : Vehicule
            Le véhicule à retirer.
        """
        if v in self.vehicules:
            self.vehicules.remove(v)
            v.route = None

    def mettre_a_jour_vehicules(self, delta_t: float) -> None:
        """
        Met à jour la position de tous les véhicules présents sur la route.

        Chaque véhicule avance en fonction de sa vitesse et du pas de temps
        fourni. Les véhicules sont triés par position afin d’assurer un ordre
        cohérent dans la mise à jour.

        Parameters
        ----------
        delta_t : float
            Pas de temps en secondes utilisé pour la mise à jour.
        """
        # Tri des véhicules selon leur position croissante
        self.vehicules.sort(key=lambda x: x.position)

        for v in list(self.vehicules):  # copie au cas où le véhicule change de route
            v.avancer(delta_t)
            # Si le véhicule atteint la fin, sa gestion est faite par le réseau
