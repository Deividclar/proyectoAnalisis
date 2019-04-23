from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot


class Worker(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(list)
    def __init__(self):
        QObject.__init__(self)

    @pyqtSlot()
    def _search_cast_(self):
        self.cc = casting()
        self.cc.initialize_cast()
        availablescc = self.cc.availablecc
        self.intReady.emit(availablecc)
        self.finished.emit()