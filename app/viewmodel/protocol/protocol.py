from PyQt5.QtCore import pyqtSignal, QThreadPool, QObject

from model.logger.loggable import Loggable
import time
from model.protocol.serport.serport import SerPort
from viewmodel.protocol.commands import InitPortRunnable, DeInitPortRunnable, WritePortRunnable, ErasePortRunnable, \
    ReadPortRunnable, GetCfgWordPortRunnable, SetCfgWordPortRunnable, JumpPortRunnable


class Protocol(Loggable, QObject):
    pbar_signal = pyqtSignal(int)

    def __init__(self, mcu, serport: SerPort, pbar_callback, parent=None):
        Loggable.__init__(self)
        QObject.__init__(self, parent)
        self.mcu = mcu
        self.serport = serport
        self.pbar_callback = pbar_callback
        self.pbar_signal.connect(pbar_callback)

    class BaseProtocolCommand(QObject, Loggable):
        finished = pyqtSignal(object)

        def __init__(self):
            Loggable.__init__(self)
            QObject.__init__(self)
            self.data = 0
            self.error = ''
            self.threadpool = QThreadPool.globalInstance()
            self.start_time = 0
            self.runnable = None

        def reset_timer(self):
            self.start_time = time.time()

        def current_timer(self):
            return time.time() - self.start_time

        def set_data(self, data):
            self.data = data

        def set_error(self, error):
            self.error = error

        def on_finished(self):
            if self.error:
                self.logger.error(self.error)

            self.finished.emit(
                {
                    'error': self.error,
                    'data': self.data,
                }
            )

        def _start(self, runnable, pbar_callback=None):
            if pbar_callback:
                runnable.signals.pbar_signal.connect(pbar_callback)
            runnable.signals.data.connect(self.set_data)
            runnable.signals.error.connect(self.set_error)
            runnable.signals.finished.connect(self.on_finished)
            self.reset_timer()
            self.threadpool.start(runnable)

        def start(self, *args, **kwargs):
            raise NotImplementedError()

    class Init(BaseProtocolCommand):
        def __init__(self):
            super().__init__()

        def start(self, mcu, serport, pbar_callback=None, **kwargs):
            super()._start(InitPortRunnable(mcu, serport, **kwargs), pbar_callback=pbar_callback)

    class DeInit(BaseProtocolCommand):
        def __init__(self):
            super().__init__()

        def start(self, mcu, serport, pbar_callback=None, **kwargs):
            super()._start(DeInitPortRunnable(mcu, serport, **kwargs), pbar_callback=pbar_callback)

    class Write(BaseProtocolCommand):
        def __init__(self):
            super().__init__()

        def start(self, mcu, serport, pbar_callback=None, **kwargs):
            super()._start(WritePortRunnable(mcu, serport, **kwargs), pbar_callback=pbar_callback)

    class Erase(BaseProtocolCommand):
        def __init__(self):
            super().__init__()

        def start(self, mcu, serport, pbar_callback=None, **kwargs):
            super()._start(ErasePortRunnable(mcu, serport, **kwargs), pbar_callback=pbar_callback)

    class Read(BaseProtocolCommand):
        def __init__(self):
            super().__init__()

        def start(self, mcu, serport, pbar_callback=None, **kwargs):
            super()._start(ReadPortRunnable(mcu, serport, **kwargs), pbar_callback=pbar_callback)

    class GetCfgWord(BaseProtocolCommand):
        def __init__(self):
            super().__init__()

        def start(self, mcu, serport, pbar_callback=None, **kwargs):
            super()._start(GetCfgWordPortRunnable(mcu, serport, **kwargs), pbar_callback=pbar_callback)

    class SetCfgWord(BaseProtocolCommand):
        def __init__(self):
            super().__init__()

        def start(self, mcu, serport, pbar_callback=None, **kwargs):
            super()._start(SetCfgWordPortRunnable(mcu, serport, **kwargs), pbar_callback=pbar_callback)

    class Jump(BaseProtocolCommand):
        def __init__(self):
            super().__init__()

        def start(self, mcu, serport, pbar_callback=None, **kwargs):
            super()._start(JumpPortRunnable(mcu, serport, **kwargs), pbar_callback=pbar_callback)

