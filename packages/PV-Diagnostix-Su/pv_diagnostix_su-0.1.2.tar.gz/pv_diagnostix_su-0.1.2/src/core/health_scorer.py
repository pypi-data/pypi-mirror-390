
import logging
from typing import Dict, Any, List, Tuple

from pv_diagnostix_su.core.equipment_config import EquipmentConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HealthScorer:
    """
    Calculates a health score for PV equipment based on signal processing results.
    """
    def __init__(self, equipment_type: str, results: Dict[str, Any], config: EquipmentConfig):
        self.equipment_type = equipment_type
        self.results = results
        self.config = config
        self.weights = self._get_weights()

    def _get_weights(self) -> Dict[str, float]:
        """Returns the scoring weights for the given equipment type."""
        if self.equipment_type == 'inverter':
            return {'FFT': 0.30, 'Kalman': 0.25, 'Hilbert': 0.25, 'Autocorrelation': 0.20}
        elif self.equipment_type == 'solar_panel':
            return {'Wavelet': 0.40, 'Autocorrelation': 0.30, 'Hilbert': 0.30}
        elif self.equipment_type == 'battery':
            return {'Kalman': 0.35, 'Autocorrelation': 0.35, 'Hilbert': 0.30}
        else:
            # Default weights
            return {'FFT': 0.25, 'Kalman': 0.25, 'Autocorrelation': 0.25, 'Hilbert': 0.25}

    def _normalize(self, value: float, min_val: float, max_val: float, invert: bool = False) -> float:
        """Normalizes a value to a 0-100 scale."""
        if max_val == min_val:
            return 100.0 if value <= min_val else 0.0
        
        score = 100 * (value - min_val) / (max_val - min_val)
        score = max(0, min(100, score))
        
        return 100 - score if invert else score

    def calculate_score(self) -> Dict[str, Any]:
        """
        Calculates the overall health score and provides recommendations.
        """
        component_scores = {}
        risk_factors = []
        recommendations = []

        # FFT Score (lower is better)
        if 'FFT' in self.results and 'harmonic_content' in self.results['FFT']:
            harmonic_content = self.results['FFT']['harmonic_content']
            component_scores['FFT'] = self._normalize(harmonic_content, 0, 50, invert=True)
            print(f"FFT Score: {component_scores['FFT']}")
            if harmonic_content > 20:
                risk_factors.append("High harmonic distortion detected.")
                recommendations.append("Install harmonic filter.")

        # Wavelet Score (lower is better)
        if 'Wavelet' in self.results and 'breakpoints' in self.results['Wavelet']:
            num_breakpoints = len(self.results['Wavelet']['breakpoints'])
            component_scores['Wavelet'] = self._normalize(num_breakpoints, 0, 10, invert=True)
            if num_breakpoints > 3:
                risk_factors.append("Signal instability detected (multiple breakpoints).")
                recommendations.append("Schedule immediate inspection.")

        # Kalman Score (lower is better)
        if 'Kalman' in self.results and 'noise_level' in self.results['Kalman']:
            noise_level = self.results['Kalman']['noise_level']
            component_scores['Kalman'] = self._normalize(noise_level, 0, 1, invert=True)
            if noise_level > 0.5:
                risk_factors.append(f"Noise level increased {noise_level*100:.0f}%")
                recommendations.append("Check sensor connections.")

        # Hilbert Score (lower is better)
        if 'Hilbert' in self.results and 'amplitude_anomaly_score' in self.results['Hilbert']:
            anomaly_score = self.results['Hilbert']['amplitude_anomaly_score']
            component_scores['Hilbert'] = self._normalize(anomaly_score, 0, 0.1, invert=True)
            if anomaly_score > 0.05:
                risk_factors.append("Amplitude envelope degrading rapidly.")
                recommendations.append("Replace aging component.")

        # Autocorrelation Score (higher is better)
        if 'Autocorrelation' in self.results and 'periodicity_loss_score' in self.results['Autocorrelation']:
            periodicity_loss = self.results['Autocorrelation']['periodicity_loss_score']
            component_scores['Autocorrelation'] = self._normalize(periodicity_loss, 0, 100, invert=True)
            if periodicity_loss > 50:
                risk_factors.append("Signal periodicity lost (potential fault).")

        # Add Algeria-specific risk factors and recommendations
        if self.equipment_type == 'solar_panel':
            if 'Wavelet' in component_scores and component_scores['Wavelet'] < 60: # Assuming low wavelet score implies degradation
                risk_factors.append("Poussière du Sahara détectée, affectant la performance des panneaux.")
                recommendations.append("Nettoyer régulièrement les panneaux solaires pour optimiser la production.")
        
        if self.equipment_type == 'inverter':
            harmonic_threshold = 20 # Default threshold
            # Corrected attribute access for self.config.config (it's a Mock object)
            if hasattr(self.config, 'config') and isinstance(self.config.config, dict) and 'harmonic_tolerance_percent' in self.config.config:
                harmonic_threshold += self.config.config['harmonic_tolerance_percent']
            
            if 'FFT' in self.results and self.results['FFT'].get('harmonic_content', 0) > harmonic_threshold:
                risk_factors.append("Instabilité du réseau Sonelgaz détectée, causant des harmoniques élevées.")
                recommendations.append("Installer un filtre harmonique pour protéger l'onduleur et améliorer la qualité de l'énergie.")

        if self.equipment_type == 'battery':
            if 'Kalman' in component_scores and component_scores['Kalman'] < 60: # Assuming low Kalman score implies thermal issues
                risk_factors.append("Stress thermique détecté, potentiellement dû au climat chaud d'Algérie.")
                recommendations.append("Vérifier le système de refroidissement de la batterie et assurer une ventilation adéquate.")

        # Calculate overall score
        overall_score = 0
        total_weight = 0
        for tech, score in component_scores.items():
            if tech in self.weights:
                overall_score += score * self.weights[tech]
                total_weight += self.weights[tech]
        
        overall_score = overall_score / total_weight if total_weight > 0 else 0

        # Determine severity
        if overall_score >= 80:
            severity = 'HEALTHY'
        elif 50 <= overall_score < 80:
            severity = 'AT_RISK'
        elif overall_score < 50 and overall_score >= 20:
            severity = 'CRITICAL'
        else:
            severity = 'FAILURE' # New severity level for very low scores

        score_dict = {
            'overall_score': round(overall_score, 2),
            'component_scores': component_scores,
            'severity': severity,
            'risk_factors': risk_factors,
            'recommendations': recommendations
        }
        
        logging.info(f"Health score calculated: {score_dict}")
        return score_dict

def explain_score(score_dict: Dict[str, Any]) -> str:
    """
    Generates a human-readable explanation of the health score.
    """
    explanation = f"Score de Santé Global : {score_dict['overall_score']}% ({score_dict['severity']})\n\n"
    explanation += "Ce score est basé sur les facteurs suivants :\n"
    for factor in score_dict['risk_factors']:
        explanation += f"- {factor}\n"
    
    if score_dict['recommendations']:
        explanation += "\nActions Recommandées :\n"
        for rec in score_dict['recommendations']:
            explanation += f"- {rec}\n"
            
    return explanation
