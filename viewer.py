from comtrade import OscReader
from PyQt4.Qt import *
from PyQt4.Qwt5 import *



if __name__ == '__main__':
    osc = OscReader('osc-examples/01340703835235278186.cfg')
    print("osc channels = " + str(len(osc.channel)))

