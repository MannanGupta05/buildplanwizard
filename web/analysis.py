import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import tempfile
import json
import shutil
import traceback
from PIL import Image
import google.generativeai as genai
from src.core import utils
from src.core import check_rules
from src.core import config_map as config

# Import from buildplanwizard - handle both relative and absolute imports
try:
    from .buildplanwizard import rule_verifier, Extractor, get_extractor_func, get_image_for_var, get_examples_for_var, get_prompt_for_var, read_pdf, create_segments
except ImportError:
    from buildplanwizard import rule_verifier, Extractor, get_extractor_func, get_image_for_var, get_examples_for_var, get_prompt_for_var, read_pdf, create_segments

def analyze_map_with_ai(file_data, filename, file_type):
    """
    Enhanced map analysis function with simplified structure using buildplanwizard
    """
    validation_text = ""
    
    try:
        print(f"Starting analysis for {filename} (type: {file_type})")
        
        #TODO: Remove temp_file dependency for image. Load directly and pass image object.
        # Create temporary file to save the uploaded data
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as temp_file:
            temp_file.write(file_data)
            temp_file_path = temp_file.name
        
        # Create temporary directories for processing
        temp_dir = tempfile.mkdtemp()
        temp_output_dir = os.path.join(temp_dir, "output")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        try:
            print("Processing file...")
            
            # Convert PDF to image if needed or load image directly
            if file_type.lower() == 'pdf':
                print("Converting PDF to image...")
                input_map_image = read_pdf(temp_file_path)
                print("PDF converted successfully")
            else:
                # Load image directly
                try:
                    input_map_image = Image.open(temp_file_path)
                    print("Image loaded successfully")
                except Exception as e:
                    print(f"Image loading error: {e}")
                    raise Exception(f"Image loading failed: {str(e)}")
            
            print("Creating segments...")
            processed_image, boxs = create_segments(input_map_image, model="YOLO")
            print(f"Segmentation completed, found {len(boxs)} objects")
            
            # Configure Gemini API using config function
            print("Configuring Gemini API...")
            try:
                gemini_model = config.configure_gemini_api()
                print("Gemini API configured successfully")
            except Exception as e:
                print(f"Gemini API configuration error: {e}")
                raise Exception(f"AI model configuration failed: {str(e)}")
            
            print("Running all room extractions...")
            
            # Define variables to extract
            variables_to_extract = [
                "bedroom", "drawingroom", "studyroom", "store", "bathroom", 
                "water_closet", "combined_bath_wc", "kitchen", "plot_area_far", 
                "lobby", "dining", "riser_treader_width", "height_plinth", "floor_count"
            ]
            
            # Initialize results dictionary
            all_var_dict = {}
            
            # Extract each variable using loop - matching your requested structure
            for variable in variables_to_extract:
                print(f"Extracting {variable}...")
                try:
                    var_image = get_image_for_var(processed_image, boxs, variable) #TODO: Implement box extraction in get_image_for_var
                    var_extractor_class = get_extractor_func(variable)
                    var_examples = get_examples_for_var(variable)
                    var_prompt = get_prompt_for_var(variable)
                    
                    if var_extractor_class and var_prompt:
                        # Create extractor instance
                        var_extractor = var_extractor_class(boxs)
                        
                        # Create Extractor and run - matching your exact structure
                        var_dict = Extractor(
                            model=gemini_model,
                            extractor=var_extractor,
                            image=var_image,
                            examples=var_examples,
                            prompt=var_prompt
                        )
                        
                        result = var_dict.run()
                        all_var_dict[variable] = result
                        print(f"{variable} extraction completed")
                    else:
                        print(f"Warning: No extractor or prompt found for {variable}")
                        all_var_dict[variable] = []
                        
                except Exception as e:
                    print(f"Error extracting {variable}: {e}")
                    all_var_dict[variable] = []
            
            # Handle special cases for multi-return extractions
            # Bedroom and drawing room are extracted together
            if "bedroom" in all_var_dict and "drawingroom" in all_var_dict:
                bedroom_drawingroom_result = all_var_dict.get("bedroom", [])
                if isinstance(bedroom_drawingroom_result, tuple) and len(bedroom_drawingroom_result) == 2:
                    all_var_dict["bedroom"] = bedroom_drawingroom_result[0]
                    all_var_dict["drawingroom"] = bedroom_drawingroom_result[1]
                elif isinstance(bedroom_drawingroom_result, list):
                    # If single list returned, assume it's bedroom data
                    all_var_dict["bedroom"] = bedroom_drawingroom_result
                    all_var_dict["drawingroom"] = []
            
            # Lobby and dining are extracted together
            if "lobby" in all_var_dict and "dining" in all_var_dict:
                lobby_dining_result = all_var_dict.get("lobby", [])
                if isinstance(lobby_dining_result, tuple) and len(lobby_dining_result) == 2:
                    all_var_dict["lobby"] = lobby_dining_result[0]
                    all_var_dict["dining"] = lobby_dining_result[1]
                elif isinstance(lobby_dining_result, list):
                    # If single list returned, assume it's lobby data
                    all_var_dict["lobby"] = lobby_dining_result
                    all_var_dict["dining"] = []
            
            # Bathroom categories need special handling
            bathroom_result = all_var_dict.get("bathroom", [])
            if isinstance(bathroom_result, tuple) and len(bathroom_result) == 3:
                all_var_dict["bathroom"] = bathroom_result[0]
                all_var_dict["water_closet"] = bathroom_result[1]
                all_var_dict["combined_bath_wc"] = bathroom_result[2]
            elif isinstance(bathroom_result, list):
                # If single list returned, extract categories from dict items
                bathroom_values = []
                water_closet_values = []
                combined_bath_wc_values = []
                
                for item in bathroom_result:
                    if isinstance(item, dict):
                        bathroom_values.append(item.get('Bathroom', 0))
                        water_closet_values.append(item.get('Water Closet (W.C.)', 0))
                        combined_bath_wc_values.append(item.get('Combined Bath and W.C.', 0))
                
                all_var_dict["bathroom"] = bathroom_values
                all_var_dict["water_closet"] = water_closet_values
                all_var_dict["combined_bath_wc"] = combined_bath_wc_values
            
            # Create final dictionary using filename without extension as key - populated using loop
            file_key = os.path.splitext(filename)[0]
            final_dict = {}
            
            # Populate final_dict using loop as requested
            for variable in variables_to_extract:
                if variable not in final_dict:
                    final_dict[file_key] = {}
                final_dict[file_key][variable] = all_var_dict.get(variable, [])
            
            # Alternative using utils.save_to_dict for compatibility
            final_dict = utils.save_to_dict(
                {},
                file_key,
                **{var: all_var_dict.get(var, []) for var in variables_to_extract}
            )
            
            # Save extracted data to temporary JSON for processing
            temp_json_path = os.path.join(temp_dir, "output.json")
            with open(temp_json_path, "w") as f:
                json.dump(final_dict, f, indent=2)
            print("Data saved to output.json")
            
            # Temporarily change working directory to ensure check_rules can find the output.json
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Run validation
                print("Running rule validation...")
                validation_results = check_rules.run_validation()
                print("Validation completed")

                # Build validation_text from logs
                if validation_results and isinstance(validation_results, dict):
                    validation_text = "\n\n".join(validation_results.get("logs", []))
                else:
                    validation_text = ""
                
                # Call rule_verifier with the extracted variables as requested
                rule_results = rule_verifier(variables=all_var_dict, rule_location="Punjab")
                
            except Exception as e:
                print(f"Validation error: {e}")
                raise Exception(f"Rule validation failed: {str(e)}")
            finally:
                os.chdir(original_cwd)
            
            # Parse validation results
            results = {}
            overall_status = "rejected"

            if validation_results and isinstance(validation_results, dict):
                structured = validation_results.get("structured", {})
                logs = validation_results.get("logs", [])

                # Flatten structured results into {rule_name: {passed, message}}
                for _, rules in structured.items():  # you only have one map_name, so ignore key
                    for rule_name, rule_result in rules.items():
                        if rule_name.lower().startswith("final"):
                            overall_status = "approved" if "pass" in str(rule_result).lower() else "rejected"
                        else:
                            # Handle structured list of dicts correctly
                            if isinstance(rule_result, list) and rule_result:
                                passed = rule_result[0].get("status", "").lower() == "pass"
                            elif isinstance(rule_result, dict):
                                passed = rule_result.get("status", "").lower() == "pass"
                            else:
                                passed = "pass" in str(rule_result).lower() or "✅" in str(rule_result)

                            results[rule_name] = {
                                "passed": passed,
                                "message": rule_result  # keep full JSON/dict instead of just string
                            }

                # If no Final Verdict found in structured, fallback to logs
                if overall_status == "rejected" and logs:
                    if any("Passed All Rules" in log for log in logs):
                        overall_status = "approved"

            print(f"Analysis completed successfully. Status: {overall_status}")
            return results, overall_status, validation_results, validation_text

            
        finally:
            # Clean up temporary files and directories
            try:
                os.unlink(temp_file_path)
                shutil.rmtree(temp_dir)
                print("Cleanup completed")
            except Exception as cleanup_error:
                print(f"Cleanup error: {cleanup_error}")
                pass
                
    except Exception as e:
        print(f"Error in map analysis: {str(e)}")
        traceback.print_exc()
        # Return error result
        return {
            "error": {
                "passed": False,
                "message": f"Analysis failed: {str(e)}"
            }
        }, "error", None, ""