import pandas as pd
from osgeo import ogr


def open_gdb(ssurgo_folder_path):
    """
        This function is usefull to open the suurgo geo data base containing all soil information
    Args:
        ssurgo_folder_path (path): path to the ssurgo .gdb folder

    Returns:

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
    layer_mu_polygon = gdb.GetLayer("MUPOLYGON")
    # MUSYM MUKEY SPATIALVER AREASYMBOL layer.SetAttributeFilter('continent = "Asia"')

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
                    pts_info_df.mu_key[index] = feature.GetField("MUKEY")
                    pts_info_df.spatial_ver[index] = feature.GetField("SPATIALVER")
                    pts_info_df.area_symbol[index] = feature.GetField("AREASYMBOL")
                    index_list.remove(index)
                    points_list.remove(point)

    return pts_info_df


def retrieve_soil_composition(coordinates, ssurgo_folder_path):
    pts_coordinates = []
    point_base = ogr.Geometry(ogr.wkbPoint)
    for coordinate in coordinates:
        point = point_base.__copy__()
        point.AddPoint(coordinate[0], coordinate[1])
        pts_coordinates.append(point)

    gdb = open_gdb(ssurgo_folder_path)

    pts_info_df = find_county_id(pts_coordinates, gdb)
    soil_id_ref = find_soil_id_ref(pts_info_df, gdb)

    del gdb
    return True
