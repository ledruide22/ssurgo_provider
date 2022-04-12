# This example is base on geodatabase obtain from ssurgo on Ohio area

from src.ssurgo_provider.tools import retrieve_multiple_soil_data

coordinates = [(38.477367, -100.5640736)]
states_info_list = retrieve_multiple_soil_data(coordinates)
