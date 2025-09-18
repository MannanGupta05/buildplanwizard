import json
import re
from PIL import Image
from io import BytesIO
import utils

class BathroomExtractor:
    def __init__(self, boxs):
        self.boxs = boxs
        
    def extraction(self, image, system_prompt, encoded_examples, model):   
        data_dict = {}
        bathroom_list = []
        water_closet_list = []
        combined_bath_wc_list = []
        floor_list = []
        
        for box in self.boxs:
            if box['class_id'] == 4:  # Only consider relevant boxes
                x1, y1, x2, y2 = box['bbox']
                cropped_img = image.crop((x1, y1, x2, y2))
                
                # Build Gemini Prompt
                messages = [{"role": "user", "parts": [{"text": system_prompt}]}]

                # Add few-shot examples
                for ex in encoded_examples:
                    messages.append({
                        "role": "user",
                        "parts": [
                            {"mime_type": "image/jpeg", "data": ex["base64"]},
                            {"text": "Give bathroom categories and floor as JSON"}
                        ]
                    })
                    messages.append({
                        "role": "model",
                        "parts": [
                            {"text": json.dumps({
                                "Bathroom": ex["Bathroom"],
                                "Water Closet (W.C.)": ex["Water Closet (W.C.)"],
                                "Combined Bath and W.C.": ex["Combined Bath and W.C."],
                                "floor": ex["floor"]
                            })}
                        ]
                    })

                # Final user query with actual image
                messages.append({
                    "role": "user",
                    "parts": [
                        cropped_img,
                        {"text": "Give bathroom categories and floor as JSON"}
                    ]
                })

                # Gemini inference
                response = model.generate_content(messages)
                output = response.text

                print("Gemini raw output:\n", output)

                json_str = re.sub(r"^```json\s*|```$", "", output.strip(), flags=re.DOTALL)

                try:
                    data_dict = json.loads(json_str)
                except:
                    data_dict = json.loads(utils.escape_inches(json_str))

                # Extract all three categories
                bathroom = data_dict.get('Bathroom', ["absent"])
                water_closet = data_dict.get('Water Closet (W.C.)', ["absent"])
                combined_bath_wc = data_dict.get('Combined Bath and W.C.', ["absent"])
                floor = data_dict.get('floor', ["absent"])
                
                # Handle floor extraction
                if isinstance(floor, list) and len(floor) > 0:
                    floor = floor[0]

                bathroom_list.append(bathroom)
                water_closet_list.append(water_closet)
                combined_bath_wc_list.append(combined_bath_wc)
                floor_list.append(floor)

        # Final structured output with all categories
        final_output = []
        for i in range(len(bathroom_list)):
            # Create the same format as other room types: (dimensions, floor)
            bathroom_data = (bathroom_list[i], floor_list[i])
            water_closet_data = (water_closet_list[i], floor_list[i])
            combined_data = (combined_bath_wc_list[i], floor_list[i])
            
            final_output.append({
                'Bathroom': bathroom_data,
                'Water Closet (W.C.)': water_closet_data,
                'Combined Bath and W.C.': combined_data
            })

        return final_output
