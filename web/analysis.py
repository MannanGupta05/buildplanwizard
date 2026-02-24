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
            
            print("Running all extractions using NEW SYSTEM - One call per extractor...")
            
            # DEBUG: Write start of analysis to debug log
            try:
                with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                    debug_file.write(f"\n=== STARTING WEB APP ANALYSIS ===\n")
                    debug_file.write(f"Starting NEW SYSTEM extraction...\n")
            except:
                pass
            
            # Define extractor groups - each extractor called ONCE
            extractor_groups = {
                "area": {
                    "extractor_class": "AreaExtractor",
                    "variables": ["total_plot_area", "ground_covered_area", "total_covered_area", "far"],
                    "prompt_key": "area"
                },
                "room": {
                    "extractor_class": "RoomExtractor", 
                    "variables": ["bedroom", "drawingroom", "studyroom", "store"],
                    "prompt_key": "room"
                },
                "setback_floors": {
                    "extractor_class": "SetbackFloorsExtractor",
                    "variables": ["no_of_floors", "front_setback", "rear_setback", "left_side_setback", "right_side_setback"],
                    "prompt_key": "setback_floors"
                },
                "staircase": {
                    "extractor_class": "StaircaseExtractor",
                    "variables": ["staircase_riser", "staircase_tread", "staircase_width"], 
                    "prompt_key": "staircase"
                },
                "height_kitchen_bathroom": {
                    "extractor_class": "HeightKitchenBathroomExtractor",
                    "variables": ["bathroom", "water_closet", "combined_bath_wc", "kitchen_only", "kitchen_with_separate_dining", "kitchen_with_separate_store", "kitchen_with_dining", "plinth_height", "building_height"],
                    "prompt_key": "height_kitchen_bathroom"
                }
            }
            
            # Initialize results dictionary
            all_var_dict = {}
            
                # Extract each GROUP using single call per extractor
            for group_name, group_config in extractor_groups.items():
                print(f"Extracting {group_name} variables: {group_config['variables']}")
                
                # Always write to debug log for web app debugging
                try:
                    with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                        debug_file.write(f"\n=== WEB APP EXTRACTION: {group_name} ===\n")
                        debug_file.write(f"Variables: {group_config['variables']}\n")
                except:
                    pass
                    
                try:
                    # Get the first variable to determine extractor (all variables in group use same extractor)
                    first_variable = group_config['variables'][0]
                    print(f"DEBUG: Using first variable '{first_variable}' for group {group_name}")
                    
                    var_image = get_image_for_var(processed_image, boxs, first_variable)
                    var_extractor_class = get_extractor_func(first_variable)
                    var_examples = get_examples_for_var(first_variable)
                    var_prompt = get_prompt_for_var(first_variable)
                    
                    print(f"DEBUG: Group {group_name} - extractor_class: {var_extractor_class}")
                    print(f"DEBUG: Group {group_name} - prompt length: {len(var_prompt) if var_prompt else 0}")
                    
                    # Always write debug info even if extraction fails
                    try:
                        with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                            debug_file.write(f"First variable: {first_variable}\n")
                            debug_file.write(f"Extractor class: {var_extractor_class}\n")
                            debug_file.write(f"Prompt length: {len(var_prompt) if var_prompt else 0}\n")
                    except:
                        pass
                    
                    if var_extractor_class and var_prompt:
                        # Write debug info to file
                        try:
                            with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                                debug_file.write(f"\n=== ANALYSIS FLOW: {group_name} ===\n")
                                debug_file.write(f"First variable: {first_variable}\n")
                                debug_file.write(f"Extractor class: {var_extractor_class}\n")
                                debug_file.write(f"About to create Extractor and run...\n")
                        except:
                            pass
                        
                        # Create Extractor and run ONCE for the entire group
                        # Pass the extractor CLASS, not an instance - buildplanwizard will instantiate it
                        var_dict = Extractor(
                            model=gemini_model,
                            extractor=var_extractor_class,  # Pass class, not instance
                            image=var_image,
                            examples=var_examples,
                            prompt=var_prompt
                        )
                        
                        result = var_dict.run()
                        
                        # Write result debug info to file  
                        try:
                            with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                                debug_file.write(f"Extraction result for {group_name}: {result}\n")
                        except:
                            pass
                        
                        # Distribute the single result to all variables in the group
                        for variable in group_config['variables']:
                            all_var_dict[variable] = result
                            
                        print(f"{group_name} extraction completed - distributed to {len(group_config['variables'])} variables")
                    else:
                        print(f"Warning: No extractor or prompt found for {group_name}")
                        try:
                            with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                                debug_file.write(f"WARNING: No extractor or prompt found for {group_name}\n")
                                debug_file.write(f"Extractor class: {var_extractor_class}\n")
                                debug_file.write(f"Prompt: {'Found' if var_prompt else 'Not Found'}\n")
                        except:
                            pass
                        # Set all variables in group to empty
                        for variable in group_config['variables']:
                            all_var_dict[variable] = []
                        
                except Exception as e:
                    print(f"Error extracting {group_name}: {e}")
                    try:
                        with open("debug_prompts.log", "a", encoding="utf-8") as debug_file:
                            debug_file.write(f"ERROR in {group_name}: {str(e)}\n")
                    except:
                        pass
                    # Set all variables in group to empty on error
                    for variable in group_config['variables']:
                        all_var_dict[variable] = []
            
            # Handle special cases for NEW SYSTEM extractions
            # Room extractor returns all room data together
            if "bedroom" in all_var_dict:
                room_result = all_var_dict.get("bedroom", {})
                if isinstance(room_result, dict) and "floor_data" in room_result:
                    # Extract room data from the new format
                    floor_data = room_result.get("floor_data", [])
                    if floor_data:
                        first_floor = floor_data[0] if floor_data else {}
                        # Use a default floor name since room extraction doesn't include floor_name
                        default_floor_name = "Ground Floor"
                        
                        # Structure room data as [(dimensions_list, floor_name)] for check_rules.py
                        all_var_dict["bedroom"] = [(first_floor.get("bedroom", ["Not Sure"]), default_floor_name)]
                        all_var_dict["drawingroom"] = [(first_floor.get("drawingroom", ["Not Sure"]), default_floor_name)]
                        all_var_dict["studyroom"] = [(first_floor.get("studyroom", ["Not Sure"]), default_floor_name)]
                        all_var_dict["store"] = [(first_floor.get("store room", ["Not Sure"]), default_floor_name)]
                        
                        # Data structure properly formatted for validation
                    else:
                        # Room extractor failed or returned no floor data - set fallback data structure
                        default_floor_name = "Unknown Floor"
                        all_var_dict["bedroom"] = [(["Not Sure"], default_floor_name)]
                        all_var_dict["drawingroom"] = [(["Not Sure"], default_floor_name)]
                        all_var_dict["studyroom"] = [(["Not Sure"], default_floor_name)]
                        all_var_dict["store"] = [(["Not Sure"], default_floor_name)]
                else:
                    # Room extractor returned invalid format - set fallback data structure
                    default_floor_name = "Unknown Floor"
                    all_var_dict["bedroom"] = [(["Not Sure"], default_floor_name)]
                    all_var_dict["drawingroom"] = [(["Not Sure"], default_floor_name)]
                    all_var_dict["studyroom"] = [(["Not Sure"], default_floor_name)]
                    all_var_dict["store"] = [(["Not Sure"], default_floor_name)]
            
            # Area extractor returns all area data together
            if "plot_area_far" in all_var_dict:
                area_result = all_var_dict.get("plot_area_far", [])
                
                # The data comes in format: [{"total_plot_area": [168.83], ...}]
                if isinstance(area_result, list) and len(area_result) > 0:
                    first_item = area_result[0]
                    if isinstance(first_item, dict):
                        try:
                            # Extract values from the nested lists
                            all_var_dict["total_plot_area"] = first_item.get("total_plot_area", [0.0])[0]
                            all_var_dict["ground_covered_area"] = first_item.get("ground_covered_area", [0.0])[0] 
                            all_var_dict["total_covered_area"] = first_item.get("total_covered_area", [0.0])[0]
                            all_var_dict["far"] = first_item.get("far", [0.0])[0]
                        except Exception as e:
                            pass
            
            # Setback extractor returns setback and floors data
            print(f"Checking for setback_floors in all_var_dict. Keys: {list(all_var_dict.keys())}")
            if "setback_floors" in all_var_dict:
                setback_result = all_var_dict.get("setback_floors", {})
                print(f"Found setback_floors: {setback_result}")
                if isinstance(setback_result, dict) and "plot_data" in setback_result:
                    plot_data = setback_result.get("plot_data", {})
                    all_var_dict["no_of_floors"] = plot_data.get("no_of_floors", "Not Sure")
                    all_var_dict["front_setback"] = plot_data.get("front_setback", ["Not Sure"])
                    all_var_dict["rear_setback"] = plot_data.get("rear_setback", ["Not Sure"])
                    all_var_dict["left_side_setback"] = plot_data.get("left_side_setback", ["Not Sure"])
                    all_var_dict["right_side_setback"] = plot_data.get("right_side_setback", ["Not Sure"])
                    print(f"Extracted setback data: floors={all_var_dict['no_of_floors']}")
                else:
                    print("setback_floors found but wrong format or missing plot_data")
            else:
                print("setback_floors NOT found - extraction probably failed")
            
            # Staircase extractor returns all staircase dimensions
            print(f"Checking for staircase in all_var_dict")
            if "staircase" in all_var_dict:
                stair_result = all_var_dict.get("staircase", {})
                print(f"Found staircase: {stair_result}")
                if isinstance(stair_result, dict):
                    all_var_dict["staircase_riser"] = stair_result.get("staircase_riser", ["Not Sure"])
                    all_var_dict["staircase_tread"] = stair_result.get("staircase_tread", ["Not Sure"])
                    all_var_dict["staircase_width"] = stair_result.get("staircase_width", ["Not Sure"])
                    print(f"Extracted staircase data")
                else:
                    print("staircase found but wrong format")
            else:
                print("staircase NOT found - extraction probably failed")
            
            # Height, Kitchen, Bathroom extractor returns comprehensive data
            if any(k in all_var_dict for k in ["bathroom", "water_closet", "combined_bath_wc", "kitchen_only", "plinth_height", "building_height"]):
                height_kitchen_bathroom_keys = ["bathroom", "water_closet", "combined_bath_wc", "kitchen_only", "kitchen_with_separate_dining", "kitchen_with_separate_store", "kitchen_with_dining", "plinth_height", "building_height"]
                height_kb_result = None
                for key in height_kitchen_bathroom_keys:
                    if key in all_var_dict:
                        height_kb_result = all_var_dict[key]
                        break
                
                if isinstance(height_kb_result, dict):
                    # Extract floor data (bathroom and kitchen info)
                    floor_data = height_kb_result.get("floor_data", [])
                    if floor_data:
                        first_floor = floor_data[0] if floor_data else {}
                        floor_name = first_floor.get("floor_name", "Unknown Floor")
                        
                        # Structure room data as [(dimensions_list, floor_name)] for check_rules.py
                        all_var_dict["bathroom"] = [(first_floor.get("bathroom", ["Not Sure"]), floor_name)]
                        all_var_dict["water_closet"] = [(first_floor.get("water_closet", ["Not Sure"]), floor_name)]
                        all_var_dict["combined_bath_wc"] = [(first_floor.get("combined_bath_wc", ["Not Sure"]), floor_name)]
                        all_var_dict["kitchen_only"] = [(first_floor.get("kitchen_only", ["Not Sure"]), floor_name)]
                        
                        # Data structure properly formatted for validation
                        
                        # For multi-part kitchens, structure properly
                        kitchen_separate_dining = first_floor.get("kitchen_with_separate_dining", [["Not Sure"], ["Not Sure"]])
                        all_var_dict["kitchen_with_separate_dining"] = [(kitchen_separate_dining, floor_name)]
                        
                        kitchen_separate_store = first_floor.get("kitchen_with_separate_store", [["Not Sure"], ["Not Sure"]])
                        all_var_dict["kitchen_with_separate_store"] = [(kitchen_separate_store, floor_name)]
                        
                        kitchen_with_dining = first_floor.get("kitchen_with_dining", [["Not Sure"], ["Not Sure"]])
                        all_var_dict["kitchen_with_dining"] = [(kitchen_with_dining, floor_name)]
                        
                        # Map kitchen_only to kitchen for compatibility with check_rules.py
                        all_var_dict["kitchen"] = all_var_dict["kitchen_only"]
                    else:
                        # Extractor failed or returned no floor data - set fallback data structure
                        default_floor_name = "Unknown Floor"
                        all_var_dict["bathroom"] = [(["Not Sure"], default_floor_name)]
                        all_var_dict["water_closet"] = [(["Not Sure"], default_floor_name)]
                        all_var_dict["combined_bath_wc"] = [(["Not Sure"], default_floor_name)]
                        all_var_dict["kitchen_only"] = [(["Not Sure"], default_floor_name)]
                        all_var_dict["kitchen_with_separate_dining"] = [([["Not Sure"], ["Not Sure"]], default_floor_name)]
                        all_var_dict["kitchen_with_separate_store"] = [([["Not Sure"], ["Not Sure"]], default_floor_name)]
                        all_var_dict["kitchen_with_dining"] = [([["Not Sure"], ["Not Sure"]], default_floor_name)]
                        all_var_dict["kitchen"] = all_var_dict["kitchen_only"]
                        all_var_dict["plinth_height"] = ["Not Sure"]
                        all_var_dict["building_height"] = ["Not Sure"]
                else:
                    # Height/Kitchen/Bathroom extractor returned invalid format - set fallback data structure
                    default_floor_name = "Unknown Floor"
                    all_var_dict["bathroom"] = [(["Not Sure"], default_floor_name)]
                    all_var_dict["water_closet"] = [(["Not Sure"], default_floor_name)]
                    all_var_dict["combined_bath_wc"] = [(["Not Sure"], default_floor_name)]
                    all_var_dict["kitchen_only"] = [(["Not Sure"], default_floor_name)]
                    all_var_dict["kitchen_with_separate_dining"] = [([["Not Sure"], ["Not Sure"]], default_floor_name)]
                    all_var_dict["kitchen_with_separate_store"] = [([["Not Sure"], ["Not Sure"]], default_floor_name)]
                    all_var_dict["kitchen_with_dining"] = [([["Not Sure"], ["Not Sure"]], default_floor_name)]
                    all_var_dict["kitchen"] = all_var_dict["kitchen_only"]
                    all_var_dict["plinth_height"] = ["Not Sure"]
                    all_var_dict["building_height"] = ["Not Sure"]
                    
                    # Extract plot data (height info)
                    plot_data = height_kb_result.get("plot_data", {})
                    all_var_dict["plinth_height"] = plot_data.get("plinth_height", ["Not Sure"])
                    all_var_dict["building_height"] = plot_data.get("building_height", ["Not Sure"])
                    
                    # Legacy variables for backward compatibility
                    all_var_dict["height_plinth"] = [f"Plinth: {plot_data.get('plinth_height', ['Not Sure'])[0]}, Building: {plot_data.get('building_height', ['Not Sure'])[0]}"]
            
            # Create final dictionary using filename without extension as key - populated using loop
            file_key = os.path.splitext(filename)[0]
            final_dict = {}
            
            # Create final dictionary with ALL new system variables
            all_variables = [
                # Original extraction variables
                "bedroom", "drawingroom", "studyroom", "store", "kitchen",
                "plot_area_far", "setback", "no_of_floors",
                "staircase_riser", "staircase_tread", "staircase_width",
                # Expanded variables from new system
                "total_plot_area", "ground_covered_area", "total_covered_area", "far",
                "front_setback", "rear_setback", "left_side_setback", "right_side_setback",
                # Height, Kitchen, and Bathroom variables
                "bathroom", "water_closet", "combined_bath_wc", 
                "kitchen_only", "kitchen_with_separate_dining", "kitchen_with_separate_store", "kitchen_with_dining",
                "plinth_height", "building_height", "height_plinth"
            ]
            
            # FINAL EXTRACTION: Make sure area variables are extracted before final output
            if "plot_area_far" in all_var_dict:
                area_result = all_var_dict.get("plot_area_far", [])
                print(f"FINAL EXTRACTION - plot_area_far data: {area_result}")
                if isinstance(area_result, list) and len(area_result) > 0:
                    first_item = area_result[0]
                    print(f"FINAL EXTRACTION - first_item: {first_item}")
                    if isinstance(first_item, dict):
                        try:
                            # Extract values with detailed debugging
                            total_plot = first_item.get("total_plot_area", [0.0])
                            ground_covered = first_item.get("ground_covered_area", [0.0])
                            total_covered = first_item.get("total_covered_area", [0.0])
                            far_val = first_item.get("far", [0.0])
                            
                            print(f"Raw values: plot={total_plot}, ground={ground_covered}, total={total_covered}, far={far_val}")
                            
                            all_var_dict["total_plot_area"] = total_plot[0] if total_plot else 0.0
                            all_var_dict["ground_covered_area"] = ground_covered[0] if ground_covered else 0.0
                            all_var_dict["total_covered_area"] = total_covered[0] if total_covered else 0.0
                            all_var_dict["far"] = far_val[0] if far_val else 0.0
                            
                            print(f"FINAL EXTRACTION - Extracted values: plot={all_var_dict['total_plot_area']}, ground={all_var_dict['ground_covered_area']}")
                        except Exception as e:
                            print(f"FINAL EXTRACTION - Error: {e}")
                else:
                    print("FINAL EXTRACTION - plot_area_far is not a list or is empty")
            else:
                print("FINAL EXTRACTION - plot_area_far not found")
                print(f"Available keys: {list(all_var_dict.keys())}")
            
            # Populate final_dict using loop as requested
            for variable in all_variables:
                if variable not in final_dict:
                    final_dict[file_key] = {}
                
                # Special handling for area variables that should default to 0.0, not []
                if variable in ["total_plot_area", "ground_covered_area", "total_covered_area", "far"]:
                    final_dict[file_key][variable] = all_var_dict.get(variable, 0.0)
                else:
                    final_dict[file_key][variable] = all_var_dict.get(variable, [])
            
            # Alternative using utils.save_to_dict for compatibility
            final_dict = utils.save_to_dict(
                {},
                file_key,
                **{var: all_var_dict.get(var, []) for var in all_variables}
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

                # Track rule validation results
                rules_passed = 0
                total_rules = 10  # We expect exactly 10 rules
                
                # Flatten structured results into {rule_name: {passed, message}}
                for _, rules in structured.items():  # you only have one map_name, so ignore key
                    for rule_name, rule_result in rules.items():
                        if rule_name.lower().startswith("final"):
                            # Skip final verdict - we'll calculate it ourselves
                            continue
                        elif rule_name.lower().startswith("rule"):
                            # This is one of the 10 rules - check if it passed
                            rule_passed = False
                            
                            # Handle structured list of dicts correctly
                            if isinstance(rule_result, list) and rule_result:
                                rule_passed = rule_result[0].get("status", "").lower() == "pass"
                            elif isinstance(rule_result, dict):
                                rule_passed = rule_result.get("status", "").lower() == "pass"
                            else:
                                rule_passed = "pass" in str(rule_result).lower() or "✅" in str(rule_result)

                            if rule_passed:
                                rules_passed += 1

                            results[rule_name] = {
                                "passed": rule_passed,
                                "message": rule_result  # keep full JSON/dict instead of just string
                            }

                # Only approve if ALL 10 rules are passed
                if rules_passed == total_rules:
                    overall_status = "approved"
                else:
                    overall_status = "rejected"
                    
                print(f"Rules validation summary: {rules_passed}/{total_rules} rules passed")
                
                # Additional safety check - if we have fewer rules than expected, something went wrong
                if len([rule for rule in structured.items() if rule[1] and any(key.lower().startswith("rule") for key in rule[1].keys())]) < total_rules:
                    print(f"WARNING: Expected {total_rules} rules, but found fewer in validation results. Status kept as rejected.")
                    overall_status = "rejected"

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


def safe_print(message):
    """Thread-safe print function"""
    try:
        print(str(message))
    except Exception as e:
        print(f"Print error: {e}")


def normalize_extraction_data(data, data_type="room"):
    """Normalize extraction data to consistent format."""
    if not data or data is None:
        return {}
        
    if isinstance(data, dict):
        return data
    elif isinstance(data, list):
        if len(data) > 0:
            return data[0] if isinstance(data[0], dict) else {}
        else:
            return {}
    else:
        return {}


def convert_unified_to_legacy(unified_data):
    """Convert unified data format to legacy format for compatibility."""
    legacy_format = {
        "room": [],
        "area": [],
        "staircase": [],
        "setback": []
    }
    
    for map_key, map_data in unified_data.items():
        if isinstance(map_data, list) and len(map_data) > 0:
            data = map_data[0]
            
            # Process room data
            if any(key in data for key in ["bedroom", "drawingroom", "studyroom", "store"]):
                room_data = {}
                for room_type in ["bedroom", "drawingroom", "studyroom", "store"]:
                    room_data[room_type] = data.get(room_type, [])
                legacy_format["room"].append(room_data)
            
            # Process area data
            if "plot_area_far" in data:
                plot_area_far = data["plot_area_far"]
                if isinstance(plot_area_far, list) and len(plot_area_far) > 0:
                    plot_data = plot_area_far[0]
                    legacy_format["area"].append(plot_data)
            
            # Process staircase data
            if any(key in data for key in ["staircase_riser", "staircase_tread", "staircase_width"]):
                staircase_data = {
                    "staircase_riser": data.get("staircase_riser", ["Not Sure"]),
                    "staircase_tread": data.get("staircase_tread", ["Not Sure"]),
                    "staircase_width": data.get("staircase_width", ["Not Sure"])
                }
                legacy_format["staircase"].append(staircase_data)
            
            # Process setback data
            if any(key in data for key in ["no_of_floors", "front_setback", "rear_setback", "left_side_setback", "right_side_setback"]):
                setback_data = {
                    "no_of_floors": [data.get("no_of_floors", "Not Sure")],
                    "front_setback": data.get("front_setback", ["Not Sure"]),
                    "rear_setback": data.get("rear_setback", ["Not Sure"]),
                    "left_side_setback": data.get("left_side_setback", ["Not Sure"]),
                    "right_side_setback": data.get("right_side_setback", ["Not Sure"])
                }
                legacy_format["setback"].append(setback_data)
    
    return legacy_format

            
