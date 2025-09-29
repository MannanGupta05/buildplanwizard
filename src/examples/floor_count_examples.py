"""
Floor count examples module.
Note: FloorCountExtractor doesn't use examples, but this module
provides a consistent interface for the buildplanwizard system.
"""

def examples(image_path):
    """
    Returns empty examples list since FloorCountExtractor 
    doesn't use examples - it analyzes legend tables directly.
    """
    return []