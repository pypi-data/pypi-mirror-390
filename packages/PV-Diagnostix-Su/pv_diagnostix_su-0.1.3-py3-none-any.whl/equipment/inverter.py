
import logging
import pandas as pd
from typing import Dict, Any, List

from pv_diagnostix_su.equipment.base_equipment import BaseEquipment
from pv_diagnostix_su.core.equipment_config import EquipmentConfig # Import EquipmentConfig

logger = logging.getLogger(__name__)

class Inverter(BaseEquipment):
    """
    Diagnostic class for Inverter equipment.
    """

    def __init__(self, equipment_id: str, data: pd.DataFrame, config: EquipmentConfig):
        super().__init__(equipment_id, equipment_type='inverter', data=data, config=config)

    def detect_power_anomalies(self) -> Dict[str, Any]:
        """
        Analyzes the 'activePower(W)' column to detect sudden drops >30%.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the count of anomalies and their timestamps.
        """
        if self.data is None or self.data.empty:
            logger.warning(f"No data available for power anomaly detection for {self.equipment_id}.")
            return {'anomalies_count': 0, 'anomaly_timestamps': []}

        power_column = 'activePower(W)'
        if power_column not in self.data.columns:
            logger.error(f"'{power_column}' column not found in data for {self.equipment_id}.")
            return {'anomalies_count': 0, 'anomaly_timestamps': []}

        power_series = self.data[power_column]
        # Calculate percentage change
        power_change = power_series.pct_change() * 100
        
        # Detect drops greater than 30%
        anomalies = power_change[power_change < -30]
        
        anomaly_timestamps = anomalies.index.tolist()
        anomalies_count = len(anomalies)

        if anomalies_count > 0:
            logger.warning(f"Detected {anomalies_count} power anomalies for {self.equipment_id}.")
        else:
            logger.info(f"No significant power anomalies detected for {self.equipment_id}.")

        return {
            'anomalies_count': anomalies_count,
            'anomaly_timestamps': anomaly_timestamps
        }

    def check_phase_balance(self) -> Dict[str, Any]:
        """
        Checks the phase balance of AC currents (L1, L2, L3).
        Assumes columns like 'acCurrent_L1(A)', 'acCurrent_L2(A)', 'acCurrent_L3(A)' exist.

        Returns
        -------
        Dict[str, Any]
            A dictionary with the balance ratio and status.
        """
        if self.data is None or self.data.empty:
            logger.warning(f"No data available for phase balance check for {self.equipment_id}.")
            return {'balance_ratio': None, 'status': 'NO_DATA'}

        phase_columns = ['acCurrent_L1(A)', 'acCurrent_L2(A)', 'acCurrent_L3(A)']
        if not all(col in self.data.columns for col in phase_columns):
            logger.warning(f"Missing one or more phase current columns for {self.equipment_id}. Skipping phase balance check.")
            return {'balance_ratio': None, 'status': 'INSUFFICIENT_DATA'}

        # Calculate instantaneous phase balance ratio
        # Max difference from mean / mean
        phase_data = self.data[phase_columns]
        mean_current = phase_data.mean(axis=1)
        max_diff = phase_data.apply(lambda row: max(abs(row - mean_current)), axis=1)
        
        # Avoid division by zero
        balance_ratio = (max_diff / mean_current).replace([np.inf, -np.inf], np.nan).mean()

        status = 'BALANCED'
        if balance_ratio is not None and balance_ratio > 0.10: # Flag if >10%
            status = 'IMBALANCED'
            logger.warning(f"Phase imbalance detected for {self.equipment_id}. Ratio: {balance_ratio:.2f}")
        else:
            logger.info(f"Phase balance is good for {self.equipment_id}. Ratio: {balance_ratio:.2f}")

        return {
            'balance_ratio': balance_ratio,
            'status': status
        }

    def specific_check(self) -> Dict[str, Any]:
        """
        Performs inverter-specific checks.
        """
        logger.info(f"Performing inverter-specific checks for {self.equipment_id}.")
        power_anomalies = self.detect_power_anomalies()
        phase_balance = self.check_phase_balance()
        return {
            'power_anomalies': power_anomalies,
            'phase_balance': phase_balance
        }
