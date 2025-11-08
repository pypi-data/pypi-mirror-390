import os

END_LINE = os.linesep  # For Reading
END_LINE_W = '\n'  # For Writing

TYPE_CAMERA = 'camera'
# ST 01032022 : Ajout des deux types d'images RAW (id:2) et JPG (id:11) 
TYPE_IMAGE_RAW = 2
TYPE_IMAGE_JPG = 11
TYPE_LIDAR = 'lidar'
TYPE_MULTISPECTRAL = 'multispectral_camera'

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d_%H:%M:%S.%f'
DATETIME_FORMAT_S = '%Y-%m-%d_%H:%M:%S'
DATETIME_FORMAT_S_TIME_DASHED = '%Y-%m-%d_%H-%M-%S'
REF_TIMESTAMP = 1622117877
