from osgeo import ogr


class GbdConnect:
    def __init__(self, ssurgo_folder_path):
        self.ssurgo_folder_path = ssurgo_folder_path
        self.gdb = self.open_connection(ssurgo_folder_path)

    @classmethod
    def open_connection(cls, ssurgo_folder_path):
        """
            This function is usefull to open the ssurgo geo data base containing all soil information
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

    def close_connection(self):
        """
            Usefully method to close connection to the geoDatabase
        """
        self.gdb.close()
