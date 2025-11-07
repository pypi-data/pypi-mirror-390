"""
Tests unitaires pour la classe Vehicule

Objectif : valider le comportement d'un véhicule.
Tests à réaliser :
• L'avancement modifie correctement la position.
• Le véhicule ne dépasse pas la longueur de la route.
• Le changement de route remet la position à zéro.
"""

import pytest
from models.vehicule import Vehicule


class TestVehicule:
    """Tests pour la classe Vehicule."""
    
    def test_creation_vehicule_valide(self):
        """Test la création d'un véhicule avec des paramètres valides."""
        # Arrange & Act
        vehicule = Vehicule(identifiant=1, route_actuelle="Route_A", position=100, vitesse=50)
        
        # Assert
        assert vehicule.identifiant == 1
        assert vehicule.route_actuelle == "Route_A"
        assert vehicule.position == 100
        assert vehicule.vitesse == 50
        assert vehicule.historique_routes == ["Route_A"]
    
   
    def test_avancer_distance_positive(self, vehicule_exemple):
        """Test que l'avancement modifie correctement la position avec une distance positive."""
        # Arrange
        vehicule = vehicule_exemple
        position_initiale = vehicule.position
        
        # Act
        vehicule.avancer(150.5)
        
        # Assert
        assert vehicule.position == position_initiale + 150.5
    
    def test_avancer_distance_nulle(self, vehicule_exemple):
        """Test l'avancement avec une distance nulle."""
        # Arrange
        vehicule = vehicule_exemple
        position_initiale = vehicule.position
        
        # Act
        vehicule.avancer(0)
        
        # Assert
        assert vehicule.position == position_initiale
    
   
    def test_changer_de_route_valide(self, vehicule_exemple):
        """Test le changement de route avec des paramètres valides."""
        # Arrange
        vehicule = vehicule_exemple
        ancienne_route = vehicule.route_actuelle
        ancienne_position = vehicule.position
        historique_initial = vehicule.historique_routes.copy()
        
        # Act
        vehicule.changer_de_route("Nouvelle_Route", 200)
        
        # Assert
        assert vehicule.route_actuelle == "Nouvelle_Route"
        assert vehicule.position == 200
        assert vehicule.historique_routes == historique_initial + ["Nouvelle_Route"]
        assert len(vehicule.historique_routes) == len(historique_initial) + 1
    
    def test_changer_de_route_position_par_defaut(self, vehicule_exemple):
        """Test le changement de route avec la position par défaut (0)."""
        # Arrange
        vehicule = vehicule_exemple
        # Act
        vehicule.changer_de_route("Nouvelle_Route")
        # Assert
        assert vehicule.route_actuelle == "Nouvelle_Route"
        assert vehicule.position == 0
    
  
    def test_representation_textuelle(self, vehicule_exemple):
        """Test la représentation textuelle du véhicule."""
        # Arrange
        vehicule = vehicule_exemple
        
        # Act
        representation = str(vehicule)
        
        # Assert
        assert "Véhicule 1" in representation
        assert "A1" in representation
        assert "position 0m" in representation
        assert "vitesse 30km/h" in representation
    
    def test_representation_technique(self, vehicule_exemple):
        """Test la représentation technique du véhicule."""
        # Arrange
        vehicule = vehicule_exemple
        
        # Act
        representation = repr(vehicule)
        
        # Assert
        assert "Vehicule" in representation
        assert "identifiant=1" in representation
        assert "route_actuelle='A1'" in representation
        assert "position=0" in representation
        assert "vitesse=30" in representation
    
    def test_historique_routes_apres_changements(self):
        """Test que l'historique des routes est correctement mis à jour."""
        # Arrange
        vehicule = Vehicule(identifiant=1, route_actuelle="Route_Initiale")
        
        # Act
        vehicule.changer_de_route("Route_Deux")
        vehicule.changer_de_route("Route_Trois")
        
        # Assert
        assert vehicule.historique_routes == ["Route_Initiale", "Route_Deux", "Route_Trois"]
        assert len(vehicule.historique_routes) == 3
    
    def test_vitesse_modifiable(self, vehicule_exemple):
        """Test que la vitesse du véhicule peut être modifiée."""
        # Arrange
        vehicule = vehicule_exemple
        
        # Act
        vehicule.vitesse = 80
        
        # Assert
        assert vehicule.vitesse == 80