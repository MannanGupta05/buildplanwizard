"""
Extractor for setback values and floor count from architectural building plans.
This extractor operates in whole-image mode (no YOLO cropping) to analyze 
the entire plan for setback dimensions and floor information.
"""

import json
import re
from PIL import Image
from io import BytesIO
from ..extractors.base_extractor import BaseExtractor


class SetbackFloorsExtractor(BaseExtractor):
    """
    Extractor for setback values and number of floors from building plans.
    Uses whole-image mode to analyze the complete architectural plan.
    """
    
    def _format_example_output(self, example):
        """Format example output for setback and floors extraction."""
        return {
            "plot_data": {
                "no_of_floors": example.get("no_of_floors", 2),
                "front_setback": example.get("front_setback", ["3.0m"]),
                "rear_setback": example.get("rear_setback", ["2.5m"]),
                "left_side_setback": example.get("left_side_setback", ["1.5m"]),
                "right_side_setback": example.get("right_side_setback", ["1.5m"])
            }
        }
    
    def extraction(self, image, prompt, examples, model):
        """
        Override extraction to add debug logging for setback floors.
        """
        print(f"SetbackFloorsExtractor: Starting extraction")
        print(f"SetbackFloorsExtractor: Prompt length: {len(prompt) if prompt else 0}")
        
        # Write debug info to file
        try:
            with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                debug_file.write(f"\n=== SETBACK FLOORS EXTRACTION ===\n")
                debug_file.write(f"Prompt received: {prompt[:200] if prompt else 'None'}...\n")
        except:
            pass
        
        result = super().extraction(image, prompt, examples, model)
        
        try:
            with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                debug_file.write(f"Final result: {result}\n")
        except:
            pass
        
        print(f"SetbackFloorsExtractor: Final extraction result: {result}")
        return result
    
    def _get_target_class_ids(self):
        """Return -1 to indicate whole-image mode (no YOLO cropping)."""
        return -1
    
    def _get_query_text(self):
        """Query text for setback and floors extraction."""
        return "Extract setback values and number of floors from this architectural plan"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for setback and floors information."""
        # Add debug logging
        try:
            with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                debug_file.write(f"\n=== SETBACK PROCESSING ===\n")
                debug_file.write(f"Raw data_dict: {data_dict}\n")
                debug_file.write(f"Data type: {type(data_dict)}\n")
        except:
            pass
        
        print(f"SetbackFloorsExtractor: Processing data_dict: {data_dict}")
        
        # New format: data_dict is a list like [{'no_of_floors': ['2'], 'front_setback': ['3.05'], ...}]
        if isinstance(data_dict, list) and len(data_dict) > 0:
            first_item = data_dict[0]
            if isinstance(first_item, dict):
                print(f"SetbackFloorsExtractor: Using new list format: {first_item}")
                return first_item  # Return the dict directly, not wrapped in list
        
        # Fallback: try old format with plot_data
        if isinstance(data_dict, dict) and 'plot_data' in data_dict:
            plot_data = data_dict['plot_data']
            print(f"SetbackFloorsExtractor: Using fallback plot_data format: {plot_data}")
            
            # Extract and format data
            no_of_floors = plot_data.get('no_of_floors', "Not Sure")
            if isinstance(no_of_floors, (int, float)):
                no_of_floors = [str(no_of_floors)]
            elif isinstance(no_of_floors, str):
                no_of_floors = [no_of_floors]
            elif not isinstance(no_of_floors, list):
                no_of_floors = ["Not Sure"]
            
            # Helper function to ensure list format
            def ensure_list_format(value):
                if isinstance(value, str):
                    return [value]
                elif isinstance(value, list):
                    return value
                else:
                    return ["Not Sure"]
            
            return {
                'no_of_floors': no_of_floors,
                'front_setback': ensure_list_format(plot_data.get('front_setback', ["Not Sure"])),
                'rear_setback': ensure_list_format(plot_data.get('rear_setback', ["Not Sure"])),
                'left_side_setback': ensure_list_format(plot_data.get('left_side_setback', ["Not Sure"])),
                'right_side_setback': ensure_list_format(plot_data.get('right_side_setback', ["Not Sure"]))
            }
        
        # Default fallback - this is probably what's being returned
        print("SetbackFloorsExtractor: Using default fallback - AI extraction likely failed")
        try:
            with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                debug_file.write(f"USING DEFAULT FALLBACK - AI extraction failed\n")
        except:
            pass
        
        return {
            'no_of_floors': ["Not Sure"],
            'front_setback': ["Not Sure"],
            'rear_setback': ["Not Sure"],
            'left_side_setback': ["Not Sure"],
            'right_side_setback': ["Not Sure"]
        }
    
    def _format_final_output(self, results):
        """Format final output for setback and floors extraction."""
        print(f"SetbackFloorsExtractor: Formatting final output, results: {results}")
        
        if not results or not results[0]:
            print("SetbackFloorsExtractor: No results, returning default")
            return [{
                'no_of_floors': ["Not Sure"],
                'front_setback': ["Not Sure"],
                'rear_setback': ["Not Sure"],
                'left_side_setback': ["Not Sure"],
                'right_side_setback': ["Not Sure"]
            }]
        
        # Return the first result wrapped in a list for consistency
        result = results[0]
        print(f"SetbackFloorsExtractor: Final formatted output: {[result]}")
        return [result]