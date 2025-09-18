import config_map as config

def examples(image_path):
    image_path_98_0 = image_path + '98 PBFDKFARID22521/object_1_class4.jpg'
    image_path_98_1 = image_path + '98 PBFDKFARID22521/object_2_class4.jpg'
    image_path_2 = image_path + '2 PBFDKFARID5069/object_1_class4.jpg'
    image_path_89_0 = image_path + '89 PBFDKFARID19707/object_1_class4.jpg'
    image_path_89_1 = image_path + '89 PBFDKFARID19707/object_3_class4.jpg'
    example_images = [
        {"path": image_path_98_0, 'riser_treader_width': ["absentxabsentxabsentxabsent"], 'floor': 'TERRACE'},
        {"path": image_path_98_1, 'riser_treader_width': ["absentxabsentxabsentxabsent"], 'floor': 'GROUND'},
        {"path": image_path_2, 'riser_treader_width': ["990x250x190xabsent"], 'floor': 'GROUND'},
        {"path": image_path_89_0, 'riser_treader_width': ["910x250x190xabsent", "990x250x200xabsent"], 'floor': 'FIRST'},
        {"path": image_path_89_1, 'riser_treader_width': ["990x250x200xabsent"], 'floor': 'GROUND'},
    ]
    return example_images 