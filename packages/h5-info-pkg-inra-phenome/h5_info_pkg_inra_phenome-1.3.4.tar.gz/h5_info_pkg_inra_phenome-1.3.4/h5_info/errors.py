DATA_ERROR_MESSAGE = "Data of type '{0}' is empty, invalid or corrupted"
GROUP_ERROR_MESSAGE = "Cannot locate HDF group '{0}'"


class DataError(Exception):
    """Exception raised for errors in a data."""

    def __init__(self, message, arg=None):
        self.message = message
        self.arg = arg

    def __str__(self):
        if self.arg is None:
            return self.message.format('Unknown element')
        else:
            return self.message.format(self.arg)
