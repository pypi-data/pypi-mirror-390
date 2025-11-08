
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import json

from pv_diagnostix_su.core.data_loader import load_csv_data
from pv_diagnostix_su.core.equipment_config import EquipmentConfig
from pv_diagnostix_su.core.signal_processor import process_signal
from pv_diagnostix_su.core.health_scorer import HealthScorer, explain_score
from pv_diagnostix_su.core.report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BaseEquipment(ABC):
    """
    Abstract base class for all PV equipment diagnostic tools.
    Defines the common interface for loading data, analyzing signals, and scoring health.
    """

    def __init__(self, equipment_id: str, equipment_type: str, data: pd.DataFrame, config: EquipmentConfig):
        if equipment_type not in ['inverter', 'solar_panel', 'battery']:
            raise ValueError(f"Invalid equipment type: {equipment_type}")

        self.equipment_id = equipment_id
        self.equipment_type = equipment_type
        self.config = config
        self.data: pd.DataFrame = data
        self.logger = logging.getLogger(self.__class__.__name__)
        self.analysis_results: Optional[Dict[str, Any]] = None
        self.health_score_results: Optional[Dict[str, Any]] = None

    # The load_data method is removed as data is now passed directly during initialization.

    def analyze(self, techniques: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyzes the loaded data using specified signal processing techniques.

        Parameters
        ----------
        techniques : Optional[List[str]]
            A list of signal processing techniques to apply. If None, uses techniques from config.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the results from each applied technique.
        """
        if self.data is None or self.data.empty:
            raise ValueError("No data loaded. Call load_data() first.")

        if techniques is None:
            techniques = self.config.get_techniques()

        self.logger.info(f"Analyzing data for {self.equipment_id} using techniques: {techniques}")
        start_time = datetime.now()
        self.analysis_results = process_signal(self.data, techniques)
        end_time = datetime.now()
        self.logger.info(f"Analysis completed in {end_time - start_time} for {self.equipment_id}.")
        return self.analysis_results

    def score(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scores the health of the equipment based on analysis results.

        Parameters
        ----------
        analysis_results : Dict[str, Any]
            The results from signal analysis.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the overall score, severity, and recommendations.
        """
        self.logger.info(f"Scoring health for {self.equipment_id}.")
        scorer = HealthScorer(self.equipment_type, analysis_results, self.config) # Pass self.config here
        self.health_score_results = scorer.calculate_score()
        self.logger.info(f"Health score for {self.equipment_id}: {self.health_score_results['overall_score']} (Severity: {self.health_score_results['severity']})")
        return self.health_score_results

    def diagnose(self) -> Dict[str, Any]:
        """
        Executes the full diagnostic workflow: load -> analyze -> score.
        Includes timing measurements for performance analysis.

        Returns
        -------
        Dict[str, Any]
            A complete diagnostic report.
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        self.logger.info(f"Starting full diagnosis for {self.equipment_id}.")
        
        # Timing for analysis
        start_analyze_time = datetime.now()
        analysis_results = self.analyze()
        end_analyze_time = datetime.now()
        analysis_duration = (end_analyze_time - start_analyze_time).total_seconds()
        self.logger.info(f"Analysis step completed in {analysis_duration:.4f} seconds for {self.equipment_id}.")

        # Timing for scoring
        start_score_time = datetime.now()
        health_score_results = self.score(analysis_results)
        end_score_time = datetime.now()
        score_duration = (end_score_time - start_score_time).total_seconds()
        self.logger.info(f"Scoring step completed in {score_duration:.4f} seconds for {self.equipment_id}.")

        report = {
            'equipment_id': self.equipment_id,
            'equipment_type': self.equipment_type,
            'timestamp': datetime.now().isoformat(),
            'overall_score': health_score_results['overall_score'],
            'component_scores': health_score_results['component_scores'],
            'severity': health_score_results['severity'],
            'risk_factors': health_score_results['risk_factors'],
            'recommendations': health_score_results['recommendations'],
            'explanation': explain_score(health_score_results),
            'performance_metrics': {
                'analysis_duration_seconds': analysis_duration,
                'scoring_duration_seconds': score_duration,
                'total_diagnosis_seconds': analysis_duration + score_duration
            }
        }
        self.logger.info(f"Diagnosis complete for {self.equipment_id}. Total duration: {analysis_duration + score_duration:.4f} seconds.")
        return report

    def export_report(self, report: Dict[str, Any], format: str = 'html', output_dir: str = '.', plots: Optional[List[Any]] = None) -> str:
        """
        Exports the diagnostic report in the specified format using ReportGenerator.

        Parameters
        ----------
        report : Dict[str, Any]
            The diagnostic report to export.
        format : str
            The desired output format ('json', 'html').
        output_dir : str
            The directory where the report will be saved.
        plots : Optional[List[Any]]
            A list of Plotly figure objects to include in the HTML report.

        Returns
        -------
        str
            The path to the generated report file.
        """
        self.logger.info(f"Exporting report for {self.equipment_id} in {format} format to {output_dir}.")
        report_generator = ReportGenerator()
        if format == 'json':
            return report_generator.generate_json_report(self, report, output_dir)
        elif format == 'html':
            return report_generator.generate_html_report(self, report, plots if plots is not None else [], output_dir)
        else:
            raise ValueError(f"Unsupported report format: {format}")

    @abstractmethod
    def specific_check(self) -> Any:
        """
        Abstract method for equipment-specific checks.
        Must be implemented by subclasses.
        """
        pass
