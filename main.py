import os   
from pdf2image import convert_from_path
import warnings
import json
from PIL import Image
from io import BytesIO

import config_map as config
from remove_zeros import SeamCarver
from yolo_inference import YoloInference
import google.generativeai as genai

import bedroom_drawingroom_examples
import studyroom_examples         # ✅ NEW
import store_examples
import bathroom_examples
import kitchen_examples
import plot_cov_area_far_examples  # ✅ NEW
import lobby_dining_examples       # ✅ NEW
import riser_treader_width_examples
import riser_treader_width_examples_class4
import riser_treader_width_examples_class5
import height_plinth_examples     # ✅ NEW


from bedroom_drawingroom_extraction import BDE
from store_extraction import StoreExtractor
from bathroom_extraction import BathroomExtractor
from kitchen_extraction import KitchenExtractor
from plot_cov_area_far_extraction import PlotAreaExtractor  # ✅ NEW
from lobby_dining_extraction import LobbyDiningExtractor     # ✅ NEW
from riser_treader_width_extraction import RiserTreaderWidthExtractor
from height_plinth_extraction import HeightPlinthExtractor   # ✅ NEW
from studyroom_extraction import StudyRoomExtractor  # ✅ NEW


import utils
import check_rules

warnings.filterwarnings("ignore")

def load_prompts(prompt_file):
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]
    return prompts

