"""
Tests unitaires unittest pour la classe Vehicule

Objectif : valider le comportement d'un véhicule avec le framework unittest.
"""

import unittest
import sys
import os

# Ajouter le chemin pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.vehicule import Vehicule


class TestVehiculeUnittest(unittest.TestCase):
    """Tests unittest pour la classe Vehicule."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        self.vehicule = Vehicule(identifiant=1, route_actuelle="Route_A", position=100, vitesse=50)
    
    def test_creation_vehicule_valide(self):
        """Test la création d'un véhicule avec des paramètres valides."""
        # Assert
        self.assertEqual(self.vehicule.identifiant, 1)
        self.assertEqual(self.vehicule.route_actuelle, "Route_A")
        self.assertEqual(self.vehicule.position, 100)
        self.assertEqual(self.vehicule.vitesse, 50)
        self.assertEqual(self.vehicule.historique_routes, ["Route_A"])
    
   
   
    def test_avancer_distance_positive(self):
        """Test que l'avancement modifie correctement la position."""
        # Arrange
        position_initiale = self.vehicule.position
        
        # Act
        self.vehicule.avancer(150.5)
        
        # Assert
        self.assertEqual(self.vehicule.position, position_initiale + 150.5)
    
    def test_avancer_distance_nulle(self):
        """Test l'avancement avec une distance nulle."""
        # Arrange
        position_initiale = self.vehicule.position
        
        # Act
        self.vehicule.avancer(0)
        
        # Assert
        self.assertEqual(self.vehicule.position, position_initiale)
    
   
    def test_changer_de_route_valide(self):
        """Test le changement de route avec des paramètres valides."""
        # Arrange
        ancienne_route = self.vehicule.route_actuelle
        ancienne_position = self.vehicule.position
        historique_initial = self.vehicule.historique_routes.copy()
        
        # Act
        self.vehicule.changer_de_route("Nouvelle_Route", 200)
        
        # Assert
        self.assertEqual(self.vehicule.route_actuelle, "Nouvelle_Route")
        self.assertEqual(self.vehicule.position, 200)
        self.assertEqual(self.vehicule.historique_routes, historique_initial + ["Nouvelle_Route"])
        self.assertEqual(len(self.vehicule.historique_routes), len(historique_initial) + 1)
    
    def test_changer_de_route_position_par_defaut(self):
        """Test le changement de route avec la position par défaut."""
        # Act
        self.vehicule.changer_de_route("Nouvelle_Route")
        
        # Assert
        self.assertEqual(self.vehicule.route_actuelle, "Nouvelle_Route")
        self.assertEqual(self.vehicule.position, 0)
    
   
    def test_representation_textuelle(self):
        """Test la représentation textuelle du véhicule."""
        # Act
        representation = str(self.vehicule)
        
        # Assert
        self.assertIn("Véhicule 1", representation)
        self.assertIn("Route_A", representation)
        self.assertIn("position 100m", representation)
        self.assertIn("vitesse 50km/h", representation)
    
    def test_representation_technique(self):
        """Test la représentation technique du véhicule."""
        # Act
        representation = repr(self.vehicule)
        
        # Assert
        self.assertIn("Vehicule", representation)
        self.assertIn("identifiant=1", representation)
        self.assertIn("route_actuelle='Route_A'", representation)
        self.assertIn("position=100", representation)
        self.assertIn("vitesse=50", representation)
    
    def test_historique_routes_apres_changements(self):
        """Test que l'historique des routes est correctement mis à jour."""
        # Act
        self.vehicule.changer_de_route("Route_Deux")
        self.vehicule.changer_de_route("Route_Trois")
        
        # Assert
        self.assertEqual(self.vehicule.historique_routes, ["Route_A", "Route_Deux", "Route_Trois"])
        self.assertEqual(len(self.vehicule.historique_routes), 3)
    
    def test_vitesse_modifiable(self):
        """Test que la vitesse du véhicule peut être modifiée."""
        # Act
        self.vehicule.vitesse = 80
        
        # Assert
        self.assertEqual(self.vehicule.vitesse, 80)


if __name__ == '__main__':
    unittest.main()