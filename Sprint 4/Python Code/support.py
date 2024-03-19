from Scripts.logger import *
try:
    from csv import reader
    from os import walk, path
    import pygame
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")

logger.debug("RealDL Support Code.")

def import_csv_layout(path):
    terrain_map =[]

    try:
        with open(path) as level_map:
            layout = reader(level_map,delimiter = ',')
            for row in layout:
                terrain_map.append(list(row))
    except:
        with open(f"../{path}") as level_map:
            layout = reader(level_map,delimiter = ',')
            for row in layout:
                terrain_map.append(list(row))
    return terrain_map

def import_folder(folder_path,return_image_list=False):
    surface_list = []
    image_list = []
    values = False

    while not values:
        for root, dirs, img_files in walk(folder_path):
            for image in img_files:
                full_path = path.join(root, image)
                try:
                    image_surf = pygame.image.load(full_path).convert_alpha()
                except:
                    image_surf = pygame.image.load(f"../{full_path}").convert_alpha()
                surface_list.append(image_surf)
                image_list.append(full_path)
        if surface_list and image_list:
            values = True  
        else:
            if "../" in folder_path:
                values = True
            else:
                folder_path = "../" + folder_path

    if return_image_list == True:
        return surface_list, image_list
    elif return_image_list == None:
        return image_list
    else:
        return surface_list