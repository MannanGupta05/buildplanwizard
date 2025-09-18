# main path 
MAIN_PATH = r"C:\Users\Mannan Gupta\Desktop\llm-map-approval-website_integration_new_rules\map_approval_codebase1"

# Paths
TEST_PDF_PATH = "data\\map_pdfs"
CONVERTED_IMAGE_PATH = "data\\map_images"
YOLO_MODEL_PATH = "data\\object_detection_v3.pt"

# Others
SAVE_IMAGES = False
ksize = 3
num_of_zeros = 5
BOX_CONF = 0.45
SAVE_CROPS = False

image_path = r"C:\Users\Mannan Gupta\Desktop\llm-map-approval-website_integration_new_rules\map_approval_codebase1\yolov8_segments\\"
bedroom_drawingroom_promptfile = "bedroom_drawingroom.prompt"
store_promptfile = "store.prompt"
bathroom_promptfile = "bathroom.prompt"
kitchen_promptfile = "kitchen.prompt"
lobby_dining_promptfile = "lobby_dining.prompt"
plot_cov_area_far_promptfile= "plot_cov_area_far.prompt"
riser_treader_width_promptfile = "riser_treader_width.prompt"
height_plinth_promptfile = "height_plinth.prompt"
studyroom_promptfile = "studyroom.prompt"

gemini_api_keys = [
    "AIzaSyDYmyJyb62Wztf9SrcpiHmJnQ0VqWoU5_w"    # Add more API keys here as needed
]

gemini_model = "gemini-2.0-flash"

def get_gemini_model():
    """Get the configured Gemini model name"""
    return gemini_model

def configure_gemini_api():
    """Configure Gemini API with key rotation. Returns configured model or None if all keys fail."""
    import google.generativeai as genai
    
    last_error = None
    for api_key in gemini_api_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(gemini_model)
            print(f"Gemini API configured with key: {api_key[:8]}...{api_key[-4:]}")
            return model
        except Exception as e:
            print(f"Gemini API error with key {api_key[:8]}...{api_key[-4:]}: {e}")
            last_error = e
    
    raise Exception(f"AI model configuration failed: {str(last_error)}")