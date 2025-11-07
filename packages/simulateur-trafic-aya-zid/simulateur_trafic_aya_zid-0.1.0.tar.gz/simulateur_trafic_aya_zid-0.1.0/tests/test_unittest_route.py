"""
Tests unitaires unittest pour la classe Route

Objectif : vérifier la gestion des véhicules sur une route avec unittest.
"""

import unittest
import sys
import os

# Ajouter le chemin pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.route import Route
from models.vehicule import Vehicule


class TestRouteUnittest(unittest.TestCase):
    """Tests unittest pour la classe Route."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        self.route = Route("Autoroute_A1", longueur=5000, limite_vitesse=130)
        self.vehicule = Vehicule(identifiant=1, route_actuelle="Autoroute_A1", position=0, vitesse=50)
    
    def test_creation_route_valide(self):
        """Test la création d'une route avec des paramètres valides."""
        # Assert
        self.assertEqual(self.route.nom, "Autoroute_A1")
        self.assertEqual(self.route.longueur, 5000)
        self.assertEqual(self.route.limite_vitesse, 130)
        self.assertEqual(self.route.vehicules_presents, {})
        self.assertEqual(len(self.route.vehicules_presents), 0)
    
    
    def test_ajouter_vehicule_valide(self):
        """Test l'ajout d'un véhicule valide à une route."""
        # Act
        self.route.ajouter_vehicule(self.vehicule)
        
        # Assert
        self.assertEqual(len(self.route.vehicules_presents), 1)
        self.assertIn(self.vehicule.identifiant, self.route.vehicules_presents)
        self.assertEqual(self.route.vehicules_presents[self.vehicule.identifiant], self.vehicule)
        self.assertEqual(self.vehicule.route_actuelle, self.route.nom)
    
    
    def test_supprimer_vehicule_existant(self):
        """Test la suppression d'un véhicule existant."""
        # Arrange
        self.route.ajouter_vehicule(self.vehicule)
        self.assertEqual(len(self.route.vehicules_presents), 1)
        
        # Act
        vehicule_supprime = self.route.supprimer_vehicule(self.vehicule.identifiant)
        
        # Assert
        self.assertEqual(vehicule_supprime, self.vehicule)
        self.assertEqual(len(self.route.vehicules_presents), 0)
        self.assertNotIn(self.vehicule.identifiant, self.route.vehicules_presents)
    
    def test_supprimer_vehicule_inexistant(self):
        """Test la suppression d'un véhicule qui n'existe pas."""
        # Act
        vehicule_supprime = self.route.supprimer_vehicule(999)  # ID inexistant
        
        # Assert
        self.assertIsNone(vehicule_supprime)
        self.assertEqual(len(self.route.vehicules_presents), 0)
    
    def test_mettre_a_jour_vehicules_aucun_depassement(self):
        """Test la mise à jour quand aucun véhicule ne dépasse la route."""
        # Arrange
        self.route.ajouter_vehicule(self.vehicule)
        
        # Act
        vehicules_sortis = self.route.mettre_a_jour_vehicules()
        
        # Assert
        self.assertEqual(vehicules_sortis, [])
        self.assertEqual(len(self.route.vehicules_presents), 1)
    
    def test_mettre_a_jour_vehicules_avec_depassement(self):
        """Test la mise à jour quand un véhicule dépasse la fin de la route."""
        # Arrange
        route_courte = Route("Route_Courte", longueur=1000, limite_vitesse=50)
        vehicule_fin = Vehicule(identifiant=3, route_actuelle=route_courte.nom, position=950, vitesse=30)
        route_courte.ajouter_vehicule(vehicule_fin)
        
        # Act - Le véhicule est à 950m sur une route de 1000m
        vehicule_fin.avancer(100)  # Maintenant à 1050m > 1000m
        vehicules_sortis = route_courte.mettre_a_jour_vehicules()
        
        # Assert
        self.assertEqual(len(vehicules_sortis), 1)
        self.assertEqual(vehicules_sortis[0], vehicule_fin)
        self.assertEqual(len(route_courte.vehicules_presents), 0)
        self.assertNotIn(vehicule_fin.identifiant, route_courte.vehicules_presents)
    
    def test_get_nombre_vehicules(self):
        """Test le comptage du nombre de véhicules."""
        # Assert - Route vide
        self.assertEqual(self.route.get_nombre_vehicules(), 0)
        
        # Act & Assert - Un véhicule
        self.route.ajouter_vehicule(self.vehicule)
        self.assertEqual(self.route.get_nombre_vehicules(), 1)
        
        # Act & Assert - Deux véhicules
        vehicule2 = Vehicule(identifiant=2, route_actuelle=self.route.nom, position=500, vitesse=40)
        self.route.ajouter_vehicule(vehicule2)
        self.assertEqual(self.route.get_nombre_vehicules(), 2)
    
    def test_get_densite_trafic_route_vide(self):
        """Test le calcul de densité sur une route vide."""
        # Act
        densite = self.route.get_densite_trafic()
        
        # Assert
        self.assertEqual(densite, 0)
    
    def test_get_densite_trafic_route_avec_vehicules(self):
        """Test le calcul de densité sur une route avec véhicules."""
        # Arrange
        route_courte = Route("Route_Courte", longueur=1000, limite_vitesse=50)  # 1km
        vehicule1 = Vehicule(identifiant=1, route_actuelle=route_courte.nom, position=0, vitesse=30)
        vehicule2 = Vehicule(identifiant=2, route_actuelle=route_courte.nom, position=500, vitesse=40)
        route_courte.ajouter_vehicule(vehicule1)
        route_courte.ajouter_vehicule(vehicule2)
        
        # Act
        densite = route_courte.get_densite_trafic()
        
        # Assert - 2 véhicules sur 1km = densité 2
        self.assertEqual(densite, 2.0)
    
    def test_representation_textuelle(self):
        """Test la représentation textuelle de la route."""
        # Act
        representation = str(self.route)
        
        # Assert
        self.assertIn("Route 'Autoroute_A1'", representation)
        self.assertIn("5000m", representation)
        self.assertIn("limite: 130km/h", representation)
        self.assertIn("0 véhicules", representation)
    
    def test_representation_technique(self):
        """Test la représentation technique de la route."""
        # Act
        representation = repr(self.route)
        
        # Assert
        self.assertIn("Route", representation)
        self.assertIn("nom='Autoroute_A1'", representation)
        self.assertIn("longueur=5000", representation)
        self.assertIn("limite_vitesse=130", representation)


if __name__ == '__main__':
    unittest.main()