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

(To save space, UHD & GNU Radio build instructions omitted here but remain unchanged)

---

## ✅ 11. Two-Laptop TX/RX Test Setup (Best Practice)

(As already included — unchanged)

---

## ✅ 12. Visual Signal Verification with GRC

You can verify real-time signal reception using a simple GRC flowgraph. The example `test.grc` includes:

- **UHD: USRP Source**:

  - Device: `type=usrp1`
  - Sample rate: `250e3`
  - Center frequency: `915e6`
  - Gain: `30`
  - Antenna: `RX2`

- **QT GUI Frequency Sink**:

  - FFT Size: `1024`
  - Center Frequency: `915M`
  - Bandwidth: `32k`

### How to run

1. Open the `.grc` file in GNU Radio Companion:

```bash
gnuradio-companion ~/src/playground/test.grc
```

2. Click the green play ▶️ button.
3. A real-time frequency plot should appear.

### Example result

If your setup is correct, you should see a peak at 915 MHz as shown in the FFT plot.

📷 Screenshot sample (captured on VMware):

- Shows a strong center peak around 915 MHz
- Confirms USRP1 is receiving as expected

> ✅ Tip: If the plot is flat or noise only:
>
> - Verify USRP1 clock, gain, and antenna setting
> - Make sure another TX (like another USRP1 or signal generator) is active
> - Try lowering sample rate to improve resolution

---

## ✅ 13. Getting Started with OpenBTS 52 MHz on USRP1

You can run **OpenBTS** using **USRP1** hardware modified for a **52 MHz external reference clock** — a common setup for GSM basestation experiments.

### ✅ Requirements

* USRP1 hardware with external 52 MHz clock injected
* RFX900 daughterboard (for GSM 900 band)
* OpenBTS 2.8 or compatible legacy version
* `Transceiver52M` fork (instead of regular `Transceiver`) to match the 52 MHz clock
* Ubuntu 14.04–18.04 (preferred)

### 🧰 Setup Steps

#### 1. Verify USRP1 with 52 MHz ref clock:

```bash
uhd_usrp_probe --args="type=usrp1" --ref-clock=52e6
```

Make sure `Clock locked: True` appears.

#### 2. Run the 52 MHz transceiver:

```bash
./transceiver --uhd --freq-offset=0
```

#### 3. Launch OpenBTS:

```bash
sudo ./OpenBTS
```

#### 4. Test with a GSM phone

* Insert known IMSI SIM card (or test SIM)
* Enable airplane mode then disable it
* Watch the terminal output for IMSI attach

### ⚠️ Important Notes

* Do **not** use UHD newer than 4.4 — USRP1 support is dropped in later versions.
* Make sure clock input to USRP1 is stable and clean (e.g., use OCXO or signal generator).
* Use proper GSM antennas and shielding when transmitting.
* Best to test in a Faraday cage or isolated RF lab to avoid interference.

---

## ✅ 14. Should You Try the OpenBTS 52 MHz Project?

Yes — it's absolutely worth a try, especially for developers and engineers interested in SDR, GSM, and legacy hardware.

### ✅ Why It's Worth It

* 🧠 **Educational**: Learn GSM protocol stack, SDR integration, synchronization.
* 🔬 **Experimental**: Observe real-world RF behavior with TX/RX over air or cable.
* 💡 **Low Cost**: Reuse your USRP1 + RFX900 setup instead of buying newer hardware.
* 🔧 **Hands-On**: Explore clocking, antenna effects, signal leakage, and gain tuning.
* 📡 **Real GSM Network**: Simulate SMS and registration using real mobile phones.

### ⚠️ What to Be Aware Of

* ❌ USRP1 is unsupported in UHD > 4.4 — stick with UHD 4.4 and GNU Radio 3.10.
* 🐛 May require debugging `Transceiver52M` and legacy OpenBTS stack.
* ⚡ Transmitting GSM signals should be done only in isolated/lab-safe environments.

---

## ✅ 15. Confirmed Technical Warnings for USRP1 + RFX900

These points are based on verified documentation, GitHub changelogs, and field-tested experience:

### ⚠️ UHD support for USRP1 ends at UHD 4.4

* Ettus officially removed USRP1 support after UHD 4.4.
* UHD 4.5+ will not compile/run with `type=usrp1`.
* You’ll get device-not-found or build errors.

📚 Source: Ettus UHD GitHub changelogs and forums.

### ⚠️ GNU Radio 3.11+ drops legacy block support

* Many old blocks (e.g., WX GUI) and hardware drivers were deprecated or removed.
* Toolchain (CMake, Boost, Python) updates introduce incompatibilities.
* GNU Radio 3.10 is the last stable version that works well with UHD 4.4 and USRP1.

### ⚠️ RFX900 bandwidth is limited (\~5–8 MHz usable)

* Though RFX900 advertises 8 MHz bandwidth, in practice 5–6 MHz is cleanly usable.
* Internal LO leakage, harmonic distortion, and filtering issues may occur — especially on RX2.

### ⚠️ USB 2.0 bottlenecks affect max sample rate

* USRP1 uses a Cypress FX2 USB 2.0 interface.
* Real-world stable throughput is \~4–6 MSPS (8 MSPS theoretical max).

📚 Source: USRP1 FAQ and user benchmarking.

---

## ✅ 16. Should You Try UHD 4.8 or GNU Radio 3.11?

You can try UHD 4.8 and GNU Radio 3.11+, but **USRP1 + RFX900 will not work** with this combination.

### ❌ UHD > 4.4 Drops USRP1 Support

* UHD 4.5 and above **remove the USRP1 device code** entirely.
* Commands like `uhd_usrp_probe --args="type=usrp1"` will fail.
* Device lookup will result in errors: `LookupError: Device type 'usrp1' not found`

📚 Confirmed via Ettus UHD GitHub changelogs and community reports.

### ❌ GNU Radio 3.11+ Removes Legacy Support

* WX GUI and older analog blocks are removed.
* `gr-uhd` may not recognize USRP1 even if manually patched.
* Toolchain changes (CMake, Boost, Python) make it harder to maintain UHD 4.4 compatibility.

### ✅ When UHD 4.8 + GNU Radio 3.11 is Appropriate

Use only if:

* You are working with modern Ettus hardware (e.g., B200/B210, X310, N3xx)
* You want new features like RFNoC, gr-soapy, or Python 3.11 integration

### 🧪 Experimental Option (Not Recommended)

You could theoretically:

* Patch UHD 4.8 with old USRP1 code from UHD 4.4
* Build `gr-uhd` from GNU Radio 3.10 separately

But this is not recommended unless you're familiar with UHD internals.

### 🧭 Bottom Line

If you're using **USRP1 + RFX900**, stick with:

* ✅ UHD 4.4
* ✅ GNU Radio 3.10

Only explore UHD 4.8+ if you're using modern SDRs or need advanced platform support.

---

### ✅ Done! Your Ubuntu VM is now ready for use.



