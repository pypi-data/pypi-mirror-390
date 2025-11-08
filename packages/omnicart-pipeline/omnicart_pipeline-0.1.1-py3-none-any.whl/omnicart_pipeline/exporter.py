# Writes results to shoplink_cleaned.json.
import json
from .logging_config import setup_logger


logger = setup_logger(__name__)


class Exporter:
    """
    An Exporter Class to export my analysis to a json file
    """
    def __init__(self, file: list) -> str:
        self.file = file


    def export_to_json(self) -> None:
        """
        Performs the Exporting to JSON file action
        """
        try:
            with open("seller_performance_report.json", "w") as file:
                json.dump(self.file, file, indent = 4)
            logger.info("File 'seller_performance_report.json' exported !!!!!")
            # print("File 'analysis.json' exported !!!!!")
        except TypeError as e:
            print(f"Serialization error: {e}")
            logger.error(f"Serialization error {e}")