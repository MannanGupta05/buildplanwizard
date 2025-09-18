import re 
import json

# Room validation thresholds
ROOM_RULES = {
    "bedroom": {"expected_area_m2": 9.5, "expected_min_width_m": 2.4},
    "drawingroom": {"expected_area_m2": 9.5, "expected_min_width_m": 2.4},
    "studyroom": {"expected_area_m2": 9.5, "expected_min_width_m": 2.4},  # Added studyroom here
    "bathroom": {"expected_area_m2": 1.8, "expected_min_width_m": 1.2},
    "water_closet": {"expected_area_m2": 1.2, "expected_min_width_m": 0.9},
    "combined_bath_wc": {"expected_area_m2": 2.8, "expected_min_width_m": 1.2},
    "store": {"expected_area_m2": 3.0, "expected_min_width_m": 1.2},
    "kitchen": {"expected_area_m2": 5.0, "expected_min_width_m": 1.8},
    "riser_treader_width": {
        "expected_min_width_m": 0.900,
        "expected_min_tread_m": 0.250,
        "expected_max_riser_m": 0.190,
    }
}

# ---------- Utility ----------
def feet_inch_to_meter(value):
    match = re.match(r"(\d+)'(?:-?(\d+(?:\.\d+)?|\d+/\d+)?)?\"?", value.strip())
    if not match:
        return None
    feet = int(match.group(1))
    inches = match.group(2)
    if inches:
        if '/' in inches:
            parts = inches.split('/')
            inches = float(parts[0]) / float(parts[1])
        else:
            inches = float(inches)
    else:
        inches = 0
    return round(feet * 0.3048 + inches * 0.0254, 3)

def parse_dimension(dim_str):
    try:
        width, length = map(feet_inch_to_meter, dim_str.lower().split('x'))
        return width, length
    except:
        return None, None

# ---------- Rule 1 ----------
def calculate_max_coverage(plot_area):
    if 60 <= plot_area <= 100:
        return 0.70 * plot_area
    elif 100 < plot_area <= 150:
        return 0.70 * plot_area
    elif 150 < plot_area <= 250:
        return 0.65 * (plot_area - 150) + 105
    elif 250 < plot_area <= 350:
        return 0.60 * (plot_area - 250) + 170
    elif 350 < plot_area <= 450:
        return 0.50 * (plot_area - 350) + 230
    elif plot_area > 450:
        return 0.40 * (plot_area - 450) + 280
    return 0

def check_ground_coverage(area_data):
    logs, structured, passed = [], [], True
    for entry in area_data:
        plot = entry.get("total_plot_area", [0])[0]
        covered = entry.get("total_covered_area", [0])[0]
        max_cov = calculate_max_coverage(plot)
        rule_status = "Pass" if covered <= max_cov else "Fail"
        if rule_status == "Fail":
            passed = False
            logs.append(f"Covered area {covered} m² exceeds max coverage {round(max_cov, 2)} m² for plot area {plot} m².")
        structured.append({
            "rule": "Ground Coverage",
            "recorded_value": covered,
            "expected_value": f"≤ {round(max_cov, 2)}",
            "status": rule_status,
            "reason": "OK" if rule_status == "Pass" else f"Exceeded allowed coverage"
        })
    return passed, logs, structured

# ---------- Rule 2 ----------
def check_far(area_data):
    logs, structured, passed = [], [], True
    for entry in area_data:
        plot = entry.get("total_plot_area", [0])[0]
        covered = entry.get("total_covered_area", [0])[0]
        max_far = 2.1 * plot
        rule_status = "Pass" if covered <= max_far else "Fail"
        if rule_status == "Fail":
            passed = False
            logs.append(f"Covered area {covered} m² exceeds max FAR {round(max_far, 2)} m².")
        structured.append({
            "rule": "FAR",
            "recorded_value": covered,
            "expected_value": f"≤ {round(max_far, 2)}",
            "status": rule_status,
            "reason": "OK" if rule_status == "Pass" else "FAR exceeded"
        })
    return passed, logs, structured

