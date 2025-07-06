# 🎯 Phase 1: Foundation - Detailed UHD Internal Hacking Guide
*USRP1 + RFX900 & B210 Focus*

## **Week 1: SDR Theory & UHD Architecture Deep Dive**

### 📚 Learning Objectives
- Understand fundamental SDR concepts through USRP hardware lens
- Master UHD architecture and internal components
- Compare USRP1 vs B210 architectural differences

### 🛠️ Hardware Setup & Initial Exploration

**Day 1-2: Hardware Reconnaissance**
```bash
# Discover and probe your hardware
uhd_find_devices
uhd_usrp_probe --args="type=usrp1"
uhd_usrp_probe --args="type=b200"

# Deep hardware inspection
uhd_usrp_probe --args="type=usrp1" --tree
uhd_usrp_probe --args="type=b200" --tree
```

**Day 3-4: UHD Source Code Exploration**
- Clone UHD repository: `git clone https://github.com/EttusResearch/uhd.git`
- Navigate key directories:
  - `/host/lib/usrp/` - Device-specific implementations
  - `/host/lib/usrp/usrp1/` - USRP1 specific code
  - `/host/lib/usrp/b200/` - B210 specific code
  - `/host/lib/transport/` - Transport layer implementations

**Day 5-7: Architecture Comparison Exercise**

Create comparison matrix:

| Feature | USRP1 + RFX900 | B210 |
|---------|----------------|------|
| Bus Interface | USB 2.0 | USB 3.0 |
| FPGA | Cyclone EP3C25 | Cyclone IV |
| ADC/DAC | External on RFX900 | Integrated AD936x |
| Frequency Range | 800-1000 MHz | 70 MHz - 6 GHz |
| Bandwidth | 8 MHz | 61.44 MHz |

### 🔍 Practical Exercises

**Exercise 1.1: UHD Device Tree Parsing**
```cpp
// Create C++ program to parse device tree
#include <uhd/usrp/multi_usrp.hpp>
#include <uhd/property_tree.hpp>

uhd::usrp::multi_usrp::sptr usrp = uhd::usrp::multi_usrp::make(args);
uhd::property_tree::sptr tree = usrp->get_tree();
// Explore /mboards/0/ properties
```

**Exercise 1.2: Transport Layer Investigation**
- Capture USB traffic during USRP operations
- Analyze packet structure differences between USRP1 and B210
- Document command/response patterns

---

## **Week 2: GNU Radio & UHD Block Architecture**

### 📚 Learning Objectives
- Master GNU Radio-UHD integration internals
- Understand gr-uhd source/sink block implementations
- Create custom UHD-based GNU Radio blocks

### 🔧 GNU Radio UHD Internals

**Day 1-3: gr-uhd Source Code Analysis**

Examine key files:
```bash
# GNU Radio UHD module source
/gnuradio/gr-uhd/lib/usrp_source_impl.cc
/gnuradio/gr-uhd/lib/usrp_sink_impl.cc
/gnuradio/gr-uhd/include/gnuradio/uhd/usrp_source.h
```

**Day 4-5: UHD Stream API Deep Dive**
```cpp
// Understand streaming internals
uhd::rx_streamer::sptr rx_stream = usrp->get_rx_stream(stream_args);
uhd::tx_streamer::sptr tx_stream = usrp->get_tx_stream(stream_args);

// Analyze buffer management
size_t samps_per_buff = rx_stream->get_max_num_samps();
```

**Day 6-7: Hardware-Specific Streaming Differences**
- USRP1: USB 2.0 limitations, packet structure
- B210: USB 3.0 streaming, higher bandwidth capabilities

### 🔍 Practical Exercises

**Exercise 2.1: Custom UHD GNU Radio Block**

Create a custom GNU Radio block that directly interfaces with UHD:
```cpp
class custom_uhd_source : public gr::sync_block {
private:
    uhd::usrp::multi_usrp::sptr d_usrp;
    uhd::rx_streamer::sptr d_rx_stream;
public:
    int work(int noutput_items, /* ... */);
};
```

**Exercise 2.2: Streaming Performance Analysis**
- Measure sustainable sample rates for both platforms
- Analyze overflow/underflow conditions
- Document performance characteristics

**Exercise 2.3: Buffer Management Study**
- Implement custom buffer management strategies
- Compare default vs optimized approaches
- Measure latency improvements

---

## **Week 3: Hardware-Specific UHD Programming & Hacking**

### 📚 Learning Objectives
- Master UHD API for both USRP1 and B210
- Understand hardware register-level programming
- Implement custom firmware modifications

### 🛠️ Low-Level UHD Programming

**Day 1-2: Register-Level Access**
```cpp
// Direct register access (USRP1)
usrp->get_tree()->access<uint32_t>("/mboards/0/fw_version").get();

// B210 specific registers
usrp->get_tree()->access<double>("/mboards/0/rx_dsps/0/rate/value").set(rate);
```

