# PV-Diagnostix-Su: Plateforme de Diagnostic Avance pour Systemes Photovoltaiques

**Une solution de diagnostic de nouvelle generation, issue de la recherche et du developpement, qui fusionne l'Intelligence Artificielle (IA) et le traitement avance du signal pour offrir une precision inegalee dans la maintenance predictive des equipements photovoltaiques.**

---

## Table des Matieres
- [Contexte Technologique](#contexte-technologique)
- [Installation](#installation)
- [Demarrage Rapide](#demarrage-rapide)
- [Capacites de la Plateforme](#capacites-de-la-plateforme)
- [Structure du Projet](#structure-du-projet)
- [Exemples d'Application](#exemples-dapplication)
- [Contribution](#contribution)
- [Licence](#licence)
- [Citation](#citation)

## Contexte Technologique

PV-Diagnostix-Su est une initiative de R&D visant a transformer la maintenance des infrastructures solaires. Notre approche unique combine des algorithmes de traitement du signal de pointe avec des modeles de Machine Learning pour analyser les signaux electriques bruts. Cette synergie permet de deceler des anomalies subtiles, de predire les degradations et d'identifier des signatures de defauts invisibles aux methodes traditionnelles, garantissant ainsi une fiabilite et une performance optimales des actifs.

## Installation

### Via pip (Recommande)
```bash
pip install pv-diagnostix-su
```

### Installation Locale
1. Clonez le depot.
2. Creez et activez un environnement virtuel.
3. Installez les dependances :
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Demarrage Rapide

Lancez une analyse complete en quelques minutes :
1.  **Preparez les donnees :** Placez vos fichiers CSV dans `data/sample_data/`.
2.  **Configurez l'equipement :** Assurez-vous qu'un fichier de configuration JSON correspondant existe dans `data/equipment_configs/`.
3.  **Executez un scenario :**
    ```bash
    python examples/example_single_inverter_analysis.py
    ```
    Un rapport de diagnostic interactif sera genere dans `examples/results/`.

## Capacites de la Plateforme

*   **Moteur d'Ingestion et de Validation :** Chargement robuste des donnees CSV avec alignement temporel, interpolation intelligente et validation des plages physiques.
*   **Noyau d'Analyse Hybride (IA & Traitement du Signal) :**
    *   **Filtrage IA (Base sur Kalman) :** Denoising avance du signal pour une clarte maximale.
    *   **Analyse Frequentielle (FFT) :** Detection des harmoniques et des perturbations electriques.
    *   **Analyse Temps-Frequence (Wavelet) :** Identification precise des degradations progressives et des evenements transitoires.
    *   **Analyse d'Enveloppe (Hilbert) :** Detection des anomalies d'amplitude et des instabilites.
    *   **Analyse de Periodicite (Autocorrelation) :** Identification des schemas recurrents et des defauts cycliques.
*   **Scoring de Sante Predictif (PHS) :** Un algorithme proprietaire qui convertit les analyses complexes en un score de sante unifie (0-100), permettant une evaluation rapide de l'etat des actifs.
*   **Classification de Severite par Machine Learning :** Categorise automatiquement l'etat de l'equipement en 'OPTIMAL', 'SOUS SURVEILLANCE', 'CRITIQUE', ou 'DEFAILLANCE IMMINENTE'.
*   **Generateur de Recommandations :** Fournit des informations exploitables et des recommandations de maintenance basees sur les signatures de defauts detectees.
*   **Configuration Flexible :** Definissez et personnalisez facilement tout type d'equipement (onduleurs, panneaux, batteries) via des fichiers de configuration simples.
*   **Rapports Interactifs :** Genere des rapports HTML dynamiques et autonomes avec des visualisations de donnees interactives (Plotly).

## Structure du Projet
```
pv_diagnostix_su/
+-- pv_diagnostix_su/      # Noyau de la bibliotheque
|   +-- core/              # Algorithmes centraux (IA, traitement signal, scoring)
|   +-- equipment/         # Modeles d'equipement (onduleur, panneau, etc.)
|   \-- utils/             # Utilitaires (validation, visualisation)
+-- tests/
+-- examples/
+-- data/
+-- docs/
+-- setup.py
+-- requirements.txt
\-- README.md
```

## Exemples d'Application
Le repertoire `examples/` contient des cas d'usage detailles pour demontrer la puissance de la plateforme.

## Contribution
Les contributions visant a faire avancer la recherche dans ce domaine sont les bienvenues.

## Licence
Ce projet est sous licence MIT.

## Confidentialite des Donnees
Cette plateforme est concue pour le diagnostic technique et ne gere aucune Donnee a Caractere Personnel (PII). L'utilisateur est entierement responsable de l'anonymisation de toutes les donnees d'entree.

## Citation
Pour toute utilisation dans un cadre academique ou de recherche, veuillez citer :
```
@misc{pvequipmentdiagnostics,
  author = {PV-Diagnostix Research Group},
  title = {PV-Diagnostix-Su: An AI-Enhanced Diagnostic Platform for Photovoltaic Systems},
  howpublished = {\url{https://github.com/your-username/pv-diagnostix-su}}
}
```
