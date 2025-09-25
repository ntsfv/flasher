import logging
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

LOGLEVEL_COLORS = {
    logging.DEBUG: 'green',
    logging.INFO: 'blue',
    logging.WARNING: 'yellow',
    logging.ERROR: 'red',
    logging.CRITICAL: 'magenta',
}

class LoggerWidgetSignaller(QtCore.QObject):
    log_event = pyqtSignal(str)

class LoggerWidgetHandler(QtCore.QObject, logging.Handler):
    def __init__(self, slotfunc, *args, **kwargs):
        super(LoggerWidgetHandler, self).__init__(*args, **kwargs)
        self.signaller = LoggerWidgetSignaller()
        self.signaller.log_event.connect(slotfunc)
        self.setFormatter(ColoredHTMLFormatter())

    def emit(self, record):
        s = self.format(record)
        self.signaller.log_event.emit(s)

class ColoredHTMLFormatter(logging.Formatter):
    def __init__(self, use_color=True):
        super().__init__()
        self.use_color = use_color

    def format(self, record):
        record.msg = str(record.msg).replace('<', '&lt;').replace('>', '&gt;')
        if self.use_color:
            color = LOGLEVEL_COLORS.get(record.levelno, "black")
            levelname_color = '<font color="%s">%s</font>' % (color, record.levelname)
            record.levelname = levelname_color
        record.msg = record.levelname + ' ' + record.msg
        return logging.Formatter.format(self, record)