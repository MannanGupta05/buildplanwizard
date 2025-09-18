
import json
import re
from PIL import Image
from io import BytesIO
import utils

class BDE:
    def __init__(self, boxs):
        self.boxs = boxs
        
    def extraction(self, image, system_prompt, encoded_examples, model):   
        data_dict = {}
        bedroom_list = []
        drawing_list = []
        floor_list = []
        
        for box in self.boxs:
            if box['class_id'] == 4:            
                x1, y1, x2, y2 = box['bbox']
                cropped_img = image.crop((x1, y1, x2, y2))
                
                # ✅ Build Messages Properly
                messages = [{"role": "user", "parts": [{"text": system_prompt}]}]

                # ✅ Examples
                for ex in encoded_examples:
                    messages.append({
                        "role": "user",
                        "parts": [
                            {"mime_type": "image/jpeg", "data": ex["base64"]},
                            {"text": "Give bedroom, drawing, and floor as JSON"}
                        ]
                    })
                    messages.append({
                        "role": "model",
                        "parts": [
                            {"text": json.dumps({
                                "bedroom": ex["bedroom"],
                                "drawing": ex["drawing"],
                                "floor": ex["floor"]
                            })}
                        ]
                    })

                # ✅ Actual Image (Direct PIL Image!) 
                messages.append({
                    "role": "user",
                    "parts": [
                        cropped_img,  # ✅ PIL.Image.Image
                        {"text": "Give bedroom, drawing, and floor as JSON"}
                    ]
                })

                # 👇 Final Generation
                response = model.generate_content(messages)
                output = response.text

                # ✅ Parse the JSON
                print("Gemini raw output:\n", output)

                json_str = re.sub(r"^```json\s*|```$", "", output.strip(), flags=re.DOTALL)

                try:
                    data_dict = json.loads(json_str)
                except:
                    data_dict = json.loads(utils.escape_inches(json_str))

                bedroom = data_dict.get('bedroom', None)
                drawing = data_dict.get('drawing', None)
                floor = data_dict.get('floor', None)
                if isinstance(floor, list) and len(floor) > 0:
                    floor = floor[0]

                bedroom_list.append(bedroom)
                drawing_list.append(drawing)
                floor_list.append(floor)

        # ✅ Final Output
        temp = []
        for i, bed in enumerate(bedroom_list):
            temp.append((bed, floor_list[i]))  # ✅ Tuple of (bedroom, floor)

        temp1 = []
        for i, draw in enumerate(drawing_list):
            temp1.append((draw, floor_list[i]))  # ✅

        return temp, temp1

                