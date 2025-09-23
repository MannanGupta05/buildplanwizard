from ..core import config_map as config
def examples(image_path):


    image_path_29_0 = image_path + '29 PBFDKFARID4034/object_2_class4.jpg' 
    image_path_29_1 = image_path + '29 PBFDKFARID4034/object_3_class4.jpg'
    image_path_31_0 = image_path + '31 PBFDKFARID7014/object_0_class4.jpg' 
    image_path_31_1 = image_path + '31 PBFDKFARID7014/object_2_class4.jpg' 
    image_path_31_2 = image_path + '31 PBFDKFARID7014/object_3_class4.jpg'
    example_images_floor = [
        {"path": image_path_29_0, 'store':["absent"], 'floor':'FIRST'},
        {"path": image_path_29_1, 'store':["2.08x1.52"], 'floor':'GROUND'},
        {"path": image_path_31_0, 'store':["5\'-6\"x7\'-6\""], 'floor':'FIRST'},
        {"path": image_path_31_1, 'store':["absent"], 'floor':'SECOND'},
        {"path": image_path_31_2, 'store':["5\'-6\"x7\'-6\""], 'floor':'GROUND'},
    ]
    return example_images_floor

# encoded_examples = [{"base64": encode_image(e["path"]), "store":e["store"], "floor":e["floor"]} for e in example_images_floor]