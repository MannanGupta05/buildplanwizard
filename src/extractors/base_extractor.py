"""
Base extractor class for architectural plan extraction.
Provides common functionality for all extractor implementations.
"""

import json
import re
from PIL import Image
from io import BytesIO


class BaseExtractor:
    """
    Base class for all extractors in the architectural plan analysis system.
    Provides common extraction workflow and methods that can be overridden.
    """
    
    def __init__(self, boxs):
        """
        Initialize the base extractor.
        
        Args:
            boxs: List of bounding boxes from YOLO detection (empty list for whole-image extractors)
        """
        self.boxs = boxs
    
    def extraction(self, image, prompt, examples, model):
        """
        Main extraction method that orchestrates the extraction process.
        
        Args:
            image: PIL Image object containing the architectural plan
            prompt: String prompt for the AI model
            examples: List of example data (empty for new extractors)
            model: AI model instance (Gemini)
            
        Returns:
            dict: Extracted data in the format expected by the system
        """
        try:
            # Get the class IDs that this extractor should process
            target_class_ids = self._get_target_class_ids()
            
            # For new extractors that process whole images, target_class_ids will be -1
            if target_class_ids == -1:
                # Process whole image
                processed_image = image
            else:
                # For legacy extractors that use YOLO crops (not used by new extractors)
                processed_image = self._get_relevant_image_region(image, target_class_ids)
            
            # Generate query text for extraction
            query_text = self._get_query_text()
            
            # Call the AI model for extraction
            response = self._call_ai_model(processed_image, prompt, model)
            
            # Process the raw response
            processed_data = self._process_extracted_data(response)
            
            # Format final output
            final_output = self._format_final_output([processed_data])
            
            return final_output
            
        except Exception as e:
            print(f"Extraction error in {self.__class__.__name__}: {str(e)}")
            # Return default/empty structure on error
            return self._get_default_output()
    
    def _call_ai_model(self, image, prompt, model):
        """
        Call the AI model with the image and prompt.
        
        Args:
            image: PIL Image to process
            prompt: Prompt string for the model
            model: AI model instance
            
        Returns:
            dict: Parsed JSON response from the model
        """
        try:
            # Convert PIL image to bytes for model input
            image_bytes = BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            
            # Prepare the content for the model
            content = [
                prompt,
                image  # Pass PIL image directly - Gemini can handle it
            ]
            
            # Generate response using the model
            response = model.generate_content(content)
            response_text = response.text
            
            # Try to extract JSON from the response
            json_response = self._extract_json_from_response(response_text)
            
            return json_response
            
        except Exception as e:
            print(f"AI model call error: {str(e)}")
            return {}
    
    def _extract_json_from_response(self, response_text):
        """
        Extract JSON from the AI model response text.
        
        Args:
            response_text: Raw text response from AI model
            
        Returns:
            dict: Parsed JSON data
        """
        try:
            print(f"Raw AI response: {response_text[:200]}...")
            
            # Write AI response to debug file
            try:
                with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                    debug_file.write(f"\n=== AI RESPONSE ===\n")
                    debug_file.write(f"Response: {response_text[:500]}...\n")
            except:
                pass
            
            # First, try to extract from markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7  # Skip the ```json part
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_str = response_text[json_start:json_end].strip()
                    print(f"Extracted JSON from markdown: {json_str}")
                    parsed_json = json.loads(json_str)
                    return parsed_json
            
            # If no markdown blocks, try to find JSON in the response - look for both objects {} and arrays []
            json_start_obj = response_text.find('{')
            json_end_obj = response_text.rfind('}') + 1
            
            json_start_arr = response_text.find('[')
            json_end_arr = response_text.rfind(']') + 1
            
            # Prefer array format if found, otherwise use object format
            if json_start_arr != -1 and json_end_arr > json_start_arr:
                json_str = response_text[json_start_arr:json_end_arr]
                print(f"Extracted JSON array: {json_str}")
                return json.loads(json_str)
            elif json_start_obj != -1 and json_end_obj > json_start_obj:
                json_str = response_text[json_start_obj:json_end_obj]
                print(f"Extracted JSON object: {json_str}")
                return json.loads(json_str)
            else:
                # If no JSON brackets found, try to parse the whole response
                print("No JSON brackets found, trying to parse whole response")
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Raw response: {response_text[:500]}...")
            return {}
    
    def _get_relevant_image_region(self, image, class_ids):
        """
        Extract relevant region from image based on class IDs (for legacy extractors).
        New extractors return the whole image.
        """
        # For new extractors, just return the whole image
        return image
    
    def _get_default_output(self):
        """
        Return default/empty output structure for error cases.
        Should be overridden by subclasses.
        """
        return {}
    
    # Abstract methods that should be implemented by subclasses
    def _format_example_output(self, example):
        """
        Format example output for the extractor.
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _format_example_output")
    
    def _get_target_class_ids(self):
        """
        Return the class IDs that this extractor should process.
        Return -1 for whole-image extractors.
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _get_target_class_ids")
    
    def _get_query_text(self):
        """
        Return query text for extraction.
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _get_query_text")
    
    def _process_extracted_data(self, data_dict):
        """
        Process extracted data from the AI model response.
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _process_extracted_data")
    
    def _format_final_output(self, results):
        """
        Format final output for the extractor.
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _format_final_output")