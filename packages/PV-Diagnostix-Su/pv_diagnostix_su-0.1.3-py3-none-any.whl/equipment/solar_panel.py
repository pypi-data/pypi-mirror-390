
import logging
import pandas as pd
from typing import Dict, Any
from sklearn.linear_model import LinearRegression
import numpy as np

from pv_diagnostix_su.equipment.base_equipment import BaseEquipment
from pv_diagnostix_su.core.equipment_config import EquipmentConfig # Import EquipmentConfig

logger = logging.getLogger(__name__)

class SolarPanel(BaseEquipment):
    """
    Diagnostic class for Solar Panel equipment.
    """

    def __init__(self, equipment_id: str, data: pd.DataFrame, config: EquipmentConfig):
        super().__init__(equipment_id, equipment_type='solar_panel', data=data, config=config)

    def calculate_degradation(self) -> Dict[str, Any]:
        """
        Calculates the degradation rate of the solar panel.
        Assumes 'power(W)' and 'irradiance(W/m2)' columns are available.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the degradation rate and projection to 80% efficiency.
        """
        if self.data is None or self.data.empty:
            logger.warning(f"No data available for degradation calculation for {self.equipment_id}.")
            return {'degradation_rate_percent_per_year': None, 'projection_years_to_80': None}

        power_column = 'power(W)'
        irradiance_column = 'irradiance(W/m2)'

        if power_column not in self.data.columns or irradiance_column not in self.data.columns:
            logger.error(f"Missing 'power(W)' or 'irradiance(W/m2)' column in data for {self.equipment_id}.")
            return {'degradation_rate_percent_per_year': None, 'projection_years_to_80': None}

        # Calculate efficiency (simplified: power / irradiance)
        # Avoid division by zero or very small irradiance values
        efficiency = self.data[power_column] / self.data[irradiance_column].replace(0, np.nan)
        efficiency = efficiency.dropna()

        if efficiency.empty or len(efficiency) < 2:
            logger.warning(f"Insufficient valid data for degradation calculation for {self.equipment_id}.")
            return {'degradation_rate_percent_per_year': None, 'projection_years_to_80': None}

        # Use time in years for linear regression
        time_in_days = (efficiency.index - efficiency.index.min()).days
        time_in_years = time_in_days / 365.25

        model = LinearRegression()
        model.fit(time_in_years.values.reshape(-1, 1), efficiency.values.reshape(-1, 1))

        degradation_rate_per_year = model.coef_[0][0] # Change in efficiency per year
        initial_efficiency = model.intercept_[0]

        if initial_efficiency <= 0:
            logger.warning(f"Initial efficiency is non-positive for {self.equipment_id}. Cannot project to 80%.")
            projection_years_to_80 = None
        else:
            # Project years to 80% of initial efficiency
            target_efficiency = 0.8 * initial_efficiency
            if degradation_rate_per_year < 0: # Only project if degrading
                projection_years_to_80 = (target_efficiency - initial_efficiency) / degradation_rate_per_year
            else:
                projection_years_to_80 = None # Not degrading or improving

        degradation_rate_percent_per_year = (degradation_rate_per_year / initial_efficiency) * 100 if initial_efficiency != 0 else 0

        logger.info(f"Degradation rate for {self.equipment_id}: {degradation_rate_percent_per_year:.2f}% per year.")
        return {
            'degradation_rate_percent_per_year': degradation_rate_percent_per_year,
            'projection_years_to_80': projection_years_to_80
        }

    def specific_check(self) -> Dict[str, Any]:
        """
        Performs solar panel-specific checks.
        """
        logger.info(f"Performing solar panel-specific checks for {self.equipment_id}.")
        degradation_results = self.calculate_degradation()
        return {
            'degradation_analysis': degradation_results
        }
