
import logging
import numpy as np
import pandas as pd
import pywt
from scipy import fft
import scipy.signal as signal
from scipy.signal import hilbert

from scipy.linalg import inv
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SignalProcessor:
    """
    A class to process signals using various techniques.
    """
    def __init__(self, signal_df: pd.DataFrame, technique: str):
        self.signal_df = signal_df
        self.technique = technique

    def process(self, **kwargs):
        """
        Process the signal using the specified technique.
        """
        # Normalize the signal
        scaler = MinMaxScaler()
        normalized_signal = scaler.fit_transform(self.signal_df.values.reshape(-1, 1)).flatten()

        if self.technique == 'FFT':
            return self.fft_analysis(normalized_signal, **kwargs)
        elif self.technique == 'Wavelet':
            return self.wavelet_decomposition(normalized_signal, **kwargs)
        elif self.technique == 'Kalman':
            return self.kalman_filter(normalized_signal, **kwargs)
        elif self.technique == 'Hilbert':
            return self.hilbert_transform(normalized_signal, **kwargs)
        elif self.technique == 'Autocorrelation':
            return self.autocorrelation_analysis(normalized_signal, **kwargs)
        else:
            raise ValueError(f"Unknown technique: {self.technique}")

    def fft_analysis(self, input_signal: np.ndarray, sampling_rate: int = 60) -> dict:
        """FFT analysis of the signal."""
        N = len(input_signal)
        if N < 2:
            return {}
        yf = fft.fft(input_signal)
        xf = fft.fftfreq(N, 1 / sampling_rate)
        magnitudes = 2.0/N * np.abs(yf[0:N//2])
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(magnitudes)
        dominant_freq = xf[dominant_freq_idx]

        # Harmonic content
        peaks, _ = signal.find_peaks(magnitudes, height=0.1 * np.max(magnitudes))
        harmonic_content = (np.sum(magnitudes[peaks]) / np.sum(magnitudes)) * 100 if np.sum(magnitudes) > 0 else 0

        # Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xf, y=magnitudes, mode='lines', name='FFT Spectrum'))
        fig.update_layout(title='FFT Analysis', xaxis_title='Frequency (Hz)', yaxis_title='Magnitude')

        return {
            'frequencies': xf,
            'magnitudes': magnitudes,
            'dominant_freq': dominant_freq,
            'harmonic_content': harmonic_content,
            'spectrum_plot': fig
        }

    def wavelet_decomposition(self, input_signal: np.ndarray, wavelet='morl') -> dict:
        """Continuous Wavelet Transform."""
        widths = np.arange(1, 31)
        
        # Use the specified wavelet function from pywt
        try:
            cwtmatr, freqs = pywt.cwt(input_signal, widths, wavelet)
        except ValueError as e:
            raise ValueError(f"Unsupported wavelet: {wavelet}. Supported wavelets from pywt must be used.") from e

        # Simplified breakpoint detection
        power = np.sum(np.abs(cwtmatr)**2, axis=1)
        breakpoints = np.where(power > 2 * np.mean(power))[0].tolist()

        # Degradation score (example)
        degradation_score = np.mean(power)

        # Plotly figure
        fig = go.Figure(data=go.Heatmap(z=cwtmatr, x=np.arange(len(input_signal)), y=freqs, colorscale='Viridis'))
        fig.update_layout(title='Wavelet Spectrogram', xaxis_title='Time', yaxis_title='Frequency')

        return {
            'coefficients': cwtmatr,
            'frequencies': freqs,
            'power': power,
            'breakpoints': breakpoints,
            'degradation_score': degradation_score,
            'spectrogram_plot': fig
        }

    def kalman_filter(self, input_signal: np.ndarray, noise_estimate: float = 0.1) -> dict:
        """Kalman filter for signal smoothing."""
        n_iter = len(input_signal)
        sz = (n_iter,)
        x = input_signal # truth value
        z = input_signal + np.random.normal(0, noise_estimate, size=sz) # observations

        Q = 1e-5 # process variance

        # allocate space for arrays
        xhat=np.zeros(sz)      # a posteri estimate of x
        P=np.zeros(sz)         # a posteri error estimate
        xhatminus=np.zeros(sz) # a priori estimate of x
        Pminus=np.zeros(sz)    # a priori error estimate
        K=np.zeros(sz)         # gain or blending factor

        R = 0.1**2 # estimate of measurement variance, change to see effect

        # intial guesses
        xhat[0] = 0.0
        P[0] = 1.0

        for k in range(1,n_iter):
            # time update
            xhatminus[k] = xhat[k-1] #X(k|k-1) = AX(k-1|k-1) + BU(k) + W(k), A=1,BU=0
            Pminus[k] = P[k-1]+Q      #P(k|k-1) = AP(k-1|k-1)A' + Q, A=1

            # measurement update
            K[k] = Pminus[k]/( Pminus[k]+R ) #Kg(k)=P(k|k-1)H'/(HP(k|k-1)H'+R), H=1
            xhat[k] = xhatminus[k]+K[k]*(z[k]-xhatminus[k]) #X(k|k) = X(k|k-1)+Kg(k)(Z(k)-HX(k|k-1)), H=1
            P[k] = (1-K[k])*Pminus[k] #P(k|k) = (1-Kg(k)H)P(k|k-1), H=1

        # Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=input_signal, mode='lines', name='Original Signal'))
        fig.add_trace(go.Scatter(y=xhat, mode='lines', name='Filtered Signal'))
        fig.update_layout(title='Kalman Filter', xaxis_title='Time', yaxis_title='Value')

        return {
            'filtered_signal': xhat,
            'residuals': input_signal - xhat,
            'noise_level': np.std(input_signal - xhat),
            'state_estimates': xhat,
            'filtered_plot': fig
        }

    def hilbert_transform(self, input_signal: np.ndarray) -> dict:
        """Hilbert transform for envelope detection."""
        analytic_signal = signal.hilbert(input_signal)
        amplitude_envelope = np.abs(analytic_signal)
        instantaneous_phase = np.unwrap(np.angle(analytic_signal))
        amplitude_derivative = np.diff(amplitude_envelope)

        # Anomaly score (example)
        amplitude_anomaly_score = np.mean(np.abs(amplitude_derivative))

        return {
            'analytic_signal': analytic_signal,
            'amplitude_envelope': amplitude_envelope,
            'instantaneous_phase': instantaneous_phase,
            'amplitude_derivative': amplitude_derivative,
            'amplitude_anomaly_score': amplitude_anomaly_score
        }

    def autocorrelation_analysis(self, input_signal: np.ndarray, max_lag: int = 100) -> dict:
        """Autocorrelation analysis for periodicity detection."""
        autocorr = signal.correlate(input_signal, input_signal, mode='full')[len(input_signal)-1:]
        lags = np.arange(len(autocorr))
        
        # Find significant lags
        significant_lags = np.where(autocorr > 0.2)[0].tolist()
        
        # Find periodicity
        peaks, _ = signal.find_peaks(autocorr, height=0.2)
        periodicity = np.mean(np.diff(peaks)) if len(peaks) > 1 else None

        # Periodicity loss score (example)
        periodicity_loss_score = 100 * (1 - (len(significant_lags) / len(autocorr))) if len(autocorr) > 0 else 0

        return {
            'autocorr': autocorr,
            'lags': lags,
            'significant_lags': significant_lags,
            'periodicity': periodicity,
            'periodicity_loss_score': periodicity_loss_score
        }

def process_signal(signal_df: pd.DataFrame, techniques: list, **kwargs):
    """
    Process a signal with a list of techniques.
    """
    results = {}
    for tech in techniques:
        try:
            processor = SignalProcessor(signal_df, tech)
            results[tech] = processor.process(**kwargs.get(tech, {}))
            logging.info(f"Successfully processed signal with {tech}.")
        except Exception as e:
            logging.error(f"Failed to process signal with {tech}: {e}")
            results[tech] = {'error': str(e)}
    return results

# Example Usage
if __name__ == '__main__':
    # Create a sample signal
    np.random.seed(42)
    time = np.linspace(0, 10, 500)
    signal_data = pd.DataFrame({
        'value': 2 * np.sin(2 * np.pi * 1.5 * time) + np.random.normal(0, 0.5, 500)
    })

    # Process with all techniques
    all_results = process_signal(signal_data, ['FFT', 'Wavelet', 'Kalman', 'Hilbert', 'Autocorrelation'])

    # Print results
    for tech, result in all_results.items():
        print(f"--- {tech} Results ---")
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            for key, value in result.items():
                if isinstance(value, go.Figure):
                    # In a real application, you would show the figure
                    print(f"{key}: Plotly figure object")
                elif isinstance(value, np.ndarray):
                    print(f"{key}: numpy array of shape {value.shape}")
                else:
                    print(f"{key}: {value}")
        print("\n")
