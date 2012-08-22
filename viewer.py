import sip
sip.setapi('QString', 2)

import sys
import os
from comtrade import OscReader
from dataplot import DataPlot
from PyQt4.Qt import *
from PyQt4.Qwt5 import *
import ConfigParser

class MainWindow(QMainWindow):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.setWindowTitle("Behold!")
        self.resize(800, 500)
        self.createWidgets()
        self.createMenus()
        self.channel_renames = dict()
        self.fillChannelRenames()

    def createWidgets(self):
        # widgets
        self.dataplot = DataPlot()
        self.channel_list = QListWidget()
        self.file_list = QListWidget()
        central_widget = QWidget()

        # layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.file_list, stretch=0)
        hbox.addWidget(self.dataplot, stretch=1)
        hbox.addWidget(self.channel_list, stretch=0)
        central_widget.setLayout(hbox)
        self.setCentralWidget(central_widget)

        # properties and signals
        self.file_list.hide()
        self.channel_list.currentRowChanged.connect(self.channelListCurrentRowChanged)
        self.file_list.currentRowChanged.connect(self.fileListCurrentRowChanged)

    def createMenus(self):
        file_open_single_action = QAction("Open ...", self)
        file_open_single_action.setShortcut("Ctrl+O")
        file_open_single_action.triggered.connect(self.showOpenFileDialog)

        file_open_directory_action = QAction("Open directory ...", self)
        file_open_directory_action.triggered.connect(self.showOpenDirectoryDialog)

        file_quit_action = QAction("Quit", self)
        file_quit_action.setShortcut("Ctrl+X")
        file_quit_action.triggered.connect(self.close)

        view_fit_to_view_action = QAction("Fit to view", self)
        view_fit_to_view_action.triggered.connect(self.autoScaleDataPlot)

        help_about_action = QAction("About", self)
        help_about_action.triggered.connect(self.displayAboutDialog)

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(file_open_single_action)
        file_menu.addAction(file_open_directory_action)
        file_menu.addSeparator()
        file_menu.addAction(file_quit_action)

        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(view_fit_to_view_action)

        self.menuBar().addSeparator()

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(help_about_action)

    def autoScaleDataPlot(self):
        self.dataplot.setAxisAutoScale(QwtPlot.yLeft)
        self.dataplot.setAxisAutoScale(QwtPlot.xBottom)
        self.dataplot.updateAxes()

    def showOpenFileDialog(self):
        fod = QFileDialog(self, "Open file ...")
        fod.setFileMode(QFileDialog.ExistingFiles)
        fod.setFilter("COMTRADE cfg (*.cfg);; All Files (*)")
        if fod.exec_():
            if len(fod.selectedFiles()) == 1:
                self.file_list.hide()
                fname = fod.selectedFiles()[0]
                self.openSingleFile(fname)
            else:
                self.openMultipleFiles(list(fod.selectedFiles()))

    def showOpenDirectoryDialog(self):
        fod = QFileDialog(self, "Select directory ...")
        fod.setFileMode(QFileDialog.DirectoryOnly)
        if fod.exec_():
            dir = fod.selectedFiles()[0]
            fnamelist = []
            for fname in os.listdir(dir):
                if fname[-4:] == '.cfg':
                    fnamelist.append(dir + os.sep + fname)
            self.openMultipleFiles(fnamelist)

    def openMultipleFiles(self, fnamelist):
        self.file_list.show()
        self.file_list.clear()
        for fname in fnamelist:
            basename = os.path.basename(fname)
            item = QListWidgetItem(basename)
            item.fullpath = fname
            self.file_list.addItem(item)

    def openSingleFile(self, fname):
        osc = OscReader(fname)
        self.attach_osc(osc)

    def fileListCurrentRowChanged(self, row):
        item = self.file_list.item(row)
        self.openSingleFile(item.fullpath)

    def displayAboutDialog(self):
        QMessageBox.about(self, "About", "Viewer for oscillograms in COMTRADE format.")

    def attach_osc(self, osc):
        self.osc = osc
        self.channel_list.clear()
        for ch in self.osc.channel:
            channel = self.osc.channel[ch]
            if channel.name in self.channel_renames:
                channel_name = self.channel_renames[channel.name]
            else:
                channel_name = channel.name
            item = QListWidgetItem(channel_name)
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

        min_y, max_y = min(self.osc.channel[ch].data), max(self.osc.channel[ch].data)
        min_t, max_t = min(t), max(t)
        # widen a bit
        min_y, max_y = min_y-0.03*(max_y-min_y), max_y+0.03*(max_y-min_y)

        self.dataplot.setAxisScale(QwtPlot.yLeft, min_y, max_y)
        self.dataplot.setAxisScale(QwtPlot.xBottom, min(t), max(t))
        self.dataplot.zoomer.setZoomBase()
        self.dataplot.replot()

    def channelListCurrentRowChanged(self, row):
        if row == -1: row = 0
        cid = self.channel_list.item(row).cid
        self.plot_osc_channel(cid)

    def fillChannelRenames(self):
        config = ConfigParser.RawConfigParser()
        config.optionxform = str
        config.read('renames.ini')
        sections = config.sections()
        if 'renames' in sections:
            print("found channel renames in renames.ini")
            for name in config.options('renames'):
                name = name.decode('utf-8')
                value = config.get('renames', name).decode('utf-8')
                self.channel_renames[name] = value
                print ('"{}" => "{}"'.format(name.encode('utf-8'), value.encode('utf-8')))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
