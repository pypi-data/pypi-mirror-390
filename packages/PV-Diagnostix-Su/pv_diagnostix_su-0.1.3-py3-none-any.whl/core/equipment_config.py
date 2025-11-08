
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EquipmentConfig:
    """
    Manages equipment configuration loaded from JSON/YAML files.
    """
    def __init__(self, equipment_type: str, config_dir: str = './data/equipment_configs'):
        self.equipment_type = equipment_type
        self.config_dir = Path(config_dir)
        self.config = self.load_config()
        self.validate_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Loads the configuration file for the specified equipment type.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the equipment configuration.
        """
        config_path = self.config_dir / f"{self.equipment_type}_config.json"
        if not config_path.exists():
            logging.error(f"Configuration file not found: {config_path}")
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logging.info(f"Successfully loaded configuration for {self.equipment_type}.")
                return config
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {config_path}: {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to load configuration from {config_path}: {e}")
            raise

    def validate_config(self) -> bool:
        """
        Validates the loaded configuration against required keys.

        Returns
        -------
        bool
            True if the configuration is valid, otherwise raises a ValueError.
        """
        required_keys = [
            'equipment_type', 'signal_columns', 'normal_ranges', 
            'fault_signatures', 'signal_techniques', 'alarm_thresholds'
        ]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required key '{key}' in configuration for {self.equipment_type}.")
        
        logging.info("Configuration validation successful.")
        return True

    def get_thresholds(self, severity: str) -> Optional[float]:
        """
        Retrieves the score threshold for a given severity level.

        Parameters
        ----------
        severity : str
            The severity level (e.g., 'green', 'yellow', 'red').

        Returns
        -------
        Optional[float]
            The score threshold, or None if not found.
        """
        return self.config.get('alarm_thresholds', {}).get(severity)

    def get_techniques(self) -> List[str]:
        """
        Retrieves the list of signal processing techniques.

        Returns
        -------
        List[str]
            A list of signal processing technique names.
        """
        return self.config.get('signal_techniques', [])

    @property
    def signal_columns(self) -> List[str]:
        return self.config.get('signal_columns', [])

    @property
    def normal_ranges(self) -> Dict[str, tuple]:
        return self.config.get('normal_ranges', {})

    @property
    def fault_signatures(self) -> Dict[str, str]:
        return self.config.get('fault_signatures', {})

    @property
    def sampling_rate(self) -> int:
        return self.config.get('sampling_rate', 60)
