# USRP1 + RFX900 Dual-Computer Manual (TX and RX using UHD Tools)

## Overview

This guide walks you through how to test USRP1 with RFX900 daughterboards on two separate computers using built-in UHD tools: `uhd_siggen` (for transmit) and `uhd_fft` (for receive). It also includes a GRC-based flowgraph example and UHD 4.0 verification tips.

---

## ✅ Requirements

- 2 computers with:
  - USB 2.0 ports
  - UHD installed (v3.15+ or UHD 4.0+)
  - USRP1 + RFX900 hardware connected
  - **Recommended:** VMware over VirtualBox (based on reliability tests)
- Proper FX2 + FPGA images downloaded via:
  ```bash
  sudo uhd_images_downloader
  ```
- USB permissions (udev rules) properly configured

---

## ⚙️ Transmitter Setup (Computer A)

### 1. Verify Detection

```bash
uhd_usrp_probe
```

Look for:

```
Daughterboard: RFX900 TX
Subdev: A:0
```

### 2. Transmit Test Tone

```bash
uhd_siggen \
  --args="type=usrp1" \
  --freq=915e6 \
  --sine \
  --samp-rate=250e3 \
  --gain=30
```

> You will see: `[UHD-SIGGEN] Press Enter to quit:`

This transmits a continuous 915 MHz sine wave.

⚠️ Ensure you use an antenna or dummy load on the TX port.

---

## 🔍 Receiver Setup (Computer B)

### 1. Verify Detection

```bash
uhd_usrp_probe
```

Look for:

```
Daughterboard: RFX900 RX
Subdev: A:0
```

### 2. Receive and Visualize

```bash
uhd_fft \
  --args="type=usrp1,rx_subdev_spec=A:0" \
  --freq=915e6 \
  --samp-rate=250e3 \
  --gain=40
```

You should see a strong signal centered at 915 MHz in the QT GUI.

---

## ✅ Troubleshooting

### USRP Not Detected

- Run `uhd_find_devices`
- Unplug/replug USB and re-run
- Ensure `uhd_images_downloader` has been run

### No Signal on Receiver

- Ensure TX and RX USRPs are both powered and running
- Check that antenna is connected or both devices share a cable with attenuator
- Try a lower or higher gain setting

---

## Optional Tests

### TX Constant Carrier

```bash
uhd_siggen --args="type=usrp1" --const --freq=915e6 --gain=30 --samp-rate=250e3
```

### Gaussian Noise Test

```bash
uhd_siggen --args="type=usrp1" --gaussian --freq=915e6 --gain=30 --samp-rate=250e3
```

This produces a wideband noise spectrum centered at 915 MHz. Useful for bandwidth and noise floor visualization.

---

## ✅ Confirmed Working

If you:

- See the signal at the expected frequency on `uhd_fft`
- Can control TX frequency, rate, and gain from `uhd_siggen`
- Verified RFX900 RX and TX via `uhd_usrp_probe`

Then your **dual-computer USRP1 test is successful.**

---

## 📦 Next Steps

### A. Build a Simple GRC Receiver Flowgraph (Computer B)

1. Launch GNU Radio Companion:

```bash
gnuradio-companion
```

2. Create a new `.grc` file
3. Add these blocks:
   - `UHD: USRP Source`
     - Device Address: `type=usrp1`
     - Center Frequency: `915e6`
     - Sample Rate: `250e3`
   - `QT GUI Frequency Sink`
4. Connect `UHD: USRP Source` ➝ `QT GUI Frequency Sink`
5. Run it. You should see the same spectrum as with `uhd_fft`

> If you see continuous `OOOO` in terminal output, try:
>
> - Reducing sample rate (e.g., `100e3`)
> - Running with higher `nice` level: `sudo nice -n -10`

### B. Add More Functionality

- Replace `QT GUI Frequency Sink` with a `Scope Sink` or `Waterfall`
- Add demod blocks (e.g., `WBFM Receiver`, `GFSK Demod`) for real signal reception

---

## 📖 UHD 4.0 + USRP1 Compatibility Notes

Even though UHD 4.0 officially dropped USRP1 support, you can still use it if the FX2 and FPGA firmware loads successfully. Check:

```bash
uhd_usrp_probe
```

Expected output:

```
[INFO] [FX2] Firmware loaded
[INFO] [FX2] FPGA image loaded
...
RX Dboard: A - RFX900 (0x0025)
TX Dboard: A - RFX900 (0x0029)
```

> Confirm sample rate, gain, and frequency settings work correctly in your UHD utilities or GRC flows.

---

## 📚 Appendix: GRC Python Equivalent (Simplified)

```python
from gnuradio import gr, qtgui, uhd
from PyQt5 import Qt
import sip, sys, signal

class grc_test(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "USRP1 Test")
        Qt.QWidget.__init__(self)
        self.samp_rate = 250e3

        self.uhd_usrp_source_0 = uhd.usrp_source(
            "type=usrp1",
            uhd.stream_args(cpu_format="fc32", channels=[0]),
        )
        self.uhd_usrp_source_0.set_center_freq(915e6, 0)
        self.uhd_usrp_source_0.set_gain(30, 0)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, qtgui.WIN_BLACKMAN_hARRIS, 915e6, self.samp_rate, "", 1
        )
        self.connect((self.uhd_usrp_source_0, 0), (self.qtgui_freq_sink_x_0, 0))

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(
            self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget
        )
        self.setLayout(Qt.QVBoxLayout())
        self.layout().addWidget(self._qtgui_freq_sink_x_0_win)

    def closeEvent(self, event):
        event.accept()

def main():
    qapp = Qt.QApplication(sys.argv)
    tb = grc_test()
    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    qapp.aboutToQuit.connect(lambda: (tb.stop(), tb.wait()))
    qapp.exec_()

if __name__ == '__main__':
    main()
```

---

## ✅ Summary

You’ve now successfully validated:

- TX and RX functions of USRP1 with RFX900
- Dual-computer over-the-air tests using `uhd_siggen` and `uhd_fft`
- Optional GRC integration and UHD 4.0 compatibility

You’re ready to move on to advanced experiments such as OpenBTS, digital demodulation, or custom GNU Radio DSP chains.

