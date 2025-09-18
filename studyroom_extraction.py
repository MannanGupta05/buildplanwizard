import json  
import re
from PIL import Image
from io import BytesIO
import utils

class StudyRoomExtractor:
    def __init__(self, boxs):
        self.boxs = boxs
        
    def extraction(self, image, system_prompt, encoded_examples, model):   
        data_dict = {}
        study_list = []
        floor_list = []
        
        for box in self.boxs:
            if box['class_id'] == 4:  # Only consider relevant boxes (same as kitchen class)
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
                            {"text": "Give study and floor as JSON"}
                        ]
                    })
                    messages.append({
                        "role": "model",
                        "parts": [
                            {"text": json.dumps({
                                "study": ex["study"],
                                "floor": ex["floor"]
                            })}
                        ]
                    })

                # Final user query with actual image
                messages.append({
                    "role": "user",
                    "parts": [
                        cropped_img,
                        {"text": "Give study and floor as JSON"}
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

                study = data_dict.get('study', None)
                floor = data_dict.get('floor', None)
                if isinstance(floor, list) and len(floor) > 0:
                    floor = floor[0]

                study_list.append(study)
                floor_list.append(floor)

        # Final structured output
        final_output = []
        for i, study in enumerate(study_list):
            final_output.append((study, floor_list[i]))  # Tuple of (study, floor)

        return final_output
