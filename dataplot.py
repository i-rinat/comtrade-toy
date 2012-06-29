from PyQt4.Qt import *
from PyQt4.Qwt5 import *

class DataPlot(QwtPlot):
    def __init__(self, *args):
        QwtPlot.__init__(self, *args)
        self.setCanvasBackground(Qt.white)
        self.plotLayout().setAlignCanvasToScales(True)
        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft, \
            QwtPicker.DragSelection, QwtPicker.AlwaysOn, self.canvas())

        self.zoomer.setRubberBandPen(QPen(Qt.green))
        self.zoomer.setRubberBand(QwtPlotZoomer.RectRubberBand)
