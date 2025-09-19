from model.logger.logger import Logger


class Loggable:
    def __init__(self):
        self.logger = Logger()