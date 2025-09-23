import json 
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class KitchenExtractor(BaseExtractor):
    
    def _format_example_output(self, example):
        """Format example for kitchen extraction."""
        return {
            "kitchen": example["kitchen"],
            "floor": example["floor"]
        }
    
    def _get_target_class_ids(self):
        """Kitchen extraction targets class_id 4."""
        return [4]
    
    def _get_query_text(self):
        """Query text for kitchen extraction."""
        return "Give kitchen and floor as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for kitchen."""
        kitchen = data_dict.get('kitchen', None)
        floor = data_dict.get('floor', None)
        floor = self.process_floor_value(floor)
        
        return (kitchen, floor)
    
    def _format_final_output(self, results):
        """Format final output for kitchen extraction."""
        return results  # Results are already in (kitchen, floor) tuple format
