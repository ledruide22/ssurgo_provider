import os
from math import isnan
from pathlib import Path

import geopandas
import pandas as pd
from osgeo import ogr, osr
from shapely.geometry import Point

from .object.ssurgo_soil_dto import SoilHorizon, SsurgoSoilDto
from .object.state_info import StateInfo, StateInfoStatus
from .param import states_code


def retrieve_mu_global_from_raster_by_zone(geojson):
    """
    This function retrieve all ++++++++ in the geojson
    Args:
        geojson (dict): geojson represent the area where mu_global should be find

    Returns:
        (list(dict)): list of  inside the geojson area with their area percentage
    """

    if geojson['type'].lower() != "polygon":
        raise ValueError("Geojson should be of type polygon only")
    return False


def retrieve_multiple_soil_data(coordinates, disable_file_error=True, disable_location_error=True):
    """
    Function to retrieve soil composition from a list of location (coordinates)
    Args:
        coordinates (list(tuple)): list of location [(lat, long), (lat,long), ...]
        disable_file_error (bool): if True disable throw exception when data file is not found for a state
        disable_location_error (bool): if True disable throw exception when location is not in USA

    Returns:
        soil_data_list (list(StateInfo)): list with complete soil StateInfo object
    """
    points = [Point(coordinate[1], coordinate[0]) for coordinate in coordinates]
    states_info_list = retrieve_state_code(points=points, disable_location_error=disable_location_error)
    states_info_list = find_ssurgo_state_folder_path(states_info_list, disable_file_error)
    soil_data_list = manage_retrieve_soils_composition(states_info_list)
    return soil_data_list


def find_ssurgo_state_folder_path(state_info_list, disable_file_error=True):
    """
    Find the gbd folder path associated to the state_code
    Args:
        state_info_list (list): list of StateInfo object with state code complete
        disable_file_error (bool): if true do not stop process with exception if missing file
    Returns:
        (list(path)): path to ssurgo soil data for the state associated to the state_point
    """

    ssurgo_data_pth = os.environ['SSURGO_DATA']
    for state_info in state_info_list:
        if state_info.status == StateInfoStatus.IN_PROGRESS:
            ssurgo_state_folder = f'gSSURGO_{state_info.state_code.upper()}.gdb'
            if ssurgo_state_folder not in os.listdir(ssurgo_data_pth):
                if not disable_file_error:
                    raise ValueError(f"no ssurgo data find for state {state_info.state_code}, please download it")
                else:
                    state_info.status = StateInfoStatus.NO_GDB_FILE_FOUND
            else:
                state_info.state_folder_pth = Path(ssurgo_data_pth) / ssurgo_state_folder
    return state_info_list


def retrieve_state_code(points, disable_location_error=True):
    """
    Find US state code for the point (lat, long)
    Args:
        points (list(Point)): list of Point
        disable_location_error (bool): if false display error and stop process if one point is out of USA
    Returns:
        (list(StateInfo)): list of state_info with US code and update status
    """
    states_info_list = []
    states_shapefile_path = Path().absolute().parent / 'resources' / 'MAP' / 'gadm36_USA_shp' / 'gadm36_USA_1.shp'
    if not states_shapefile_path.exists():
        raise FileNotFoundError(f"no gadm36_USA_1.shp find in {str(states_shapefile_path.parent)}")
    states_gdf = geopandas.read_file(states_shapefile_path)

    for state_name in states_gdf.NAME_1:
        state_code = states_code[state_name.lower().replace(" ", "_")]
        lat_lim = state_code['lat_lim']
        long_lim = state_code['long_lim']
        geom = None
        for point in points:
            if lat_lim[0] <= point.y <= lat_lim[1] and long_lim[0] <= point.x <= long_lim[1]:
                if geom is None:
                    geom = states_gdf[states_gdf.NAME_1 == state_name].geometry.unary_union
                if geom.contains(point):
                    points.remove(point)
                    states_info_list.append(
                        StateInfo(state_code=state_code["code"], points=point,
                                  status=StateInfoStatus.IN_PROGRESS))
        if len(points) == 0:
            return states_info_list

    [states_info_list.append(StateInfo(state_code=None, points=point, status=StateInfoStatus.NOT_IN_USA)) for point in
     points]
    if not disable_location_error:
        raise ValueError(f'point: ({points}) are not in USA, please select a point in USA')
    return states_info_list


def open_gdb(ssurgo_folder_path):
    """
        This function is usefull to open the ssurgo geo data base containing all soil information
    Args:
        ssurgo_folder_path (path): path to the ssurgo .gdb folder

    Returns:
        gdb (DataSource): ssurgo state datasource
    """

    # get the driver
    driver = ogr.GetDriverByName("OpenFileGDB")
    if driver is None:
        raise Exception("OpenFileGDB driver is absent from your gdal installation")

    # opening the FileGDB
    try:
        gdb = driver.Open(str(ssurgo_folder_path), 0)
    except Exception as e:
        raise Exception(f"Unable to open ssurgo gdb {e}")
    return gdb


