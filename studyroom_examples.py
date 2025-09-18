import config_map as config

def examples(image_path):
    image_path_19_0 = image_path + '19 PBFDKFARID4757/object_1_class4.jpg'
    image_path_19_1 = image_path + '19 PBFDKFARID4757/object_3_class4.jpg'

    image_path_20_0 = image_path + '20 PBFDKFARID3366/object_0_class4.jpg'
    image_path_20_1 = image_path + '20 PBFDKFARID3366/object_1_class4.jpg'

    image_path_31_0 = image_path + '31 PBFDKFARID7014/object_0_class4.jpg'
    image_path_31_1 = image_path + '31 PBFDKFARID7014/object_2_class4.jpg'
    image_path_31_2 = image_path + '31 PBFDKFARID7014/object_3_class4.jpg'

    image_path_18 = image_path + '18 PBFDKFARID4621/object_5_class4.jpg'

    example_images_floor = [
        {"path": image_path_19_0, 'study': ["absent"], 'floor': 'FIRST'},
        {"path": image_path_19_1, 'study': ["absent"], 'floor': 'GROUND'},

        {"path": image_path_31_0, 'study': ["11'-0\"x6'-11\""], 'floor': 'FIRST'},
        {"path": image_path_31_1, 'study': ["absent"], 'floor': 'SECOND'},
        {"path": image_path_31_2, 'study': ["absent"], 'floor': 'GROUND'},

        {"path": image_path_18, 'study': ["absent"], 'floor': 'FIRST'},
    ]

    return example_images_floor


# Encoded version of the examples
#def encoded_examples(image_path):
#    data = examples(image_path)
#    return [{"base64": encode_image(e["path"]), "study": e["study"], "floor": e["floor"]} for e in data]
