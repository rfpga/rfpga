# Verifying USRP1 Functionality on UHD 4.0

This guide walks you through verifying that an Ettus USRP1 device functions correctly on a system using UHD 4.0.0+, even though official support was removed after UHD 3.15.x.

---

## Prerequisites

- **USRP1 hardware** with RFX daughterboards installed (e.g., RFX900, RFX1800)
- **UHD 4.0.0+ installed from source** (with USRP1 support not fully removed)
- **GNU Radio (3.8 or later)**

---

## 1. Verify UHD Version

Run the following to check your UHD version:

```bash
uhd_config_info --version
```

Expected output:

```
UHD 4.0.0.0-XXX-gXXXXXXXX
```

---

## 2. Probe USRP1 Device

Run:

```bash
sudo uhd_usrp_probe
```

Look for output confirming:

- FPGA image loads (e.g., `FPGA image loaded`)
- Daughterboards are detected (e.g., `RFX900`, `RFX1800`)
- Clock rate shows `64.000000 MHz` (default)

---

## 3. Spectrum Scan (Receive Test)

Launch a real-time FFT spectrum viewer:

```bash
uhd_fft --args="type=usrp1" --freq=915e6 --gain=30
```

Expected:

- Frequency spectrum window opens
- Baseline noise or signals visible

---

## 4. Loopback Test (TX to RX)

Terminal A:

```bash
uhd_siggen --args="type=usrp1,tx_subdev_spec=A:0" --freq=915e6 --gain=10 --rate=1e6 --wave-type=SINE
```

Terminal B:

```bash
uhd_fft --args="type=usrp1,rx_subdev_spec=B:0" --freq=915e6 --gain=30 --rate=1e6
```

Expected:

- Visible sine wave at 915 MHz on RX side

---

## 5. GRC Flowgraph Test

Create a simple GNU Radio Companion flow:

- **USRP Source**
  - Device Addr: `type=usrp1`
  - Center Freq: `915e6`
  - Gain: `40`
- Connect to:
  - **QT GUI Frequency Sink**

Run it and observe the spectrum.

---

## 6. (Optional) OpenBTS Integration

For OpenBTS:

- Use a 52 MHz FPGA image (e.g., `usrp1_fpga_52mhz.rbf`)
- Replace `/usr/local/share/uhd/images/usrp1_fpga.rbf` with the 52 MHz version
- Launch `uhd_usrp_probe` to verify 52 MHz clock
- Modify OpenBTS transceiver config accordingly

---

## Notes

- USRP1 is **officially unsupported** in UHD 4.x but may still work in early 4.0.x builds
- Full compatibility for OpenBTS or GSM stack may require UHD 3.15.x

---

## Conclusion

If all the above steps succeed, your USRP1 is functional under UHD 4.0.0, at least for RX/TX. Proceed with caution and consider UHD 3.15.x for long-term support or OpenBTS integration.

