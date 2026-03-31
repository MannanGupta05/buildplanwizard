# This is the top level file which is going to contain rule_verifier and Extractor functionalities. 
# It also defines relative paths for example folders, prompts

import os
import sys
import psutil
import fitz  # PyMuPDF
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.core import config_map as config
from PIL import Image
from pdf2image import convert_from_path

from src.extractors.area_extraction import AreaExtractor
from src.extractors.room_extraction import RoomExtractor
from src.extractors.setback_floors_extraction import SetbackFloorsExtractor
from src.extractors.staircase_extraction import StaircaseExtractor
from src.extractors.height_kitchen_bathroom_extraction import HeightKitchenBathroomExtractor

from src.core import utils

# Import rule_verifier from separate file - handle both relative and absolute imports
try:
    from .rule_verifier import rule_verifier
except ImportError:
    from rule_verifier import rule_verifier


import platform

def print_memory_usage(label=""):
    """Print current process RAM usage in MB for debugging on Render logs."""
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss  # in bytes
    prefix = f"{label} " if label else ""
    print(f"{prefix}Memory usage: {mem / (1024 ** 2):.2f} MB", flush=True)

def read_pdf(file_path):
    """Convert PDF to image and return the first page"""
    try:
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        print_memory_usage("[PDF->Image] Before conversion")

        # Current logic: Use PyMuPDF for lower RAM usage.
        doc = fitz.open(file_path)
        try:
            page = doc.load_page(0)  # first page only

            # Lower resolution for better memory efficiency.
            zoom = 1.5
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            mode = "RGBA" if pix.alpha else "RGB"
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            if mode == "RGBA":
                image = image.convert("RGB")
        finally:
            doc.close()

        # Previous logic (pdf2image) kept for easy rollback.
        # On Windows use bundled poppler
        # if platform.system() == "Windows":
        #     poppler_path = os.path.join(config.MAIN_PATH, "poppler-24.08.0", "Library", "bin")
        #     images = convert_from_path(file_path, dpi=300, poppler_path=poppler_path)
        # else:
        #     # On Linux (Render) poppler is installed in system PATH
        #     images = convert_from_path(file_path, dpi=300)

        # if not images:
        #     raise Exception("Failed to convert PDF to image")

        # image = images[0]

        mem_after = process.memory_info().rss
        print_memory_usage("[PDF->Image] After conversion")
        print(
            f"[PDF->Image] RAM delta: {(mem_after - mem_before) / (1024 ** 2):.2f} MB",
            flush=True,
        )

        return image

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
        "total_plot_area": "src/prompts/area.prompt",
        "ground_covered_area": "src/prompts/area.prompt",
        "total_covered_area": "src/prompts/area.prompt",
        "far": "src/prompts/area.prompt",
        "plot_area_far": "src/prompts/area.prompt",
        
        # Room extractions use room.prompt
        "bedroom": "src/prompts/room.prompt",
        "drawingroom": "src/prompts/room.prompt",
        "studyroom": "src/prompts/room.prompt",
        "store": "src/prompts/room.prompt",
        
        # Setback and floors use setback_floors.prompt
        "setback": "src/prompts/setback_floors.prompt",
        "floors": "src/prompts/setback_floors.prompt",
        "no_of_floors": "src/prompts/setback_floors.prompt",
        "front_setback": "src/prompts/setback_floors.prompt",
        "rear_setback": "src/prompts/setback_floors.prompt",
        "left_side_setback": "src/prompts/setback_floors.prompt",
        "right_side_setback": "src/prompts/setback_floors.prompt",
        
        # Staircase dimensions use staircase.prompt
        "staircase": "src/prompts/staircase.prompt",
        "staircase_riser": "src/prompts/staircase.prompt",
        "staircase_tread": "src/prompts/staircase.prompt",
        "staircase_width": "src/prompts/staircase.prompt",
        
        # Height, Kitchen, and Bathroom extractions use height_kitchen_bathroom.prompt
        "bathroom": "src/prompts/height_kitchen_bathroom.prompt",
        "water_closet": "src/prompts/height_kitchen_bathroom.prompt",
        "combined_bath_wc": "src/prompts/height_kitchen_bathroom.prompt",
        "kitchen_only": "src/prompts/height_kitchen_bathroom.prompt",
        "kitchen_with_separate_dining": "src/prompts/height_kitchen_bathroom.prompt",
        "kitchen_with_separate_store": "src/prompts/height_kitchen_bathroom.prompt",
        "kitchen_with_dining": "src/prompts/height_kitchen_bathroom.prompt",
        "plinth_height": "src/prompts/height_kitchen_bathroom.prompt",
        "building_height": "src/prompts/height_kitchen_bathroom.prompt",
        "height_plinth": "src/prompts/height_kitchen_bathroom.prompt",
        "kitchen": "src/prompts/height_kitchen_bathroom.prompt"
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