def find_county_id(points, gdb):
    """
        This function is useful to retrieve county id associated to each locations

    Args:
        points(list): list of Points
        gdb (DataSource): ssurgo state datasource

    Returns:
        pts_info_df (DataFrame): dataframe with county_id for each location
    """
    layer_sa_polygon = gdb.GetLayer("SAPOLYGON")
    pts_info_df = pd.DataFrame({'points': [], 'county_id': []}, columns=['points', 'county_id'])

    try:
        for feature in layer_sa_polygon:
            county_id = feature.GetField("AREASYMBOL")
            geometry = feature.GetGeometryRef()
            for point in points:
                if point.Within(geometry):
                    pt_info = {'county_id': county_id,
                               'points': point}
                    pts_info_df = pts_info_df.append(pt_info, ignore_index=True)
                    points.remove(point)
                    if len(points) < 0:
                        raise ValueError("No more points to iterate")
    except ValueError:
        if len(points) < 0:
            pass
    return pts_info_df


def find_soil_id_ref(pts_info_df, gdb):
    """
    Find soil references related to the soil ID and the location
    Args:
        pts_info_df(DataFrame): see. find_county_id
        gdb (DataSource): ssurgo state datasource

    Returns:
        pts_info_df (DataFrame): dataframe with mu_sym mu_key spatial_ver area_symbol for each location
    """
    layer_mu_polygon = gdb.GetLayer("MUPOLYGON")
    new_pts_info = {'mu_sym': [], 'mu_key': [], 'spatial_ver': [], 'area_symbol': []}
    pts_info_df = pd.concat(
        [pts_info_df, pd.DataFrame(new_pts_info, columns=['mu_sym', 'mu_key', 'spatial_ver', 'area_symbol'])])
    unique_county_id = pts_info_df.county_id.unique()
    for county_id in unique_county_id:
        layer_mu_polygon.SetAttributeFilter(f"AREASYMBOL = '{county_id}'")
        reduce_pts_info_df = pts_info_df[pts_info_df['county_id'] == county_id]
        index_list = list(reduce_pts_info_df.index)
        points_list = list(reduce_pts_info_df.points)

        for feature in layer_mu_polygon:
            geometry = feature.GetGeometryRef()
            if len(index_list) == 0:
                break
            for index, point in zip(index_list, points_list):
                if point.Within(geometry):
                    pts_info_df.mu_sym[index] = feature.GetField("MUSYM")
                    pts_info_df.mu_key[index] = int(feature.GetField("MUKEY"))
                    pts_info_df.spatial_ver[index] = feature.GetField("SPATIALVER")
                    pts_info_df.area_symbol[index] = feature.GetField("AREASYMBOL")
                    index_list.remove(index)
                    points_list.remove(point)

    return pts_info_df


def find_soil_horizon_distribution(pts_info_df, gdb):
    """
        This function is useful to determine the soil horizon distribution by percentage for each location
    Args:
        pts_info_df (datframe): with mu_sym mu_key spatial_ver area_symbol for each location (see find_soil_id_ref)
        gdb (DataSource): ssurgo state datasource

    Returns:
            (dataframe) dataframe with co_key_1/2/3 co_key_1/2/3 for each location

    """
    component = gdb.GetLayer("component")

    new_pts_info = {'co_key_0': [], 'co_key_1': [], 'co_key_2': [], 'co_key_0_pct': [], 'co_key_1_pct': [],
                    'co_key_2_pct': []}
    pts_info_df = pd.concat([pts_info_df, pd.DataFrame(new_pts_info,
                                                       columns=['co_key_0', 'co_key_1', 'co_key_2', 'co_key_0_pct',
                                                                'co_key_1_pct', 'co_key_2_pct'])])
    for mu_key in pts_info_df.mu_key.unique():
        co_key_info = []
        component.SetAttributeFilter(f"mukey = '{int(mu_key)}'")
        for feature_component in component:
            comp_pct = feature_component.GetField("comppct_r")
            co_key_info.append((comp_pct if comp_pct is not None else -1, feature_component.GetField("cokey")))
        co_key_info.sort(reverse=True)
        for idx in pts_info_df[pts_info_df.mu_key == mu_key].index:
            for component_nb in range(0, 3):
                if co_key_info[component_nb][0] > -1:
                    pts_info_df[f"co_key_{component_nb}"][idx] = co_key_info[component_nb][1]
                    pts_info_df[f"co_key_{component_nb}_pct"][idx] = co_key_info[component_nb][0]
                else:
                    pts_info_df[f"co_key_{component_nb}"][idx] = None
                    pts_info_df[f"co_key_{component_nb}_pct"][idx] = None
    return pts_info_df


