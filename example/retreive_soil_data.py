from pathlib import Path

from src.main import retrieve_soil_composition

# This example is base on geodatabase obtain from ssurgo on Ohio area
ssurgo_folder_path = Path().absolute().parent / 'resources' / 'SSURGO' / 'soils_GSSURGO_oh_3905571_01' \
                     / 'soils' / 'gssurgo_g_oh' / 'gSSURGO_OH.gdb'
coordinates = [(40.574234, -83.292448), (40.519224, -82.799437), (40.521048, -82.790174)]

soil_data_list = retrieve_soil_composition(coordinates, ssurgo_folder_path)
