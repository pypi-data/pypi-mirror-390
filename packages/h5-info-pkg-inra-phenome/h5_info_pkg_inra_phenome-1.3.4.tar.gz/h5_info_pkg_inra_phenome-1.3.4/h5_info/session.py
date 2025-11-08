from datetime import datetime

from h5_info import DATETIME_FORMAT, DATETIME_FORMAT_S


class Session:
    """Store HDF5 Session and Trial attributes in a simplified structure"""
    def __init__(self):
        self.date = ""
        self.experiment_id = ""
        self.experiment_uri = ""
        self.local_infra = ""
        self.national_infra = ""

    def to_json(self):
        json_dict = {
            "date": self.date.strftime(DATETIME_FORMAT_S),
            "experiment_id": self.experiment_id,
            "experiment_uri": self.experiment_uri,
            "local_infra": self.local_infra,
            "national_infra": self.national_infra
        }
        return json_dict

    def from_json(self, json_dict):
        self.date = datetime.strptime(json_dict['date'], DATETIME_FORMAT_S)
        self.experiment_id = json_dict["experiment_id"]
        self.experiment_uri = json_dict["experiment_uri"]
        self.local_infra = json_dict["local_infra"]
        self.national_infra = json_dict["national_infra"]
