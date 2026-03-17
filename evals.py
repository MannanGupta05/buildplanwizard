"""
Evals utility: converts the runtime-generated output.json to a CSV row appended
to evals_output.csv in the project root.

This module is only active when the IS_LOCAL environment variable is set to "true".
Do NOT set IS_LOCAL on the deployed server.
"""

import os
import csv
import json
from datetime import datetime

# All variables captured during extraction (must match analysis.py all_variables)
ALL_VARIABLES = [
    "bedroom", "drawingroom", "studyroom", "store", "kitchen",
    "plot_area_far", "setback", "no_of_floors",
    "staircase_riser", "staircase_tread", "staircase_width",
    "total_plot_area", "ground_covered_area", "total_covered_area", "far",
    "front_setback", "rear_setback", "left_side_setback", "right_side_setback",
    "bathroom", "water_closet", "combined_bath_wc",
    "kitchen_only", "kitchen_with_separate_dining", "kitchen_with_separate_store", "kitchen_with_dining",
    "plinth_height", "building_height", "height_plinth",
]

CSV_COLUMNS = ["timestamp", "filename"] + ALL_VARIABLES
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evals_output.csv")


def is_local() -> bool:
    """Return True only when running in a local environment."""
    return os.environ.get("IS_LOCAL", "").lower() == "true"


def json_to_csv(json_path: str) -> None:
    """
    Read the output.json produced at runtime and append one row per entry
    to evals_output.csv.  Does nothing when not running locally.
    """
    if not is_local():
        return

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[evals] Could not read {json_path}: {e}")
        return

    write_header = not os.path.exists(CSV_PATH)

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
        if write_header:
            writer.writeheader()

        timestamp = datetime.now().isoformat(timespec="seconds")

        for filename, entries in data.items():
            # save_to_dict stores entries as a list of dicts; flatten into one row
            if isinstance(entries, list):
                variables = entries[0] if entries else {}
            else:
                variables = entries

            row = {"timestamp": timestamp, "filename": filename}
            for var in ALL_VARIABLES:
                value = variables.get(var, "")
                # Lists are stored as a semicolon-separated string for readability
                if isinstance(value, list):
                    row[var] = "; ".join(str(v) for v in value)
                else:
                    row[var] = value
            writer.writerow(row)

    print(f"[evals] Appended results to {CSV_PATH}")
