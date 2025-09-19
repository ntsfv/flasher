from model.logger.loggable import Loggable


class ProtException(Exception, Loggable):
    def __init__(self, msg):
        Loggable.__init__(self)
        self.logger.error(msg)
        Exception.__init__(self, msg)