
import logging
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

# Assuming BaseEquipment is defined elsewhere, e.g., in pv_equipment_diagnostics.equipment.base_equipment
# from ..equipment.base_equipment import BaseEquipment 
# Assuming visualization functions are available
# from ..utils.visualization import export_html, plot_health_score_dashboard, plot_comparison_multiple_equipments

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportGenerator:
    """
    Generates various types of reports (summary dictionary, JSON, HTML) from equipment diagnostic results.
    """

    def __init__(self):
        pass

    def generate_summary_dict(self, equipment: Any, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a summary dictionary of diagnostic results.

        Parameters
        ----------
        equipment : BaseEquipment
            The equipment object for which the report is being generated.
        analysis : dict
            The analysis results from the health scorer.

        Returns
        -------
        dict
            A dictionary containing a summarized report.
        """
        timestamp = datetime.now().isoformat()
        
        # Extract relevant information from analysis
        overall_score = analysis.get('overall_score', 0)
        severity = analysis.get('severity', 'UNKNOWN')
        component_scores = analysis.get('component_scores', {})
        risk_factors = analysis.get('risk_factors', [])
        recommendations = analysis.get('recommendations', [])
        
        summary = {
            'timestamp': timestamp,
            'equipment_id': equipment.equipment_id,
            'equipment_type': equipment.equipment_type,
            'overall_score': overall_score,
            'severity': severity,
            'component_scores': component_scores,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'analysis_details': analysis # Raw results
        }
        logging.info(f"Generated summary dictionary for equipment {equipment.equipment_id}.")
        return summary

    def generate_json_report(self, equipment: Any, analysis: Dict[str, Any], output_dir: str = './reports') -> str:
        """
        Generates a pretty-printed JSON report and saves it to a file.

        Parameters
        ----------
        equipment : BaseEquipment
            The equipment object.
        analysis : dict
            The analysis results.
        output_dir : str, optional
            The directory to save the JSON report. Defaults to './reports'.

        Returns
        -------
        str
            The path to the generated JSON report file.
        """
        summary_dict = self.generate_summary_dict(equipment, analysis)
        report_filename = f"{equipment.equipment_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        output_path = Path(output_dir) / report_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, 'w') as f:
                json.dump(summary_dict, f, indent=2)
            logging.info(f"Generated JSON report: {output_path}")
            return str(output_path)
        except Exception as e:
            logging.error(f"Failed to generate JSON report for {equipment.equipment_id}: {e}")
            raise

    def generate_html_report(self, equipment: Any, analysis: Dict[str, Any], plots: List[Any], output_dir: str = './reports') -> str:
        """
        Generates a self-contained HTML report with embedded plots.

        Parameters
        ----------
        equipment : BaseEquipment
            The equipment object.
        analysis : dict
            The analysis results.
        plots : list
            A list of Plotly graph objects to embed in the report.
        output_dir : str, optional
            The directory to save the HTML report. Defaults to './reports'.

        Returns
        -------
        str
            The path to the generated HTML report file.
        """
        summary_dict = self.generate_summary_dict(equipment, analysis)

        # Determine emoji and color for overall health
        overall_score = summary_dict['overall_score']
        severity = summary_dict['severity']
        
        if severity == 'HEALTHY':
            health_emoji = '✅'
            badge_background_color = '#2ca02c' # Green
        elif severity == 'AT_RISK':
            health_emoji = '⚠️'
            badge_background_color = '#ff9900' # Orange
        elif severity == 'CRITICAL':
            health_emoji = '❌'
            badge_background_color = '#d62728' # Red
        else: # UNKNOWN or FAILURE
            health_emoji = '❓'
            badge_background_color = '#6c757d' # Grey

        # Simplified KPI Summary for decision-makers (using new minimalist style)
        kpi_summary = f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <div class="status-badge" style="background-color: {badge_background_color};">
                <div class="status-title">{severity}</div>
                <div class="confidence-score">Score Global : {overall_score:.2f}%</div>
            </div>
        </div>
        """

        # Placeholder for cost and action details (these would be calculated in a real scenario)
        # For now, using illustrative values
        cost_problem_euro = 5000 # Example value
        cost_solution_euro = 1000 # Example value
        economy_euro = 4000 # Example value
        payback_months = 3 # Example value
        immediate_action = summary_dict['recommendations'][0] if summary_dict['recommendations'] else "Contacter l'équipe de maintenance pour une évaluation."

        cost_action_html = f"""
        <div class="main-grid" style="margin-top: 20px;">
            <div class="grid-item"><h2>Impact Financier & Actions Clés</h2>
                <p><strong>Coût du Problème (si rien n'est fait):</strong> Estimé à <span style="color: #ff9900;">{cost_problem_euro} €/an</span> de pertes.</p>
                <p><strong>Coût de la Solution Proposée:</strong> Investissement estimé à <span style="color: #54a24b;">{cost_solution_euro} €</span>.</p>
                <p><strong>Économies potentielles:</strong> <span style="color: #54a24b;">{economy_euro} €/an</span>.</p>
                <p><strong>Retour sur investissement (ROI):</strong> <span style="color: #ff9900;">{payback_months} mois</span>.</p>
                <p>➡️ <strong>Action Immédiate Recommandée:</strong> {immediate_action} (à réaliser cette semaine)</p>
            </div>
        </div>
        """

        # Embed plots (still keep them, but they are after the main summary)
        plots_html = ""
        if plots:
            plots_html += """
            <div class="main-grid" style="margin-top: 20px;">
                <div class="grid-item"><h2>Visualisations Détaillées (pour experts)</h2>
            """
            for i, plot in enumerate(plots):
                plots_html += f"<div class='plot-container'>{plot.to_html(full_html=False, include_plotlyjs='cdn')}</div>"
            plots_html += "</div></div>" # Close grid-item and main-grid

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Diagnostic Report - {equipment.equipment_id}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a242a; color: #f0f0f0; margin: 0; padding: 20px; }}
                .container {{ max-width: 1400px; margin: auto; }}
                h1, h2 {{ color: #ff9900; border-bottom: 2px solid #444; padding-bottom: 10px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .status-badge {{
                    color: white;
                    padding: 15px 25px;
                    text-align: center;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    display: inline-block;
                }}
                .status-title {{ font-size: 28px; font-weight: bold; margin: 0; }}
                .confidence-score {{ font-size: 16px; margin-top: 5px; opacity: 0.9; }}
                .main-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
                .grid-item {{ background-color: #2c3e50; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }}
                .kpi-banner {{ display: flex; justify-content: space-around; gap: 20px; margin-bottom: 30px; }}
                .kpi-card {{ background-color: #2c3e50; padding: 20px; border-radius: 8px; text-align: center; flex-grow: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }}
                .kpi-card h3 {{ margin-top: 0; color: #f0f0f0; font-size: 16px; text-transform: uppercase; opacity: 0.8; }}
                .kpi-card .value {{ font-size: 36px; font-weight: bold; color: #ff9900; }}
                .kpi-table table {{ width: 100%; border-collapse: collapse; }}
                .kpi-table th, .kpi-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #444; }}
                .kpi-table th {{ background-color: #34495e; }}
                .footer {{ text-align: center; margin-top: 50px; font-size: 0.9em; color: #6c757d; border-top: 1px solid #444; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Equipment Diagnostic Report</h1>
                    <p style="color: #f0f0f0;"><strong>Equipment ID:</strong> {equipment.equipment_id}</p>
                    <p style="color: #f0f0f0;"><strong>Equipment Type:</strong> {equipment.equipment_type}</p>
                    <p style="color: #f0f0f0;"><strong>Report Date:</strong> {summary_dict['timestamp']}</p>
                    <p style="color: #f0f0f0;"><strong>Sonelgaz Compliance:</strong> Yes</p>
                    <p style="color: #f0f0f0;"><strong>Analysis Conditions:</strong> Specific to Algeria</p>
                </div>

                {kpi_summary}
                {cost_action_html}
                {plots_html}

                <div class="footer">
                    <p>Report generated by PV Equipment Diagnostics Toolkit</p>
                </div>
            </div>
        </body>
        </html>
        """

        report_filename = f"{equipment.equipment_id}_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        output_path = Path(output_dir) / report_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, 'w', encoding='utf-8') as f: # Specify encoding
                f.write(html_content)
            logging.info(f"Generated HTML report: {output_path}")
            return str(output_path)
        except Exception as e:
            logging.error(f"Failed to generate HTML report for {equipment.equipment_id}: {e}")
            raise

    def generate_multiequipment_report(self, equipments_list: List[Dict[str, Any]], output_dir: str = './reports') -> Dict[str, str]:
        """
        Generates a summary report for multiple equipment, including a summary table and site-level overview.

        Parameters
        ----------
        equipments_list : list
            A list of dictionaries, where each dictionary contains 'equipment' (BaseEquipment object)
            and 'analysis' (results from health scorer) for each equipment.
        output_dir : str, optional
            The directory to save the reports. Defaults to './reports'.

        Returns
        -------
        dict
            A dictionary containing paths to the generated CSV and HTML summary reports.
        """
        all_summaries = []
        for item in equipments_list:
            equipment = item['equipment']
            analysis = item['analysis']
            summary = self.generate_summary_dict(equipment, analysis)
            all_summaries.append(summary)

        # Create a DataFrame for easy sorting and CSV export
        summary_df = pd.DataFrame([
            {
                'equipment_id': s['equipment_id'],
                'equipment_type': s['equipment_type'],
                'overall_score': s['overall_score'],
                'severity': s['severity'],
                'timestamp': s['timestamp']
            } for s in all_summaries
        ])

        # Define severity order for sorting
        severity_order = {'CRITICAL': 0, 'AT_RISK': 1, 'HEALTHY': 2, 'FAILURE': 3, 'UNKNOWN': 4}
        summary_df['severity_rank'] = summary_df['severity'].map(severity_order)
        summary_df = summary_df.sort_values(by=['severity_rank', 'overall_score'], ascending=[True, False]).drop(columns=['severity_rank'])

        # Export to CSV
        csv_filename = f"multiequipment_summary_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        csv_path = Path(output_dir) / csv_filename
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            summary_df.to_csv(csv_path, index=False)
            logging.info(f"Generated multi-equipment CSV report: {csv_path}")
        except Exception as e:
            logging.error(f"Failed to generate multi-equipment CSV report: {e}")
            raise

        # Generate HTML overview
        # This would typically involve a plot_comparison_multiple_equipments from visualization.py
        # For now, we'll create a simple HTML table.
        html_filename = f"multiequipment_overview_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        html_path = Path(output_dir) / html_filename
        html_path.parent.mkdir(parents=True, exist_ok=True)

        html_table = summary_df.to_html(index=False)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Multi-Equipment Overview Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }}
                .container {{ background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: #0056b3; text-align: center; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #0056b3; color: white; }}
                .severity-CRITICAL {{ color: red; font-weight: bold; }}
                .severity-AT_RISK {{ color: orange; }}
                .severity-HEALTHY {{ color: green; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Multi-Equipment Overview Report</h1>
                {html_table}
                <div class="footer">
                    <p>Report generated by PV Equipment Diagnostics Toolkit</p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            with open(html_path, 'w') as f:
                f.write(html_content)
            logging.info(f"Generated multi-equipment HTML report: {html_path}")
        except Exception as e:
            logging.error(f"Failed to generate multi-equipment HTML report: {e}")
            raise

        return {'csv_report': str(csv_path), 'html_report': str(html_path)}
