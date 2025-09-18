import config_map as config

def examples(image_path):

    image_path_3_0 = image_path + '3 PBFDKFARID3327/object_1_class4.jpg' 
    image_path_3_1 = image_path + '3 PBFDKFARID3327/object_3_class4.jpg'

    image_path_4_0 = image_path + '4 PBFDKFARID2526/object_0_class4.jpg'
    image_path_4_1 = image_path + '4 PBFDKFARID2526/object_3_class4.jpg' 
    image_path_4_2 = image_path + '4 PBFDKFARID2526/object_5_class4.jpg'

    example_images_floor = [
        {"path": image_path_3_0, 'lobby': ["absent"], 'dining': ["absent"], 'floor': 'FIRST'},
        {"path": image_path_3_1, 'lobby': ["3.2 X 5.0"], 'dining': ["absent"], 'floor': 'GROUND'},

        {"path": image_path_4_0, 'lobby': ["21'-10.5\" X 22'-0\""], 'dining': ["10'x8'-6\""], 'floor': 'GROUND'},
        {"path": image_path_4_1, 'lobby': ["21'-10.5\" X 22'-0\""], 'dining': ["absent"], 'floor': 'FIRST'},
        {"path": image_path_4_2, 'lobby': ["absent"], 'dining': ["absent"], 'floor': 'TERRACE'},
    ]

    return example_images_floor
