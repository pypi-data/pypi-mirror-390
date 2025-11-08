
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

# Adjust the import path as necessary for your project structure
from pv_diagnostix_su.core.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):

    def setUp(self):
        self.report_generator = ReportGenerator()
        self.mock_equipment = Mock()
        self.mock_equipment.equipment_id = "INV001"
        self.mock_equipment.equipment_type = "inverter"
        self.mock_analysis = {
            "overall_score": 75.5,
            "component_scores": {"FFT": 80, "Kalman": 70},
            "severity": "AT_RISK",
            "risk_factors": ["High harmonic distortion"],
            "recommendations": ["Check input voltage"],
            "analysis_details": {"raw_data": "..."}
        }
        self.output_dir = Path("./test_reports")
        self.output_dir.mkdir(exist_ok=True)

    def tearDown(self):
        for f in self.output_dir.glob("*"):
            f.unlink()
        self.output_dir.rmdir()

    def test_generate_summary_dict(self):
        summary = self.report_generator.generate_summary_dict(self.mock_equipment, self.mock_analysis)
        self.assertIsInstance(summary, dict)
        self.assertIn('timestamp', summary)
        self.assertEqual(summary['equipment_id'], "INV001")
        self.assertEqual(summary['overall_score'], 75.5)

    def test_generate_json_report(self):
        report_path = self.report_generator.generate_json_report(self.mock_equipment, self.mock_analysis, str(self.output_dir))
        self.assertTrue(Path(report_path).exists())
        with open(report_path, 'r') as f:
            report_content = json.load(f)
        self.assertEqual(report_content['equipment_id'], "INV001")

    def test_generate_html_report(self):
        mock_plot = Mock()
        mock_plot.to_html.return_value = "<div>Mock Plot</div>"
        report_path = self.report_generator.generate_html_report(self.mock_equipment, self.mock_analysis, [mock_plot], str(self.output_dir))
        self.assertTrue(Path(report_path).exists())
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        self.assertIn("Equipment Diagnostic Report", html_content)
        self.assertIn("INV001", html_content)
        self.assertIn("<div>Mock Plot</div>", html_content)

    def test_generate_multiequipment_report(self):
        mock_equipment_2 = Mock()
        mock_equipment_2.equipment_id = "SP001"
        mock_equipment_2.equipment_type = "solar_panel"
        mock_analysis_2 = {
            "overall_score": 40.0,
            "component_scores": {"Wavelet": 35, "Autocorrelation": 45},
            "severity": "CRITICAL",
            "risk_factors": ["Panel degradation"],
            "recommendations": ["Replace panel"],
            "analysis_details": {"raw_data": "..."}
        }
        equipments_list = [
            {'equipment': self.mock_equipment, 'analysis': self.mock_analysis},
            {'equipment': mock_equipment_2, 'analysis': mock_analysis_2}
        ]
        report_paths = self.report_generator.generate_multiequipment_report(equipments_list, str(self.output_dir))
        self.assertIn('csv_report', report_paths)
        self.assertIn('html_report', report_paths)
        self.assertTrue(Path(report_paths['csv_report']).exists())
        self.assertTrue(Path(report_paths['html_report']).exists())

        # Verify CSV content
        df = pd.read_csv(report_paths['csv_report'])
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['equipment_id'], "SP001") # CRITICAL should be first

if __name__ == '__main__':
    unittest.main()
