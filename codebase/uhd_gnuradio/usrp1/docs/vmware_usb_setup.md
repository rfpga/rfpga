# VMware USB Passthrough Setup for USRP on Ubuntu VM

This guide helps you enable USB passthrough for Ettus USRP1 (or other USB-based devices) when running Ubuntu inside VMware (Fusion, Workstation, or Player).

---

## ✅ Prerequisites

- Ubuntu 24.04.x running in **VMware**
- USRP1 device connected via USB
- UHD and GNU Radio already installed

---

## 🔌 Step-by-Step USB Setup in VMware

### 1. Add USB Controller to VM

Before powering on the VM:

- Go to **VM Settings** → **USB & Bluetooth**
- Ensure a **USB Controller** is added (USB 2.0 or USB 3.0 is OK)

### 2. Select the USRP Device

While VM is **powered on**:

- In **VMware USB settings**, under "Connect USB devices",
  - ✅ Select: `Free Software Folks USRP Rev 4`
  - Ensure it says **"Connect to Linux"** or **"Connect to this virtual machine"**

> 📷 *As seen in the screenshot, select the correct device and confirm it's connected.*

---

## 🔍 Verify in Ubuntu

### 3. Check USB Device Presence

```bash
lsusb
```

Expected output should include something like:

```
Bus 001 Device 004: ID fffe:0002 Free Software Folks USRP Rev 4
```

If not found:

- Unplug/replug the USRP
- Reconnect it to the VM via the VMware menu

### 4. Fix USB Permissions

By default, USB devices may be blocked for non-root users. To fix:

#### A. Add a udev rule

Create file:

```bash
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="fffe", ATTR{idProduct}=="0002", MODE="0666"' | sudo tee /etc/udev/rules.d/10-usrp.rules
```

Reload udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

> 🔁 Reconnect the USRP after this step.

#### B. Add your user to plugdev (if needed):

```bash
sudo usermod -aG plugdev $USER
```

Then log out and back in.

---

## ✅ Test UHD Connection

Run:

```bash
uhd_find_devices
```

Expected:

```
[INFO] [UHD] linux; ...
[INFO] [USRP1] Opening a USRP1 device...
...
```

If still failing with `USB open failed: insufficient permissions`:

- Retry as `sudo`
- Check if another app (e.g., VMware Tools) is locking USB

---

## 🔁 Notes

- Some USB devices may require USB 2.0 instead of USB 3.0 for proper operation.
- VMware Fusion sometimes forgets USB preferences after VM reboot — double-check each time.

---

For further support:

- [UHD Manual](https://files.ettus.com/manual/)
- [VMware Docs](https://docs.vmware.com/)

