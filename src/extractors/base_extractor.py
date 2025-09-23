"""
Base extractor class that defines common functionality for all room/feature extractors.

This module provides the BaseExtractor superclass that handles common operations
like image cropping, message building, JSON parsing, and Gemini model interaction.
All specific extractors should inherit from this class.
"""

import json
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
from io import BytesIO
import sys
import os

# Import utils using relative import
from ..core import utils


class BaseExtractor(ABC):
    """
    Abstract base class for all feature extractors.
    
    Provides common functionality for:
    - Box filtering by class_id
    - Image cropping from bounding boxes
    - Building Gemini API messages with examples
    - JSON parsing and error handling
    - Standard extraction workflow
    """
    
    def __init__(self, boxs: List[Dict[str, Any]]):
        """
        Initialize the extractor with detected bounding boxes.
        
        Args:
            boxs: List of bounding box dictionaries with 'bbox' and 'class_id' keys
        """
        self.boxs = boxs
    
    def filter_boxes_by_class(self, class_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Filter bounding boxes by class ID(s).
        
        Args:
            class_ids: List of class IDs to filter by
            
        Returns:
            List of filtered bounding box dictionaries
        """
        return [box for box in self.boxs if box['class_id'] in class_ids]
    
    def crop_image_from_box(self, image: Image.Image, box: Dict[str, Any]) -> Image.Image:
        """
        Crop image using bounding box coordinates.
        
        Args:
            image: PIL Image to crop
            box: Bounding box dictionary with 'bbox' key containing [x1, y1, x2, y2]
            
        Returns:
            Cropped PIL Image
        """
        x1, y1, x2, y2 = box['bbox']
        return image.crop((x1, y1, x2, y2))
    
    def build_messages(self, system_prompt: str, encoded_examples: List[Dict[str, Any]], 
                      cropped_img: Image.Image, query_text: str) -> List[Dict[str, Any]]:
        """
        Build standardized message structure for Gemini API.
        
        Args:
            system_prompt: System prompt text
            encoded_examples: List of example dictionaries with base64 images
            cropped_img: Cropped PIL Image for inference
            query_text: Text query for the model
            
        Returns:
            List of message dictionaries for Gemini API
        """
        messages = [{"role": "user", "parts": [{"text": system_prompt}]}]
        
        # Add few-shot examples
        for ex in encoded_examples:
            # User message with example image
            messages.append({
                "role": "user",
                "parts": [
                    {"mime_type": "image/jpeg", "data": ex["base64"]},
                    {"text": query_text}
                ]
            })
            
            # Model response with example output
            example_output = self._format_example_output(ex)
            messages.append({
                "role": "model",
                "parts": [{"text": json.dumps(example_output)}]
            })
        
        # Final user query with actual image
        messages.append({
            "role": "user",
            "parts": [
                cropped_img,
                {"text": query_text}
            ]
        })
        
        return messages
    
    def parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini response text to extract JSON data.
        
        Args:
            response_text: Raw response text from Gemini model
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            json.JSONDecodeError: If JSON parsing fails
        """
        print("Gemini raw output:\n", response_text)
        
        # Remove markdown code block markers
        json_str = re.sub(r"^```json\s*|```$", "", response_text.strip(), flags=re.DOTALL)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback: try escaping inches/quotes
            return json.loads(utils.escape_inches(json_str))
    
    def process_floor_value(self, floor_value: Any) -> Any:
        """
        Standardize floor value processing.
        
        Args:
            floor_value: Floor value from parsed JSON (could be list or single value)
            
        Returns:
            Processed floor value (extracts first element if list)
        """
        if isinstance(floor_value, list) and len(floor_value) > 0:
            return floor_value[0]
        return floor_value
    
    @abstractmethod
    def _format_example_output(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format example dictionary for model training.
        Each subclass must implement this to define which fields to include.
        
        Args:
            example: Example dictionary with all available fields
            
        Returns:
            Formatted dictionary for model response
        """
        pass
    
    @abstractmethod
    def _get_target_class_ids(self) -> List[int]:
        """
        Return the class IDs this extractor should process.
        
        Returns:
            List of class IDs to filter by
        """
        pass
    
    @abstractmethod
    def _get_query_text(self) -> str:
        """
        Return the query text to use for this extractor.
        
        Returns:
            Query string for Gemini API
        """
        pass
    
    @abstractmethod
    def _process_extracted_data(self, data_dict: Dict[str, Any]) -> Any:
        """
        Process the extracted data dictionary into the final output format.
        Each subclass defines its own output structure.
        
        Args:
            data_dict: Parsed JSON dictionary from Gemini response
            
        Returns:
            Processed data in the format expected by this extractor
        """
        pass
    
    def extraction(self, image: Image.Image, system_prompt: str, 
                  encoded_examples: List[Dict[str, Any]], model) -> Any:
        """
        Standard extraction workflow that can be used by most extractors.
        
        Args:
            image: PIL Image to process
            system_prompt: System prompt for the model
            encoded_examples: List of example dictionaries
            model: Gemini model instance
            
        Returns:
            Extracted data in format defined by subclass
        """
        target_boxes = self.filter_boxes_by_class(self._get_target_class_ids())
        results = []
        
        for box in target_boxes:
            cropped_img = self.crop_image_from_box(image, box)
            messages = self.build_messages(system_prompt, encoded_examples, 
                                         cropped_img, self._get_query_text())
            
            # Get Gemini response
            response = model.generate_content(messages)
            data_dict = self.parse_gemini_response(response.text)
            
            # Process data according to subclass implementation
            processed_data = self._process_extracted_data(data_dict)
            results.append(processed_data)
        
        return self._format_final_output(results)
    
    @abstractmethod
    def _format_final_output(self, results: List[Any]) -> Any:
        """
        Format the list of processed results into final output format.
        
        Args:
            results: List of processed data from each bounding box
            
        Returns:
            Final output in the format expected by the caller
        """
        pass