class Vector:
    """Store HDF5 Vector attributes in a simplified structure"""
    def __init__(self):
        self.id = ""
        self.uri = ""
        self.serial_nb = ""
        self.acquisition_version = ""
        self.format_version = ""

    def to_json(self):
        json_dict = {
            "id": self.id,
            "uri": self.uri,
            "serial_nb": self.serial_nb,
            "acquisition_version": self.acquisition_version,
            "format_version": self.format_version
        }
        return json_dict

    def from_json(self, json_dict):
        self.id = json_dict["id"]
        self.uri = json_dict["uri"]
        self.serial_nb = json_dict["serial_nb"]
        self.acquisition_version = json_dict["acquisition_version"]
        self.format_version = json_dict["format_version"]
