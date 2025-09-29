# 📋 Adding New Rules to the Map Approval System

## Overview

This guide explains how to add a new validation rule to the map approval system. The system follows a structured approach where rules are extracted from building plans using AI, then validated against building codes.

## 🏗️ System Architecture

The rule validation system consists of several key components:

```
📤 User uploads map
    ↓
🔍 YOLO detects image segments (class0, class1, class4, etc.)
    ↓  
🤖 AI Extractors analyze segments → extract building data
    ↓
📊 Data stored in JSON format
    ↓
✅ Rule validators check compliance → generate results
    ↓
📋 Results displayed to user
```

## 📝 Step-by-Step Guide to Add a New Rule

### Step 1: Create the Extractor Class

Create a new extractor in `src/extractors/your_rule_extraction.py`:

```python
import json
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class YourRuleExtractor(BaseExtractor):
    """
    Extractor for [describe what this extracts].
    Uses class[X] images and [describe approach].
    """
    
    def _format_example_output(self, example):
        """Format example for your rule extraction."""
        return {
            "your_field": example["your_field"],
            "floor": example.get("floor", "")  # Include if floor-specific
        }
    
    def _get_target_class_ids(self):
        """Your rule extraction targets class_id [X]."""
        return [X]  # Replace X with appropriate class ID
    
    def _get_query_text(self):
        """Query text for your rule extraction."""
        return "Give [what you want extracted] as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for your rule."""
        # Ensure values are in list format for validation compatibility
        def ensure_list(value):
            if value is None:
                return ["absent"]  # or [0] for numeric values
            elif isinstance(value, list):
                return value
            else:
                return [value]
        
        return {
            "your_field": ensure_list(data_dict.get('your_field'))
        }
    
    def _format_final_output(self, results):
        """Format final output for your rule extraction."""
        return results  # Or customize based on your needs
```

**Key Points:**
- **Inherit from BaseExtractor** for consistent functionality
- **Choose appropriate class_id** (0=legends, 1=area details, 4=floor plans, etc.)
- **Return data in list format** for validation compatibility
- **Handle missing/invalid data** gracefully

### Step 2: Create the Prompt File

Create `src/prompts/your_rule.prompt`:

```
You are an expert architectural plan analyst. Your responses must be in JSON format.

**Task Instructions:**

1. **Image Analysis:** Analyze the provided architectural plan image.
2. **Data Extraction:** Extract [specific information you need].
3. **Validation:** Ensure extracted data is accurate and complete.
4. **Output Format:** Return JSON with key "your_field" containing the extracted value.

Example expected output:
{
    "your_field": "extracted_value"
}
```

### Step 3: Create Examples File (if needed)

Create `src/examples/your_rule_examples.py`:

```python
from ..core import config_map as config

def examples(image_path):
    """
    Returns example data for your rule extraction.
    """
    return [
        {
            "path": image_path + "example1.jpg",
            "your_field": ["example_value_1"],
            "floor": "GROUND"
        },
        {
            "path": image_path + "example2.jpg", 
            "your_field": ["example_value_2"],
            "floor": "FIRST"
        }
    ]
```

**Note:** If your rule doesn't need examples (like floor_count), create an empty examples file or skip this step.

### Step 4: Add Validation Rule

Add your validation function to `src/core/check_rules.py`:

```python
# Add constant at the top with other rules
YOUR_RULE_THRESHOLD = 100  # Replace with your actual threshold

# Add validation function with other check_ functions
def check_your_rule(your_data):
    """Validate your specific rule."""
    logs, structured, passed = [], [], True
    
    for entry in your_data:
        your_value = entry.get("your_field", [0])[0]
        
        try:
            # Convert to appropriate type
            value = float(your_value) if isinstance(your_value, str) else your_value
            
            # Apply your validation logic
            rule_status = "Pass" if value <= YOUR_RULE_THRESHOLD else "Fail"
            
            if rule_status == "Fail":
                passed = False
                logs.append(f"Your rule failed: {value} exceeds {YOUR_RULE_THRESHOLD}")
            
            structured.append({
                "rule": "Your Rule Name",
                "recorded_value": value,
                "expected_value": f"≤ {YOUR_RULE_THRESHOLD}",
                "status": rule_status,
                "reason": "OK" if rule_status == "Pass" else "Exceeds permitted limit"
            })
            
        except (ValueError, TypeError):
            passed = False
            logs.append(f"Invalid value for your rule: {your_value}")
            structured.append({
                "rule": "Your Rule Name",
                "recorded_value": f"Invalid: {your_value}",
                "expected_value": f"Valid number ≤ {YOUR_RULE_THRESHOLD}",
                "status": "Fail",
                "reason": "Invalid or non-numeric value"
            })
    
    return passed, logs, structured
```

