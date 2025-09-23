import json  
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class StudyRoomExtractor(BaseExtractor):
    
    def _format_example_output(self, example):
        """Format example for study room extraction."""
        return {
            "study": example["study"],
            "floor": example["floor"]
        }
    
    def _get_target_class_ids(self):
        """Study room extraction targets class_id 4."""
        return [4]
    
    def _get_query_text(self):
        """Query text for study room extraction."""
        return "Give study and floor as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for study room."""
        study = data_dict.get('study', None)
        floor = data_dict.get('floor', None)
        floor = self.process_floor_value(floor)
        
        return (study, floor)
    
    def _format_final_output(self, results):
        """Format final output for study room extraction."""
        return results  # Results are already in (study, floor) tuple format
