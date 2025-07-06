# Verifying USRP1 Functionality on Ubuntu 20.04.6 with UHD 3.15 and Kernel 5.15.0-139-generic

## System Information

- **Host OS:** Ubuntu 20.04.6 LTS
- **Kernel Version:** 5.15.0-139-generic
- **User:** rfnoc
- **UHD Version:** 3.15.x (installed)

## Step-by-Step Manual

### 1. Confirm Kernel and OS

```bash
uname -r
# Output should be: 5.15.0-139-generic
lsb_release -a
# Ensure Ubuntu 20.04.6 is reported
```

### 2. Confirm UHD Version

```bash
uhd_config_info --version
# Expect version: 3.15.x
```

### 3. Connect and Enumerate USRP1

Ensure USRP1 is connected via USB 2.0.

```bash
lsusb
# Look for: "FFFE:0002" or "Ettus Research LLC USRP1"
```

### 4. Probe Device with UHD

```bash
sudo uhd_usrp_probe
```

Expected Output:

- ✅ FX2 firmware is loaded
- ✅ FPGA image is loaded
- ✅ RX Dboard: A - RFX900
- ✅ TX Dboard: A - RFX900
- ✅ Clock rate: 64.000000 MHz

This confirms correct USRP1 hardware detection.

### 5. Firmware and FPGA Image Verification

If not installed:

```bash
sudo uhd_images_downloader
```

Manually verify image:

```bash
ls /usr/share/uhd/images/usrp1*
```

### 6. Run a Basic Signal Generation Test

```bash
uhd_siggen --args="type=usrp1" --freq=915e6 --samp-rate=1e6 --gain=10 --sine
```

Expected Behavior:

- Terminal prints streaming messages
- No `OOOOOO` (overruns)
- Signal visible via uhd\_fft or GRC

Note: If you get an error regarding unknown arguments, use the following instead:

```bash
uhd_siggen -a type=usrp1 -f 915e6 -s 1e6 -g 10 --sine
```

### 7. Verify GNU Radio Compatibility

```bash
gnuradio-companion
# Confirm the GRC GUI launches
```

#### Create a Test Flowgraph:

1. Open `gnuradio-companion`
2. Add a `USRP Source` block
3. Set `device_args` to:
   ```
   type=usrp1
   ```
4. Add a `QT GUI Frequency Sink`
5. Connect output of `USRP Source` to input of `QT GUI Frequency Sink`
6. Set sample rate to `32000`, center frequency to `0`, gain to `0`, and antenna to `RX2`
7. Save and run the flowgraph
8. If using USRP1, **edit the generated Python script** and comment out the line:
   ```python
   self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec())
   ```
   This line is not supported on USRP1 and causes:
   ```
   RuntimeError: LookupError: Path not found in tree: /mboards/0/time/pps
   ```

Expected:

- Live spectrum data visible in GUI
- No errors on run
- Flowgraph like screenshot shown below:

**Example Layout:**

- UHD: USRP Source → QT GUI Frequency Sink
- Variables: `samp_rate = 32000`
- Block path: `/usr/share/gnuradio/grc/blocks`

### 8. Caution on Multiple Application Access

Do **not** run `uhd_siggen` and `uhd_fft` or GRC at the same time using the **same USRP1**. Doing so results in USB transfer errors such as:

```
uhd::usb_error: usb tx2 submit failed: LIBUSB_ERROR_NO_DEVICE
```

This error is caused when you run `uhd_fft` first (e.g., `uhd_fft -a type=usrp1 -f 915e6 -s 1e6 -g 30`) and then attempt to launch `uhd_siggen` afterward, which fails because the USB resource is already occupied by `uhd_fft`.

USRP1 only supports **one active host application** at a time due to its limited USB 2.0 interface and firmware architecture. Always quit any signal generation or probing utility before launching another.

---

### 9. Troubleshooting: No Signal in UHD FFT

If `uhd_fft` displays a **flat line** or **no signal**, check the following:

- ✅ **Gain too low** — try `--gain=40` or higher
- ✅ **Wrong antenna port** — set `Antenna` to `RX2` or verify with `ls /usr/local/share/uhd/images/usrp1_*`
- ✅ **No strong ambient signals** — try tuning to FM band (88–108 MHz)
- ✅ **No TX-RX loopback** — connect USRP1 TX/RX to RX input with SMA cable to see `uhd_siggen` output
- ✅ **One app at a time** — close `uhd_siggen` before running `uhd_fft` and vice versa
- ✅ **Autoscale or Y Range** — adjust FFT sink display options in GRC or UHD FFT GUI

#### 🔁 Loopback Test with Sine

Use an **SMA cable with a 20–30 dB attenuator** to connect the **TX/RX** port to the **RX port (e.g., RX2)**:

```bash
uhd_siggen -a type=usrp1 -f 915e6 -s 1e6 -g 10 --sine
```

Then in another terminal:

```bash
uhd_fft -a type=usrp1 -f 915e6 -s 1e6 -g 40
```

Expected:

- Visible sine signal on FFT
- No overrun errors (`OOOO`) or LIBUSB crashes

⚠️ **Warning**: Never connect TX directly to RX without attenuation. Use 30 dB attenuator to avoid hardware damage.

---

## Fresh UHD 3.15 Installation (Manual Build)

### Step 1: Install Dependencies

```bash
sudo apt update
sudo apt install -y git cmake g++ libboost-all-dev libusb-1.0-0-dev \
    python3 python3-mako python3-numpy python3-requests python3-setuptools \
    python3-ruamel.yaml libuhd-dev libgps-dev libncurses5-dev
```

### Step 2: Remove Old UHD (Optional Clean Removal)

```bash
sudo apt-get remove --purge uhd-host libuhd*
sudo rm -rf /usr/lib/libuhd* /usr/local/lib/libuhd* /usr/include/uhd /usr/local/include/uhd
sudo ldconfig
```

### Step 3: Clone UHD 3.15 Source

```bash
cd ~/src
git clone https://github.com/EttusResearch/uhd.git
cd uhd
git checkout v3.15.0.0
cd host
```

### Step 4: Build and Install

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_GRQT=ON -DENABLE_PYTHON=ON -DENABLE_INTERNAL_VOLK=OFF
make -j$(nproc)
sudo make install
sudo ldconfig
```

### Step 5: Install Compatible VOLK (C++11 safe version)

```bash
cd ~/src
git clone --branch v2.2.1 https://github.com/gnuradio/volk.git
cd volk
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
sudo ldconfig
```

### Step 6: Build GNU Radio from Source (to match UHD 3.15)

```bash
cd ~/src
git clone --branch maint-3.8 https://github.com/gnuradio/gnuradio.git
cd gnuradio
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DENABLE_GRQT=ON
make -j$(nproc)
sudo make install
sudo ldconfig
```

### Step 7: Launch and Test GRC

```bash
gnuradio-companion
# Confirm GUI launches
```

---

## Notes

- USRP1 uses USB 2.0 and has limited bandwidth
- UHD 4.x+ dropped support for USRP1 — this guide is for UHD 3.15
- Clock modifications (e.g. 52 MHz for OpenBTS) may require custom firmware
- When using GRC-generated scripts, do not include `set_time_unknown_pps()` — USRP1 does not support PPS
- Use TX-to-RX loopback with RFX900 modules at same center frequency (e.g., 915 MHz) for testing
- **Only one UHD-based application should access USRP1 at any given time**

---

Author: Rongjun Geng\
Date: July 13, 2025

