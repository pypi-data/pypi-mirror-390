
import unittest
import numpy as np
import pandas as pd
from pv_diagnostix_su.core.signal_processor import SignalProcessor

class TestSignalProcessor(unittest.TestCase):

    def setUp(self):
        # Create a sample DataFrame for testing
        self.sample_data = pd.DataFrame({
            'value': np.sin(np.linspace(0, 100, 1000)) + np.random.randn(1000) * 0.1
        })
        self.sampling_rate = 60 # Example sampling rate

    def test_fft_analysis(self):
        processor = SignalProcessor(self.sample_data, 'FFT')
        results = processor.process(sampling_rate=self.sampling_rate)
        self.assertIn('frequencies', results)
        self.assertIn('magnitudes', results)
        self.assertIn('dominant_freq', results)
        self.assertIn('harmonic_content', results)
        self.assertIn('spectrum_plot', results)

    def test_wavelet_decomposition(self):
        processor = SignalProcessor(self.sample_data, 'Wavelet')
        results = processor.process()
        self.assertIn('coefficients', results)
        self.assertIn('frequencies', results)
        self.assertIn('power', results)
        self.assertIn('breakpoints', results)
        self.assertIn('degradation_score', results)
        self.assertIn('spectrogram_plot', results)

    def test_kalman_filter(self):
        processor = SignalProcessor(self.sample_data, 'Kalman')
        results = processor.process()
        self.assertIn('filtered_signal', results)
        self.assertIn('residuals', results)
        self.assertIn('noise_level', results)
        self.assertIn('state_estimates', results)
        self.assertIn('filtered_plot', results)

    def test_hilbert_transform(self):
        processor = SignalProcessor(self.sample_data, 'Hilbert')
        results = processor.process()
        self.assertIn('analytic_signal', results)
        self.assertIn('amplitude_envelope', results)
        self.assertIn('instantaneous_phase', results)
        self.assertIn('amplitude_derivative', results)
        self.assertIn('amplitude_anomaly_score', results)

    def test_autocorrelation_analysis(self):
        processor = SignalProcessor(self.sample_data, 'Autocorrelation')
        results = processor.process()
        self.assertIn('autocorr', results)
        self.assertIn('lags', results)
        self.assertIn('significant_lags', results)
        self.assertIn('periodicity', results)
        self.assertIn('periodicity_loss_score', results)

    def test_process_signal_all_techniques(self):
        techniques = ['FFT', 'Wavelet', 'Kalman', 'Hilbert', 'Autocorrelation']
        for tech in techniques:
            processor = SignalProcessor(self.sample_data, tech)
            results = processor.process()
            self.assertIsInstance(results, dict)
            self.assertGreater(len(results), 0)

if __name__ == '__main__':
    unittest.main()
