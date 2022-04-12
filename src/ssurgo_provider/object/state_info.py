from enum import Enum


class StateInfo:
    def __init__(self, state_code, points, status):
        self.status = status
        self.state_code = state_code
        self.points = points
        self.state_folder_pth = None
        self.soil_data = None

    def set_soil(self, soil_data):
        self.soil_data = soil_data
        self.status = StateInfoStatus.SUCCEED

    def soil_data_to_dict(self):
        return self.soil_data.to_dict()


class StateInfoStatus(Enum):
    NOT_IN_USA = "FAILED"
    NO_GDB_FILE_FOUND = "FAILED"
    SUCCEED = "SUCCEED"
    IN_PROGRESS = "PENDING"
