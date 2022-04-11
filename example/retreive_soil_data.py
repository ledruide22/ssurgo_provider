# This example is base on geodatabase obtain from ssurgo on Ohio area
from shapely.geometry import Point

from src.ssurgo_provider.tools import retrieve_soil_composition, retrieve_state_code, find_ssurgo_state_folder_path, \
    retrieve_multiple_soil_data

states_info_list = coordinates = [(38.477367, -100.5640736)]
states_info_list = retrieve_multiple_soil_data(coordinates)
#points = [Point(coordinate[1], coordinate[0]) for coordinate in coordinates]
#states_info_list = retrieve_state_code(points=points)
#states_info_list = find_ssurgo_state_folder_path(states_info_list)
#soil_data_list = retrieve_soil_composition(states_info_list)
a =1
