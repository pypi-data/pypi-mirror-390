# PV-Diagnostix-Su: Plateforme de Diagnostic Avancé pour Systèmes Photovoltaïques

**Une solution de diagnostic de nouvelle génération, issue de la recherche et du développement, qui fusionne l'Intelligence Artificielle (IA) et le traitement avancé du signal pour offrir une précision inégalée dans la maintenance prédictive des équipements photovoltaïques.**

---

## Table des Matières
- [Contexte Technologique](#contexte-technologique)
- [Installation](#installation)
- [Démarrage Rapide](#démarrage-rapide)
- [Capacités de la Plateforme](#capacités-de-la-plateforme)
- [Structure du Projet](#structure-du-projet)
- [Exemples d'Application](#exemples-dapplication)
- [Contribution](#contribution)
- [Licence](#licence)
- [Citation](#citation)

## Contexte Technologique

PV-Diagnostix-Su est une initiative de R&D visant à transformer la maintenance des infrastructures solaires. Notre approche unique combine des algorithmes de traitement du signal de pointe avec des modèles de Machine Learning pour analyser les signaux électriques bruts. Cette synergie permet de déceler des anomalies subtiles, de prédire les dégradations et d'identifier des signatures de défauts invisibles aux méthodes traditionnelles, garantissant ainsi une fiabilité et une performance optimales des actifs.

## Installation

### Via pip (Recommandé)
```bash
pip install pv-diagnostix-su
```

### Installation Locale
1. Clonez le dépôt.
2. Créez et activez un environnement virtuel.
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Démarrage Rapide

Lancez une analyse complète en quelques minutes :
1.  **Préparez les données :** Placez vos fichiers CSV dans `data/sample_data/`.
2.  **Configurez l'équipement :** Assurez-vous qu'un fichier de configuration JSON correspondant existe dans `data/equipment_configs/`.
3.  **Exécutez un scénario :**
    ```bash
    python examples/example_single_inverter_analysis.py
    ```
    Un rapport de diagnostic interactif sera généré dans `examples/results/`.

## Capacités de la Plateforme

*   **Moteur d'Ingestion et de Validation :** Chargement robuste des données CSV avec alignement temporel, interpolation intelligente et validation des plages physiques.
*   **Noyau d'Analyse Hybride (IA & Traitement du Signal) :**
    *   **Filtrage IA (Basé sur Kalman) :** Denoising avancé du signal pour une clarté maximale.
    *   **Analyse Fréquentielle (FFT) :** Détection des harmoniques et des perturbations électriques.
    *   **Analyse Temps-Fréquence (Wavelet) :** Identification précise des dégradations progressives et des événements transitoires.
    *   **Analyse d'Enveloppe (Hilbert) :** Détection des anomalies d'amplitude et des instabilités.
    *   **Analyse de Périodicité (Autocorrélation) :** Identification des schémas récurrents et des défauts cycliques.
*   **Scoring de Santé Prédictif (PHS) :** Un algorithme propriétaire qui convertit les analyses complexes en un score de santé unifié (0-100), permettant une évaluation rapide de l'état des actifs.
*   **Classification de Sévérité par Machine Learning :** Catégorise automatiquement l'état de l'équipement en 'OPTIMAL', 'SOUS SURVEILLANCE', 'CRITIQUE', ou 'DÉFAILLANCE IMMINENTE'.
*   **Générateur de Recommandations :** Fournit des informations exploitables et des recommandations de maintenance basées sur les signatures de défauts détectées.
*   **Configuration Flexible :** Définissez et personnalisez facilement tout type d'équipement (onduleurs, panneaux, batteries) via des fichiers de configuration simples.
*   **Rapports Interactifs :** Génère des rapports HTML dynamiques et autonomes avec des visualisations de données interactives (Plotly).

## Structure du Projet
```
pv_diagnostix_su/
├── pv_diagnostix_su/      # Noyau de la bibliothèque
│   ├── core/              # Algorithmes centraux (IA, traitement signal, scoring)
│   ├── equipment/         # Modèles d'équipement (onduleur, panneau, etc.)
│   └── utils/             # Utilitaires (validation, visualisation)
├── tests/
├── examples/
├── data/
├── docs/
├── setup.py
├── requirements.txt
└── README.md
```

## Exemples d'Application
Le répertoire `examples/` contient des cas d'usage détaillés pour démontrer la puissance de la plateforme.

## Contribution
Les contributions visant à faire avancer la recherche dans ce domaine sont les bienvenues.

## Licence
Ce projet est sous licence MIT.

## Confidentialité des Données
Cette plateforme est conçue pour le diagnostic technique et ne gère aucune Donnée à Caractère Personnel (PII). L'utilisateur est entièrement responsable de l'anonymisation de toutes les données d'entrée.

## Citation
Pour toute utilisation dans un cadre académique ou de recherche, veuillez citer :
```
@misc{pvequipmentdiagnostics,
  author = {PV-Diagnostix Research Group},
  title = {PV-Diagnostix-Su: An AI-Enhanced Diagnostic Platform for Photovoltaic Systems},
  howpublished = {\url{https://github.com/your-username/pv-diagnostix-su}}
}
```
