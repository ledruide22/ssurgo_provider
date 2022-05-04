from pathlib import Path

import geopandas


class OpenMap:
    def __init__(self, is_permanent=False):
        self.states_gdf = self.__open()
        self.is_permanent = is_permanent

    @classmethod
    def __open(cls):
        map_path = Path().absolute().parent / 'resources' / 'MAP' / 'gadm36_USA_shp' / 'gadm36_USA_1.shp'
        if not map_path.exists():
            raise FileNotFoundError(f"no gadm36_USA_1.shp find in {str(map_path.parent)}")
        return geopandas.read_file(map_path)
