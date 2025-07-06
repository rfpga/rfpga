# GNU Radio GRC-like Python Code for FM TX/RX over USRP1 + RFX900

# Transmitter Flowgraph (fm_tx_usrp1_rfx900_audio.py)
from gnuradio import gr, audio, analog, blocks, filter, uhd
import time

class fm_tx_usrp1_rfx900_audio(gr.top_block):
    def __init__(self, fallback=False):
        gr.top_block.__init__(self, "FM TX USRP1 RFX900 - Mic Input")

        # Variables
        self.audio_rate = 48000
        self.quad_rate = 480000  # Must be an integer multiple of audio_rate
        self.center_freq = 915e6
        self.gain = 20

        # Blocks
        if fallback:
            print("[WARN] Audio input unavailable, using test tone.")
            self.audio_source = analog.sig_source_f(self.audio_rate, analog.GR_SIN_WAVE, 1000, 0.5, 0)
        else:
            self.audio_source = audio.source(self.audio_rate, "hw:0,0", True)  # Using ALSA mic device explicitly

        self.resampler = filter.rational_resampler_fff(
            interpolation=self.quad_rate,
            decimation=self.audio_rate,
        )
        self.wfm_tx = analog.wfm_tx(
            audio_rate=self.audio_rate,
            quad_rate=self.quad_rate,
            tau=75e-6,
            max_dev=5e3
        )
        self.usrp_sink = uhd.usrp_sink(
            "type=usrp1,tx_subdev_spec=A:0",
            uhd.stream_args(cpu_format="fc32")
        )
        self.usrp_sink.set_samp_rate(self.quad_rate)
        self.usrp_sink.set_center_freq(self.center_freq)
        self.usrp_sink.set_gain(self.gain)

        # Connections
        self.connect(self.audio_source, self.resampler)
        self.connect(self.resampler, self.wfm_tx)
        self.connect(self.wfm_tx, self.usrp_sink)


# Receiver Flowgraph (fm_rx_usrp1_rfx900_audio.py)
class fm_rx_usrp1_rfx900_audio(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "FM RX USRP1 RFX900 - Speaker Output")

        # Variables
        self.audio_rate = 48000
        self.quad_rate = 500000
        self.center_freq = 915e6
        self.gain = 40

        # Blocks
        self.usrp_source = uhd.usrp_source(
            "type=usrp1,rx_subdev_spec=A:0",
            uhd.stream_args(cpu_format="fc32")
        )
        self.usrp_source.set_samp_rate(self.quad_rate)
        self.usrp_source.set_center_freq(self.center_freq)
        self.usrp_source.set_gain(self.gain)

        self.wfm_rcv = analog.wfm_rcv(
            quad_rate=self.quad_rate,
            audio_decimation=int(self.quad_rate / self.audio_rate)
        )

        self.audio_sink = audio.sink(self.audio_rate, "plughw:0,0", True)


        # Connections
        self.connect(self.usrp_source, self.wfm_rcv)
        self.connect(self.wfm_rcv, self.audio_sink)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="FM TX/RX with USRP1 + RFX900")
    parser.add_argument('--rx', action='store_true', help='Run in receiver mode')
    parser.add_argument('--mic', action='store_true', help='Use microphone instead of test tone (TX only)')
    args = parser.parse_args()

    if args.rx:
        tb = fm_rx_usrp1_rfx900_audio()
    else:
        try:
            tb = fm_tx_usrp1_rfx900_audio(fallback=not args.mic)
        except RuntimeError:
            print("[ERROR] Failed to initialize microphone. Falling back to test tone.")
            tb = fm_tx_usrp1_rfx900_audio(fallback=True)

    tb.start()
    try:
        input('Press Enter to stop...\n')
    finally:
        tb.stop()
        tb.wait()