**Day 3-4: USRP1 Firmware Exploration**
- Examine USRP1 firmware source in `/firmware/fx2/`
- Understand USB endpoint configuration
- Study RFX900 daughterboard interface

**Day 5-7: B210 FPGA Image Analysis**
- Download B210 FPGA source
- Analyze DSP chain implementation
- Understand AD936x integration

### 🔍 Advanced Practical Exercises

**Exercise 3.1: Custom USRP1 Firmware Modification**
```c
// Modify USRP1 firmware to add custom USB commands
// File: /firmware/fx2/usrp1/usrp_main.c
case VRQ_CUSTOM_COMMAND:
    // Your custom implementation
    break;
```

**Exercise 3.2: B210 FPGA Custom Build**
- Modify B210 FPGA image
- Add custom DSP processing block
- Build and flash custom image

**Exercise 3.3: UHD Transport Layer Hacking**
```cpp
// Create custom transport for optimized performance
class custom_usb_transport : public uhd::transport::zero_copy_if {
    // Implement optimized USB transport
};
```

**Exercise 3.4: Hardware-Specific Calibration**
- Implement custom calibration routines for RFX900
- Create B210 frequency response correction
- Compare calibration approaches

### 🎯 Capstone Project: Multi-Platform UHD Application

Create a comprehensive application that:

1. **Auto-detects** USRP1 vs B210 hardware
2. **Optimizes** streaming parameters per platform
3. **Implements** hardware-specific features
4. **Provides** unified API abstraction

```cpp
class UniversalUSRP {
private:
    enum usrp_type_t { USRP1_RFX900, B210 } device_type;
    uhd::usrp::multi_usrp::sptr usrp;
    
public:
    void auto_configure();
    void optimize_for_hardware();
    double get_optimal_sample_rate();
    void apply_hardware_specific_settings();
};
```

### 📊 Assessment Criteria

- **Technical Depth**: Understanding of UHD internals
- **Hardware Knowledge**: Platform-specific optimizations
- **Code Quality**: Clean, efficient implementations
- **Innovation**: Creative solutions to hardware limitations
- **Documentation**: Clear explanation of discoveries

### 🛠️ Required Tools & Environment

**Software Requirements:**
- UHD 4.0+ with development headers
- GNU Radio 3.9+
- GCC/G++ with C++17 support
- Git
- USB protocol analyzer (Wireshark with USBPcap)
- Logic analyzer software (optional but recommended)

**Hardware Requirements:**
- USRP1 with RFX900 daughterboard
- USRP B210
- USB 2.0 and USB 3.0 cables
- RF cables and adapters
- Spectrum analyzer or SDR for verification

**Development Environment Setup:**
```bash
# Install UHD from source for development
git clone https://github.com/EttusResearch/uhd.git
cd uhd/host
mkdir build && cd build
cmake -DCMAKE_INSTALL_PREFIX=/usr/local ../
make -j4 && sudo make install

# Install GNU Radio development environment
sudo apt-get install gnuradio-dev
```

### 📚 Additional Learning Resources

**Essential Documentation:**
- UHD Manual: https://files.ettus.com/manual/
- USRP1 Hardware Manual
- B210 Hardware Manual
- GNU Radio UHD Documentation
- Ettus Research Knowledge Base

**Recommended Reading:**
- "Software Defined Radio using MATLAB & Simulink and the RTL-SDR"
- "Software Radio: A Modern Approach to Radio Engineering"
- USRP1 and B210 schematics and reference designs

**Online Communities:**
- GNU Radio Mailing List
- Ettus Research Forums
- Reddit r/RTLSDR and r/AmateurRadio
- Stack Overflow SDR tags

### 🎯 Learning Outcomes

By the end of Phase 1, you will:

1. **Master UHD Architecture**: Deep understanding of UHD's internal structure and how it interfaces with different USRP hardware
2. **Hardware Expertise**: Comprehensive knowledge of USRP1 and B210 differences, capabilities, and limitations
3. **GNU Radio Integration**: Ability to create custom GNU Radio blocks that efficiently interface with UHD
4. **Low-Level Programming**: Skills in register-level programming and firmware modification
5. **Performance Optimization**: Understanding of how to optimize streaming performance for different hardware platforms
6. **Problem-Solving**: Ability to debug and troubleshoot complex SDR hardware and software issues

### 📋 Phase 1 Completion Checklist

- [ ] Successfully probe and characterize both USRP1 and B210 hardware
- [ ] Complete all practical exercises with documented results
- [ ] Build and test custom UHD-based GNU Radio blocks
- [ ] Implement at least one firmware or FPGA modification
- [ ] Create comprehensive comparison documentation
- [ ] Complete capstone project with working demonstration
- [ ] Document all discoveries and optimizations
- [ ] Prepare presentation of key learnings and innovations

---

*This intensive 3-week foundation provides deep UHD knowledge while building practical skills with both legacy (USRP1) and modern (B210) hardware platforms. The focus on internal hacking and low-level programming prepares you for advanced FPGA development in subsequent phases.*