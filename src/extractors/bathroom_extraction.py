import json
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class BathroomExtractor(BaseExtractor):
    
    def _format_example_output(self, example):
        """Format example for bathroom categories."""
        return {
            "Bathroom": example["Bathroom"],
            "Water Closet (W.C.)": example["Water Closet (W.C.)"],
            "Combined Bath and W.C.": example["Combined Bath and W.C."],
            "floor": example["floor"]
        }
    
    def _get_target_class_ids(self):
        """Bathroom extraction targets class_id 4."""
        return [4]
    
    def _get_query_text(self):
        """Query text for bathroom extraction."""
        return "Give bathroom categories and floor as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for bathroom categories."""
        # Extract all three categories
        bathroom = data_dict.get('Bathroom', ["absent"])
        water_closet = data_dict.get('Water Closet (W.C.)', ["absent"])
        combined_bath_wc = data_dict.get('Combined Bath and W.C.', ["absent"])
        floor = data_dict.get('floor', ["absent"])
        
        # Handle floor extraction
        floor = self.process_floor_value(floor)
        
        return {
            'Bathroom': bathroom,
            'Water Closet (W.C.)': water_closet,
            'Combined Bath and W.C.': combined_bath_wc,
            'floor': floor
        }
    
    def _format_final_output(self, results):
        """Format final output for bathroom extraction."""
        final_output = []
        for result in results:
            # Create the same format as other room types: (dimensions, floor)
            bathroom_data = (result['Bathroom'], result['floor'])
            water_closet_data = (result['Water Closet (W.C.)'], result['floor'])
            combined_data = (result['Combined Bath and W.C.'], result['floor'])
            
            final_output.append({
                'Bathroom': bathroom_data,
                'Water Closet (W.C.)': water_closet_data,
                'Combined Bath and W.C.': combined_data
            })
        
        return final_output