# ---------- Rule 3–6 ----------
def check_room_dimensions(room_type, room_data):
    rule = ROOM_RULES[room_type]
    logs, structured, passed = [], [], True
    for dims, floor in room_data:
        for dim in dims:
            if dim.lower() == "absent":
                continue
            width, length = parse_dimension(dim)
            if not width or not length:
                continue
            area = width * length
            area_ok = area >= rule['expected_area_m2']
            width_ok = width >= rule['expected_min_width_m']
            rule_status = "Pass" if area_ok and width_ok else "Fail"
            if rule_status == "Fail":
                passed = False
                logs.append(f"{room_type.title()} on {floor} – {dim}: Area {area:.2f} m², Width {width:.2f} m.")
            structured.append({
                "rule": f"{room_type.title()} Dimensions",
                "floor": floor,
                "recorded_value": f"{area:.2f} m², width {width:.2f} m",
                "expected_value": f"≥ {rule['expected_area_m2']} m², width ≥ {rule['expected_min_width_m']} m",
                "status": rule_status,
                "reason": "OK" if rule_status == "Pass" else "Area or width too small"
            })
    return passed, logs, structured

# ---------- Rule 6.1 ----------
def check_bathroom_categories(building_data):
    logs, structured, passed = [], [], True
    
    # Check bathroom
    bathroom_data = building_data.get("bathroom", [])
    bathroom_result = check_room_dimensions("bathroom", bathroom_data)
    passed_bathroom, logs_bathroom, structured_bathroom = bathroom_result
    
    # Check water closet
    water_closet_data = building_data.get("water_closet", [])
    water_closet_result = check_room_dimensions("water_closet", water_closet_data)
    passed_wc, logs_wc, structured_wc = water_closet_result
    
    # Check combined bath and WC
    combined_data = building_data.get("combined_bath_wc", [])
    combined_result = check_room_dimensions("combined_bath_wc", combined_data)
    passed_combined, logs_combined, structured_combined = combined_result
    
    # Combine all results
    passed = passed_bathroom and passed_wc and passed_combined
    logs.extend(logs_bathroom)
    logs.extend(logs_wc)
    logs.extend(logs_combined)
    structured.extend(structured_bathroom)
    structured.extend(structured_wc)
    structured.extend(structured_combined)
    
    return passed, logs, structured

# ---------- Rule 7 ----------
def check_staircase(data):
    rule = ROOM_RULES["riser_treader_width"]
    logs, structured, passed = [], [], True
    for entry in data:
        width = entry.get("staircase_width", ["absent"])[0]
        tread = entry.get("staircase_tread", ["absent"])[0]
        riser = entry.get("staircase_riser", ["absent"])[0]
        floor = entry.get("floor", ["absent"])[0] if isinstance(entry.get("floor"), list) else entry.get("floor")
        if "absent" in [width, tread, riser]:
            continue
        try:
            width, tread, riser = float(width), float(tread), float(riser)
            width_ok = width >= rule['expected_min_width_m']
            tread_ok = tread >= rule['expected_min_tread_m']
            riser_ok = riser <= rule['expected_max_riser_m']
            rule_status = "Pass" if width_ok and tread_ok and riser_ok else "Fail"
            if rule_status == "Fail":
                passed = False
                logs.append(f"Staircase on {floor} – width: {width}, tread: {tread}, riser: {riser}")
            structured.append({
                "rule": "Staircase",
                "floor": floor,
                "recorded_value": f"width {width}, tread {tread}, riser {riser}",
                "expected_value": f"width ≥ {rule['expected_min_width_m']}, tread ≥ {rule['expected_min_tread_m']}, riser ≤ {rule['expected_max_riser_m']}",
                "status": rule_status,
                "reason": "OK" if rule_status == "Pass" else "Dimension(s) invalid"
            })
        except:
            passed = False
            structured.append({
                "rule": "Staircase",
                "floor": floor,
                "recorded_value": f"width: {width}, tread: {tread}, riser: {riser}",
                "expected_value": "Valid numeric values",
                "status": "Fail",
                "reason": "Invalid or non-numeric value"
            })
    return passed, logs, structured

