# Installing UHD 4.8, GNU Radio 3.11, and RFNoC on Ubuntu 24.04.2 (VMware)

This guide walks you through installing the **latest UHD 4.8**, **GNU Radio 3.11**, and **RFNoC** support on **Ubuntu 24.04.2** running in **VMware**.

---

## ✅ System Preparation

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install -y \
  cmake g++ python3-dev python3-mako python3-numpy python3-gi \
  libboost-all-dev libgmp-dev swig libusb-1.0-0-dev \
  libfftw3-dev libcomedi-dev libcppunit-dev libgsl-dev \
  libqwt-qt5-dev libqt5svg5-dev python3-pyqt5 \
  liblog4cpp5-dev libzmq3-dev libsndfile1-dev \
  git pkg-config doxygen graphviz python3-sphinx \
  python3-lxml liborc-0.4-dev python3-setuptools \
  libspdlog-dev libvolk-dev pybind11-dev \
  python3-pygccxml python3-cairo \
  gir1.2-cairo-1.0 python3-gi-cairo \
  python3-matplotlib qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools
```

> ✅ **Note**: `python3-setuptools` is **required** to build the UHD Python components (e.g., `pyuhd`, `usrp_mpm`). If missing, `make` will fail at the final stages with a `ModuleNotFoundError`. ✅ `python3-matplotlib` is required if you want to use instrumentation blocks in GNU Radio Companion (e.g., DistanceRadar, AzElPlot). ✅ `qtbase5-dev`, `qtchooser`, `qt5-qmake`, and `qtbase5-dev-tools` are essential for building `gr-qtgui`, which provides QT GUI and instrumentation blocks.

---

## 📦 UHD 4.8 Installation (Latest)

### 2. Clone UHD 4.8 from Source

```bash
cd ~/src
git clone --branch UHD-4.8 https://github.com/EttusResearch/uhd.git
cd uhd/host
mkdir build && cd build
```

### 3. Configure UHD with RFNoC

```bash
cmake -DENABLE_RFNOC=ON ..
```

### 4. Build and Install UHD

```bash
make -j$(nproc)
sudo make install
sudo ldconfig
```

### 5. Download Firmware and FPGA Images

```bash
sudo /usr/local/lib/uhd/utils/uhd_images_downloader.py
```

---

## 📻 GNU Radio Installation (Latest from `main` Branch)

### 6. Clone GNU Radio

```bash
cd ~/src
git clone --recursive https://github.com/gnuradio/gnuradio.git
cd gnuradio
```

### 7. Checkout GNU Radio Source Code

```bash
# Already cloned in previous step
git checkout main
git pull
git submodule update --init --recursive
```

### 8. Build GNU Radio

```bash
rm -rf build
mkdir build && cd build
cmake -DENABLE_GR_UHD=ON -DENABLE_GR_FFT=ON -DENABLE_GR_ANALOG=ON \
      -DENABLE_GR_BLOCKS=ON -DENABLE_GRC=ON -DENABLE_GR_QTGUI=ON ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

> 🔄 If Instrumentation blocks (like `AzElPlot`) are still missing in GRC:
>
> Ensure `python3-matplotlib` and all QT5 dev packages are installed:
>
> ```bash
> sudo apt install python3-matplotlib qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools
> ```
>
> Then **rebuild GNU Radio** from Step 8.

---

## ⚙️ RFNoC Enablement

RFNoC (RF Network-on-Chip) enables FPGA-accelerated block processing for supported USRPs. UHD 4.8 includes RFNoC support by default when `-DENABLE_RFNOC=ON` is passed to `cmake`.

To verify:

```bash
uhd_usrp_probe | grep RFNOC
```

If you see lines like:

```
[INFO] [RFNOC] Initialized RFNoC blocks...
```

Then RFNoC is successfully enabled and loaded.

Note:

