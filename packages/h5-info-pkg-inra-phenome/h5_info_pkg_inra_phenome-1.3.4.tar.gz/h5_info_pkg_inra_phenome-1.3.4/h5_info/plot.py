class Plot:
    """Store HDF5 Plot attributes in a simplified structure"""
    def __init__(self):
        self.id = ""
        self.uri = ""
        self.coordinates = []
        self.orientation = ""

    def to_json(self):
        json_dict = {
            "id": self.id,
            "uri": self.uri,
            "coordinates": self.coordinates,
            "orientation": self.orientation
        }
        return json_dict

    def from_json(self, json_dict):
        self.id = json_dict["id"]
        self.uri = json_dict["uri"]
        self.coordinates = json_dict["coordinates"]
        self.orientation = json_dict["orientation"]
