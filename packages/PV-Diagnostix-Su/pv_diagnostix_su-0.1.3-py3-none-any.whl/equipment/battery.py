
import logging
import pandas as pd
from typing import Dict, Any

from pv_diagnostix_su.equipment.base_equipment import BaseEquipment
from pv_diagnostix_su.core.equipment_config import EquipmentConfig # Import EquipmentConfig

logger = logging.getLogger(__name__)

class Battery(BaseEquipment):
    """
    Diagnostic class for Battery equipment.
    """

    def __init__(self, equipment_id: str, data: pd.DataFrame, config: EquipmentConfig):
        super().__init__(equipment_id, equipment_type='battery', data=data, config=config)

    def detect_thermal_stress(self) -> Dict[str, Any]:
        """
        Monitors temperature trends to detect thermal stress.
        Flags if temperature >45°C or rising >5°C/hour.

        Returns
        -------
        Dict[str, Any]
            A dictionary indicating thermal stress and current temperature.
        """
        if self.data is None or self.data.empty:
            logger.warning(f"No data available for thermal stress detection for {self.equipment_id}.")
            return {'thermal_stress': False, 'current_temp': None, 'temperature_rise_rate': None}

        temp_column = 'temperature(C)'
        if temp_column not in self.data.columns:
            logger.error(f"'{temp_column}' column not found in data for {self.equipment_id}.")
            return {'thermal_stress': False, 'current_temp': None, 'temperature_rise_rate': None}

        temperature_series = self.data[temp_column]
        current_temp = temperature_series.iloc[-1] if not temperature_series.empty else None
        thermal_stress = False
        temperature_rise_rate = None

        if current_temp is not None:
            if current_temp > 45:
                thermal_stress = True
                logger.warning(f"Battery {self.equipment_id} temperature ({current_temp}°C) is above 45°C.")

            # Check for rising temperature if enough data points
            if len(temperature_series) >= 2:
                # Assuming data is sampled at 1-minute intervals, so diff is per minute
                temp_diff = temperature_series.diff().iloc[-1]
                time_diff_hours = (temperature_series.index[-1] - temperature_series.index[-2]).total_seconds() / 3600
                if time_diff_hours > 0:
                    temperature_rise_rate = temp_diff / time_diff_hours # °C per hour
                    if temperature_rise_rate > 5:
                        thermal_stress = True
                        logger.warning(f"Battery {self.equipment_id} temperature rising at {temperature_rise_rate:.2f}°C/hour (above 5°C/hour).")

        return {
            'thermal_stress': thermal_stress,
            'current_temp': current_temp,
            'temperature_rise_rate': temperature_rise_rate
        }

    def specific_check(self) -> Dict[str, Any]:
        """
        Performs battery-specific checks.
        """
        logger.info(f"Performing battery-specific checks for {self.equipment_id}.")
        thermal_stress_results = self.detect_thermal_stress()
        return {
            'thermal_stress_analysis': thermal_stress_results
        }
