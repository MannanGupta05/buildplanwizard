import json
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class RiserTreaderWidthExtractor(BaseExtractor):
    
    def extraction(self, image, *args):
        """
        Custom extraction method for riser/treader/width that handles dual prompts and class IDs.
        This overrides the base extraction method due to unique requirements.
        
        Supports both calling conventions:
        1. Legacy: extraction(image, prompt_class4, examples_class4, prompt_class5, examples_class5, model)
        2. Standard: extraction(image, prompt, examples, model) - uses class4 prompt for compatibility
        """
        if len(args) == 5:
            # Legacy calling convention: (prompt_class4, examples_class4, prompt_class5, examples_class5, model)
            prompt_class4, examples_class4, prompt_class5, examples_class5, model = args
        elif len(args) == 3:
            # Standard calling convention: (prompt, examples, model) - use as class4
            prompt_class4, examples_class4, model = args
            # For standard calls, use empty class5 data (no class 5 processing)
            prompt_class5, examples_class5 = "", []
        else:
            raise ValueError(f"Invalid number of arguments for extraction: expected 3 or 5, got {len(args)}")
        output_list = []

        for box in self.boxs:
            if box['class_id'] == 4:
                prompt = prompt_class4
                examples = examples_class4
                floor_key = True
                query_text = "Give staircase_width, staircase_tread, staircase_riser, and floor as JSON"
            elif box['class_id'] == 5:
                prompt = prompt_class5
                examples = examples_class5
                floor_key = False
                query_text = "Give staircase_width, staircase_tread, staircase_riser as JSON"
            else:
                continue
                
            cropped_img = self.crop_image_from_box(image, box)
            
            # Build messages with class-specific examples
            messages = [{"role": "user", "parts": [{"text": prompt}]}]
            
            for ex in examples:
                messages.append({
                    "role": "user",
                    "parts": [
                        {"mime_type": "image/jpeg", "data": ex["base64"]},
                        {"text": query_text}
                    ]
                })
                model_parts = {
                    "staircase_width": ex.get("staircase_width", ["absent"]),
                    "staircase_tread": ex.get("staircase_tread", ["absent"]),
                    "staircase_riser": ex.get("staircase_riser", ["absent"])
                }
                if floor_key:
                    model_parts["floor"] = ex.get("floor", ["absent"])
                messages.append({
                    "role": "model",
                    "parts": [{"text": json.dumps(model_parts)}]
                })
                
            messages.append({
                "role": "user",
                "parts": [cropped_img, {"text": query_text}]
            })
            
            response = model.generate_content(messages)
            data_dict = self.parse_gemini_response(response.text)
            
            # Ensure all keys exist
            result = {
                "staircase_width": data_dict.get("staircase_width", ["absent"]),
                "staircase_tread": data_dict.get("staircase_tread", ["absent"]),
                "staircase_riser": data_dict.get("staircase_riser", ["absent"])
            }
            if floor_key:
                result["floor"] = data_dict.get("floor", ["absent"])
            output_list.append(result)
            
        return output_list
    
    # These methods are required by the base class but not used due to custom extraction
    def _format_example_output(self, example):
        """Not used due to custom extraction method."""
        pass
    
    def _get_target_class_ids(self):
        """Not used due to custom extraction method."""
        return [4, 5]
    
    def _get_query_text(self):
        """Not used due to custom extraction method."""
        pass
    
    def _process_extracted_data(self, data_dict):
        """Not used due to custom extraction method."""
        pass
    
    def _format_final_output(self, results):
        """Not used due to custom extraction method."""
        pass
