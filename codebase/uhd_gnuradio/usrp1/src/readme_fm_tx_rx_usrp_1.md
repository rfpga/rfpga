# FM TX/RX with USRP1 + RFX900 on GNU Radio

This guide explains how to set up and use the `fm_tx_rx_usrp_1.py` script to transmit and receive FM audio (either microphone or test tone) using two USRP1 devices with RFX900 daughterboards.

---

## 📦 Requirements

- Two USRP1 + RFX900
- GNU Radio (>= 3.8, compiled with ALSA audio backend)
- UHD (tested on UHD 4.8)
- Working ALSA microphone and speaker setup
- Python 3

---

## 🔧 Build GNU Radio with ALSA Audio Backend (if not using prebuilt)

```bash
rm -rf build
mkdir build && cd build
cmake -DENABLE_GR_UHD=ON \
      -DENABLE_GR_FFT=ON \
      -DENABLE_GR_ANALOG=ON \
      -DENABLE_GR_BLOCKS=ON \
      -DENABLE_GRC=ON \
      -DENABLE_GR_QTGUI=ON \
      -DENABLE_GR_AUDIO=ON \
      -DAUDIO_BACKEND=alsa \
      ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

---

## 🖥️ Audio Setup (ALSA)

### 1. Check Available Devices
```bash
aplay -L
arecord -L
```

### 2. Test Microphone
```bash
arecord -D hw:0,0 -f cd -d 5 test.wav
aplay test.wav
```

If that works, `hw:0,0` or `plughw:0,0` is your mic device.

### 3. Make sure your user is in the `audio` group:
```bash
sudo usermod -aG audio $USER
newgrp audio
```

---

## 🚀 Running the Application

### Transmit using Test Tone (default)
```bash
python3 fm_tx_rx_usrp_1.py
```

### Transmit using Microphone
```bash
python3 fm_tx_rx_usrp_1.py --mic
```

### Receive and play back
```bash
python3 fm_tx_rx_usrp_1.py --rx
```

---

## 📡 Behavior
- Transmitter transmits at **915 MHz** with **480 ksps** sample rate.
- If `--mic` is given, ALSA mic input is used (default: `hw:0,0`).
- If no mic is available or audio fails to initialize, a **1kHz test tone** is used.
- Receiver captures from 915 MHz and plays to system's default speaker.

---

## 🛠️ To-Do / Future Enhancements
- [ ] Add `--device` argument to select audio device (mic/speaker)
- [ ] Add FFT GUI or scope to visualize signal
- [ ] Add logging or signal strength monitor

---

## 🧪 Troubleshooting

- **"/dev/dsp not found" errors**: Rebuild GNU Radio with ALSA (`-DAUDIO_BACKEND=alsa`)
- **No sound from mic**: Confirm mic works with `arecord`, check group permissions.
- **Receiver silent**: Confirm antenna and center frequency match.
- **USRP sample rate mismatch**: Slight rate offset (e.g., 480000 → 481203) is OK.

---

## ✅ Confirmed Working
- OS: Ubuntu 22.04 / 24.04
- USRP1 + RFX900 (TX/RX on separate laptops)
- GNU Radio 3.11 built from source with ALSA support
- UHD 4.8.0

---

Happy SDR hacking! 🧠📡

