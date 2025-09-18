import config_map as config

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
        # image_path_2_0: Room labeled "TOILET" → Combined Bath and W.C.
        {"path": image_path_2_0, 
         'Bathroom': ["absent"], 
         'Water Closet (W.C.)': ["absent"], 
         'Combined Bath and W.C.': ["5'-9\"x6'-9\""], 
         'floor': 'GROUND'},
        
        # image_path_2_1: Room labeled "W.C." → Water Closet (W.C.)
        {"path": image_path_2_1, 
         'Bathroom': ["absent"], 
         'Water Closet (W.C.)': ["6'-9\"x5'-0\""], 
         'Combined Bath and W.C.': ["absent"], 
         'floor': 'FIRST'},
        
        # image_path_2_2: No bathroom-related rooms
        {"path": image_path_2_2, 
         'Bathroom': ["absent"], 
         'Water Closet (W.C.)': ["absent"], 
         'Combined Bath and W.C.': ["absent"], 
         'floor': 'TERRACE'},
        
        # image_path_2_3: No bathroom-related rooms
        {"path": image_path_2_3, 
         'Bathroom': ["absent"], 
         'Water Closet (W.C.)': ["absent"], 
         'Combined Bath and W.C.': ["absent"], 
         'floor': 'TERRACE'},

        # image_path_27_0: Two rooms labeled "TOILET" → Combined Bath and W.C.
        {"path": image_path_27_0, 
         'Bathroom': ["absent"], 
         'Water Closet (W.C.)': ["absent"], 
         'Combined Bath and W.C.': ["1.52x1.87", "1.52x2.32"], 
         'floor': 'GROUND'},
        
        # image_path_27_1: No bathroom-related rooms
        {"path": image_path_27_1, 
         'Bathroom': ["absent"], 
         'Water Closet (W.C.)': ["absent"], 
         'Combined Bath and W.C.': ["absent"], 
         'floor': 'FIRST'},
        
        # image_path_27_2: DEMOLISH PLAN → all absent
        {"path": image_path_27_2, 
         'Bathroom': ["absent"], 
         'Water Closet (W.C.)': ["absent"], 
         'Combined Bath and W.C.': ["absent"], 
         'floor': 'DEMOLISH'},

        # image_path_32_0: No bathroom-related rooms
        {"path": image_path_32_0, 
         'Bathroom': ["absent"], 
         'Water Closet (W.C.)': ["absent"], 
         'Combined Bath and W.C.': ["absent"], 
         'floor': 'GROUND'},
        
        # image_path_32_1: No bathroom-related rooms
        {"path": image_path_32_1, 
         'Bathroom': ["absent"], 
         'Water Closet (W.C.)': ["absent"], 
         'Combined Bath and W.C.': ["absent"], 
         'floor': 'FIRST'},
    ]

    return example_images_floor


# encoded_examples = [{"base64": encode_image(e["path"]), "Bathroom": e["Bathroom"], "Water Closet (W.C.)": e["Water Closet (W.C.)"], "Combined Bath and W.C.": e["Combined Bath and W.C."], "floor": e["floor"]} for e in example_images_floor]
