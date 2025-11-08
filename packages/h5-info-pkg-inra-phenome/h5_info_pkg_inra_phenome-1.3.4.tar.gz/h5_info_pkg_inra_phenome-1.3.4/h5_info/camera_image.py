from datetime import datetime

from h5_info.constants import DATETIME_FORMAT, REF_TIMESTAMP


class CameraImage:
    """Store HDF5 CameraImage attributes in a simplified structure"""
    def __init__(self):
        self.name = ""
        self.date = datetime.utcfromtimestamp(REF_TIMESTAMP)
        self.shutter_time = 0
        self.width = 0
        self.height = 0
        self.size = 0
        self.image = None

    def to_json(self):
        json_dict = {
            "name": self.name,
            "date": self.date.strftime(DATETIME_FORMAT),
            "shutter_time": self.shutter_time,
            "width": self.width,
            "height": self.height,
            "size": self.size
        }
        return json_dict

    def from_json(self, json_dict):
        self.name = json_dict["name"]
        self.date = datetime.strptime(json_dict["date"], DATETIME_FORMAT)
        self.shutter_time = json_dict["shutter_time"]
        self.width = json_dict["width"]
        self.height = json_dict["height"]
        self.size = json_dict["size"]