# ---------- Rule 8 ----------
def check_plinth_level(data):
    logs, structured, passed = [], [], True
    for entry in data:
        plinth = entry.get("plinth level", ["absent"])[0]
        if plinth == "absent":
            continue
        try:
            plinth_val = float(plinth.replace("'", "").replace('"', '').strip())
            rule_status = "Pass" if plinth_val <= 0.9 else "Fail"
            if rule_status == "Fail":
                passed = False
                logs.append(f"Plinth level {plinth_val} m exceeds 0.9 m limit.")
            structured.append({
                "rule": "Plinth Level",
                "recorded_value": plinth_val,
                "expected_value": "≤ 0.9 m",
                "status": rule_status,
                "reason": "OK" if rule_status == "Pass" else "Plinth too high"
            })
        except:
            passed = False
            structured.append({
                "rule": "Plinth Level",
                "recorded_value": plinth,
                "expected_value": "Valid numeric ≤ 0.9",
                "status": "Fail",
                "reason": "Invalid or non-numeric"
            })
    return passed, logs, structured

# ---------- Rule 9 ----------
def check_building_height(data):
    logs, structured, passed = [], [], True
    for entry in data:
        height = entry.get("height", ["absent"])[0]
        plinth = entry.get("plinth level", ["absent"])[0]
        if "absent" in [height, plinth]:
            continue
        try:
            height_val = float(height.replace("'", "").replace('"', '').strip())
            from_plinth = height_val
            rule_status = "Pass" if from_plinth <= 11.0 else "Fail"
            if rule_status == "Fail":
                passed = False
                logs.append(f"Height {from_plinth} m from plinth exceeds 11.0 m limit.")
            structured.append({
                "rule": "Building Height",
                "recorded_value": from_plinth,
                "expected_value": "≤ 11.0 m",
                "status": rule_status,
                "reason": "OK" if rule_status == "Pass" else "Height exceeds permissible limit"
            })
        except:
            passed = False
            structured.append({
                "rule": "Building Height",
                "recorded_value": f"height: {height}, plinth: {plinth}",
                "expected_value": "Valid numeric values",
                "status": "Fail",
                "reason": "Invalid or non-numeric value"
            })
    return passed, logs, structured

# ---------- MAIN PROCESSING ----------
def process_rooms(data):
    human_logs = []
    structured_results = {}

    for map_name, values in data.items():
        building = values[0]
        structured_results[map_name] = {}
        human_log = [f"Map: {map_name}"]
        overall_passed = True

        def log(rule_name, passed, txt_logs, structured):
            nonlocal overall_passed
            human_log.append(f"{rule_name} - {'Passed ✅' if passed else 'Failed ❌'}")
            human_log.extend([f"  - {log}" for log in txt_logs])
            structured_results[map_name][rule_name] = structured
            if not passed:
                overall_passed = False

        log("Rule 1: Ground Coverage", *check_ground_coverage(building.get("plot_area_far", [])))
        log("Rule 2: FAR", *check_far(building.get("plot_area_far", [])))
        log("Rule 3: Habitable Rooms", *combine_room_results(
            check_room_dimensions("bedroom", building.get("bedroom", [])),
            check_room_dimensions("drawingroom", building.get("drawingroom", [])),
            check_room_dimensions("studyroom", building.get("studyroom", []))
        ))
        log("Rule 4: Kitchen", *check_room_dimensions("kitchen", building.get("kitchen", [])))
        log("Rule 5: Bathroom Categories", *check_bathroom_categories(building))
        log("Rule 6: Store", *check_room_dimensions("store", building.get("store", [])))
        log("Rule 7: Staircase", *check_staircase(building.get("riser_treader_width", [])))
        log("Rule 8: Plinth Level", *check_plinth_level(building.get("height_plinth", [])))
        log("Rule 9: Building Height", *check_building_height(building.get("height_plinth", [])))

        human_log.append(
            "Final Verdict: ✅ Passed All Rules"
            if overall_passed else
            "Final Verdict: ❌ Failed One or More Rules"
        )
        human_logs.append("\n".join(human_log))

    # ✅ Instead of writing validation.txt, just return everything
    return {
        "logs": human_logs,
        "structured": structured_results
    }

def combine_room_results(*results):
    passed_all = True
    combined_logs = []
    combined_struct = []
    for res in results:
        passed, logs, struct = res
        if not passed:
            passed_all = False
        combined_logs.extend(logs)
        combined_struct.extend(struct)
    return passed_all, combined_logs, combined_struct

def run_validation():
    with open("output.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return process_rooms(data)

