
import json
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class BDE(BaseExtractor):
    
    def _format_example_output(self, example):
        """Format example for bedroom and drawing room extraction."""
        return {
            "bedroom": example["bedroom"],
            "drawing": example["drawing"],
            "floor": example["floor"]
        }
    
    def _get_target_class_ids(self):
        """Bedroom/drawing room extraction targets class_id 4."""
        return [4]
    
    def _get_query_text(self):
        """Query text for bedroom and drawing room extraction."""
        return "Give bedroom, drawing, and floor as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for bedroom and drawing room."""
        bedroom = data_dict.get('bedroom', None)
        drawing = data_dict.get('drawing', None)
        floor = data_dict.get('floor', None)
        floor = self.process_floor_value(floor)
        
        return {
            'bedroom': bedroom,
            'drawing': drawing,
            'floor': floor
        }
    
    def _format_final_output(self, results):
        """Format final output for bedroom and drawing room extraction."""
        bedroom_output = []
        drawing_output = []
        
        for result in results:
            bedroom_output.append((result['bedroom'], result['floor']))
            drawing_output.append((result['drawing'], result['floor']))
        
        return bedroom_output, drawing_output

                