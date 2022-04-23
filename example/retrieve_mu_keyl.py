from pathlib import Path

from ssurgo_provider.spatial_tools import retrieve_mu_key_from_raster_by_zone

geojson = {'type': 'Polygon', 'coordinates': [
    [(40.574234, -83.292448), (40.584234, -83.292448), (40.584234, -83.302448), (40.574234, -83.302448),
     (40.574234, -83.292448)]]}

ssurgo_folder_path = Path().absolute().parent / 'resources' / 'SSURGO' / 'gSSURGO_OH.gdb'

mu_key_list = retrieve_mu_key_from_raster_by_zone(geojson, ssurgo_folder_path)
