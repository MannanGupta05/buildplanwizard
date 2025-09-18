# This is the top level file which is going to contain rule_verifier and Extractor functionalities. 
# It also defines relative paths for example folders, prompts

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append('yolov8_segments')

import config_map as config
from PIL import Image
from pdf2image import convert_from_path
from remove_zeros import SeamCarver
from yolo_inference import YoloInference

# Import all example modules
import bedroom_drawingroom_examples
import studyroom_examples
import store_examples
import bathroom_examples
import kitchen_examples
import plot_cov_area_far_examples
import lobby_dining_examples
import riser_treader_width_examples_class4
import riser_treader_width_examples_class5
import height_plinth_examples

# Import all extraction modules
from bedroom_drawingroom_extraction import BDE
from store_extraction import StoreExtractor
from bathroom_extraction import BathroomExtractor
from kitchen_extraction import KitchenExtractor
from plot_cov_area_far_extraction import PlotAreaExtractor
from lobby_dining_extraction import LobbyDiningExtractor
from riser_treader_width_extraction import RiserTreaderWidthExtractor
from height_plinth_extraction import HeightPlinthExtractor
from studyroom_extraction import StudyRoomExtractor

import utils

# Import rule_verifier from separate file
from rule_verifier import rule_verifier

def read_pdf(file_path):
    """Convert PDF to image and return the first page"""
    try:
        poppler_path = r"C:\Users\Mannan Gupta\Desktop\llm-map-approval-website_integration_new_rules\map_approval_codebase1\poppler-24.08.0\Library\bin"
        images = convert_from_path(file_path, dpi=300, poppler_path=poppler_path)
        if not images:
            raise Exception("Failed to convert PDF to image")
        return images[0]
    except Exception as e:
        raise Exception(f"PDF conversion failed: {str(e)}")

def create_segments(input_map_image, model="YOLO"):
    """Process image and create segments using YOLO detection"""
    try:
        # Remove zeros from image
        sc = SeamCarver(input_map_image)
        processed_image = sc.get_seam_carving_cuts(config.ksize, config.num_of_zeros)
        
        # Run YOLO object detection
        yolo = YoloInference(os.path.join(config.MAIN_PATH, config.YOLO_MODEL_PATH), config.BOX_CONF)
        boxs = yolo.detect_yolo_objects(processed_image)
        
        return processed_image, boxs
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
            # Encode examples
            encoded_examples = []
            for e in self.examples:
                encoded = {"base64": utils.encode_image(e["path"])}
                # Add all other fields from the example
                for key, value in e.items():
                    if key != "path":
                        encoded[key] = value
                encoded_examples.append(encoded)
            
            # Run extraction
            self.result = self.extractor.extraction(self.image, self.prompt, encoded_examples, self.model)
            return self.result
        except Exception as e:
            print(f"Extraction error: {e}")
            self.result = []
            return self.result

def get_extractor_func(variable):
    """Returns the appropriate extractor class for the given variable"""
    extractor_dict = {
        "bedroom": BDE,
        "drawingroom": BDE,
        "studyroom": StudyRoomExtractor,
        "store": StoreExtractor,
        "bathroom": BathroomExtractor,
        "water_closet": BathroomExtractor,
        "combined_bath_wc": BathroomExtractor,
        "kitchen": KitchenExtractor,
        "plot_area_far": PlotAreaExtractor,
        "lobby": LobbyDiningExtractor,
        "dining": LobbyDiningExtractor,
        "riser_treader_width": RiserTreaderWidthExtractor,
        "height_plinth": HeightPlinthExtractor
    }
    return extractor_dict.get(variable)

def get_image_for_var(map_image, boxs, variable):
    """Returns the appropriate image for extraction based on variable type"""
    # Variable-specific box extraction mapping
    variable_box_mapping = {
        "bedroom": ["room", "bedroom"],
        "drawingroom": ["room", "drawing_room", "living_room"],
        "studyroom": ["room", "study"],
        "store": ["room", "store"],
        "bathroom": ["bathroom", "toilet"],
        "water_closet": ["toilet", "wc"],
        "combined_bath_wc": ["bathroom", "toilet"],
        "kitchen": ["kitchen"],
        "plot_area_far": ["plot", "boundary"],
        "lobby": ["lobby", "hall"],
        "dining": ["dining", "room"],
        "riser_treader_width": ["stair", "staircase"],
        "height_plinth": ["elevation", "section"]
    }
    
    # For now, return the processed image as is
    # Future enhancement: Filter boxes based on variable_box_mapping
    # and crop relevant regions from the image
    
    relevant_classes = variable_box_mapping.get(variable, [])
    if relevant_classes and boxs:
        # TODO: Implement actual box filtering and cropping
        # For now, just return the original image
        pass
    
    return map_image

