"""
Tests unitaires pour la classe Route

Objectif : vérifier la gestion des véhicules sur une route.
Tests à réaliser :
• L'ajout de véhicule fonctionne.
• La mise à jour avance les véhicules.
"""

import pytest
from models.route import Route
from models.vehicule import Vehicule


class TestRoute:
    """Tests pour la classe Route."""
    
    def test_creation_route_valide(self):
        """Test la création d'une route avec des paramètres valides."""
        # Arrange & Act
        route = Route("Autoroute_A1", longueur=5000, limite_vitesse=130)
        
        # Assert
        assert route.nom == "Autoroute_A1"
        assert route.longueur == 5000
        assert route.limite_vitesse == 130
        assert route.vehicules_presents == {}
        assert len(route.vehicules_presents) == 0
    

    def test_supprimer_vehicule_existant(self, route_simple, vehicule_exemple):
        """Test la suppression d'un véhicule existant."""
        # Arrange
        route = route_simple
        route.ajouter_vehicule(vehicule_exemple)
        assert len(route.vehicules_presents) == 1
        # Act
        vehicule_supprime = route.supprimer_vehicule(vehicule_exemple.identifiant)
        # Assert
        assert vehicule_supprime == vehicule_exemple
        assert len(route.vehicules_presents) == 0
        assert vehicule_exemple.identifiant not in route.vehicules_presents
    
    def test_supprimer_vehicule_inexistant(self, route_simple):
        """Test la suppression d'un véhicule qui n'existe pas."""
        # Arrange
        route = route_simple
        
        # Act
        vehicule_supprime = route.supprimer_vehicule(999)  # ID inexistant
        
        # Assert
        assert vehicule_supprime is None
        assert len(route.vehicules_presents) == 0
    
    def test_mettre_a_jour_vehicules_aucun_depassement(self, route_simple, vehicule_exemple):
        """Test la mise à jour quand aucun véhicule ne dépasse la route."""
        # Arrange
        route = route_simple
        route.ajouter_vehicule(vehicule_exemple)
        # Act
        vehicules_sortis = route.mettre_a_jour_vehicules()
        # Assert
        assert vehicules_sortis == []
        assert len(route.vehicules_presents) == 1
    
    def test_mettre_a_jour_vehicules_avec_depassement(self, route_simple, vehicule_pres_fin_route):
        """Test la mise à jour quand un véhicule dépasse la fin de la route."""
        # Arrange
        route = route_simple
        vehicule = vehicule_pres_fin_route
        route.ajouter_vehicule(vehicule)
        
        # Act - Le véhicule est à 950m sur une route de 1000m
        vehicule.avancer(100)  # Maintenant à 1050m > 1000m
        vehicules_sortis = route.mettre_a_jour_vehicules()
        
        # Assert
        assert len(vehicules_sortis) == 1
        assert vehicules_sortis[0] == vehicule
        assert len(route.vehicules_presents) == 0
        assert vehicule.identifiant not in route.vehicules_presents
    
    def test_get_nombre_vehicules(self, route_simple, vehicule_exemple, vehicule_avance):
        """Test le comptage du nombre de véhicules."""
        # Arrange
        route = route_simple
        
        # Act & Assert - Route vide
        assert route.get_nombre_vehicules() == 0
        
        # Act & Assert - Un véhicule
        route.ajouter_vehicule(vehicule_exemple)
        assert route.get_nombre_vehicules() == 1
        
        # Act & Assert - Deux véhicules
        route.ajouter_vehicule(vehicule_avance)
        assert route.get_nombre_vehicules() == 2
    
    def test_get_densite_trafic_route_vide(self, route_simple):
        """Test le calcul de densité sur une route vide."""
        # Arrange
        route = route_simple
        
        # Act
        densite = route.get_densite_trafic()
        
        # Assert
        assert densite == 0
    
    def test_get_densite_trafic_route_avec_vehicules(self, route_simple, vehicule_exemple, vehicule_avance):
        """Test le calcul de densité sur une route avec véhicules."""
        # Arrange
        route = route_simple
        route.ajouter_vehicule(vehicule_exemple)
        route.ajouter_vehicule(vehicule_avance)
        
        # Act
        densite = route.get_densite_trafic()
        
        # Assert - 2 véhicules sur 1km = densité 2
        assert densite == 2.0
    
    def test_get_densite_trafic_route_longue(self, route_longue, vehicule_exemple):
        """Test le calcul de densité sur une route longue."""
        # Arrange
        route = route_longue  # 5km de long
        route.ajouter_vehicule(vehicule_exemple)
        # Act
        densite = route.get_densite_trafic()
        
        # Assert - 1 véhicule sur 5km = densité 0.2
        assert densite == 0.2
    
    def test_representation_textuelle(self, route_simple):
        """Test la représentation textuelle de la route."""
        # Arrange
        route = route_simple
        
        # Act
        representation = str(route)
        
        # Assert
        assert "Route 'A1'" in representation
        assert "1000m" in representation
        assert "limite: 50km/h" in representation
        assert "0 véhicules" in representation
    
    def test_representation_technique(self, route_simple):
        """Test la représentation technique de la route."""
        # Arrange
        route = route_simple
        
        # Act
        representation = repr(route)
        
        # Assert
        assert "Route" in representation
        assert "nom='A1'" in representation
        assert "longueur=1000" in representation
        assert "limite_vitesse=50" in representation