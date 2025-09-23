from ..core import config_map as config

def examples(image_path):
    image_path_1_0 = image_path + '2 PBFDKFARID5069/object_1_class4.jpg'
    image_path_1_1 = image_path + '3 PBFDKFARID3327/object_2_class4.jpg'
    image_path_1_2 = image_path + '4 PBFDKFARID2526/object_0_class4.jpg'
    image_path_1_3 = image_path + '5 PBFDKFARID6489/object_1_class4.jpg'
    example_images = [
        {"path": image_path_1_0, 'riser_treader_width': ["900x250x190x2200"], 'floor': 'GROUND'},
        {"path": image_path_1_1, 'riser_treader_width': ["1000x250x190x2200"], 'floor': 'FIRST'},
        {"path": image_path_1_2, 'riser_treader_width': ["900x250xabsentx2200"], 'floor': 'SECOND'},
        {"path": image_path_1_3, 'riser_treader_width': ["absent"], 'floor': 'TERRACE'},
    ]
    return example_images 