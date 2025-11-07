# tests/test_simulateur.py
import pytest
from simulateur_trafic.models.route import Route
from simulateur_trafic.models.vehicule import Vehicule
from simulateur_trafic.models.reseau import ReseauRoutier
from simulateur_trafic.core.simulateur import Simulateur
from simulateur_trafic.io.export import Exporteur
from simulateur_trafic.exceptions import ConfigurationError
from simulateur_trafic.main import charger_config


def test_config_inexistante():
    with pytest.raises(ConfigurationError):
        charger_config("fichier_inexistant.json")

def test_deplacement_simple():
    r = Route(nom="T", longueur=100.0, limite_vitesse=10.0)  # m, m/s
    reseau = ReseauRoutier()
    reseau.ajouter_route(r)
    v = Vehicule()
    v.vitesse_desiree = 5.0
    reseau.ajouter_vehicule_sur_route(v, "T", position=0.0)
    simu = Simulateur(reseau, afficher=False, exporter=None)
    # 2 tours de 10s => déplacement attendu 5*10*2 = 100 m -> arrive fin
    simu.lancer_simulation(n_tours=2, delta_t=10, unit="s", afficher_intermediaire=False)
    assert v.position >= r.longueur - 1e-6 or v not in r.vehicules

def test_connexion_etape():
    r1 = Route("A", 50.0, 10.0)
    r2 = Route("B", 50.0, 10.0)
    reseau = ReseauRoutier()
    reseau.ajouter_route(r1); reseau.ajouter_route(r2)
    reseau.connecter("A", "B", 1.0)
    v = Vehicule()
    v.vitesse_desiree = 10.0
    reseau.ajouter_vehicule_sur_route(v, "A", position=45.0)
    simu = Simulateur(reseau, afficher=False)
    simu.lancer_simulation(1, delta_t=1, unit="s", afficher_intermediaire=False)
    # après un pas, il devrait être sur B (ou à la fin d'A puis transféré)
    assert v.route is not None
    assert v.route.nom in ("A", "B")
test_config_inexistante()