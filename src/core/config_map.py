import os

# main path - get from environment or use current directory
MAIN_PATH = os.environ.get("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configuration for image processing
SAVE_IMAGES = False
ksize = 3
num_of_zeros = 5
BOX_CONF = 0.45
SAVE_CROPS = False

# Get Gemini API keys from environment variables
gemini_api_keys = [
    key for key in [
        os.environ.get("GEMINI_API_KEY"),
        os.environ.get("GEMINI_API_KEY_2"),  # Optional backup key
        os.environ.get("GEMINI_API_KEY_3"),  # Optional backup key
    ] if key  # Only include non-empty keys
]

# Ensure we have at least one API key
if not gemini_api_keys:
    raise ValueError("No Gemini API keys found! Set GEMINI_API_KEY environment variable.")

gemini_model = "gemini-2.5-flash"

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