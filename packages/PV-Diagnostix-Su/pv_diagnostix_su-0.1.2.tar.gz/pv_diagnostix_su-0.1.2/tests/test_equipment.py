
import unittest
from unittest.mock import Mock, patch
from pv_diagnostix_su.equipment.base_equipment import BaseEquipment
from pv_diagnostix_su.equipment.inverter import Inverter
from pv_diagnostix_su.equipment.solar_panel import SolarPanel
from pv_diagnostix_su.equipment.battery import Battery
import pandas as pd

class TestEquipment(unittest.TestCase):

    def setUp(self):
        self.mock_df = pd.DataFrame({
            'Time': pd.to_datetime(pd.date_range(start='2023-01-01', periods=10, freq='min')),
            'value': [i for i in range(10)]
        }).set_index('Time')

        # Mock EquipmentConfig for initialization
        self.mock_config = Mock()
        self.mock_config.signal_columns = ['value']
        self.mock_config.get_techniques.return_value = ['FFT'] # Mock get_techniques to return an iterable

    def test_base_equipment_initialization(self):
        with self.assertRaises(TypeError): # BaseEquipment is abstract
            BaseEquipment("EQ001", "base", self.mock_df, self.mock_config)

    def test_inverter_initialization(self):
        inverter = Inverter("INV001", self.mock_df, self.mock_config)
        self.assertEqual(inverter.equipment_id, "INV001")
        self.assertEqual(inverter.equipment_type, "inverter")
        self.assertTrue(inverter.data.equals(self.mock_df))

    def test_solar_panel_initialization(self):
        solar_panel = SolarPanel("SP001", self.mock_df, self.mock_config)
        self.assertEqual(solar_panel.equipment_id, "SP001")
        self.assertEqual(solar_panel.equipment_type, "solar_panel")

    def test_battery_initialization(self):
        battery = Battery("BAT001", self.mock_df, self.mock_config)
        self.assertEqual(battery.equipment_id, "BAT001")
        self.assertEqual(battery.equipment_type, "battery")

    @patch('pv_diagnostix_su.equipment.base_equipment.process_signal')
    def test_full_diagnosis_workflow(self, mock_process_signal):
        # Mock the process_signal function to return a dictionary that HealthScorer can process
        mock_process_signal.return_value = {
            'FFT': {'harmonic_content': 10.0},
            'Kalman': {'noise_level': 0.05}
        }

        inverter = Inverter("INV001", self.mock_df, self.mock_config)
        diagnosis_results = inverter.diagnose()

        self.assertIn('overall_score', diagnosis_results)
        self.assertGreater(diagnosis_results['overall_score'], 0) # Check for a non-zero score

    @patch('pv_diagnostix_su.equipment.base_equipment.ReportGenerator')
    def test_export_report(self, MockReportGenerator):
        mock_report_generator_instance = Mock()
        mock_report_generator_instance.generate_json_report.return_value = "path/to/report.json"
        mock_report_generator_instance.generate_html_report.return_value = "path/to/report.html"
        MockReportGenerator.return_value = mock_report_generator_instance

        inverter = Inverter("INV001", self.mock_df, self.mock_config)
        inverter.diagnosis_results = {'overall_score': 90}

        mock_plot_obj = Mock()

        json_path = inverter.export_report(report=inverter.diagnosis_results, format='json', output_dir='.')
        self.assertEqual(json_path, "path/to/report.json")
        mock_report_generator_instance.generate_json_report.assert_called_once_with(inverter, inverter.diagnosis_results, '.')

        html_path = inverter.export_report(report=inverter.diagnosis_results, format='html', output_dir='.', plots=[mock_plot_obj])
        self.assertEqual(html_path, "path/to/report.html")
        mock_report_generator_instance.generate_html_report.assert_called_once_with(inverter, inverter.diagnosis_results, [mock_plot_obj], '.')

if __name__ == '__main__':
    unittest.main()