def extract_soil_horizon_data(pts_info_df, gdb):
    """
        This function is useful to extract all
    Args:
        pts_info_df (dataframe): see find_soil_horizon_distribution
        gdb (DataSource): ssurgo state datasource

    Returns:
        soil_data_dict (dict): dict with SoilHorizon for each co_key in pts_info_df
    """
    co_key_list = list(pts_info_df.co_key_0) + list(pts_info_df.co_key_1) + list(pts_info_df.co_key_2)
    co_key_list_filtered = set([int(co_key) for co_key in co_key_list if not isnan(co_key)])
    c_horizon_polygon = gdb.GetLayer("chorizon")
    soil_data_dict = dict()
    for co_key in co_key_list_filtered:
        feature_nb = c_horizon_polygon.SetAttributeFilter(f"cokey = '{co_key}'")
        if feature_nb == 0:
            soil_data_dict[str(co_key)] = None
        for feature_horizon in c_horizon_polygon:
            soil_data_dict[str(co_key)] = SoilHorizon(None, feature_horizon)

    return soil_data_dict


def build_soil_composition(pts_info_df, soil_data_dict):
    """
        This function is useful to build list of SsurgoSoilDto for each location
    Args:
        pts_info_df (dataframe): see extract_soil_horizon_data
        soil_data_dict (dict): dict with SoilHorizon for each co_key in pts_info_df

    Returns:
        soil_composition_list (list): list of SsurgoSoilDto, one for each location in pts_info_df
    """
    soil_composition_list = []
    for _, pt_info in pts_info_df.iterrows():
        ssurgo_soil_dto = SsurgoSoilDto(pt_info.points.GetX(), pt_info.points.GetY())
        if not isnan(pt_info.co_key_0):
            soil_horizon = soil_data_dict[str(int(pt_info.co_key_0))]
            if soil_horizon is not None:
                soil_horizon.comppct_r = pt_info.co_key_0_pct
            ssurgo_soil_dto.horizon_0 = soil_horizon
        if not isnan(pt_info.co_key_1):
            soil_horizon = soil_data_dict[str(int(pt_info.co_key_1))]
            if soil_horizon is not None:
                soil_horizon.comppct_r = pt_info.co_key_1_pct
            ssurgo_soil_dto.horizon_1 = soil_horizon
        if not isnan(pt_info.co_key_2):
            soil_horizon = soil_data_dict[str(int(pt_info.co_key_2))]
            if soil_horizon is not None:
                soil_horizon.comppct_r = pt_info.co_key_2_pct
            ssurgo_soil_dto.horizon_2 = soil_horizon
        soil_composition_list.append(ssurgo_soil_dto)
    return soil_composition_list


def manage_retrieve_soils_composition(state_info_list):
    sort_by_state = {}
    state_list = []
    for state_info in state_info_list:
        if state_info.status == StateInfoStatus.IN_PROGRESS:
            if state_info not in state_list:
                state_list.append(state_info.state_code)
                sort_by_state[state_info.state_code] = [state_info]
            else:
                sort_by_state[state_info.state_code].append(state_info)
    for state in state_list:
        ssurgo_folder_path = sort_by_state[state][0].state_folder_pth
        coordinates = [(state_info.points.y, state_info.points.x) for state_info in sort_by_state[state]]
        soil_data_list = retrieve_soil_composition(coordinates, ssurgo_folder_path)
        [state_info.set_soil(soil_data)
         for state_info, soil_data in zip(sort_by_state[state], soil_data_list)]
    return state_info_list


def retrieve_soil_composition(coordinates, ssurgo_folder_path):
    """
        This function is usefull to retrieve soil data for the location specified in coordinates
    Args:
        coordinates (list): list of Points (lat, long coordinate) (espg 4326)
        ssurgo_folder_path (path): path to the ssurgo database at the state level

    Returns:
        soil_composition_list (list): list of SsurgoSoilDto, one for each location

    """
    target = osr.SpatialReference()
    target.ImportFromWkt('PROJCS["USA_Contiguous_Albers_Equal_Area_Conic_USGS_version",'
                         'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",'
                         'SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],'
                         'UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],'
                         'PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],'
                         'PARAMETER["Central_Meridian",-96.0],PARAMETER["Standard_Parallel_1",29.5],'
                         'PARAMETER["Standard_Parallel_2",45.5],PARAMETER["Latitude_Of_Origin",23.0],'
                         'UNIT["Meter",1.0],AUTHORITY["ESRI","102039"]]')
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source, target)

    pts_coordinates = []
    point_base = ogr.Geometry(ogr.wkbPoint)
    for coordinate in coordinates:
        point = point_base.__copy__()
        point.AddPoint(coordinate[0], coordinate[1])
        point.Transform(transform)
        pts_coordinates.append(point)

    gdb = open_gdb(ssurgo_folder_path)

    pts_info_df = find_county_id(pts_coordinates, gdb)
    pts_info_df = find_soil_id_ref(pts_info_df, gdb)
    pts_info_df = find_soil_horizon_distribution(pts_info_df, gdb)
    soil_data_dict = extract_soil_horizon_data(pts_info_df, gdb)
    del gdb

    soil_composition_list = build_soil_composition(pts_info_df, soil_data_dict)
    return soil_composition_list