class Examples:
    """Centralized examples management class"""
    
    def __init__(self, image_path):
        self.image_path = image_path
        self._examples_dict = {
            "bedroom": bedroom_drawingroom_examples.examples,
            "drawingroom": bedroom_drawingroom_examples.examples,
            "studyroom": studyroom_examples.examples,
            "store": store_examples.examples,
            "bathroom": bathroom_examples.examples,
            "water_closet": bathroom_examples.examples,
            "combined_bath_wc": bathroom_examples.examples,
            "kitchen": kitchen_examples.examples,
            "plot_area_far": plot_cov_area_far_examples.examples,
            "lobby": lobby_dining_examples.examples,
            "dining": lobby_dining_examples.examples,
            "riser_treader_width": riser_treader_width_examples_class4.examples,
            "height_plinth": height_plinth_examples.examples
        }
    
    @property
    def bedroom(self):
        return self._examples_dict["bedroom"](self.image_path)
    
    @property
    def drawingroom(self):
        return self._examples_dict["drawingroom"](self.image_path)
    
    @property
    def studyroom(self):
        return self._examples_dict["studyroom"](self.image_path)
    
    @property
    def store(self):
        return self._examples_dict["store"](self.image_path)
    
    @property
    def bathroom(self):
        return self._examples_dict["bathroom"](self.image_path)
    
    @property
    def water_closet(self):
        return self._examples_dict["water_closet"](self.image_path)
    
    @property
    def combined_bath_wc(self):
        return self._examples_dict["combined_bath_wc"](self.image_path)
    
    @property
    def kitchen(self):
        return self._examples_dict["kitchen"](self.image_path)
    
    @property
    def plot_area_far(self):
        return self._examples_dict["plot_area_far"](self.image_path)
    
    @property
    def lobby(self):
        return self._examples_dict["lobby"](self.image_path)
    
    @property
    def dining(self):
        return self._examples_dict["dining"](self.image_path)
    
    @property
    def riser_treader_width(self):
        return self._examples_dict["riser_treader_width"](self.image_path)
    
    @property
    def height_plinth(self):
        return self._examples_dict["height_plinth"](self.image_path)
    
    def get_examples(self, variable):
        """Get examples for a specific variable"""
        return getattr(self, variable, [])

# Global examples instance
examples = Examples(config.image_path)

def get_examples_for_var(variable):
    """Returns the appropriate examples for the given variable using Examples class"""
    return examples.get_examples(variable)

def get_prompt_for_var(variable):
    """Returns the appropriate prompt file content for extracting the given variable"""
    # Get parent directory path (map_approval_codebase1)
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    
    var_prompt_dict = {
        "bedroom": config.bedroom_drawingroom_promptfile,
        "drawingroom": config.bedroom_drawingroom_promptfile,
        "studyroom": config.studyroom_promptfile,
        "store": config.store_promptfile,
        "bathroom": config.bathroom_promptfile,
        "water_closet": config.bathroom_promptfile,
        "combined_bath_wc": config.bathroom_promptfile,
        "kitchen": config.kitchen_promptfile,
        "plot_area_far": config.plot_cov_area_far_promptfile,
        "lobby": config.lobby_dining_promptfile,
        "dining": config.lobby_dining_promptfile,
        "riser_treader_width": 'riser_treader_width_class4.prompt',
        "height_plinth": config.height_plinth_promptfile
    }
    
    prompt_file = var_prompt_dict.get(variable)
    if prompt_file:
        try:
            # Construct full path to prompt file in parent directory
            full_prompt_path = os.path.join(parent_dir, prompt_file)
            with open(full_prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Warning: {prompt_file} not found in {parent_dir}")
    return ""