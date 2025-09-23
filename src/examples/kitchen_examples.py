from ..core import config_map as config

def examples(image_path):
    image_path_2_0 = image_path + '2 PBFDKFARID5069/object_1_class4.jpg'
    image_path_2_1 = image_path + '2 PBFDKFARID5069/object_3_class4.jpg'
    image_path_2_2 = image_path + '2 PBFDKFARID5069/object_6_class4.jpg'
    image_path_2_3 = image_path + '2 PBFDKFARID5069/object_7_class4.jpg'

    image_path_27_0 = image_path + '27 PBFDKFARID8026/object_0_class4.jpg'
    image_path_27_1 = image_path + '27 PBFDKFARID8026/object_1_class4.jpg'
    image_path_27_2 = image_path + '27 PBFDKFARID8026/object_5_class4.jpg'

    image_path_32_0 = image_path + '32 PBFDKFARID5331/object_0_class4.jpg'
    image_path_32_1 = image_path + '32 PBFDKFARID5331/object_4_class4.jpg'

    example_images_floor = [
        {"path": image_path_2_0, 'kitchen': ["11'-10.5\"x8'-4.5\""], 'floor': 'GROUND'},
        {"path": image_path_2_1, 'kitchen': ["absent"], 'floor': 'FIRST'},
        {"path": image_path_2_2, 'kitchen': ["absent"], 'floor': 'TERRACE'},
        {"path": image_path_2_3, 'kitchen': ["absent"], 'floor': 'TERRACE'},

        {"path": image_path_27_0, 'kitchen': ["3.05x2.90"], 'floor': 'GROUND'},
        {"path": image_path_27_1, 'kitchen': ["absent"], 'floor': 'FIRST'},
        {"path": image_path_27_2, 'kitchen': ["absent"], 'floor': 'DEMOLISH'},

        {"path": image_path_32_0, 'kitchen': ["absent"], 'floor': 'GROUND'},
        {"path": image_path_32_1, 'kitchen': ["absent"], 'floor': 'FIRST'},
    ]

    return example_images_floor


# encoded_examples = [{"base64": encode_image(e["path"]), "kitchen": e["kitchen"], "floor": e["floor"]} for e in example_images_floor ]

