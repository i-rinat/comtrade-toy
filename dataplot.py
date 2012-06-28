from PyQt4.Qt import *
from PyQt4.Qwt5 import *

class DataPlot(QwtPlot):
    def __init__(self, *args):
        QwtPlot.__init__(self, *args)
        self.setCanvasBackground(Qt.white)
        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft, \
            QwtPicker.DragSelection, QwtPicker.AlwaysOff, self.canvas())
        self.zoomer.setRubberBandPen(QPen(Qt.green))
