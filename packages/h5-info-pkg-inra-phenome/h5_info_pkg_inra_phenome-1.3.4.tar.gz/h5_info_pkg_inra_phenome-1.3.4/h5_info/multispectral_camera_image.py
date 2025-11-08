from datetime import datetime

from h5_info.constants import DATETIME_FORMAT, REF_TIMESTAMP


class MultispectralCameraImage:
    """Store HDF5 MultispectralCameraImage attributes in a simplified structure"""
    def __init__(self):
        self.name = ""
        self.date = datetime.utcfromtimestamp(REF_TIMESTAMP)
        self.size = 0
        self.data = None
        self.channel = 0

    def to_json(self):
        json_dict = {
            "name": self.name,
            "date": self.date.strftime(DATETIME_FORMAT),
            "size": self.size,
            "channel": self.channel
        }
        return json_dict

    def from_json(self, json_dict):
        self.name = json_dict["name"]
        self.date = datetime.strptime(json_dict["date"], DATETIME_FORMAT)
        self.size = json_dict["size"]
        self.channel = json_dict["channel"]
