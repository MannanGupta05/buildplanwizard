import numpy as np
from PIL import Image
import json
from io import BytesIO
import re
from .base_extractor import BaseExtractor

class LobbyDiningExtractor(BaseExtractor):
    
    def _format_example_output(self, example):
        """Format example for lobby and dining extraction."""
        return {
            "lobby": example["lobby"],
            "dining": example["dining"],
            "floor": example["floor"]
        }
    
    def _get_target_class_ids(self):
        """Lobby/dining extraction targets class_id 4."""
        return [4]
    
    def _get_query_text(self):
        """Query text for lobby and dining extraction."""
        return "Give lobby, dining, and floor as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for lobby and dining."""
        lobby = data_dict.get('lobby', None)
        dining = data_dict.get('dining', None)
        floor = data_dict.get('floor', None)
        floor = self.process_floor_value(floor)
        
        return {
            'lobby': lobby,
            'dining': dining,
            'floor': floor
        }
    
    def _format_final_output(self, results):
        """Format final output for lobby and dining extraction."""
        lobby_output = []
        dining_output = []
        
        for result in results:
            lobby_output.append((result['lobby'], result['floor']))
            dining_output.append((result['dining'], result['floor']))
        
        return lobby_output, dining_output
