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
        self.createWidgets()
        self.createMenus()

    def createWidgets(self):
        # widgets
        self.dataplot = DataPlot()
        self.channel_list = QListWidget()
        central_widget = QWidget()

        # layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.dataplot, stretch=1)
        hbox.addWidget(self.channel_list, stretch=0)
        central_widget.setLayout(hbox)
        self.setCentralWidget(central_widget)

        # properties and signals
        self.channel_list.currentRowChanged.connect(self.channelListCurrentRowChanged)

    def createMenus(self):
        file_open_single_action = QAction("Open ...", self)
        file_open_single_action.setShortcut("Ctrl+O")
        file_open_single_action.triggered.connect(self.openSingleFile)

        file_open_directory_action = QAction("Open directory ...", self)
        file_open_directory_action.triggered.connect(self.openDirectory)

        file_quit_action = QAction("Quit", self)
        file_quit_action.setShortcut("Ctrl+X")
        file_quit_action.triggered.connect(self.close)

        help_about_action = QAction("About", self)
        help_about_action.triggered.connect(self.displayAboutDialog)

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(file_open_single_action)
        file_menu.addAction(file_open_directory_action)
        file_menu.addSeparator()
        file_menu.addAction(file_quit_action)

        self.menuBar().addSeparator()

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(help_about_action)

    def openSingleFile(self):
        pass

    def openDirectory(self):
        pass

    def displayAboutDialog(self):
        QMessageBox.about(self, "About", "Viewer for oscillograms in COMTRADE format.")

    def attach_osc(self, osc):
        self.osc = osc
        self.channel_list.reset()
        for ch in self.osc.channel:
            channel = self.osc.channel[ch]
            item = QListWidgetItem(channel.name)
            item.cid = ch
            self.channel_list.addItem(item)
        self.plot_osc_channel(1)

    def plot_osc_channel(self, ch):
        self.dataplot.detachItems()
        curve = QwtPlotCurve("Channel data")
        curve.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(), QPen(Qt.black), QSize(7,7)))
        curve.setPen(QPen(Qt.red))
        curve.attach(self.dataplot)
        dt = 1.0 / self.osc.sample_rate
        t = [dt * s for s in range(0, len(self.osc.channel[ch].data))]
        curve.setData(t, self.osc.channel[ch].data)
        self.dataplot.setAxisTitle(QwtPlot.xBottom, "Time (s)")
        if self.osc.channel[ch].ctype == 'A':
            self.dataplot.setAxisTitle(QwtPlot.yLeft, self.osc.channel[ch].units)
            self.dataplot.setAxisAutoScale(QwtPlot.yLeft)
        else:
            self.dataplot.setAxisTitle(QwtPlot.yLeft, "on/off")
            self.dataplot.setAxisScale(QwtPlot.yLeft, 0, 1)
        self.dataplot.replot()

    def channelListCurrentRowChanged(self, row):
        cid = self.channel_list.item(row).cid
        self.plot_osc_channel(cid)

if __name__ == '__main__':
    osc = OscReader('osc-examples/01340703835235278186.cfg')
    app = QApplication(sys.argv)

    mw = MainWindow()
    mw.attach_osc(osc)
    mw.show()
    sys.exit(app.exec_())
