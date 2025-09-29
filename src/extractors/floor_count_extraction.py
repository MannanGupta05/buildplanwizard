import json
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class FloorCountExtractor(BaseExtractor):
    """
    Extractor for counting the number of floors from architectural plans.
    Uses class0 images (legends) and a specialized prompt without examples.
    """
    
    def _format_example_output(self, example):
        """Not used for floor count extraction as it doesn't use examples."""
        pass
    
    def _get_target_class_ids(self):
        """Floor count extraction targets class_id 0 (legends)."""
        return [0]
    
    def _get_query_text(self):
        """Query text for floor count extraction."""
        return "Analyze the legend table and provide floor count as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for floor count."""
        floor_count = data_dict.get('floor_count', 0)
        
        # Ensure the value is an integer and wrap in list format for validation compatibility
        try:
            if isinstance(floor_count, str):
                floor_count = int(floor_count)
            elif isinstance(floor_count, list) and len(floor_count) > 0:
                floor_count = int(floor_count[0])
            else:
                floor_count = int(floor_count) if floor_count else 0
        except (ValueError, TypeError):
            floor_count = 0
        
        return {"floor_count": [floor_count]}
    
    def _format_final_output(self, results):
        """Format final output for floor count extraction."""
        return results  # Results are already in correct dict format
    
    def extraction(self, image, system_prompt, encoded_examples, model):
        """
        Custom extraction method for floor count that doesn't use examples.
        Overrides base class method since we don't need examples for this extraction.
        """
        target_boxes = self.filter_boxes_by_class(self._get_target_class_ids())
        results = []
        
        for box in target_boxes:
            cropped_img = self.crop_image_from_box(image, box)
            
            # Build simple message without examples
            messages = [
                {"role": "user", "parts": [{"text": system_prompt}]},
                {
                    "role": "user",
                    "parts": [
                        cropped_img,
                        {"text": self._get_query_text()}
                    ]
                }
            ]
            
            # Get Gemini response
            response = model.generate_content(messages)
            data_dict = self.parse_gemini_response(response.text)
            
            # Process data according to subclass implementation
            processed_data = self._process_extracted_data(data_dict)
            results.append(processed_data)
        
        return self._format_final_output(results)