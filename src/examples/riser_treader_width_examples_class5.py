from ..core import config_map as config

def examples(image_path):
    image_path_3 = image_path + '3 PBFDKFARID3327/object_6_class5.jpg'
    image_path_94 = image_path + '94 PBFDKFARID20950/object_3_class5.jpg'
    image_path_5 = image_path + '5 PBFDKFARID6489/object_5_class3.jpg'  # Example with different class, but available
    image_path_89 = image_path + '89 PBFDKFARID19707/object_1_class4.jpg'  # Example with class4, for demonstration
    example_images = [
        {"path": image_path_94, 'riser_treader_width': ["910x270x170xabsent"]},
        {"path": image_path_3, 'riser_treader_width': ["910x250x200xabsent"]},
        {"path": image_path_5, 'riser_treader_width': ["absentxabsentxabsentxabsent"]},
        {"path": image_path_89, 'riser_treader_width': ["910x250x190xabsent"]},
    ]
    return example_images 