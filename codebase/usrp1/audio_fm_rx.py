#!/usr/bin/env python3
from PyQt5 import Qt
from gnuradio import gr, analog, audio, qtgui, uhd, blocks, filter
from gnuradio.filter import firdes
import sip
import sys
import signal

class AudioFMRX(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "Audio FM RX")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Audio FM RX (RFX900)")
        self.top_layout = Qt.QVBoxLayout(self)
        self.setLayout(self.top_layout)

        ##################################################
        # Variables
        ##################################################
        samp_rate = 500000
        audio_rate = 50000
        freq = 915e6
        rx_gain = 30

        ##################################################
        # USRP Source (RX)
        ##################################################
        self.usrp_source = uhd.usrp_source(
            "type=usrp1",
            uhd.stream_args(cpu_format="fc32", channels=[0])
        )
        self.usrp_source.set_samp_rate(samp_rate)
        self.usrp_source.set_center_freq(freq)
        self.usrp_source.set_gain(rx_gain)
        self.usrp_source.set_antenna("TX/RX")

        ##################################################
        # FM Demod
        ##################################################
        self.fm_rcv = analog.wfm_rcv(
            quad_rate=samp_rate,
            audio_decimation=int(samp_rate // audio_rate),
        )

        self.audio_sink = audio.sink(audio_rate, '', True)

        self.freq_sink = qtgui.freq_sink_c(
            1024, firdes.WIN_HAMMING, 0, samp_rate, "RX Spectrum", 1)
        self._freq_sink_win = sip.wrapinstance(self.freq_sink.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._freq_sink_win)

        ##################################################
        # Connections
        ##################################################
        self.connect(self.usrp_source, self.freq_sink)
        self.connect(self.usrp_source, self.fm_rcv)
        self.connect(self.fm_rcv, self.audio_sink)

    def closeEvent(self, event):
        self.stop()
        self.wait()
        event.accept()

def main():
    qapp = Qt.QApplication(sys.argv)
    tb = AudioFMRX()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.show()
    qapp.exec_()

if __name__ == '__main__':
    main()
