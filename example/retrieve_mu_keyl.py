from pathlib import Path

from ssurgo_provider.spatial_tools import retrieve_mu_key_from_raster_by_zone, convert_geojson_to_polygon

geojson = {'type': 'Polygon', 'coordinates': [
    (-83.292448, 40.574234), (-83.292448, 40.584234), (-83.302448, 40.584234), (-83.302448, 40.574234),
    (-83.292448, 40.574234)]}  # [(long, lat), (long,lat)]
ssurgo_folder_path = Path().absolute().parent / 'resources' / 'SSURGO' / 'gSSURGO_OH.gdb'
polygon = convert_geojson_to_polygon(geojson)
mu_key_dict = retrieve_mu_key_from_raster_by_zone(polygon, ssurgo_folder_path)
