# This is the top level file which is going to contain rule_verifier and Extractor functionalities. 
# It also defines relative paths for example folders, prompts
# Updated to use ONLY the new extractors_new system

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.core import config_map as config
from PIL import Image
from pdf2image import convert_from_path

# Import ONLY the new extractors (no YOLO needed - whole image mode)
from src.extractors_new.area_extraction import AreaExtractor
from src.extractors_new.room_extraction import RoomExtractor
from src.extractors_new.setback_floors_extraction import SetbackFloorsExtractor
from src.extractors_new.staircase_extraction import StaircaseExtractor
from src.extractors_new.height_kitchen_bathroom_extraction import HeightKitchenBathroomExtractor

from src.core import utils

# Import rule_verifier from separate file - handle both relative and absolute imports
try:
    from .rule_verifier import rule_verifier
except ImportError:
    from rule_verifier import rule_verifier

def read_pdf(file_path):
    """Convert PDF to image and return the first page"""
    try:
        # Try to find poppler path - check multiple possible locations
        poppler_path = None
        
        # First, try the bundled version if it exists
        bundled_poppler = os.path.join(config.MAIN_PATH, "poppler-24.08.0", "Library", "bin")
        if os.path.exists(bundled_poppler):
            poppler_path = bundled_poppler
        
        # On Render/Linux systems, poppler is typically installed system-wide
        # pdf2image will find it automatically if poppler_path is None
        
        if poppler_path:
            images = convert_from_path(file_path, dpi=300, poppler_path=poppler_path)
        else:
            # Let pdf2image find poppler automatically (works on most Linux systems)
            images = convert_from_path(file_path, dpi=300)
            
        if not images:
            raise Exception("Failed to convert PDF to image")
        return images[0]
    except Exception as e:
        raise Exception(f"PDF conversion failed: {str(e)}")

def create_segments(input_map_image, model="WHOLE_IMAGE"):
    """Process image for whole-image extraction (no YOLO segmentation needed)"""
    try:
        # Return the image as-is for whole-image processing
        # No YOLO detection needed for the new extractors
        return input_map_image, []  # Empty boxs list since we don't need YOLO boxes
    except Exception as e:
        raise Exception(f"Image processing failed: {str(e)}")

class Extractor():
    def __init__(self, model, extractor, image, examples, prompt):
        self.model = model
        self.extractor = extractor
        self.image = image
        self.examples = examples
        self.prompt = prompt
        self.result = None
    
    def run(self):
        """Execute the extraction based on the configured parameters"""
        try:
            # For the new extractors, we don't need YOLO boxes - they process whole images
            # Initialize extractor with empty boxes list (required by BaseExtractor)
            extractor_instance = self.extractor([])
            
            # Run extraction with whole image
            self.result = extractor_instance.extraction(self.image, self.prompt, [], self.model)
            return self.result
        except Exception as e:
            print(f"Extraction error: {e}")
            self.result = {}
            return self.result

def get_extractor_func(variable):
    """Returns the appropriate extractor class for the given variable (NEW SYSTEM ONLY)"""
    extractor_dict = {
        # Area-related extractions
        "total_plot_area": AreaExtractor,
        "ground_covered_area": AreaExtractor,
        "total_covered_area": AreaExtractor,
        "far": AreaExtractor,
        "plot_area_far": AreaExtractor,
        
        # Room-related extractions
        "bedroom": RoomExtractor,
        "drawingroom": RoomExtractor,
        "studyroom": RoomExtractor,
        "store": RoomExtractor,
        
        # Setback and floors
        "setback": SetbackFloorsExtractor,
        "floors": SetbackFloorsExtractor,
        "no_of_floors": SetbackFloorsExtractor,
        "front_setback": SetbackFloorsExtractor,
        "rear_setback": SetbackFloorsExtractor,
        "left_side_setback": SetbackFloorsExtractor,
        "right_side_setback": SetbackFloorsExtractor,
        
        # Staircase dimensions
        "staircase": StaircaseExtractor,
        "staircase_riser": StaircaseExtractor,
        "staircase_tread": StaircaseExtractor,
        "staircase_width": StaircaseExtractor,
        
        # Height, Kitchen, and Bathroom extractions
        "bathroom": HeightKitchenBathroomExtractor,
        "water_closet": HeightKitchenBathroomExtractor,
        "combined_bath_wc": HeightKitchenBathroomExtractor,
        "kitchen_only": HeightKitchenBathroomExtractor,
        "kitchen_with_separate_dining": HeightKitchenBathroomExtractor,
        "kitchen_with_separate_store": HeightKitchenBathroomExtractor,
        "kitchen_with_dining": HeightKitchenBathroomExtractor,
        "plinth_height": HeightKitchenBathroomExtractor,
        "building_height": HeightKitchenBathroomExtractor,
        "height_plinth": HeightKitchenBathroomExtractor,
        
        # Old variables that are still supported through the new extractor
        "kitchen": HeightKitchenBathroomExtractor,
        "lobby": None,  # Not supported by HeightKitchenBathroomExtractor
        "dining": None,  # Not supported by HeightKitchenBathroomExtractor
        "riser_treader_width": None,
        "floor_count": None
    }
    return extractor_dict.get(variable)

