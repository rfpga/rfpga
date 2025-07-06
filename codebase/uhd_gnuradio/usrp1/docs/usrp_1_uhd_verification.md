# Verifying USRP1 Functionality

This guide walks you through verifying that an Ettus USRP1 device functions correctly using either UHD 3.15.x (full legacy support) or UHD 4.0+ (partial support for modern tooling). These two manuals are provided separately.

---

## ✅ Manual A: UHD 3.15 — Full USRP1 Support

### 1. Install Dependencies (Ubuntu 22.04.5)

```bash
sudo apt update
sudo apt install -y git cmake g++ libboost-all-dev libusb-1.0-0-dev \
                    python3-dev python3-mako python3-numpy python3-requests \
                    libqt5opengl5-dev qtbase5-dev libqwt-qt5-dev
```

### 2. Clone UHD 3.15.0.0 Source

```bash
git clone --branch release_003_015_000 https://github.com/EttusResearch/uhd.git
cd uhd
```

### 3. Build & Install UHD 3.15

```bash
mkdir host/build
cd host/build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

### 4. Install USRP1 FPGA Images

```bash
cd ../../
sudo uhd_images_downloader -t usrp1
```

Confirm:

```bash
ls /usr/local/share/uhd/images/usrp1_fpga.rbf
```

### 5. Test USRP1 Device

```bash
uhd_usrp_probe
```

Expected:

```
-- Opening a USRP1 device...
-- FX2 loaded
-- FPGA loaded
-- Clock rate: 64 MHz
-- RX Dboard: RFX900
-- TX Dboard: RFX900
```

✅ UHD 3.15 now fully installed and functional for USRP1.

---

## GRC Flowgraph Example (UHD 3.15)

### Example Python Code Generated from GRC

```python
from gnuradio import gr, qtgui, uhd
from PyQt5 import Qt
import sip, sys, signal, time

class grc_test(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "USRP1 Test")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("USRP1 Test")
        self.samp_rate = 500e3

        self.uhd_usrp_source_0 = uhd.usrp_source(
            "type=usrp1",
            uhd.stream_args(cpu_format="fc32", channels=[0]),
        )
        self.uhd_usrp_source_0.set_center_freq(915e6, 0)
        self.uhd_usrp_source_0.set_gain(30, 0)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, qtgui.WIN_BLACKMAN_hARRIS, 915e6, self.samp_rate, "", 1
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, -60)
        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(
            self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget
        )

        self.connect((self.uhd_usrp_source_0, 0), (self.qtgui_freq_sink_x_0, 0))

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

## ⚠️ VirtualBox Ubuntu Slow Boot/Freeze (RCU Stall Fix)

If you experience very long delays or see logs like `rcu: INFO: rcu_preempt detected expedited stalls`, it's **not normal**. To fix:

### ✅ Recommended Fixes:

1. **Give the VM more resources**:

   - 2+ CPUs, 4+ GB RAM

2. **Use Ubuntu 20.04.6 with Kernel 5.15** (Best Stability):

   Ubuntu 22.04.5 ships with unstable 6.8.x kernels for USRP1/VirtualBox. Instead, use Ubuntu 20.04.6 which natively runs the **5.15.0-91-generic** kernel — no manual overrides needed.

   - Download from: [https://releases.ubuntu.com/20.04.6/](https://releases.ubuntu.com/20.04.6/)
   - Install as usual, then confirm:
     ```bash
     uname -r
     # Should show: 5.15.0-91-generic
     ```

   **Why?**

   - Faster VirtualBox boot
   - Avoids emergency mode / RCU hangs
   - Full compatibility with UHD 3.15 + USRP1

3. **Enable Host I/O Cache** in VirtualBox for the virtual disk.

4. **Avoid clipboard sharing temporarily**: can cause issues.

5. **Reinstall Guest Additions**:

   ```bash
   sudo apt install virtualbox-guest-utils virtualbox-guest-x11
   ```

---

## Final Recommendation

- ✅ **Use UHD 3.15** if you want complete support for USRP1, OpenBTS, or reliable TX/RX.
- ⚠️ **Do not mix UHD 3.15 and UHD 4.0** in the same environment. Isolate with Docker or VMs if needed.
- ✅ **Use Ubuntu 20.04.6 LTS + kernel 5.15.x** for best performance in VirtualBox with USRP1.

Let us know if you want a Dockerfile or .grc sample.

