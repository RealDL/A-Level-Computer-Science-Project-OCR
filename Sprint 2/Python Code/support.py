from csv import reader
from os import walk, path
import pygame

def import_csv_layout(path):
	terrain_map = []
	with open(path) as level_map:
		layout = reader(level_map,delimiter = ',')
		for row in layout:
			terrain_map.append(list(row))
		return terrain_map

def import_folder(folder_path):
    surface_list = []
    image_list = []
    send_back = False

    while not send_back:
        for root, dirs, img_files in walk(folder_path):
            for image in img_files:
                full_path = path.join(root, image)
                try:
                    image_surf = pygame.image.load(full_path).convert_alpha()
                except pygame.error:
                    alt_path = path.join('..', folder_path, image)
                    image_surf = pygame.image.load(alt_path).convert_alpha()
                surface_list.append(image_surf)
                image_list.append(full_path)
        if surface_list and image_list:
            send_back = True
        else:
            if not folder_path.startswith('../'):
                folder_path = '../' + folder_path
            else:
                 send_back = True
             
    return surface_list, image_list