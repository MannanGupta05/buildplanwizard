import json
import re
from PIL import Image
from io import BytesIO
import utils

class PlotAreaExtractor:
    def __init__(self, boxs):
        self.boxs = boxs
        
    def extraction(self, image, system_prompt, encoded_examples, model):   
        data_dict = {}
        plot_area_list = []
        covered_area_list = []
        far_list = []
        
        for box in self.boxs:
            if box['class_id'] == 1:  # 🧠 Only consider relevant boxes for area/FAR
                x1, y1, x2, y2 = box['bbox']
                cropped_img = image.crop((x1, y1, x2, y2))
                
                # 🧠 Build Gemini Prompt
                messages = [{"role": "user", "parts": [{"text": system_prompt}]}]

                # 🧪 Add few-shot examples
                for ex in encoded_examples:
                    messages.append({
                        "role": "user",
                        "parts": [
                            {"mime_type": "image/jpeg", "data": ex["base64"]},
                            {"text": "Give total_plot_area, total_covered_area and far as JSON"}
                        ]
                    })
                    messages.append({
                        "role": "model",
                        "parts": [
                            {"text": json.dumps({
                                "total_plot_area": ex["total_plot_area"],
                                "total_covered_area": ex["total_covered_area"],
                                "far": ex["far"]
                            })}
                        ]
                    })

                # 🖼️ Final user query with actual image
                messages.append({
                    "role": "user",
                    "parts": [
                        cropped_img,  # PIL.Image.Image format
                        {"text": "Give total_plot_area, total_covered_area and far as JSON"}
                    ]
                })

                # 🤖 Gemini inference
                response = model.generate_content(messages)
                output = response.text

                print("Gemini raw output:\n", output)

                json_str = re.sub(r"^```json\s*|```$", "", output.strip(), flags=re.DOTALL)

                try:
                    data_dict = json.loads(json_str)
                except:
                    data_dict = json.loads(utils.escape_inches(json_str))

                plot_area = data_dict.get('total_plot_area', None)
                covered_area = data_dict.get('total_covered_area', None)
                far = data_dict.get('far', None)

                plot_area_list.append(plot_area)
                covered_area_list.append(covered_area)
                far_list.append(far)

        # 📦 Final structured output
        final_output = []
        for i in range(len(plot_area_list)):
            final_output.append({
                "total_plot_area": plot_area_list[i],
                "total_covered_area": covered_area_list[i],
                "far": far_list[i]
            })

        return final_output
    

    