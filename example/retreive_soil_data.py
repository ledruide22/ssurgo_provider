from pathlib import Path

from src.main import retrieve_soil_composition

ssurgo_folder_path = Path().absolute().parent / 'resources' / 'SSURGO' / 'soils_GSSURGO_oh_3905571_01' \
                     / 'soils' / 'gssurgo_g_oh' / 'gSSURGO_OH.gdb'
coordinates = [(993448, 1954498), (962309, 2065705), (993448, 2065705)]

soil_data_list = retrieve_soil_composition(coordinates, ssurgo_folder_path)
