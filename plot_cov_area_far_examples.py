import config_map as config

def examples(image_path):
    image_path_2 = image_path + '2 PBFDKFARID5069/object_0_class1.jpg'
    image_path_96 = image_path + '96 PBFDKFARID18539/object_5_class1.jpg'
    image_path_94 = image_path + '94 PBFDKFARID20950/object_2_class1.jpg'
    image_path_91 = image_path + '91 PBFDKFARID17180/object_5_class1.jpg'
    image_path_5 = image_path + '5 PBFDKFARID6489/object_4_class1.jpg'

    example_images = [
        {"path": image_path_2, "total_plot_area": 167.22, "total_covered_area": 131.5, "far": "1:0.78"},
        {"path": image_path_96, "total_plot_area": 203.48, "total_covered_area": 180, "far": "1:0.88"},
        {"path": image_path_94, "total_plot_area": 101.58, "total_covered_area": 87, "far": "1:0.85"},
        {"path": image_path_91, "total_plot_area": 92, "total_covered_area": 130, "far": "1:1.40"},
        {"path": image_path_5, "total_plot_area": 195, "total_covered_area": 153, "far": "1:0.7847"},
    ]

    return example_images
