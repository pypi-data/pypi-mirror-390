
import unittest
import pandas as pd
from pathlib import Path
import os
import json

# Assuming the module is in the parent directory, adjust as needed
from pv_diagnostix_su.core.data_loader import load_csv_data, load_metadata, validate_data_quality

class TestDataLoader(unittest.TestCase):

    def setUp(self):
        """Set up test data and files."""
        self.test_data_dir = Path('test_data')
        self.test_data_dir.mkdir(exist_ok=True)

        # Create a sample CSV for testing
        self.csv_path = self.test_data_dir / 'sample_data.csv'
        data = {
            'Time': pd.to_datetime(['2023-01-01 00:00:00', '2023-01-01 00:01:00', '2023-01-01 00:02:00']),            'power': [100, 102, 101],
            'voltage': [230, 231, 229],
            'current': [0.43, 0.44, 0.44],
            'frequency': [50, 50.1, 49.9]
        }
        pd.DataFrame(data).to_csv(self.csv_path, index=False)

        # Create a sample JSON metadata file
        self.json_path = self.test_data_dir / 'metadata.json'
        with open(self.json_path, 'w') as f:
            json.dump({'equipment': 'inverter', 'model': 'TestModel'}, f)

    def tearDown(self):
        """Clean up test files."""
        for item in self.test_data_dir.iterdir():
            item.unlink()
        self.test_data_dir.rmdir()

    def test_load_csv_data_success(self):
        """Test successful loading of a valid CSV file."""
        df = load_csv_data(str(self.csv_path), required_columns=['power', 'voltage'])
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)

    def test_load_csv_data_file_not_found(self):
        """Test FileNotFoundError for a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_csv_data('non_existent_file.csv', required_columns=['power', 'voltage'])

    def test_load_metadata_json_success(self):
        """Test successful loading of a JSON metadata file."""
        metadata = load_metadata(str(self.json_path))
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata['equipment'], 'inverter')

    def test_validate_data_quality(self):
        """Test the data quality validation function."""
        df = pd.DataFrame({'A': [1, 2, 3, 4, 5], 'B': [1, 2, None, 4, 5]})
        quality_metrics = validate_data_quality(df)
        self.assertIn('missing_%', quality_metrics)
        self.assertIn('outliers_%', quality_metrics)
        self.assertIn('valid_rows', quality_metrics)

if __name__ == '__main__':
    unittest.main()
