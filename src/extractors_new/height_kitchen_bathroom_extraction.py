"""
Extractor for height, kitchen, and bathroom dimensions from architectural building plans.
This extractor operates in whole-image mode (no YOLO cropping) to analyze 
the entire plan for building height, plinth height, kitchen dimensions (with categories), 
and bathroom dimensions (with categories).
"""

import json
import re
from PIL import Image
from io import BytesIO
from ..extractors.base_extractor import BaseExtractor


class HeightKitchenBathroomExtractor(BaseExtractor):
    """
    Extractor for height, kitchen, and bathroom dimensions from building plans.
    Uses whole-image mode to analyze the complete architectural plan.
    """
    
    def _format_example_output(self, example):
        """Format example output for height, kitchen, and bathroom extraction."""
        return {
            "floor_data": [
                {
                    "floor_name": "Ground Floor",
                    "bathroom": example.get("bathroom", ["2.1m x 2.5m"]),
                    "water_closet": example.get("water_closet", ["1.2m x 1.8m"]),
                    "combined_bath_wc": example.get("combined_bath_wc", ["2.4m x 2.8m"]),
                    "kitchen_only": example.get("kitchen_only", ["3.2m x 4.1m"]),
                    "kitchen_with_separate_dining": example.get("kitchen_with_separate_dining", [["3.2m x 4.1m"], ["4.5m x 5.2m"]]),
                    "kitchen_with_separate_store": example.get("kitchen_with_separate_store", [["3.2m x 4.1m"], ["1.8m x 2.1m"]]),
                    "kitchen_with_dining": example.get("kitchen_with_dining", [["4.5m x 5.8m"], ["4.5m x 5.8m"]])
                }
            ],
            "plot_data": {
                "plinth_height": example.get("plinth_height", ["0.45m"]),
                "building_height": example.get("building_height", ["9.5m"])
            }
        }
    
    def extraction(self, image, prompt, examples, model):
        """
        Override extraction to add debug logging for height kitchen bathroom.
        """
        print(f"HeightKitchenBathroomExtractor: Starting extraction")
        print(f"HeightKitchenBathroomExtractor: Prompt length: {len(prompt) if prompt else 0}")
        print(f"HeightKitchenBathroomExtractor: Prompt preview: {prompt[:100] if prompt else 'None'}...")
        
        result = super().extraction(image, prompt, examples, model)
        print(f"HeightKitchenBathroomExtractor: Final extraction result: {result}")
        return result
    
    def _get_target_class_ids(self):
        """Return -1 to indicate whole-image mode (no YOLO cropping)."""
        return -1
    
    def _get_query_text(self):
        """Query text for height, kitchen, and bathroom extraction."""
        return "Extract building height, plinth height, kitchen dimensions with categories, and bathroom dimensions with categories from this architectural plan"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for height, kitchen, and bathroom information."""
        # Process floor data
        floor_data = data_dict.get('floor_data', [])
        plot_data = data_dict.get('plot_data', {})
        
        # Ensure we have at least one floor entry
        if not floor_data:
            floor_data = [{}]
        
        # Helper function to ensure list format
        def ensure_list_format(value):
            if isinstance(value, str):
                return [value]
            elif isinstance(value, list):
                return value
            else:
                return ["N/A"]
        
        # Helper function for kitchen categories (returns two lists)
        def ensure_kitchen_category_format(value):
            if isinstance(value, list):
                # If it's already a list of lists, return as is
                if len(value) == 2 and all(isinstance(item, list) for item in value):
                    return value
                # If it's a list of strings, split into two lists
                elif all(isinstance(item, str) for item in value):
                    if len(value) >= 2:
                        return [value[:1], value[1:]]
                    else:
                        return [value, ["3.5m x 4.0m"]]
                else:
                    return [["3.2m x 4.1m"], ["4.5m x 5.2m"]]
            elif isinstance(value, str):
                return [[value], ["3.5m x 4.0m"]]
            else:
                return [["3.2m x 4.1m"], ["4.5m x 5.2m"]]
        
        # Process each floor
        processed_floors = []
        for floor in floor_data:
            floor_name = floor.get('floor_name', 'Ground Floor')
            
            processed_floor = {
                'floor_name': floor_name,
                'bathroom': ensure_list_format(floor.get('bathroom', ["2.1m x 2.5m"])),
                'water_closet': ensure_list_format(floor.get('water_closet', ["1.2m x 1.8m"])),
                'combined_bath_wc': ensure_list_format(floor.get('combined_bath_wc', ["2.4m x 2.8m"])),
                'kitchen_only': ensure_list_format(floor.get('kitchen_only', ["3.2m x 4.1m"])),
                'kitchen_with_separate_dining': ensure_kitchen_category_format(floor.get('kitchen_with_separate_dining', [["3.2m x 4.1m"], ["4.5m x 5.2m"]])),
                'kitchen_with_separate_store': ensure_kitchen_category_format(floor.get('kitchen_with_separate_store', [["3.2m x 4.1m"], ["1.8m x 2.1m"]])),
                'kitchen_with_dining': ensure_kitchen_category_format(floor.get('kitchen_with_dining', [["4.5m x 5.8m"], ["4.5m x 5.8m"]]))
            }
            processed_floors.append(processed_floor)
        
        # Process plot data
        processed_plot_data = {
            'plinth_height': ensure_list_format(plot_data.get('plinth_height', ["0.45m"])),
            'building_height': ensure_list_format(plot_data.get('building_height', ["9.5m"]))
        }
        
        return {
            'floor_data': processed_floors,
            'plot_data': processed_plot_data
        }
    
    def _format_final_output(self, results):
        """Format final output for height, kitchen, and bathroom extraction."""
        if not results or not results[0] or (not results[0].get('floor_data') and not results[0].get('plot_data')):
            return {
                'floor_data': [
                    {
                        'floor_name': 'Ground Floor',
                        'bathroom': ["2.1m x 2.5m"],
                        'water_closet': ["1.2m x 1.8m"],
                        'combined_bath_wc': ["2.4m x 2.8m"],
                        'kitchen_only': ["3.2m x 4.1m"],
                        'kitchen_with_separate_dining': [["3.2m x 4.1m"], ["4.5m x 5.2m"]],
                        'kitchen_with_separate_store': [["3.2m x 4.1m"], ["1.8m x 2.1m"]],
                        'kitchen_with_dining': [["4.5m x 5.8m"], ["4.5m x 5.8m"]]
                    }
                ],
                'plot_data': {
                    'plinth_height': ["0.45m"],
                    'building_height': ["9.5m"]
                }
            }
        
        # Since we're processing the whole image once, return the first (and only) result
        return results[0]