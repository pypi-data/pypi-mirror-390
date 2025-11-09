import  os
from typing import List, Dict, Any, Optional, Iterable
import logging
import json


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

# output_path = os.path.join(os.path.dirname(__file__), "..", "seller_performance_report.json")
# output_path = os.path.abspath(output_path)

output_path = os.path.join(os.getcwd(), "seller_performance_report.json")


from omnicart_pipeline.api_client import APIClient
from omnicart_pipeline.data_enricher import DataEnricher
from omnicart_pipeline.data_analyzer import DataAnalyzer
from omnicart_pipeline.config import ConfigManager





class OMNICartETL:
    def __init__(self,config="pipeline.cfg"):
        self.config = config
        

    def run(self) -> Dict[str, Any]:
        
## The Scenario
        logger.info("Pipeline execution started...")

        config_parser = ConfigManager(self.config)


        pipeline_name = config_parser.get_pipeline_name()
        base_url = config_parser.get_load_base_url()
        limit = config_parser.get_load_limit()

        api_client = APIClient(base_url)
        logger.info("Fetching products...")

        products = api_client.get_all_products(start=1, limit=limit)

        logger.info("Fetching users...")
        users = api_client.get_all_users()

        logger.info("Enriching data...")
        data_enricher = DataEnricher(products=products, users=users)
        enriched_data = data_enricher.enrich_data()

        logger.info("Generating analysis...")
        data_analyzer = DataAnalyzer(data=enriched_data)
        analysis_results = data_analyzer.analyze_data()

        if analysis_results:
            with open(output_path, 'w', newline="", encoding="utf-8") as f:
                json.dump(analysis_results, f,indent=2)
            logger.info(f"Pipeline complete. Report saved to seller_performnce.json")
        
       

