from ..core import config_map as config
def examples(image_path):
    

    image_path_98_0 = image_path + '98 PBFDKFARID22521/object_2_class4.jpg' 
    image_path_98_1 = image_path + '98 PBFDKFARID22521/object_1_class4.jpg' 

    image_path_96_0 = image_path + '96 PBFDKFARID18539/object_0_class4.jpg' 
    image_path_96_1 = image_path + '96 PBFDKFARID18539/object_1_class4.jpg' 

    image_path_94 = image_path + '94 PBFDKFARID20950/object_1_class4.jpg'

    image_path_89_0 = image_path + '89 PBFDKFARID19707/object_0_class4.jpg'
    image_path_89_1 = image_path + '89 PBFDKFARID19707/object_1_class4.jpg' 
    image_path_89_2 = image_path + '89 PBFDKFARID19707/object_3_class4.jpg' 

    image_path_91_0 = image_path + '91 PBFDKFARID17180/object_0_class4.jpg' 
    image_path_91_1 = image_path + '91 PBFDKFARID17180/object_1_class4.jpg' 
    image_path_91_2 = image_path + '91 PBFDKFARID17180/object_3_class4.jpg' 

    image_path_59_0 = image_path + '59 PBFDKFARID10175/object_0_class4.jpg'
    image_path_59_1 = image_path + '59 PBFDKFARID10175/object_1_class4.jpg'
    example_images_floor = [
        
        {"path": image_path_98_0, 'bedroom':["10\'-0\"x10\'-0\""], 'drawing':["absent"], 'floor':'GROUND'},
        {"path": image_path_98_1, 'bedroom':["absent"], 'drawing':["absent"], 'floor':'TERRACE'},
        
        {"path": image_path_96_1, 'bedroom':["13\'-1\"x16\'"], 'drawing':["absent"], 'floor':'FIRST'},
        {"path": image_path_96_0, 'bedroom':["11\'-6\"x14\', 11\'-3\"x14\'"], 'drawing':["11\'x12\""], 'floor':'GROUND'},
        
        {"path": image_path_94, 'bedroom':["11\'-1\"x12\'", "10\'-4\"x10\'-6\""], 'drawing':["absent"], 'floor':'GROUND'},
        
        {"path": image_path_89_0, 'bedroom':["absent"], 'drawing':["absent"], 'floor':'TERRACE'},
        {"path": image_path_89_1, 'bedroom':["10\'-0\"x12\'-0\""], 'drawing':["10\'-0\"x10\'-3\""], 'floor':'FIRST'},
        {"path": image_path_89_2, 'bedroom':["10\'-0\"x12\'-0\"", "10\'-0\"x12\'-0\""], 'drawing':["10\'-0\"x10\'-3\""], 'floor':'GROUND'},
        
        {"path": image_path_91_0, 'bedroom':["10\'x11\'-10\""], 'drawing':["absent"], 'floor':'FIRST'},
        {"path": image_path_91_1, 'bedroom':["12\'-2\"x10\'-11\"", "12\'-1\"x10\'-11\""], 'drawing':["10\'x11\'-10\""], 'floor':'FIRST'},
        {"path": image_path_91_2, 'bedroom':["absent"], 'drawing':["absent"], 'floor':'TERRACE'},
                                           
        {"path": image_path_59_0, 'bedroom':["4.04x3.05", "4.42x3.05"] , 'drawing':["4.57x3.05"], 'floor':'FIRST'},
        {"path": image_path_59_1, 'bedroom':["4.57x3.05"], 'drawing':["absent"], 'floor':'GROUND'},
        
    ]

    return example_images_floor

#encoded_examples = [{"base64": encode_image(e["path"]), "bedroom":e["bedroom"], "drawing":e["drawing"], "floor":e["floor"]} for e in example_images_floor]
