import unittest
from unittest.mock import Mock
from pv_diagnostix_su.core.health_scorer import HealthScorer
from pv_diagnostix_su.core.equipment_config import EquipmentConfig

class TestHealthScorer(unittest.TestCase):

    def setUp(self):
        self.mock_inverter_results = {
            'FFT': {'harmonic_content': 10.0},
            'Wavelet': {'breakpoints': [], 'degradation_score': 90.0},
            'Kalman': {'noise_level': 0.05},
            'Hilbert': {'amplitude_anomaly_score': 0.01},
            'Autocorrelation': {'periodicity_loss_score': 10}
        }
        self.mock_solar_panel_results = {
            'Wavelet': {'breakpoints': [1, 2], 'degradation_score': 40.0},
            'Autocorrelation': {'periodicity_loss_score': 60},
            'Hilbert': {'amplitude_anomaly_score': 0.06}
        }
        self.mock_battery_results = {
            'Kalman': {'noise_level': 0.2},
            'Autocorrelation': {'periodicity_loss_score': 70},
            'Hilbert': {'amplitude_anomaly_score': 0.07}
        }
        # Mock EquipmentConfig for initialization
        self.mock_config = Mock(spec=EquipmentConfig)
        self.mock_config.alarm_thresholds = {'green': 85, 'yellow': 60, 'red': 40}
        self.mock_config.scoring_weights = {
            'inverter': {'FFT': 0.3, 'Wavelet': 0.2, 'Kalman': 0.2, 'Hilbert': 0.1, 'Autocorrelation': 0.2},
            'solar_panel': {'Wavelet': 0.4, 'Autocorrelation': 0.3, 'Hilbert': 0.3},
            'battery': {'Kalman': 0.35, 'Autocorrelation': 0.35, 'Hilbert': 0.3}
        }
        # Set equipment_type for the mock config when used in HealthScorer
        self.mock_config.equipment_type = 'inverter' # Default for most tests, can be overridden

    def test_scoring_weights(self):
        # Test inverter weights
        scorer = HealthScorer('inverter', self.mock_inverter_results, self.mock_config)
        self.assertAlmostEqual(scorer.weights['FFT'], 0.30)
        # Test solar_panel weights
        self.mock_config.equipment_type = 'solar_panel'
        scorer = HealthScorer('solar_panel', self.mock_solar_panel_results, self.mock_config)
        self.assertAlmostEqual(scorer.weights['Wavelet'], 0.40)
        # Test battery weights
        self.mock_config.equipment_type = 'battery'
        scorer = HealthScorer('battery', self.mock_battery_results, self.mock_config)
        self.assertAlmostEqual(scorer.weights['Kalman'], 0.35)

    def test_severity_classification(self):
        # Test HEALTHY
        healthy_results = self.mock_inverter_results.copy()
        healthy_results['FFT']['harmonic_content'] = 5.0 # Score 90
        healthy_results['Kalman']['noise_level'] = 0.02 # Score 98
        healthy_results['Hilbert']['amplitude_anomaly_score'] = 0.005 # Score 95
        healthy_results['Autocorrelation']['periodicity_loss_score'] = 5 # Score 95
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', healthy_results, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertEqual(score_data['severity'], 'HEALTHY')

        # Test AT_RISK
        at_risk_results = self.mock_inverter_results.copy()
        at_risk_results['FFT']['harmonic_content'] = 15.0 # Score 70
        at_risk_results['Kalman']['noise_level'] = 0.2 # Score 80
        at_risk_results['Hilbert']['amplitude_anomaly_score'] = 0.03 # Score 70
        at_risk_results['Autocorrelation']['periodicity_loss_score'] = 30 # Score 70
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', at_risk_results, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertEqual(score_data['severity'], 'AT_RISK')

        # Test CRITICAL (overall score around 40-50)
        critical_results = self.mock_inverter_results.copy()
        critical_results['FFT']['harmonic_content'] = 30.0 # Score 40
        critical_results['Kalman']['noise_level'] = 0.6 # Score 40
        critical_results['Hilbert']['amplitude_anomaly_score'] = 0.06 # Score 40
        critical_results['Autocorrelation']['periodicity_loss_score'] = 60 # Score 40
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', critical_results, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertEqual(score_data['severity'], 'CRITICAL')

        # Test FAILURE (overall score < 20)
        failure_results = self.mock_inverter_results.copy()
        failure_results['FFT']['harmonic_content'] = 45.0 # Score 10
        failure_results['Kalman']['noise_level'] = 0.9 # Score 10
        failure_results['Hilbert']['amplitude_anomaly_score'] = 0.09 # Score 10
        failure_results['Autocorrelation']['periodicity_loss_score'] = 90 # Score 10
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', failure_results, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertEqual(score_data['severity'], 'FAILURE')

    def test_risk_factors_detection(self):
        # Test FFT risk factor
        inverter_risk_fft = self.mock_inverter_results.copy()
        inverter_risk_fft['FFT']['harmonic_content'] = 25.0 # > 20
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', inverter_risk_fft, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertIn('High harmonic distortion detected.', score_data['risk_factors'])

        # Test Wavelet risk factor
        solar_panel_risk_wavelet = self.mock_solar_panel_results.copy()
        solar_panel_risk_wavelet['Wavelet']['breakpoints'] = [1, 2, 3, 4] # > 3 breakpoints
        self.mock_config.equipment_type = 'solar_panel'
        scorer = HealthScorer('solar_panel', solar_panel_risk_wavelet, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertIn('Signal instability detected (multiple breakpoints).', score_data['risk_factors'])

        # Test Kalman risk factor
        inverter_risk_kalman = self.mock_inverter_results.copy()
        inverter_risk_kalman['Kalman']['noise_level'] = 0.6 # > 0.5
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', inverter_risk_kalman, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertIn('Noise level increased 60%', score_data['risk_factors'])

        # Test Hilbert risk factor
        inverter_risk_hilbert = self.mock_inverter_results.copy()
        inverter_risk_hilbert['Hilbert']['amplitude_anomaly_score'] = 0.08 # > 0.05
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', inverter_risk_hilbert, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertIn('Amplitude envelope degrading rapidly.', score_data['risk_factors'])

        # Test Autocorrelation risk factor
        inverter_risk_autocorr = self.mock_inverter_results.copy()
        inverter_risk_autocorr['Autocorrelation']['periodicity_loss_score'] = 60 # > 50
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', inverter_risk_autocorr, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertIn('Signal periodicity lost (potential fault).', score_data['risk_factors'])

    def test_recommendations_generation(self):
        # Test FFT recommendation
        inverter_rec_fft = self.mock_inverter_results.copy()
        inverter_rec_fft['FFT']['harmonic_content'] = 25.0 # > 20
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', inverter_rec_fft, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertIn('Install harmonic filter.', score_data['recommendations'])

        # Test Wavelet recommendation
        solar_panel_rec_wavelet = self.mock_solar_panel_results.copy()
        solar_panel_rec_wavelet['Wavelet']['breakpoints'] = [1, 2, 3, 4] # > 3 breakpoints
        self.mock_config.equipment_type = 'solar_panel'
        scorer = HealthScorer('solar_panel', solar_panel_rec_wavelet, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertIn('Schedule immediate inspection.', score_data['recommendations'])

        # Test Kalman recommendation
        inverter_rec_kalman = self.mock_inverter_results.copy()
        inverter_rec_kalman['Kalman']['noise_level'] = 0.6 # > 0.5
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', inverter_rec_kalman, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertIn('Check sensor connections.', score_data['recommendations'])

        # Test Hilbert recommendation
        inverter_rec_hilbert = self.mock_inverter_results.copy()
        inverter_rec_hilbert['Hilbert']['amplitude_anomaly_score'] = 0.08 # > 0.05
        self.mock_config.equipment_type = 'inverter'
        scorer = HealthScorer('inverter', inverter_rec_hilbert, self.mock_config)
        score_data = scorer.calculate_score()
        self.assertIn('Replace aging component.', score_data['recommendations'])

if __name__ == '__main__':
    unittest.main()