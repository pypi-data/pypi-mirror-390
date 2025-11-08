from datetime import datetime

from h5_info.constants import DATETIME_FORMAT, REF_TIMESTAMP


class LidarImage:
    """Store HDF5 CameraImage attributes in a simplified structure"""

    def __init__(self):
        self.name = ""
        self.date = datetime.utcfromtimestamp(REF_TIMESTAMP)
        self.frequency = 0.0
        self.angle_increment = 0.0
        self.scans = {}

    def to_json(self):
        json_dict = {
            "name": self.name,
            "date": self.date.strftime(DATETIME_FORMAT),
            "frequency": self.frequency,
            "angle_increment": self.angle_increment
        }
        return json_dict

    def from_json(self, json_dict):
        self.name = json_dict["name"]
        self.date = datetime.strptime(json_dict["date"], DATETIME_FORMAT)
        self.frequency = json_dict["frequency"]
        self.angle_increment = json_dict["angle_increment"]
