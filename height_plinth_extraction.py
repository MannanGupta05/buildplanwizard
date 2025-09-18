import json
import re
from PIL import Image
from io import BytesIO
import utils

class HeightPlinthExtractor:
    def __init__(self, boxs):
        self.boxs = boxs
        
    def extraction(self, image, system_prompt, encoded_examples, model):   
        data_dict = {}
        height_list = []
        plinth_list = []
        
        for box in self.boxs:
            if box['class_id'] == 3:  # Only consider relevant boxes
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
                            {"text": "Give height and plinth level as JSON"}
                        ]
                    })
                    messages.append({
                        "role": "model",
                        "parts": [
                            {"text": json.dumps({
                                "height": ex["height"],
                                "plinth level": ex["plinth level"]
                            })}
                        ]
                    })

                # Final user query with actual image
                messages.append({
                    "role": "user",
                    "parts": [
                        cropped_img,
                        {"text": "Give height and plinth level as JSON"}
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

                height = data_dict.get('height', None)
                plinth = data_dict.get('plinth level', None)

                height_list.append(height)
                plinth_list.append(plinth)

        # Final structured output
        final_output = []
        for i, height in enumerate(height_list):
            final_output.append({"height": height_list[i], "plinth level": plinth_list[i]})

        return final_output
