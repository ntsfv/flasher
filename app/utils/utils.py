import inspect

from model.logger.logger import Logger


def text2int(q_object):
    try:
        num = int(q_object.text(), 10)
        num_format = 'dec'
    except ValueError:
        num = int(q_object.text(), 16)
        num_format = 'hex'
    return num, num_format

def save_bin(name, data):
    Logger().info("Сохранение %0d байт данных в файл %s" % (len(data), name))
    bin_file = open(name, "wb")
    bin_file.write(bytes(data))
    bin_file.close()

def dict_key(mydict, dict_value):
    return list(mydict.keys())[list(mydict.values()).index(dict_value)]

def whoami():
    return inspect.getouterframes(inspect.currentframe())[1].function
