from ..core import config_map as config

def examples(image_path):
    image_path_29_0 = image_path + '30 PBFDKFARID7804/object_2_class3.jpg'
    #image_path_30_0 = image_path + '159267/object_0_class3.jpg'
    #image_path_30_1 = image_path + '159267/object_2_class3.jpg'
    #image_path_31_0 = image_path + '85 PBFDKFARID8942/object_2_class3.jpg'

    example_images_height = [
        {"path": image_path_29_0, 'height': ["7.60"], 'plinth level': ["0.46"]},
        #{"path": image_path_30_0, 'height': ["28' 6\""], 'plinth level': ["2' 0\""]},
        #{"path": image_path_30_1, 'height': ["28' 6\""], 'plinth level': ["2' 0\""]},
        #{"path": image_path_31_0, 'height': ["4.50"], 'plinth level': ["0.46"]},
    ]
    return example_images_height

# Example encoding call:
# encoded_examples = [{"base64": encode_image(e["path"]), "height":e["height"], "plinth level":e["plinth level"]} for e in example_images_height]
