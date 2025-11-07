import json

from pathlib import Path

from .api_client import APIClient
from .config import ConfigManager
from .data_analyzer import DataAnalyzer
from .data_enricher import DataEnricher




class Pipeline:
    def __init__(self) -> None:
        self.config = ConfigManager()
        self.api_client = APIClient()
        self.data_enricher = DataEnricher()
        self.data_analyzer = DataAnalyzer()
        
        
    def run(self)-> None:
        base_url, limit = self.config.config()
        products = next(self.api_client.get_products(base_url, limit))
        users = self.api_client.get_users(base_url)[:5]
        enriched_data = self.data_enricher.enrich_data(products, users)
        analyzed_data = self.data_analyzer.analyze_data(enriched_data)
        
        output_path = Path.cwd() / 'seller_performance_report.json'
        with open(output_path, 'w') as file:
            json.dump(analyzed_data, file, indent=4)
        
      