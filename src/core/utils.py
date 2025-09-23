import base64
import re 

def encode_image(image_input):
    import base64

    if isinstance(image_input, bytes):
        return base64.b64encode(image_input).decode("utf-8")
    elif isinstance(image_input, str):
        with open(image_input, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    else:
        raise TypeError("Input must be a file path or bytes.")

r'''
def escape_inches(st):
    # Add a single backslash before a " that follows a digit
    return re.sub(r'(?<=\d)"', '\\"', st)
'''

def escape_inches(s):
    """
    Sanitize a malformed JSON string:
    - Replace invalid escaped single quotes (\' -> ')
    - Escape inch marks (") properly after digits
    - Remove invalid backslashes
    """
    # Step 1: Fix wrongly escaped single quotes (\' → ')
    s = s.replace("\\'", "'")

    # Step 2: Escape inch marks after digits (e.g., 7'-0"x6'-0")
    s = re.sub(r'(?<=\d)"', r'\\"', s)

    # Step 3: Remove invalid backslashes (e.g., \x)
    s = re.sub(r'\\(?!["\\/bfnrtu])', '', s)

    return s


def save_to_dict(data_dict, key, **room_data):
    """
    Appends room data under a given key (e.g., image name) in a dictionary.

    Parameters:
    - data_dict: the main dictionary to update
    - key: the image name or unique identifier
    - **room_data: keyword arguments like bedroom=..., drawingroom=...
    """
    if data_dict is None:
        data_dict = {}

    entry = {room: values for room, values in room_data.items()}

    if key in data_dict:
        data_dict[key].append(entry)
    else:
        data_dict[key] = [entry]

    return data_dict

