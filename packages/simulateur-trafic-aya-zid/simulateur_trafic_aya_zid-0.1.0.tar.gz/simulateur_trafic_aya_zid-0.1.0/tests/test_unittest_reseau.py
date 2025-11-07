"""
Tests unitaires unittest pour la classe ReseauRoutier

Objectif : vérifier la cohérence globale du réseau routier avec unittest.
"""

import unittest
import sys
import os

# Ajouter le chemin pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.reseau import ReseauRoutier
from models.route import Route
from models.vehicule import Vehicule

class TestReseauRoutierUnittest(unittest.TestCase):
    """Tests unittest pour la classe ReseauRoutier."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        self.reseau = ReseauRoutier()
        self.route1 = Route("Route_A", longueur=1000, limite_vitesse=50)
        self.route2 = Route("Route_B", longueur=2000, limite_vitesse=70)
        self.vehicule = Vehicule(identifiant=1, route_actuelle="Route_A", position=0, vitesse=30)
    
    def test_creation_reseau_vide(self):
        """Test la création d'un réseau routier vide."""
        # Assert
        self.assertEqual(self.reseau.routes, {})
        self.assertEqual(self.reseau.intersections, {})
        self.assertEqual(self.reseau.historique_trafic, [])
        self.assertEqual(len(self.reseau.routes), 0)
        self.assertEqual(len(self.reseau.intersections), 0)
        self.assertEqual(len(self.reseau.historique_trafic), 0)
    
    def test_ajouter_route_valide(self):
        """Test l'ajout d'une route valide au réseau."""
        # Act
        self.reseau.ajouter_route(self.route1)
        
        # Assert
        self.assertEqual(len(self.reseau.routes), 1)
        self.assertIn(self.route1.nom, self.reseau.routes)
        self.assertEqual(self.reseau.routes[self.route1.nom], self.route1)
        self.assertIn(self.route1.nom, self.reseau.intersections)
        self.assertEqual(self.reseau.intersections[self.route1.nom], [])
    
    
    def test_ajouter_intersection_valide(self):
        """Test l'ajout d'une intersection valide entre deux routes."""
        # Arrange
        self.reseau.ajouter_route(self.route1)
        self.reseau.ajouter_route(self.route2)
        
        # Act
        self.reseau.ajouter_intersection("Route_A", "Route_B")
        
        # Assert
        self.assertIn("Route_B", self.reseau.intersections["Route_A"])
        self.assertEqual(len(self.reseau.intersections["Route_A"]), 1)
    
    def test_ajouter_intersection_dupliquee(self):
        """Test que l'ajout de la même intersection plusieurs fois ne crée pas de doublons."""
        # Arrange
        self.reseau.ajouter_route(self.route1)
        self.reseau.ajouter_route(self.route2)
        
        # Act
        self.reseau.ajouter_intersection("Route_A", "Route_B")
        self.reseau.ajouter_intersection("Route_A", "Route_B")  # Dupliqué
        
        # Assert
        self.assertIn("Route_B", self.reseau.intersections["Route_A"])
        self.assertEqual(len(self.reseau.intersections["Route_A"]), 1)  # Pas de doublon
    
    def test_get_route_existante(self):
        """Test la récupération d'une route existante."""
        # Arrange
        self.reseau.ajouter_route(self.route1)
        
        # Act
        route = self.reseau.get_route("Route_A")
        
        # Assert
        self.assertIsNotNone(route)
        self.assertEqual(route.nom, "Route_A")
    
    def test_get_route_inexistante(self):
        """Test la récupération d'une route inexistante."""
        # Act
        route = self.reseau.get_route("Route_Inexistante")
        
        # Assert
        self.assertIsNone(route)
    
    def test_get_routes_destination_existantes(self):
        """Test la récupération des routes destination pour une route source existante."""
        # Arrange
        self.reseau.ajouter_route(self.route1)
        self.reseau.ajouter_route(self.route2)
        self.reseau.ajouter_intersection("Route_A", "Route_B")
        
        # Act
        destinations = self.reseau.get_routes_destination("Route_A")
        
        # Assert
        self.assertEqual(destinations, ["Route_B"])
        self.assertEqual(len(destinations), 1)
    
    def test_get_routes_destination_inexistante(self):
        """Test la récupération des routes destination pour une route source inexistante."""
        # Act
        destinations = self.reseau.get_routes_destination("Route_Inexistante")
        
        # Assert
        self.assertEqual(destinations, [])
    
    def test_get_nombre_total_vehicules_reseau_vide(self):
        """Test le comptage des véhicules dans un réseau vide."""
        # Act
        total = self.reseau.get_nombre_total_vehicules()
        
        # Assert
        self.assertEqual(total, 0)
    
    def test_get_nombre_total_vehicules_reseau_avec_vehicules(self):
        """Test le comptage des véhicules dans un réseau avec véhicules."""
        # Arrange
        self.reseau.ajouter_route(self.route1)
        self.reseau.ajouter_route(self.route2)
        self.route1.ajouter_vehicule(self.vehicule)
        
        vehicule2 = Vehicule(identifiant=2, route_actuelle="Route_B", position=500, vitesse=40)
        self.route2.ajouter_vehicule(vehicule2)
        
        # Act
        total = self.reseau.get_nombre_total_vehicules()
        
        # Assert
        self.assertEqual(total, 2)  # 1 véhicule sur Route_A + 1 véhicule sur Route_B
    
    def test_get_densite_trafic_moyenne_reseau_vide(self):
        """Test le calcul de densité moyenne dans un réseau vide."""
        # Act
        densite_moyenne = self.reseau.get_densite_trafic_moyenne()
        
        # Assert
        self.assertEqual(densite_moyenne, 0)
    
    def test_get_densite_trafic_moyenne_reseau_avec_routes(self):
        """Test le calcul de densité moyenne dans un réseau avec routes."""
        # Arrange
        route_courte = Route("Route_Courte", longueur=1000, limite_vitesse=50)  # 1km
        route_longue = Route("Route_Longue", longueur=5000, limite_vitesse=80)  # 5km
        
        # Ajouter des véhicules
        vehicule1 = Vehicule(identifiant=1, route_actuelle="Route_Courte", position=0, vitesse=30)
        vehicule2 = Vehicule(identifiant=2, route_actuelle="Route_Longue", position=500, vitesse=40)
        route_courte.ajouter_vehicule(vehicule1)
        route_longue.ajouter_vehicule(vehicule2)
        
        self.reseau.ajouter_route(route_courte)
        self.reseau.ajouter_route(route_longue)
        
        # Act
        densite_moyenne = self.reseau.get_densite_trafic_moyenne()
        
        # Assert
        # Route_Courte: 1 véhicule sur 1km = densité 1
        # Route_Longue: 1 véhicule sur 5km = densité 0.2
        # Moyenne = (1 + 0.2) / 2 = 0.6
        self.assertEqual(densite_moyenne, 0.6)
    
    def test_mettre_a_jour_reseau_sans_changements(self):
        """Test la mise à jour du réseau sans véhicules sortants."""
        # Arrange
        self.reseau.ajouter_route(self.route1)
        self.route1.ajouter_vehicule(self.vehicule)
        historique_initial = len(self.reseau.historique_trafic)
        
        # Act
        stats = self.reseau.mettre_a_jour_reseau()
        
        # Assert
        self.assertEqual(stats['changements_route'], 0)
        self.assertEqual(stats['vehicules_sortis'], 0)
        self.assertEqual(len(self.reseau.historique_trafic), historique_initial + 1)
        self.assertEqual(self.reseau.get_nombre_total_vehicules(), 1)  # Le véhicule est toujours là
    
    def test_representation_textuelle(self):
        """Test la représentation textuelle du réseau."""
        # Arrange
        self.reseau.ajouter_route(self.route1)
        self.route1.ajouter_vehicule(self.vehicule)
        
        # Act
        representation = str(self.reseau)
        
        # Assert
        self.assertIn("Réseau routier", representation)
        self.assertIn("1 routes", representation)
        self.assertIn("1 véhicules", representation)
    
    def test_representation_technique(self):
        """Test la représentation technique du réseau."""
        # Arrange
        self.reseau.ajouter_route(self.route1)
        self.route1.ajouter_vehicule(self.vehicule)
        
        # Act
        representation = repr(self.reseau)
        
        # Assert
        self.assertIn("ReseauRoutier", representation)
        self.assertIn("nb_routes=1", representation)
        self.assertIn("nb_vehicules=1", representation)
    
    def test_historique_trafic_apres_mise_a_jour(self):
        """Test que l'historique du trafic est mis à jour correctement."""
        # Arrange
        self.reseau.ajouter_route(self.route1)
        self.route1.ajouter_vehicule(self.vehicule)
        historique_initial = len(self.reseau.historique_trafic)
        
        # Act
        self.reseau.mettre_a_jour_reseau()
        self.reseau.mettre_a_jour_reseau()
        
        # Assert
        self.assertEqual(len(self.reseau.historique_trafic), historique_initial + 2)
        
        # Vérifier la structure des données historiques
        dernier_etat = self.reseau.historique_trafic[-1]
        self.assertIn('timestamp', dernier_etat)
        self.assertIn('total_vehicules', dernier_etat)
        self.assertIn('densite_moyenne', dernier_etat)
        self.assertEqual(dernier_etat['timestamp'], len(self.reseau.historique_trafic) - 1)


if __name__ == '__main__':
    unittest.main()