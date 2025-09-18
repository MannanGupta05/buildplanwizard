import json
import re
from PIL import Image
from io import BytesIO
import utils

class RiserTreaderWidthExtractor:
    def __init__(self, boxs):
        self.boxs = boxs

    def extraction(self, image, prompt_class4, examples_class4, prompt_class5, examples_class5, model):
        data_dict = {}
        output_list = []

        for box in self.boxs:
            if box['class_id'] == 4:
                prompt = prompt_class4
                examples = examples_class4
                floor_key = True
            elif box['class_id'] == 5:
                prompt = prompt_class5
                examples = examples_class5
                floor_key = False
            else:
                continue
            x1, y1, x2, y2 = box['bbox']
            cropped_img = image.crop((x1, y1, x2, y2))
            messages = [{"role": "user", "parts": [{"text": prompt}]}]
            for ex in examples:
                messages.append({
                    "role": "user",
                    "parts": [
                        {"mime_type": "image/jpeg", "data": ex["base64"]},
                        {"text": "Give staircase_width, staircase_tread, staircase_riser{} as JSON".format(', and floor' if floor_key else '')}
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
                    "parts": [
                        {"text": json.dumps(model_parts)}
                    ]
                })
            messages.append({
                "role": "user",
                "parts": [
                    cropped_img,
                    {"text": "Give staircase_width, staircase_tread, staircase_riser{} as JSON".format(', and floor' if floor_key else '')}
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
