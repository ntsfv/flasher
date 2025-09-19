import sys
import serial
import glob


# https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def list_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        # self.log_err("Невозможно открыть порты - неподдерживаемая платформа")
        raise EnvironmentError('Unsupported platform')

    result = []
    # self.log_dbg(ports)
    for port in ports:
        try:
            s = serial.Serial(port, baudrate=115200)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    # self.log_dbg(result)
    return result