def main():
    final_dict = {}

    print("Converting PDFs to images...")
    pdf_dir = os.path.join(config.MAIN_PATH, config.TEST_PDF_PATH)
    output_dir = os.path.join(config.MAIN_PATH, config.CONVERTED_IMAGE_PATH)
    os.makedirs(output_dir, exist_ok=True)

    pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]

    for pdf in pdfs:
        print("Processing PDF:", pdf)
        pdf_path = os.path.join(pdf_dir, pdf)
        poppler_path = r"C:\Users\chauh\Downloads\map_approval_codebase (1)\map_approval_codebase\poppler-24.08.0\Library\bin"
        image = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)[0]
        #image = convert_from_path(pdf_path, dpi=300)[0]

        print("Removing zeros from image...")
        sc = SeamCarver(image)
        image = sc.get_seam_carving_cuts(config.ksize, config.num_of_zeros)

        if config.SAVE_IMAGES:
            image_filename = os.path.splitext(pdf)[0] + ".jpg"
            image_path = os.path.join(output_dir, image_filename)
            image.save(image_path, 'JPEG')
            print(f"Saved image: {image_path}")

        print("Running YOLO object detection...")
        yolo = YoloInference(os.path.join(config.MAIN_PATH, config.YOLO_MODEL_PATH), config.BOX_CONF)
        boxs = yolo.detect_yolo_objects(image)

        # Configure Gemini API with key rotation
        gemini_model = None
        last_error = None
        for api_key in config.gemini_api_keys:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(config.gemini_model)
                print(f"Gemini API configured with key: {api_key[:8]}...{api_key[-4:]}")
                gemini_model = model
                break
            except Exception as e:
                print(f"Gemini API error with key {api_key[:8]}...{api_key[-4:]}: {e}")
                last_error = e
        if not gemini_model:
            raise Exception(f"AI model configuration failed: {str(last_error)}")

        ### 🛏️ BEDROOM + DRAWING EXTRACTION
        print("Extracting bedroom and drawing room...")
        bed_drawg_prompt = '\n'.join(load_prompts(config.bedroom_drawingroom_promptfile))
        example_images_bed = bedroom_drawingroom_examples.examples(config.image_path)
        encoded_bed_examples = [
            {
                "base64": utils.encode_image(e["path"]),
                "bedroom": e["bedroom"],
                "drawing": e["drawing"],
                "floor": e["floor"]
            }
            for e in example_images_bed
        ]
        bde = BDE(boxs)
        bedroom_values, drawingroom_values = bde.extraction(image, bed_drawg_prompt, encoded_bed_examples, model)


        ### 📖 STUDY ROOM EXTRACTION
        print("Extracting study room...")
        studyroom_prompt = '\n'.join(load_prompts(config.studyroom_promptfile))
        example_images_studyroom = studyroom_examples.examples(config.image_path)
        encoded_studyroom_examples = [
            {
                "base64": utils.encode_image(e["path"]),
                "study": e["study"],
                "floor": e["floor"]
            }
            for e in example_images_studyroom
        ]
        studyroom_extractor = StudyRoomExtractor(boxs)
        studyroom_values = studyroom_extractor.extraction(image, studyroom_prompt, encoded_studyroom_examples, model)

        ### 🧱 STORE EXTRACTION
        print("Extracting store room...")
        store_prompt = '\n'.join(load_prompts(config.store_promptfile))
        example_images_store = store_examples.examples(config.image_path)
        encoded_store_examples = [
            {
                "base64": utils.encode_image(e["path"]),
                "store": e["store"],
                "floor": e["floor"]
            }
            for e in example_images_store
        ]
        store_extractor = StoreExtractor(boxs)
        store_values = store_extractor.extraction(image, store_prompt, encoded_store_examples, model)

        ### 🚿 BATHROOM EXTRACTION
        print("Extracting bathroom...")
        bathroom_prompt = '\n'.join(load_prompts(config.bathroom_promptfile))
        example_images_bath = bathroom_examples.examples(config.image_path)
        encoded_bath_examples = [
            {
                "base64": utils.encode_image(e["path"]),
                "Bathroom": e["Bathroom"],
                "Water Closet (W.C.)": e["Water Closet (W.C.)"],
                "Combined Bath and W.C.": e["Combined Bath and W.C."],
                "floor": e["floor"]
            }
            for e in example_images_bath
        ]
        bath_extractor = BathroomExtractor(boxs)
        bathroom_extraction_result = bath_extractor.extraction(image, bathroom_prompt, encoded_bath_examples, model)
        
        # Extract the three bathroom categories from the result
        bathroom_values = [item['Bathroom'] for item in bathroom_extraction_result]
        water_closet_values = [item['Water Closet (W.C.)'] for item in bathroom_extraction_result]
        combined_bath_wc_values = [item['Combined Bath and W.C.'] for item in bathroom_extraction_result]

        ### 🍳 KITCHEN EXTRACTION
        print("Extracting kitchen...")
        kitchen_prompt = '\n'.join(load_prompts(config.kitchen_promptfile))
        example_images_kitchen = kitchen_examples.examples(config.image_path)
        encoded_kitchen_examples = [
            {
                "base64": utils.encode_image(e["path"]),
                "kitchen": e["kitchen"],
                "floor": e["floor"]
            }
            for e in example_images_kitchen
        ]
        kitchen_extractor = KitchenExtractor(boxs)
        kitchen_values = kitchen_extractor.extraction(image, kitchen_prompt, encoded_kitchen_examples, model)

        ### 📐 PLOT AREA, COVERED AREA & FAR EXTRACTION
        print("Extracting plot area, covered area and FAR...")
        plot_prompt = '\n'.join(load_prompts(config.plot_cov_area_far_promptfile))
        example_images_plot = plot_cov_area_far_examples.examples(config.image_path)
        encoded_plot_examples = [
            {
                "base64": utils.encode_image(e["path"]),
                "total_plot_area": e["total_plot_area"],
                "total_covered_area": e["total_covered_area"],
                "far": e["far"]
            }
            for e in example_images_plot
        ]
        plot_area_extractor = PlotAreaExtractor(boxs)
        plot_far_values = plot_area_extractor.extraction(image, plot_prompt, encoded_plot_examples, model)

        ### 🛋️ LOBBY + DINING EXTRACTION
        print("Extracting lobby and dining room...")
        lobby_dining_prompt = '\n'.join(load_prompts(config.lobby_dining_promptfile))
        example_images_lobby = lobby_dining_examples.examples(config.image_path)
        encoded_lobby_examples = [
            {
                "base64": utils.encode_image(e["path"]),
                "lobby": e["lobby"],
                "dining": e["dining"],
                "floor": e["floor"]
            }
            for e in example_images_lobby
        ]
        lobby_dining_extractor = LobbyDiningExtractor(boxs)
        lobby_values, dining_values = lobby_dining_extractor.extraction(image, lobby_dining_prompt, encoded_lobby_examples, model)

        ### 🪜 RISER, TREAD, WIDTH EXTRACTION (Class 4 & 5)
        print("Extracting riser, tread, width, and head height (class 4 & 5)...")
        with open('riser_treader_width_class4.prompt', 'r', encoding='utf-8') as f:
            prompt_class4 = f.read()
        with open('riser_treader_width_class5.prompt', 'r', encoding='utf-8') as f:
            prompt_class5 = f.read()
        example_images_class4 = riser_treader_width_examples_class4.examples(config.image_path)
        example_images_class5 = riser_treader_width_examples_class5.examples(config.image_path)
        encoded_examples_class4 = [
            {
                "base64": utils.encode_image(e["path"]),
                "riser_treader_width": e["riser_treader_width"],
                "floor": e["floor"]
            }
            for e in example_images_class4
        ]
        encoded_examples_class5 = [
            {
                "base64": utils.encode_image(e["path"]),
                "riser_treader_width": e["riser_treader_width"]
            }
            for e in example_images_class5
        ]
        rtw_extractor = RiserTreaderWidthExtractor(boxs)
        riser_treader_width_values = rtw_extractor.extraction(
            image,
            prompt_class4, encoded_examples_class4,
            prompt_class5, encoded_examples_class5,
            model
        )

        ### 📏 HEIGHT & PLINTH LEVEL EXTRACTION
        print("Extracting height and plinth level (class 3)...")
        height_plinth_prompt = '\n'.join(load_prompts(config.height_plinth_promptfile))
        example_images_height = height_plinth_examples.examples(config.image_path)
        encoded_examples_height = [
            {
                "base64": utils.encode_image(e["path"]),
                "height": e["height"],
                "plinth level": e["plinth level"]
            }
            for e in example_images_height
        ]
        hp_extractor = HeightPlinthExtractor(boxs)
        height_plinth_values = hp_extractor.extraction(image, height_plinth_prompt, encoded_examples_height, model)

        # Aggregate all extractions for this PDF
        key = pdf.split('.pdf')[0]
        final_dict = utils.save_to_dict(
            final_dict,
            key,
            bedroom=bedroom_values,
            drawingroom=drawingroom_values,
            studyroom=studyroom_values,
            bathroom=bathroom_values,
            water_closet=water_closet_values,
            combined_bath_wc=combined_bath_wc_values,
            store=store_values,
            kitchen=kitchen_values,
            plot_area_far=plot_far_values,
            lobby=lobby_values,
            dining=dining_values,
            riser_treader_width=riser_treader_width_values,
            height_plinth=height_plinth_values   # ✅ NEW
        )
        break  # Only process the first PDF and then exit the loop

    # After all PDFs processed, save output.json and run validation
    with open("output.json", "w") as f:
        json.dump(final_dict, f, indent=2)

    print("Running rule validation...")
    validation_results = check_rules.run_validation()
    with open("validation_result.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(validation_results, indent=2))
    print("Validation complete. ✅")

if __name__ == "__main__":
    main()
