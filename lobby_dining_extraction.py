import utils
import numpy as np
from PIL import Image
import json
from io import BytesIO
import re

class LobbyDiningExtractor:
    def __init__(self, boxs):
        self.boxs = boxs
        
    def extraction(self, image, system_prompt, encoded_examples, model):   
        data_dict = {}
        lobby_list = []
        dining_list = []
        floor_list = []

        for box in self.boxs:
            if box['class_id'] == 4:            
                x1, y1, x2, y2 = box['bbox']
                cropped_img = image.crop((x1, y1, x2, y2))
                
                # Build messages as in other extractors
                messages = [{"role": "user", "parts": [{"text": system_prompt}]}]

                for ex in encoded_examples:
                    messages.append({
                        "role": "user",
                        "parts": [
                            {"mime_type": "image/jpeg", "data": ex["base64"]},
                            {"text": "Give lobby, dining, and floor as JSON"}
                        ]
                    })
                    messages.append({
                        "role": "model",
                        "parts": [
                            {"text": json.dumps({
                                "lobby": ex["lobby"],
                                "dining": ex["dining"],
                                "floor": ex["floor"]
                            })}
                        ]
                    })

                # Encode cropped image as base64
                buffer = BytesIO()
                cropped_img.save(buffer, format="JPEG")
                buffer.seek(0)
                image_bytes = buffer.getvalue()
                test_img = utils.encode_image(image_bytes)

                messages.append({
                    "role": "user",
                    "parts": [
                        {"mime_type": "image/jpeg", "data": test_img},
                        {"text": "Give lobby, dining, and floor as JSON"}
                    ]
                })

                response = model.generate_content(messages)
                output = response.text

                print("Gemini raw output:\n", output)

                json_str = re.sub(r"^```json\s*|```$", "", output.strip(), flags=re.DOTALL)

                try:
                    data_dict = json.loads(json_str)
                except:
                    data_dict = json.loads(utils.escape_inches(json_str))

                lobby = data_dict.get('lobby', None)
                dining = data_dict.get('dining', None)
                floor = data_dict.get('floor', None)

                lobby_list.append(lobby)
                dining_list.append(dining)
                floor_list.append(floor)
        
        temp = []
        for i, lob in enumerate(lobby_list):
            temp.append((lob, floor_list[i]))

        temp1 = []
        for i, din in enumerate(dining_list):
            temp1.append((din, floor_list[i]))

        return temp, temp1
