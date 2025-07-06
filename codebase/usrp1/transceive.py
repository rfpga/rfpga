#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.version import StrictVersion
import ctypes
import sys
if sys.platform.startswith('linux'):
    try:
        x11 = ctypes.cdll.LoadLibrary('libX11.so')
        x11.XInitThreads()
    except:
        print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui, gr, uhd, analog, blocks
from gnuradio.filter import firdes
import sip
import signal
import time

class tx_rx_demo(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "USRP1 TX + RX Demo")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("USRP1 TX + RX Demo")
        qtgui.util.check_set_qss()

        self.top_layout = Qt.QVBoxLayout(self)
        self.setLayout(self.top_layout)

        ##################################################
        # Variables
        ##################################################
        samp_rate = 1e6
        freq = 915e6
        tx_gain = 30
        rx_gain = 30

        ##################################################
        # TX Path
        ##################################################
        self.tx_signal = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 100e3, 0.5)
        self.usrp_sink = uhd.usrp_sink(
            "type=usrp1",
            uhd.stream_args(cpu_format="fc32", channels=[0]),
        )
        self.usrp_sink.set_samp_rate(samp_rate)
        self.usrp_sink.set_center_freq(freq)
        self.usrp_sink.set_gain(tx_gain)
        self.usrp_sink.set_antenna("TX/RX")

        ##################################################
        # RX Path
        ##################################################
        self.usrp_source = uhd.usrp_source(
            "type=usrp1",
            uhd.stream_args(cpu_format="fc32", channels=[0]),
        )
        self.usrp_source.set_samp_rate(samp_rate)
        self.usrp_source.set_center_freq(freq)
        self.usrp_source.set_gain(rx_gain)
        self.usrp_source.set_antenna("RX2")

        self.freq_sink = qtgui.freq_sink_c(
            1024, firdes.WIN_BLACKMAN_hARRIS, 0, samp_rate, "Received Spectrum", 1
        )
        self.freq_sink.set_update_time(0.1)
        self.freq_sink.enable_grid(True)
        self.freq_sink.set_y_axis(-120, 0)

        self.time_sink = qtgui.time_sink_c(
            1024, samp_rate, "Received Signal", 1
        )

        self.top_layout.addWidget(sip.wrapinstance(self.freq_sink.pyqwidget(), Qt.QWidget))
        self.top_layout.addWidget(sip.wrapinstance(self.time_sink.pyqwidget(), Qt.QWidget))

        ##################################################
        # Connections
        ##################################################
        self.connect(self.tx_signal, self.usrp_sink)
        self.connect(self.tx_signal, self.freq_sink)
        self.connect(self.tx_signal, self.time_sink)


    def closeEvent(self, event):
        self.stop()
        self.wait()
        event.accept()


def main():
    app = Qt.QApplication(sys.argv)
    tb = tx_rx_demo()

    def sig_handler(*_):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.show()

    app.exec_()

if __name__ == "__main__":
    main()