- RFNoC blocks are only supported by FPGA-enabled USRPs (e.g., X310, N310). USRP1 does **not** support FPGA RFNoC block execution, but UHD will still compile with RFNoC libraries present.
- Useful for mixed environments where newer USRPs are also used.

---

## 🧰 Optional: gr-ettus and RFNoCModTool (Legacy UHD 4.0 + GR 3.8)

If you are working with UHD 4.0 and GNU Radio 3.8 and want to create or customize your own RFNoC blocks, you may also install `gr-ettus` and use the `rfnocmodtool`.

```bash
cd ~/src
git clone --branch maint-3.8-uhd4.0 https://github.com/ettusresearch/gr-ettus.git gr-ettus
mkdir gr-ettus/build && cd gr-ettus/build
cmake -DENABLE_QT=True ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

Then verify the tool:

```bash
export PYTHONPATH=/usr/local/lib/python3/dist-packages/:$PYTHONPATH
rfnocmodtool help
```

This step is **not needed** for UHD 4.8 and GNU Radio 3.11+, where RFNoC support is built into the UHD and GRC tools directly.

---

## 🧪 Testing UHD and GNU Radio

### 9. Verify UHD Installation

```bash
sudo uhd_usrp_probe
```

You can confirm the UHD version from the output, e.g.:

```
[INFO] [UHD] UHD version: 4.8.0.x
```

### 10. Verify GNU Radio Version

```bash
gnuradio-config-info --version
```

This should return something like:

```
3.11.x
```

### 11. Verify RFNoC Support

```bash
uhd_usrp_probe | grep RFNOC
```

If RFNoC blocks are listed or not marked as disabled, RFNoC is properly built in.

### 12. Launch UHD FFT Tool

```bash
uhd_fft --args="type=usrp1" --freq=10e6
```

### 13. Start GNU Radio Companion

```bash
gnuradio-companion
```

Build a simple flowgraph with `UHD: USRP Source` and `QT GUI Sink` to verify.

> 🔍 **Missing Instrumentation Blocks?**
>
> If you don’t see blocks like `AzElPlot` or `DistanceRadar`, ensure:
>
> - `python3-matplotlib` was installed before building GNU Radio.
> - All QT5 dev tools were installed.
> - You **rebuilt GNU Radio** (Step 8).

---

## ⚙️ VMware USB Passthrough

### 14. Connect USRP to VM

- Shut down VM
- In VMware settings:
  - Add USB Controller (2.0 or 3.0)
  - Add USRP USB device
- Boot VM and verify with `uhd_find_devices`

---

## 🛠 USB Device Not Detected? Try This

If you see the following error:

```
[ERROR] [USB] USB open failed: insufficient permissions.
No UHD Devices Found
```

Try:

1. Shut down the VM.
2. In VMware:
   - Go to **Settings > USB & Bluetooth**
   - Under “Connect USB devices”, make sure your **USRP1** (or similar) is listed and set to **“Connect to Linux”**
3. Restart VM and check again:

```bash
uhd_find_devices
```

It should now detect the device and print something like:

```text
[INFO] [UHD] Found USRP1...
```

---

## 📂 Optional: Set Environment Variables

### 15. Add to `~/.bashrc`

```bash
export PATH=/usr/local/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/usr/local/lib/python3/dist-packages/:$PYTHONPATH
```

```bash
source ~/.bashrc
```

---

## ✅ Summary

| Component      | Version | Status                     |
| -------------- | ------- | -------------------------- |
| Ubuntu         | 24.04.2 | ✅ Installed                |
| UHD            | 4.8.x   | ✅ From source              |
| GNU Radio      | main    | ✅ From source              |
| RFNoC          | Enabled | ✅ Verified                 |
| VMware USB     | Yes     | ✅ Connected                |
| USRP1 + RFX900 | ✅       | ✅ Works with UHD 4.8 + GRC |

---

For questions or troubleshooting, refer to:

- [Ettus UHD Docs](https://files.ettus.com/manual/)
- [GNU Radio Wiki](https://wiki.gnuradio.org/index.php/Main_Page)

