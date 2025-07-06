#!/usr/bin/env python3
from gnuradio import gr, analog, uhd
import time

class AudioFMTX(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Audio FM TX")

        samp_rate = 500000
        audio_rate = 50000
        freq = 915e6
        tx_gain = 30

        self.tone = analog.sig_source_f(audio_rate, analog.GR_SIN_WAVE, 1000, 0.5)
        self.fm_mod = analog.wfm_tx(
            audio_rate=audio_rate,
            quad_rate=samp_rate,
            tau=75e-6,
            max_dev=75e3,
        )

        self.usrp_sink = uhd.usrp_sink(
            "type=usrp1",
            uhd.stream_args(cpu_format="fc32", channels=[0])
        )
        self.usrp_sink.set_samp_rate(samp_rate)
        self.usrp_sink.set_center_freq(freq)
        self.usrp_sink.set_gain(tx_gain)
        self.usrp_sink.set_antenna("TX/RX")

        self.connect(self.tone, self.fm_mod, self.usrp_sink)

def main():
    tb = AudioFMTX()
    tb.start()
    print("Transmitting 1 kHz tone via FM...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    tb.stop()
    tb.wait()

if __name__ == '__main__':
    main()
