# USRP1 + RFX900 Full Setup and Testing Manual

This complete manual combines installation, basic FM RX verification, GUI spectrum test, and TX-to-RX loopback instructions for **USRP1 + RFX900** on Ubuntu 20.04 with GNU Radio 3.8 and UHD 3.15.

---

## ✅ System Overview

| Component     | Version                 | Notes                                  |
| ------------- | ----------------------- | -------------------------------------- |
| **GNU Radio** | 3.8.x (e.g., 3.8.2.0)   | Last major version with WX GUI support |
| **UHD**       | 3.15.x (e.g., 3.15.0.0) | Last UHD with full USRP1 support       |
| **Python**    | 3.6–3.8                 | Python 3.8 is native to Ubuntu 20.04   |
| **Hardware**  | USRP1 + RFX900          | Tested with TX/RX (52–1000 MHz tuning) |
| **Audio**     | ALSA/PortAudio          | ALSA friendly (OSS deprecated)         |

---

## 🛠️ 1. OS Setup (Ubuntu 20.04 LTS)

Install essential packages:

```bash
sudo apt update
sudo apt install -y git cmake g++ libboost-all-dev libusb-1.0-0-dev \
    python3 python3-mako python3-numpy python3-requests python3-setuptools \
    python3-ruamel.yaml libuhd-dev libgps-dev libncurses5-dev
```

---

## 📦 2. Install UHD 3.15.x from Source

```bash
cd ~/src
git clone https://github.com/EttusResearch/uhd.git
cd uhd
git checkout v3.15.0.0
cd host
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

### ⬇️ Download FPGA and Firmware Images

```bash
sudo /usr/local/lib/uhd/utils/uhd_images_downloader.py
```

### 🔍 Verify UHD Install

```bash
uhd_find_devices
uhd_usrp_probe
```

Expected output should confirm:

- USRP1 device loaded with FPGA
- RX/TX Dboards = RFX900

---

## 📦 3. Install GNU Radio 3.8.x from Source

```bash
cd ~/src
git clone --recursive https://github.com/gnuradio/gnuradio.git -b maint-3.8 gr-3.8
cd gr-3.8
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

### 🔍 Confirm GRC

```bash
gnuradio-companion
```

---

## 🎚️ 4. Setup ALSA Audio

```bash
sudo apt install alsa-utils
aplay -l
arecord -l
```

Use `audio_sink` (not deprecated `audio_oss_sink`) and device = `default`.

---

## 🧰 5. Verify with UHD FFT

```bash
uhd_fft --args="type=usrp1" --freq=915e6 --rate=2e6 --gain=20
```

---

## 📻 6. Basic FM RX GRC Flowgraph Summary

| Block               | Parameters               |
| ------------------- | ------------------------ |
| **UHD Source**      | Freq: 915e6, Rate: 2e6   |
| **Low Pass Filter** | Cutoff: 100k, Trans: 50k |
| **WBFM Receiver**   | Quad: 200k, Audio: 48k   |
| **Audio Sink**      | Device: `default`        |

---

## 🚧 7. Fixing Common Errors

- ❌ `audio_oss_sink : No such file or directory` → Use `audio_sink`
- ❌ `'NoneType' object is not subscriptable` → Corrupt/incompatible .grc file
- ❌ Sample rate too low (< 250k) → Set at least 250e3
- ❌ `set_time_unknown_pps()` error → USRP1 does **not** support PPS

---

## 🧪 8. Minimal Verified Flowgraph (915 MHz Spectrum Viewer)

```python
self.uhd_usrp_source_0.set_center_freq(915e6, 0)
self.uhd_usrp_source_0.set_gain(0, 0)
self.uhd_usrp_source_0.set_antenna('RX2', 0)
self.uhd_usrp_source_0.set_samp_rate(250e3)
```

- Connected to `qtgui.freq_sink_c`
- No `set_time_unknown_pps()` present

---

## 🔁 9. Loopback Test (TX to RX) — Same Frequency Band Only

### Requirements

- Two RFX900 boards (or shared RX/TX with isolation)
- Coax + attenuator **or** separated antennas

### Terminal A — Transmit Sine:

```bash
uhd_siggen --args="type=usrp1,tx_subdev_spec=A:0" \
  --freq=915e6 --gain=10 --samp-rate=8e6 --sine
```

### Terminal B — Receive:

```bash
uhd_fft --args="type=usrp1,rx_subdev_spec=A:0" \
  --freq=915e6 --gain=30 --samp-rate=1e6
```

⚠️ USRP1 only supports **one process at a time**. Do **not** run these simultaneously.

---

## 🔄 Optional: Environment Setup

```bash
# ~/.bashrc additions
export PYTHONPATH=/usr/local/lib/python3/dist-packages:$PYTHONPATH
export PATH=/usr/local/bin:$PATH
source ~/.bashrc
```

---

## ✅ Final Checklist

-

