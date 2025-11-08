from datetime import datetime
import os
import h5py
import json
import struct

from h5_info.constants import END_LINE_W, DATE_FORMAT, DATETIME_FORMAT, DATETIME_FORMAT_S, DATETIME_FORMAT_S_TIME_DASHED, TYPE_CAMERA
from h5_info.errors import DataError, GROUP_ERROR_MESSAGE
from h5_info.geo import Geo
from h5_info.position import Position
from h5_info.logger import Logger
from h5_info.session import Session
from h5_info.sensor import Sensor
from h5_info.plot import Plot
from h5_info.vector import Vector
from h5_info.utils import read_datetime


class H5Info:
    """Structure containing the necessary HDF5 meta-data"""

    def __init__(self):
        """Constructs a H5Info structure directly from a HDF5 file given the list of sensor names"""
        self.session = Session()
        self.plot = Plot()
        self.vector = Vector()
        self.sensors = []
        self.geo = []
        self.static_transforms = {}
        self.geo_filename = "geo.csv"

    def save_metadata(self, filename):
        """Save the current HDF5 Info structure to the given JSON metadata file"""
        Logger.info("Saving '" + filename + "' file")
        geo_fullname = os.path.splitext(filename)[0] + "_geo.csv"
        self.geo_filename = os.path.basename(geo_fullname)
        with open(filename, "w") as file:
            file.write(self.to_json())

        # Save geolocalisation to file <filename>_geo.csv
        Logger.debug("Saving '" + geo_fullname + "' file")
        with open(geo_fullname, "w+") as file:
            file.write("date;longitude;latitude;uncertainty;altitude;uncertainty_altitude;tray_height;heading;course;roll;pitch;sog" + END_LINE_W)
            for geo_item in self.geo:
                geo_item.write_to(file)

    def load_metadata(self, filename):
        """Load a HDF5 Info structure from the given JSON metadata file"""
        Logger.info("Loading '" + filename + "' file")
        with open(filename, "r") as file:
            try:
                self.from_json(file.read())
            except ValueError as error:
                raise DataError(str(error))

        # Load the geolocalisation from _geo.csv file
        geo_fullname = os.path.dirname(filename) + "/" + self.geo_filename
        Logger.debug("Loading '" + geo_fullname + "' file")
        with open(geo_fullname, 'r') as file:
            file.readline()  # Skip headers line
            line = file.readline()
            while line:
                geo_item = Geo()
                geo_item.read_from_line(line)
                self.geo.append(geo_item)
                line = file.readline()

    @staticmethod
    def try_get_key(path, attrs, key):
        try:
            return attrs[key]
        except KeyError:
            Logger.debug("The key '" + str(key) + "' wasn't found in the '" + str(path) + "' metadata")
            return ""

    @staticmethod
    def try_get_key_bytes(path, attrs, key):
        try:
            return str(attrs[key], "utf-8")
        except KeyError:
            Logger.debug("The key '" + str(key) + "' wasn't found in the '" + str(path) + "' metadata")
            return ""

    def load_data(self, h5_file, sensor_names=None):

        if sensor_names is None:
            sensor_names = []

        with h5py.File(h5_file, 'r') as hdf:

            # Load Session Metadata
            ##########################
            session_id = 'Session1'
            Logger.debug("Loading '" + session_id + "' information")
            session_gp = hdf.get(session_id)
            if session_gp is None:
                raise DataError(GROUP_ERROR_MESSAGE, session_id)
            self.session = Session()
            session_str = str(session_gp.attrs['Date'], "utf-8")
            self.session.date = read_datetime(session_str)

            # Load Trial Meta data
            ##########################
            trial_id = "MetaData/TrialInformation"
            Logger.debug("Loading '" + trial_id + "' information")
            trial_gp = hdf.get(trial_id)
            if trial_gp is None:
                Logger.info("No trial information found (manual mode)")
            else:
                trial_attrs = trial_gp.attrs
                if 'ExperimentId' in trial_attrs:
                    self.session.experiment_id = str(trial_attrs['ExperimentId'], "utf-8")
                if 'ExperimentURI' in trial_attrs:
                    self.session.experiment_uri = str(trial_attrs['ExperimentURI'], "utf-8")
                if 'LocalInfrastructure' in trial_attrs:
                    self.session.local_infra = str(trial_attrs['LocalInfrastructure'], "utf-8")
                if 'NationalInfrastructure' in trial_attrs:
                    self.session.national_infra = str(trial_attrs['NationalInfrastructure'], "utf-8")

            # Load Plot Meta data
            ##########################
            plot_id = list(session_gp.items())[0][0]
            Logger.debug("Loading '" + plot_id + "' information")
            plot_gp = session_gp.get(plot_id)
            if plot_gp is None:
                raise DataError(GROUP_ERROR_MESSAGE, plot_id)
            else:
                plot_attrs = plot_gp.attrs
                self.plot = Plot()
                if 'MicroPlotId' in plot_attrs:
                    try:
                        self.plot.id = plot_attrs['MicroPlotId'].decode()
                    except (AttributeError, UnicodeDecodeError):
                        self.plot.id = str(plot_attrs['MicroPlotId'])
                else:
                    self.plot.id = plot_id
                if 'MicroPlotURI' in plot_attrs:
                    self.plot.uri = str(plot_attrs['MicroPlotURI'], "utf-8")
                if 'Coordinates' in plot_attrs:
                    self.plot.coordinates = plot_attrs['Coordinates'].tolist()
                if 'MicroPlotOrientation' in plot_attrs:
                    self.plot.orientation = plot_attrs['MicroPlotOrientation']

            # Load Vector data
            ##########################
            vector_id = "Vector1"
            Logger.debug("Loading '" + vector_id + "' information")
            vector_gp = session_gp.get(vector_id)
            if vector_gp is None:
                raise DataError(GROUP_ERROR_MESSAGE, vector_id)
            vector_attrs = vector_gp.attrs
            self.vector = Vector()
            self.vector.id = str(vector_attrs['EquipmentId'], "utf-8")
            if 'EquipmentURI' in vector_attrs:
                self.vector.uri = str(vector_attrs['EquipmentURI'], "utf-8")
            self.vector.serial_nb = str(vector_attrs['EquipmentSerialNb'], "utf-8")
            self.vector.acquisition_version = str(vector_attrs['AcquisitionVersionId'], "utf-8")
            self.vector.format_version = str(vector_attrs['FormatVersionId'], "utf-8")

            head_data = session_gp.get('Vector1/Head1')
            head_attrs = head_data.attrs
            if 'HeadSerialNb' in head_attrs.keys():
                if 'LITERAL' in str(head_attrs['HeadSerialNb'], "utf-8").upper():
                    self.vector.serial_nb = str(head_attrs['HeadSerialNb'], "utf-8").upper()

            # Load Sensors data
            ##########################
            self.sensors = []

            found_sensors = session_gp.get(vector_id + '/Head1/')
            sensors_list = []
            for sensor_id in found_sensors:
                for sensor_name in sensor_names:
                    if sensor_id.startswith(sensor_name):
                        sensors_list.append(sensor_id)

            for sensor_id in sensors_list:
                Logger.debug("Loading '" + sensor_id + "' information")
                sensor_path = 'Vector1/Head1/' + sensor_id
                sensor_gp = session_gp.get(sensor_path)
                if sensor_gp is None:
                    raise DataError(GROUP_ERROR_MESSAGE, sensor_path)
                sensor_attrs = sensor_gp.attrs

                curr_sensor = Sensor()

                curr_sensor.description = str(sensor_attrs['SensorDescription'], "utf-8")
                curr_sensor.type = Sensor.get_type_from_description(curr_sensor.description)
                curr_sensor.manufacturer = str(sensor_attrs['SensorManufacturer'], "utf-8")
                curr_sensor.model = str(sensor_attrs['SensorModel'], "utf-8")
                curr_sensor.serial_nb = str(sensor_attrs['SensorSerialNb'], "utf-8")
                curr_sensor.firmware = str(sensor_attrs['SensorFirmware'], "utf-8")
                curr_sensor.id = sensor_attrs['SensorId']
                if 'SensorURI' in sensor_attrs:
                    curr_sensor.uri = str(sensor_attrs['SensorURI'], "utf-8")
                curr_sensor.position.pitch = sensor_attrs['Pitch']
                curr_sensor.position.roll = sensor_attrs['Roll']
                curr_sensor.position.x = sensor_attrs['X']
                curr_sensor.position.y = sensor_attrs['Y']
                curr_sensor.position.yaw = sensor_attrs['Yaw']
                curr_sensor.position.z = sensor_attrs['Z']
                # ST 01032022 : Ajout de la lecture du champ "DataFormatId" qui va renseigner
                # le format de trame pour le capteur considéré
                curr_sensor.data_format = sensor_attrs['DataFormatId']

                if curr_sensor.type == TYPE_CAMERA:
                    if session_gp.get('Vector1/Head1/Positioning').attrs['DataFormatId'] == 12:
                        curr_sensor.bayer_grid = self.try_get_key_bytes(sensor_path, sensor_attrs, 'PixelFormat')
                        curr_sensor.focal_length = self.try_get_key(sensor_path, sensor_attrs, 'FocalLength')
                        curr_sensor.pixel_size = self.try_get_key(sensor_path, sensor_attrs, 'PixelSize')
                        curr_sensor.width = self.try_get_key(sensor_path, sensor_attrs, 'Width')
                        curr_sensor.height = self.try_get_key(sensor_path, sensor_attrs, 'Height')
                    else:
                        curr_sensor.bayer_grid = self.try_get_key_bytes(sensor_path, sensor_attrs, 'BayerGrid')
                        curr_sensor.focal_length = self.try_get_key(sensor_path, sensor_attrs, 'FocalLength')
                        curr_sensor.lens_angular_aperture = self.try_get_key(sensor_path, sensor_attrs, 'LensAngularAperture')

                Logger.debug("Loading '" + sensor_id + "' dataset")
                data_gp = plot_gp.get("Measurement1/" + sensor_id)
                curr_sensor.load_data(data_gp, sensor_gp)

                self.sensors.append(curr_sensor)

            # Load Positioning data
            ##########################
            geo_id = "Positioning"
            Logger.debug("Loading '" + geo_id + "' information")
            geo_gp = plot_gp.get("Measurement1/" + geo_id)
            if geo_gp is None:
                raise DataError(GROUP_ERROR_MESSAGE, geo_id)
            geo_data = geo_gp.get('Data')

            offset = 0
            if session_gp.get('Vector1/Head1/Positioning').attrs['DataFormatId'] == 12:
                while geo_data is not None and offset < len(geo_data):
                    geo_item = Geo()
                    geo_item.date = int.from_bytes(geo_data[offset:offset + 8], "little")
                    geo_item.longitude = struct.unpack('d', geo_data[offset + 8:offset + 16])[0]
                    geo_item.latitude = struct.unpack('d', geo_data[offset + 16:offset + 24])[0]
                    geo_item.uncertainty = struct.unpack('d', geo_data[offset + 24:offset + 32])[0]
                    geo_item.altitude = struct.unpack('d', geo_data[offset + 32:offset + 40])[0]
                    geo_item.uncertainty_altitude = struct.unpack('d', geo_data[offset + 40:offset + 48])[0]
                    geo_item.tray_height = struct.unpack('d', geo_data[offset + 48:offset + 56])[0]
                    geo_item.heading = struct.unpack('d', geo_data[offset + 56:offset + 64])[0]
                    geo_item.course = struct.unpack('d', geo_data[offset + 64:offset + 72])[0]
                    geo_item.roll = struct.unpack('d', geo_data[offset + 72:offset + 80])[0]
                    geo_item.pitch = struct.unpack('d', geo_data[offset + 80:offset + 88])[0]
                    geo_item.sog = struct.unpack('d', geo_data[offset + 88:offset + 96])[0]
                    self.geo.append(geo_item)
                    offset += 96

            else:
                while geo_data is not None and offset < len(geo_data):
                    geo_item = Geo()
                    geo_item.date = int.from_bytes(geo_data[offset:offset + 8], "little")
                    geo_item.longitude = struct.unpack('d', geo_data[offset + 8:offset + 16])[0]
                    geo_item.latitude = struct.unpack('d', geo_data[offset + 16:offset + 24])[0]
                    geo_item.uncertainty = struct.unpack('d', geo_data[offset + 24:offset + 32])[0]
                    geo_item.tray_height = struct.unpack('d', geo_data[offset + 32:offset + 40])[0]
                    geo_item.heading = struct.unpack('d', geo_data[offset + 40:offset + 48])[0]
                    geo_item.course = struct.unpack('d', geo_data[offset + 48:offset + 56])[0]
                    geo_item.roll = struct.unpack('d', geo_data[offset + 56:offset + 64])[0]
                    geo_item.pitch = struct.unpack('d', geo_data[offset + 64:offset + 72])[0]
                    geo_item.sog = struct.unpack('d', geo_data[offset + 72:offset + 80])[0]
                    self.geo.append(geo_item)
                    offset += 80

            # Load Static Transform matrix
            #################################
            transform_id = "StaticTransforms"
            Logger.debug("Loading '" + transform_id + "' information")
            matrix_path = 'Vector1/' + transform_id
            matrix_data = session_gp.get(matrix_path)
            if matrix_data is None:
                raise DataError(GROUP_ERROR_MESSAGE, matrix_data)

            for item in matrix_data:
                position = Position()

                position.x = item['X']
                position.y = item['Y']
                position.z = item['Z']
                position.roll = item['Roll']
                position.pitch = item['Pitch']
                position.yaw = item['Yaw']

                self.static_transforms[str(item['ChildReferenceName'], 'utf-8')] = position

    def to_json(self):
        """Converts the H5Info structure into a JSON formatted string"""
        Logger.debug("Converting HDF information to JSON format")
        json_dict = {
            "session": self.session.to_json(),
            "plot": self.plot.to_json(),
            "vector": self.vector.to_json(),
            "geolocalisation": {"filename": self.geo_filename},
            "sensors": [],
            "static_transforms": {}
        }

        for sensor in self.sensors:
            json_dict["sensors"].append(sensor.to_json())

        for key in self.static_transforms:
            json_dict["static_transforms"][key] = self.static_transforms[key].to_json()

        return json.dumps(json_dict, indent=4)

    def from_json(self, json_str):
        json_dict = json.loads(json_str)

        self.session.from_json(json_dict["session"])
        self.plot.from_json(json_dict["plot"])
        self.vector.from_json(json_dict["vector"])

        for sensor_dict in json_dict["sensors"]:
            sensor = Sensor()
            sensor.from_json(sensor_dict)
            self.sensors.append(sensor)

        for key in json_dict["static_transforms"]:
            position = Position()
            position.from_json(json_dict["static_transforms"][key])
            self.static_transforms[key] = position

        self.geo_filename = json_dict["geolocalisation"]["filename"]
