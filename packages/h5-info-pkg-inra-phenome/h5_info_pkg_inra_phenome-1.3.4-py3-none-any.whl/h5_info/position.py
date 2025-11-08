class Position:
    """Store HDF5 Position attributes in a simplified structure"""
    def __init__(self):
        self.pitch = 0.0
        self.roll = 0.0
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.z = 0

    def to_json(self):
        json_dict = {
            "pitch": self.pitch,
            "roll": self.roll,
            "x": self.x,
            "y": self.y,
            "yaw": self.yaw,
            "z": self.z
        }
        return json_dict

    def from_json(self, json_dict):
        self.pitch = json_dict["pitch"]
        self.roll = json_dict["roll"]
        self.x = json_dict["x"]
        self.y = json_dict["y"]
        self.yaw = json_dict["yaw"]
        self.z = json_dict["z"]
