
import unittest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
from pathlib import Path
import json

# Import core components and equipment classes
from pv_diagnostix_su.core.data_loader import load_csv_data, load_metadata
from pv_diagnostix_su.core.signal_processor import SignalProcessor
from pv_diagnostix_su.core.health_scorer import HealthScorer
from pv_diagnostix_su.core.equipment_config import EquipmentConfig
from pv_diagnostix_su.core.report_generator import ReportGenerator
from pv_diagnostix_su.equipment.inverter import Inverter
from pv_diagnostix_su.equipment.solar_panel import SolarPanel
from pv_diagnostix_su.equipment.battery import Battery

class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.test_data_dir = Path('test_data')
        self.test_data_dir.mkdir(exist_ok=True)

        # Create a dummy CSV file for data loading
        self.csv_path = self.test_data_dir / 'integration_data.csv'
        data = {
            'Time': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100, freq='min')),
            'dcVoltage(V)': np.random.uniform(400, 900, 100),
            'acVoltage(V)': np.random.uniform(200, 240, 100),
            'acCurrent(A)': np.random.uniform(0, 50, 100),
            'acFrequency(Hz)': np.random.uniform(49.5, 50.5, 100),
            'activePower(W)': np.random.uniform(0, 15000, 100)
        }
        pd.DataFrame(data).to_csv(self.csv_path, index=False)

        # Create dummy config files
        self.config_dir = Path('pv_equipment_diagnostics/data/equipment_configs')
        self.config_dir.mkdir(parents=True, exist_ok=True)

        inverter_config_content = {
            'equipment_type': 'inverter',
            'signal_columns': ['dcVoltage(V)', 'acVoltage(V)', 'acCurrent(A)', 'acFrequency(Hz)', 'activePower(W)'],
            'normal_ranges': {
                'dcVoltage': [400, 900],
                'acVoltage': [200, 240],
                'acCurrent': [0, 50],
                'acFrequency': [49.5, 50.5],
                'activePower': [0, 15000]
            },
            'fault_signatures': {},
            'signal_techniques': ['FFT', 'Kalman'],
            'alarm_thresholds': {'green': 85, 'yellow': 60, 'red': 40}
        }
        with open(self.config_dir / 'inverter_config.json', 'w') as f:
            json.dump(inverter_config_content, f)

        solar_panel_config_content = {
            'equipment_type': 'solar_panel',
            'signal_columns': ['irradiance(W/m2)', 'power(W)', 'temperature(C)'],
            'normal_ranges': {},
            'fault_signatures': {},
            'signal_techniques': ['Wavelet'],
            'alarm_thresholds': {'green': 85, 'yellow': 60, 'red': 40}
        }
        with open(self.config_dir / 'solar_panel_config.json', 'w') as f:
            json.dump(solar_panel_config_content, f)

    def tearDown(self):
        for f in self.test_data_dir.glob("*"):
            f.unlink()
        self.test_data_dir.rmdir()
        for f in self.config_dir.glob("*"):
            f.unlink()
        self.config_dir.rmdir()

    def test_end_to_end_inverter_analysis(self):
        # 1. Load data
        df = load_csv_data(str(self.csv_path), required_columns=['Time', 'dcVoltage(V)', 'acVoltage(V)', 'acCurrent(A)', 'acFrequency(Hz)', 'activePower(W)'])
        self.assertFalse(df.empty)

        # 2. Load config
        inverter_config = EquipmentConfig('inverter', str(self.config_dir))
        self.assertEqual(inverter_config.equipment_type, 'inverter')

        # 3. Initialize Inverter equipment
        inverter = Inverter('INV_TEST_001', df, inverter_config)
        self.assertEqual(inverter.equipment_id, 'INV_TEST_001')

        # 4. Perform diagnosis
        diagnosis_results = inverter.diagnose()
        self.assertIn('overall_score', diagnosis_results)
        self.assertIn('severity', diagnosis_results)
        self.assertIn('component_scores', diagnosis_results)

        # 5. Generate report (mocking plotly export for simplicity)
        with patch('pv_diagnostix_su.core.report_generator.ReportGenerator.generate_html_report') as mock_html_report:
            mock_html_report.return_value = "mock_report.html"
            report_path = inverter.export_report(report=diagnosis_results, format='html', plots=[Mock()])
            self.assertEqual(report_path, "mock_report.html")
            mock_html_report.assert_called_once()

    def test_multiple_equipment_comparison(self):
        # Load data for inverter
        inverter_df = load_csv_data(str(self.csv_path), required_columns=['Time', 'dcVoltage(V)', 'acVoltage(V)', 'acCurrent(A)', 'acFrequency(Hz)', 'activePower(W)'])
        inverter_config = EquipmentConfig('inverter', str(self.config_dir))
        inverter = Inverter('INV_TEST_001', inverter_df, inverter_config)
        inverter_analysis = inverter.diagnose()

        # Load data for solar panel (using same dummy data for now, ideally different)
        solar_panel_df = load_csv_data(str(self.csv_path), required_columns=['Time', 'dcVoltage(V)', 'acVoltage(V)', 'acCurrent(A)', 'acFrequency(Hz)', 'activePower(W)'])
        solar_panel_config = EquipmentConfig('solar_panel', str(self.config_dir))
        solar_panel = SolarPanel('SP_TEST_001', solar_panel_df, solar_panel_config)
        solar_panel_analysis = solar_panel.diagnose()

        equipments_list = [
            {'equipment': inverter, 'analysis': inverter_analysis},
            {'equipment': solar_panel, 'analysis': solar_panel_analysis}
        ]

        report_generator = ReportGenerator()
        with patch('pv_diagnostix_su.core.report_generator.ReportGenerator.generate_multiequipment_report') as mock_multi_report:
            mock_multi_report.return_value = {'csv_report': 'multi_report.csv', 'html_report': 'multi_report.html'}
            report_paths = report_generator.generate_multiequipment_report(equipments_list, output_dir=str(self.test_data_dir))
            self.assertIn('csv_report', report_paths)
            self.assertIn('html_report', report_paths)
            mock_multi_report.assert_called_once()

if __name__ == '__main__':
    unittest.main()