def get_image_for_var(map_image, boxs, variable):
    """Returns the appropriate image for extraction (whole image for new extractors)"""
    # New extractors process the whole image, no cropping needed
    return map_image

def get_examples_for_var(variable):
    """Returns empty examples list as new extractors don't use examples"""
    # New extractors don't use example-based learning
    return []

def get_prompt_for_var(variable):
    """Returns the appropriate prompt file content for extracting the given variable (NEW SYSTEM)"""
    # Get parent directory path (map_approval_codebase1)
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    
    var_prompt_dict = {
        # Area extractions use area.prompt
        "total_plot_area": "src/prompts_new/area.prompt",
        "ground_covered_area": "src/prompts_new/area.prompt",
        "total_covered_area": "src/prompts_new/area.prompt",
        "far": "src/prompts_new/area.prompt",
        "plot_area_far": "src/prompts_new/area.prompt",
        
        # Room extractions use room.prompt
        "bedroom": "src/prompts_new/room.prompt",
        "drawingroom": "src/prompts_new/room.prompt",
        "studyroom": "src/prompts_new/room.prompt",
        "store": "src/prompts_new/room.prompt",
        
        # Setback and floors use setback_floors.prompt
        "setback": "src/prompts_new/setback_floors.prompt",
        "floors": "src/prompts_new/setback_floors.prompt",
        "no_of_floors": "src/prompts_new/setback_floors.prompt",
        "front_setback": "src/prompts_new/setback_floors.prompt",
        "rear_setback": "src/prompts_new/setback_floors.prompt",
        "left_side_setback": "src/prompts_new/setback_floors.prompt",
        "right_side_setback": "src/prompts_new/setback_floors.prompt",
        
        # Staircase dimensions use staircase.prompt
        "staircase": "src/prompts_new/staircase.prompt",
        "staircase_riser": "src/prompts_new/staircase.prompt",
        "staircase_tread": "src/prompts_new/staircase.prompt",
        "staircase_width": "src/prompts_new/staircase.prompt",
        
        # Height, Kitchen, and Bathroom extractions use height_kitchen_bathroom.prompt
        "bathroom": "src/prompts_new/height_kitchen_bathroom.prompt",
        "water_closet": "src/prompts_new/height_kitchen_bathroom.prompt",
        "combined_bath_wc": "src/prompts_new/height_kitchen_bathroom.prompt",
        "kitchen_only": "src/prompts_new/height_kitchen_bathroom.prompt",
        "kitchen_with_separate_dining": "src/prompts_new/height_kitchen_bathroom.prompt",
        "kitchen_with_separate_store": "src/prompts_new/height_kitchen_bathroom.prompt",
        "kitchen_with_dining": "src/prompts_new/height_kitchen_bathroom.prompt",
        "plinth_height": "src/prompts_new/height_kitchen_bathroom.prompt",
        "building_height": "src/prompts_new/height_kitchen_bathroom.prompt",
        "height_plinth": "src/prompts_new/height_kitchen_bathroom.prompt",
        "kitchen": "src/prompts_new/height_kitchen_bathroom.prompt"
    }
    
    prompt_file = var_prompt_dict.get(variable)
    print(f"DEBUG: Looking for prompt for variable '{variable}', found file: {prompt_file}")
    if prompt_file:
        try:
            # Construct full path to prompt file in parent directory
            full_prompt_path = os.path.join(parent_dir, prompt_file)
            print(f"DEBUG: Trying to read prompt from: {full_prompt_path}")
            with open(full_prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Extract the actual prompt text from the system_prompt structure
                # Look for the "text": """ content
                import re
                text_match = re.search(r'"text":\s*"""(.*?)"""', content, re.DOTALL)
                if text_match:
                    extracted_text = text_match.group(1).strip()
                    print(f"DEBUG: Successfully extracted prompt text, length: {len(extracted_text)} chars")
                    # Write debug info to file so we can see it
                    with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                        debug_file.write(f"\n=== PROMPT FOR {variable} ===\n")
                        debug_file.write(f"Extracted text length: {len(extracted_text)}\n")
                        debug_file.write(f"Preview: {extracted_text[:200]}...\n")
                    return extracted_text
                else:
                    print(f"DEBUG: Could not extract text from system_prompt structure")
                    print(f"DEBUG: Raw content preview: {content[:200]}...")
                    return content
        except FileNotFoundError:
            print(f"Warning: {prompt_file} not found in {parent_dir}")
    else:
        print(f"DEBUG: No prompt file mapping found for variable '{variable}'")
    return ""