"""
Tests unitaires pour la classe ReseauRoutier

Objectif : vérifier la cohérence globale du réseau routier.
Tests à réaliser :
• Ajout de routes au réseau.
• Mise à jour de l'ensemble des routes.
"""

import pytest
from models.reseau import ReseauRoutier
from models.route import Route
from models.vehicule import Vehicule


class TestReseauRoutier:
    """Tests pour la classe ReseauRoutier."""
    
    def test_creation_reseau_vide(self):
        """Test la création d'un réseau routier vide."""
        # Arrange & Act
        reseau = ReseauRoutier()
        
        # Assert
        assert reseau.routes == {}
        assert reseau.intersections == {}
        assert reseau.historique_trafic == []
        assert len(reseau.routes) == 0
        assert len(reseau.intersections) == 0
        assert len(reseau.historique_trafic) == 0
    
    def test_ajouter_route_valide(self, route_simple):
        """Test l'ajout d'une route valide au réseau."""
        # Arrange
        reseau = ReseauRoutier()
        
        # Act
        reseau.ajouter_route(route_simple)
        # Assert
        assert len(reseau.routes) == 1
        assert route_simple.nom in reseau.routes
        assert reseau.routes[route_simple.nom] == route_simple
        assert route_simple.nom in reseau.intersections
        assert reseau.intersections[route_simple.nom] == []
    
    
    def test_ajouter_intersection_valide(self, reseau_simple, route_longue):
        """Test l'ajout d'une intersection valide entre deux routes."""
        # Arrange
        reseau = reseau_simple
        reseau.ajouter_route(route_longue)
        # Act
        reseau.ajouter_intersection("A1", "Autoroute_A2") 
        # Assert
        assert "Autoroute_A2" in reseau.intersections["A1"]
        assert len(reseau.intersections["A1"]) == 1
    
    def test_ajouter_intersection_dupliquee(self, reseau_simple, route_longue):
        """Test que l'ajout de la même intersection plusieurs fois ne crée pas de doublons."""
        # Arrange
        reseau = reseau_simple
        reseau.ajouter_route(route_longue)
        
        # Act
        reseau.ajouter_intersection("A1", "Autoroute_A2")
        reseau.ajouter_intersection("A1", "Autoroute_A2")  # Dupliqué
        
        # Assert
        assert "Autoroute_A2" in reseau.intersections["A1"]
        assert len(reseau.intersections["A1"]) == 1  # Pas de doublon
    
    def test_get_route_existante(self, reseau_simple):
        """Test la récupération d'une route existante."""
        # Arrange
        reseau = reseau_simple
        
        # Act
        route = reseau.get_route("A1")
        
        # Assert
        assert route is not None
        assert route.nom == "A1"
    
    def test_get_route_inexistante(self, reseau_simple):
        """Test la récupération d'une route inexistante."""
        # Arrange
        reseau = reseau_simple
        
        # Act
        route = reseau.get_route("Route_Inexistante")
        
        # Assert
        assert route is None
    
    def test_get_routes_destination_existantes(self, reseau_complexe):
        """Test la récupération des routes destination pour une route source existante."""
        # Arrange
        reseau = reseau_complexe
        
        # Act
        destinations = reseau.get_routes_destination("A1")
        
        # Assert
        assert destinations == ["Autoroute_A2"]
        assert len(destinations) == 1
    
    def test_get_routes_destination_inexistante(self, reseau_simple):
        """Test la récupération des routes destination pour une route source inexistante."""
        # Arrange
        reseau = reseau_simple
        
        # Act
        destinations = reseau.get_routes_destination("Route_Inexistante")
        
        # Assert
        assert destinations == []
    
    def test_get_nombre_total_vehicules_reseau_vide(self):
        """Test le comptage des véhicules dans un réseau vide."""
        # Arrange
        reseau = ReseauRoutier()
        
        # Act
        total = reseau.get_nombre_total_vehicules()
        
        # Assert
        assert total == 0
    
    def test_get_nombre_total_vehicules_reseau_avec_vehicules(self, reseau_complexe):
        """Test le comptage des véhicules dans un réseau avec véhicules."""
        # Arrange
        reseau = reseau_complexe
        
        # Act
        total = reseau.get_nombre_total_vehicules()
        
        # Assert
        assert total == 2  # 1 véhicule sur A1 + 1 véhicule sur Autoroute_A2
    
    def test_get_densite_trafic_moyenne_reseau_vide(self):
        """Test le calcul de densité moyenne dans un réseau vide."""
        # Arrange
        reseau = ReseauRoutier()
        
        # Act
        densite_moyenne = reseau.get_densite_trafic_moyenne()
        
        # Assert
        assert densite_moyenne == 0
    
    def test_get_densite_trafic_moyenne_reseau_avec_routes(self, reseau_complexe):
        """Test le calcul de densité moyenne dans un réseau avec routes."""
        # Arrange
        reseau = reseau_complexe
        
        # Act
        densite_moyenne = reseau.get_densite_trafic_moyenne()
        
        # Assert
        # A1: 1 véhicule sur 1km = densité 1
        # Autoroute_A2: 1 véhicule sur 5km = densité 0.2
        # Moyenne = (1 + 0.2) / 2 = 0.6
        assert densite_moyenne == 0.6
    
    def test_mettre_a_jour_reseau_sans_changements(self, reseau_simple):
        """Test la mise à jour du réseau sans véhicules sortants."""
        # Arrange
        reseau = reseau_simple
        historique_initial = len(reseau.historique_trafic)
        
        # Act
        stats = reseau.mettre_a_jour_reseau()
        
        # Assert
        assert stats['changements_route'] == 0
        assert stats['vehicules_sortis'] == 0
        assert len(reseau.historique_trafic) == historique_initial + 1
        assert reseau.get_nombre_total_vehicules() == 1  # Le véhicule est toujours là
    
    def test_mettre_a_jour_reseau_avec_changement_route(self, reseau_complexe, vehicule_pres_fin_route):
        """Test la mise à jour du réseau avec changement de route."""
        # Arrange
        reseau = reseau_complexe
        route_a1 = reseau.get_route("A1")
        route_a1.ajouter_vehicule(vehicule_pres_fin_route)
        
        # Faire avancer le véhicule pour qu'il dépasse la fin de A1
        vehicule_pres_fin_route.avancer(100)  # Position = 1050 > 1000
        
        # Act
        stats = reseau.mettre_a_jour_reseau()
        
        # Assert
        assert stats['vehicules_sortis'] == 1  # Un véhicule a quitté A1
        assert stats['changements_route'] == 1  # Un véhicule a changé de route
        assert route_a1.get_nombre_vehicules() == 1  # Le véhicule original est toujours là
        # Le véhicule qui a changé de route devrait être sur Autoroute_A2 maintenant
    
    def test_representation_textuelle(self, reseau_simple):
        """Test la représentation textuelle du réseau."""
        # Arrange
        reseau = reseau_simple
        
        # Act
        representation = str(reseau)
        
        # Assert
        assert "Réseau routier" in representation
        assert "1 routes" in representation
        assert "1 véhicules" in representation
    
    def test_representation_technique(self, reseau_simple):
        """Test la représentation technique du réseau."""
        # Arrange
        reseau = reseau_simple
        
        # Act
        representation = repr(reseau)
        
        # Assert
        assert "ReseauRoutier" in representation
        assert "nb_routes=1" in representation
        assert "nb_vehicules=1" in representation
    
    def test_historique_trafic_apres_mise_a_jour(self, reseau_simple):
        """Test que l'historique du trafic est mis à jour correctement."""
        # Arrange
        reseau = reseau_simple
        historique_initial = len(reseau.historique_trafic)
        
        # Act
        reseau.mettre_a_jour_reseau()
        reseau.mettre_a_jour_reseau()
        
        # Assert
        assert len(reseau.historique_trafic) == historique_initial + 2
        
        # Vérifier la structure des données historiques
        dernier_etat = reseau.historique_trafic[-1]
        assert 'timestamp' in dernier_etat
        assert 'total_vehicules' in dernier_etat
        assert 'densite_moyenne' in dernier_etat
        assert dernier_etat['timestamp'] == len(reseau.historique_trafic) - 1