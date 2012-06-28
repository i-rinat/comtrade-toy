import sys
from comtrade import OscReader
from dataplot import DataPlot
from PyQt4.Qt import *
from PyQt4.Qwt5 import *

class MainWindow(QMainWindow):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.setWindowTitle("Behold!")
        self.resize(800, 500)
        self.dataplot = DataPlot()
        self.setCentralWidget(self.dataplot)

    def attach_osc(self, osc):
        self.osc = osc
        self.plot_osc_channel(1)

    def plot_osc_channel(self, ch):
        curve = QwtPlotCurve("Channel data")
        curve.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(), QPen(Qt.black), QSize(7,7)))
        curve.setPen(QPen(Qt.red))
        curve.attach(self.dataplot)
        dt = 1.0 / self.osc.sample_rate
        print self.osc.line_frequency
        t = [dt * s for s in range(0, len(self.osc.channel[ch].data))]
        curve.setData(t, self.osc.channel[ch].data)
        self.dataplot.setAxisTitle(QwtPlot.xBottom, "Time (s)")
        if self.osc.channel[ch].ctype == 'A':
            self.dataplot.setAxisTitle(QwtPlot.yLeft, self.osc.channel[ch].units)
        else:
            self.dataplot.setAxisTitle(QwtPlot.yLeft, "on/off")
            self.dataplot.setAxisScale(QwtPlot.yLeft, 0, 1)
        self.dataplot.replot()

if __name__ == '__main__':
    osc = OscReader('osc-examples/01340703835235278186.cfg')
    print("osc channels = " + str(len(osc.channel)))
    app = QApplication(sys.argv)

    mw = MainWindow()
    mw.attach_osc(osc)
    mw.show()
    sys.exit(app.exec_())
