import sys


class Logger:
    # PRIVATE MEMBERS
    #################
    class __Logger:
        def __init__(self, is_debug=False):
            self.is_debug = is_debug

        def __str__(self):
            return repr(self) + str(self.is_debug)

    instance = None

    def __new__(cls):
        return cls.__get_instance()

    def __setattr__(self, attr, is_debug):
        return setattr(self.instance, attr, is_debug)

    @staticmethod
    def __get_instance():
        if not Logger.instance:
            Logger.instance = Logger.__Logger()
        return Logger.instance

    @staticmethod
    def __is_debug():
        return Logger.__get_instance().is_debug

    @staticmethod
    def init(is_debug):
        Logger.__get_instance().is_debug = is_debug

    # PUBLIC MEMBERS
    ################

    @staticmethod
    def info(message):
        sys.stdout.write(message + '\n')

    @staticmethod
    def debug(message):
        if Logger.__is_debug():
            sys.stdout.write(message + '\n')

    @staticmethod
    def warning(message):
        sys.stdout.write('warning: ' + message + '\n')

    @staticmethod
    def error(error):
        if isinstance(error, str):
            sys.stderr.write(error + '\n')
        elif isinstance(error, BaseException):
            sys.stderr.write(str(type(error).__name__) + ": {0}".format(error) + '\n')