**Then integrate it into the main validation pipeline:**

Find the `process_rooms()` function and add your rule:

```python
log("Rule X: Your Rule Name", *check_your_rule(building.get("your_rule", [])))
```

Replace `X` with the next available rule number.

### Step 5: Update Configuration

Add your prompt path to `src/core/config_map.py`:

```python
your_rule_promptfile = "src/prompts/your_rule.prompt"
```

### Step 6: Register in Web System

Update `web/buildplanwizard.py`:

**Add imports:**
```python
from src.extractors.your_rule_extraction import YourRuleExtractor
from src.examples import your_rule_examples  # If using examples
```

**Add to extractor mapping:**
```python
# In get_extractor_func()
"your_rule": YourRuleExtractor,
```

**Add to prompt mapping:**
```python
# In get_prompt_for_var()
"your_rule": config.your_rule_promptfile,
```

**Add to examples (if using):**
```python
# In Examples class _examples_dict
"your_rule": your_rule_examples.examples,

# Add property to Examples class
@property
def your_rule(self):
    return self._examples_dict["your_rule"](self.image_path)
```

### Step 7: Add to Extraction Pipeline

Update `web/analysis.py`:

Add your rule to the extraction list:

```python
variables_to_extract = [
    "bedroom", "drawingroom", "studyroom", "store", "bathroom", 
    "water_closet", "combined_bath_wc", "kitchen", "plot_area_far", 
    "lobby", "dining", "riser_treader_width", "height_plinth", 
    "floor_count", "your_rule"  # Add your rule here
]
```

### Step 8: Update Module Exports

Update `src/extractors/__init__.py`:

```python
from .your_rule_extraction import YourRuleExtractor

__all__ = [
    'BaseExtractor',
    # ... other extractors ...
    'YourRuleExtractor'
]
```

## 🧪 Testing Your New Rule

1. **Restart the Flask application**
2. **Upload a test building plan**
3. **Check the validation results** for your new rule
4. **Debug any issues** by checking console logs

## 📋 Checklist

Use this checklist to ensure you've completed all steps:

- [ ] ✅ Created extractor class (`src/extractors/your_rule_extraction.py`)
- [ ] ✅ Created prompt file (`src/prompts/your_rule.prompt`)
- [ ] ✅ Created examples file (`src/examples/your_rule_examples.py`) - if needed
- [ ] ✅ Added validation function (`src/core/check_rules.py`)
- [ ] ✅ Integrated rule in validation pipeline (`check_rules.py`)
- [ ] ✅ Added config entry (`src/core/config_map.py`)
- [ ] ✅ Updated buildplanwizard mappings (`web/buildplanwizard.py`)
- [ ] ✅ Added to extraction pipeline (`web/analysis.py`)
- [ ] ✅ Updated module exports (`src/extractors/__init__.py`)
- [ ] ✅ Tested with sample building plan

## 🎯 Example: Floor Count Rule

For reference, see how the floor count rule was implemented:

- **Extractor**: `src/extractors/floor_count_extraction.py`
- **Prompt**: `src/prompts/floor_count.prompt`
- **Validation**: `check_floor_count()` in `src/core/check_rules.py`
- **Integration**: Added as "Rule 10: Floor Count"

## 🔧 Common Patterns

### Class ID Usage:
- **class_id 0**: Legend tables, title blocks
- **class_id 1**: Area details, FAR information  
- **class_id 3**: Height/elevation information
- **class_id 4**: Floor plans, room layouts
- **class_id 5**: Staircase details

### Data Format:
- **Always wrap values in lists** for validation compatibility
- **Handle missing data** with appropriate defaults
- **Use consistent field naming** across extractor and validator

### Error Handling:
- **Graceful degradation** for missing/invalid data
- **Clear error messages** for debugging
- **Structured output** for web display

## 🚀 Tips for Success

1. **Follow existing patterns** - Look at similar extractors for guidance
2. **Test incrementally** - Verify each component works before integration
3. **Use descriptive names** - Make your code self-documenting
4. **Handle edge cases** - Consider missing data, invalid formats, etc.
5. **Document your logic** - Add comments explaining validation criteria
6. **Keep it simple** - Start with basic functionality, then enhance

## 🐛 Troubleshooting

### Common Issues:

**Import Errors:**
- Check all import paths are correct
- Ensure `__init__.py` files are updated

**Validation Not Running:**
- Verify rule is added to `process_rooms()` function
- Check data key matches between extractor and validator

**Data Format Issues:**
- Ensure extractor returns data in list format
- Check validation function expects correct data structure

**Web Integration Problems:**
- Verify variable name is in `variables_to_extract` list
- Check all buildplanwizard mappings are complete

---

**Happy coding! 🎉 Your new rule will help ensure building plans meet safety and regulatory requirements.**