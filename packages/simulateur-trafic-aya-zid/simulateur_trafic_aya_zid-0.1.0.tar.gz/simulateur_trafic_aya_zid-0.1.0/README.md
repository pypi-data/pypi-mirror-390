# 🚦 Simulateur de Trafic Routier Intelligent

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Un simulateur de trafic routier complet écrit en **Python**, permettant de **modéliser, simuler et analyser** un réseau routier intelligent composé de routes, intersections et véhicules.

---

## 🧠 Objectifs du projet
- Concevoir une **application orientée objet complète**.  
- Simuler la **circulation de véhicules** dans un réseau défini.  
- Fournir des **statistiques dynamiques** (vitesses, congestions, temps de parcours).  
- Produire des **visualisations graphiques** et **exports de données**.  
- Démontrer une **architecture modulaire, testable et extensible**.

---

## 🚀 Exécution

### 1️⃣ Simulation complète :
```bash
python main.py -t 60 -d 60 -c data/config_reseau.json --graphique --export --affichage
```
- `-t` : nombre de tours (par ex. 60 minutes)  
- `-d` : durée d’un pas de simulation (en secondes)  
- `-c` : fichier de configuration du réseau  
- `--graphique` : active les visualisations  
- `--export` : exporte les résultats  
- `--affichage` : affiche la progression en temps réel  

### 2️⃣ Démonstration rapide :
```bash
python main.py
```
(exécute la simulation par défaut sans arguments)

---

## 🧮 Exemple de configuration (`data/config_reseau.json`)
Ce fichier définit le **réseau routier initial** :
- les **routes** et leurs caractéristiques (longueur, vitesse limite),  
- les **intersections** et connexions entre routes,  
- la **liste des véhicules** avec leur position et vitesse initiale.  

---

## 📊 Fonctionnalités principales

| Module | Rôle |
|--------|------|
| `Vehicule` | Modélise un véhicule (position, vitesse, route actuelle). |
| `Route` | Gère les véhicules circulant sur une route et leurs mises à jour. |
| `ReseauRoutier` | Coordonne l’ensemble des routes et intersections. |
| `Simulateur` | Lance la simulation, fait évoluer les états et collecte les données. |
| `Analyseur` | Calcule vitesses moyennes, congestions, et temps de parcours. |
| `Affichage` | Affiche la simulation et les statistiques sous forme graphique. |
| `Export` | Enregistre les résultats dans différents formats. |

---

## 📈 Résultats attendus
- Évolution des vitesses et densités au cours du temps.  
- Détection automatique des zones de congestion.  
- Statistiques globales sur la performance du réseau.  
- Visualisation du trafic sous forme de graphiques et tableaux.

---

## 📜 Licence
Projet distribué sous licence **MIT**.  
© 2025 Aya Zid — Simulateur de Trafic Routier Intelligent.
