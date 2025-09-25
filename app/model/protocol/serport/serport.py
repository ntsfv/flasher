class SerPort:
    @staticmethod
    def open(port='/dev/ttyUSB0', baudrate=115200):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def reset_input_buffer(self):
        raise NotImplementedError()

    def write(self, data):
        raise NotImplementedError()

    def read(self, size=1):
        raise NotImplementedError()