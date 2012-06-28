from PyQt4.Qt import *
from PyQt4.Qwt5 import *

class DataPlot(QwtPlot):
    def __init__(self, *args):
        QwtPlot.__init__(self, *args)
        self.setCanvasBackground(Qt.white)
