import json
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class StoreExtractor(BaseExtractor):
    
    def _format_example_output(self, example):
        """Format example for store extraction."""
        return {
            "store": example["store"],
            "floor": example["floor"]
        }
    
    def _get_target_class_ids(self):
        """Store extraction targets class_id 4."""
        return [4]
    
    def _get_query_text(self):
        """Query text for store extraction."""
        return "Give store and floor as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for store."""
        store = data_dict.get('store', None)
        floor = data_dict.get('floor', None)
        floor = self.process_floor_value(floor)
        
        return (store, floor)
    
    def _format_final_output(self, results):
        """Format final output for store extraction."""
        return results  # Results are already in (store, floor) tuple format
