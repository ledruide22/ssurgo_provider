import os
from math import isnan
from pathlib import Path

import geopandas
import pandas as pd
from osgeo import ogr, osr
from shapely.geometry import Point, Polygon

from .object.ssurgo_soil_dto import SoilHorizon, SsurgoSoilDto
from .object.state_info import StateInfo, StateInfoStatus
from .param import states_code


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
