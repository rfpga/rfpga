# Ubuntu on VMware Fusion: First-Time Setup Checklist

After installing Ubuntu on VMware Fusion, follow this checklist to optimize your VM:

---

## ✅ 1. Install VMware Tools (or open-vm-tools)

Enhance integration (copy/paste, drag-and-drop, screen resizing):

```bash
sudo apt update
sudo apt install open-vm-tools open-vm-tools-desktop
sudo reboot
```

---

## ✅ 2. Update System Packages

Ensure system is fully up-to-date:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

---

## ✅ 3. Enable Clipboard Sharing and Drag-and-Drop

1. Shut down the VM (do not suspend).
2. In the macOS menu bar, go to **Virtual Machine > Settings > Isolation**.
3. Enable:
   - ✅ **Enable drag and drop**
   - ✅ **Enable copy and paste**

> ⚠️ If this still does not work:
>
> - Ensure `open-vm-tools` and `open-vm-tools-desktop` are installed.
> - Reboot Ubuntu after installation.
> - Some desktop environments (like minimal Ubuntu or Wayland sessions) may not fully support clipboard integration. Try using the Xorg session instead by selecting it at login.

---

## ✅ 4. Install Useful Software

Install common utilities and development tools:

```bash
sudo apt install git curl wget build-essential gnome-tweaks gparted -y
```

---

## ✅ 5. Fix Display Resolution (Optional)

If screen resolution doesn't adjust automatically:

```bash
sudo apt install x11-utils xserver-xorg-video-vmware
```

---

## ✅ 6. Create a Snapshot

Create a snapshot to save a clean state:

- Go to **VMware Fusion > Virtual Machine > Snapshots > Take Snapshot**

---

## ✅ 7. (Optional) Install VMware Tools Manually

If `open-vm-tools` is not enough:

- Use **Virtual Machine > Install VMware Tools**
- Mount the ISO and run the installer inside Ubuntu.

---

## ✅ 8. Enable Shared Folders (Optional)

1. Enable folder sharing under **Settings > Sharing** in VMware.
2. In Ubuntu, access shared folders under `/mnt/hgfs/`.

---

## ✅ 9. Developer Build Environment (GNU Radio/UHD)

For SDR development (e.g. UHD/GNU Radio), install:

```bash
sudo apt install git cmake g++ libboost-all-dev libgmp-dev swig \
python3-numpy python3-mako python3-sphinx python3-lxml \
doxygen libfftw3-dev libsdl2-dev libgsl-dev libqwt-qt5-dev \
libqt5opengl5-dev python3-pyqt5 liblog4cpp5-dev libzmq3-dev \
python3-yaml python3-click python3-click-plugins python3-zmq \
python3-scipy python3-gi python3-gi-cairo gobject-introspection \
gir1.2-gtk-3.0 build-essential libusb-1.0-0-dev python3-docutils \
python3-setuptools python3-ruamel.yaml python-is-python3 \
pkg-config liborc-dev libasound2-dev libvolk-dev pybind11-dev libspdlog-dev
```

> ℹ️ `libtinfo6` and `libncurses6` are already included by default on Ubuntu 24.04.

> ⚠️ If build fails due to missing Volk, pybind11, or spdlog:
>
> ```bash
> sudo apt install libvolk-dev pybind11-dev libspdlog-dev
> ```
>
> If FFTW is missing:
>
> ```bash
> sudo apt install libfftw3-dev
> ```
>
> Then rerun `cmake` with the correct flags.

---

## ✅ 10. Build UHD and GNU Radio from Source

To verify USRP1 with UHD 4.4 and GNU Radio:

### 🔧 Build UHD 4.4

```bash
cd ~/src
rm -rf uhd
git clone --branch UHD-4.4 https://github.com/EttusResearch/uhd.git
cd uhd/host
mkdir build && cd build
cmake -DENABLE_USRP1=ON ..
```

> 🛠️ If build fails with a `uint8_t` error, edit this file:
>
> ```bash
> nano ~/src/uhd/host/lib/include/uhdlib/utils/compat_check.hpp
> ```
>
> Add this line at the top:
>
> ```cpp
> #include <cstdint>
> ```

Then continue:

```bash
make -j$(nproc)
sudo make install
sudo ldconfig
```

Test with:

```bash
sudo uhd_usrp_probe
```

If you see `RFX900` recognized under RX and TX Dboards, your USRP1 + RFX900 is working correctly.

To run `uhd_fft`, install GNU Radio:

```bash
sudo apt install gnuradio  # ⚠️ This installs the latest version (usually 3.11+), not 3.10
uhd_fft --args="type=usrp1"
```

> ⚠️ For USRP1, GNU Radio **3.10** is required. The package above may not work correctly—see below to build it manually.

### ✅ To run GRC (GNU Radio Companion):

If you built GNU Radio 3.10 from source:

```bash
export PYTHONPATH=/usr/local/lib/python3/dist-packages/:$PYTHONPATH
export PATH=/usr/local/bin:$PATH
sudo ldconfig
gnuradio-companion
```

If it still says `command not found`, check:

```bash
ls /usr/local/bin/gnuradio-companion
```

If not present, ensure you enabled GRC during cmake:

```bash
cd ~/src/gnuradio
rm -rf build
mkdir build && cd build
cmake -DENABLE_GRC=ON -DENABLE_DEFAULT=ON .. | tee cmake_output.txt
grep -i grc cmake_output.txt
```

Then rebuild:

```bash
make -j$(nproc)
sudo make install
sudo ldconfig
```

Check again:

```bash
ls /usr/local/bin/gnuradio-companion
```

If still missing, install GUI dependencies:

```bash
sudo apt install python3-pyqt5 qtbase5-dev python3-cairo python3-gi-cairo gir1.2-gtk-3.0 python3-gi
```

Then re-run `cmake`, `make`, and `sudo make install` again.

---

### 🔧 Build GNU Radio 3.10 (compatible with UHD 4.4)

> ✅ GNU Radio 3.10 is recommended because it maintains compatibility with UHD 4.4, which is the **last UHD release that supports USRP1**. Newer GNU Radio versions (3.11+) may **drop legacy blocks and compatibility**, causing issues with older devices like USRP1.

```bash
cd ~/src
rm -rf gnuradio
git clone --branch maint-3.10 https://github.com/gnuradio/gnuradio.git
cd gnuradio
mkdir build && cd build
cmake -DENABLE_DEFAULT=OFF \
  -DENABLE_GR_UHD=ON \
  -DENABLE_GR_ANALOG=ON \
  -DENABLE_GR_BLOCKS=ON \
  -DENABLE_GR_DIGITAL=ON \
  -DENABLE_GR_FILTER=ON \
  -DENABLE_GR_FFT=ON \
  -DENABLE_GNURADIO_RUNTIME=ON \
  -DENABLE_GRC=ON ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

> ✅ Tip: Use Xorg session (not Wayland) to ensure GNU Radio Companion (GRC) displays properly.

---

### ✅ Done! Your Ubuntu VM is now ready for use.

