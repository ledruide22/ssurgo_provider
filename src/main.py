import pandas as pd
from osgeo import ogr

from src.object.ssurgo_soil_dto import SoilHorizon


def open_gdb(ssurgo_folder_path):
    """
        This function is usefull to open the suurgo geo data base containing all soil information
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


def find_soil_composition(pts_info_df, gdb):
    component = gdb.GetLayer("component")
    c_horizon_polygon = gdb.GetLayer("chorizon")
    result_temps = []
    for mu_key in pts_info_df.mu_key.unique():
        component.SetAttributeFilter(f"mukey = '{int(mu_key)}'")
        co_keys = []
        for feature_component in component:
            co_keys.append(feature_component.GetField("cokey"))
        for co_key in co_keys:
            c_horizon_polygon.SetAttributeFilter(f"cokey = '{co_key}'")
            for feature_horizon in c_horizon_polygon:
                result_temps.append(SoilHorizon(feature_horizon))
        print('finish')
    return True


def retrieve_soil_composition(coordinates, ssurgo_folder_path):
    """
        This function is usefull to retrieve soil data for the location specified in coordinates
    Args:
        coordinates (list): list of Points (lat, long coordinate)
        ssurgo_folder_path (path): path to the ssurgo database at the state level

    Returns:

    """
    pts_coordinates = []
    point_base = ogr.Geometry(ogr.wkbPoint)
    for coordinate in coordinates:
        point = point_base.__copy__()
        point.AddPoint(coordinate[0], coordinate[1])
        pts_coordinates.append(point)

    gdb = open_gdb(ssurgo_folder_path)

    pts_info_df = find_county_id(pts_coordinates, gdb)
    pts_info_df = find_soil_id_ref(pts_info_df, gdb)
    pts_info_df = find_soil_horizon_distribution(pts_info_df, gdb)
    #find_soil_composition(pts_info_df, gdb)

    del gdb
    return True
