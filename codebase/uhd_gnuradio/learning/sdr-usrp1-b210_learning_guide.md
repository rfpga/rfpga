# Complete SDR Learning Guide: UHD, GNU Radio & FPGA Development

## 📋 Learning Path Overview

This guide takes you from C++/Python basics through advanced FPGA development for software-defined radio systems using accessible hardware platforms.

### Prerequisites Checklist
- ✅ C++ proficiency (classes, templates, memory management)
- ✅ Python proficiency (modules, NumPy, SciPy)
- ✅ Basic Linux command line
- ⬜ Digital Signal Processing fundamentals
- ⬜ FPGA development (we'll cover this)

### Hardware Requirements

**Option 1: USRP1 + RFX900 (Classic Platform)**
- **Cost**: ~$1,500 used
- **Frequency Range**: 750-1050 MHz (RFX900)
- **Sample Rate**: Up to 8 MS/s
- **Interface**: USB 2.0
- **FPGA**: Altera Cyclone EP1C12 (12k LEs)
- **Best For**: Learning FPGA basics, cost-effective development

**Option 2: USRP B210 (Modern Platform)**
- **Cost**: ~$2,100 new
- **Frequency Range**: 70 MHz - 6 GHz (full duplex)
- **Sample Rate**: Up to 61.44 MS/s
- **Interface**: USB 3.0
- **FPGA**: Xilinx Spartan-6 XC6SLX150
- **Best For**: Advanced applications, higher performance

**Hardware Comparison Table**
| Feature | USRP1 + RFX900 | USRP B210 |
|---------|-----------------|-----------|
| FPGA Resources | 12k LEs | 147k LUTs |
| Max Sample Rate | 8 MS/s | 61.44 MS/s |
| Frequency Coverage | 750-1050 MHz | 70 MHz - 6 GHz |
| Full Duplex | No | Yes |
| GPSDO Support | External | External |
| MIMO Support | Limited | 2x2 |

---

## 🎯 Phase 1: Foundation (Weeks 1-3)

### Week 1: SDR Theory & Architecture

**Day 1-2: Core Concepts**
```bash
# Essential reading
- Understanding I/Q sampling
- Nyquist theorem and aliasing
- Digital downconversion (DDC)
- Digital upconversion (DUC)
```

**Practice Exercise 1.1: I/Q Visualization**
```python
import numpy as np
import matplotlib.pyplot as plt

# Generate complex baseband signal
t = np.linspace(0, 1, 1000)
freq = 10  # Hz
signal = np.exp(1j * 2 * np.pi * freq * t)

# Plot I/Q components
plt.figure(figsize=(12, 4))
plt.subplot(131)
plt.plot(t, signal.real, label='I (Real)')
plt.plot(t, signal.imag, label='Q (Imaginary)')
plt.legend()
plt.title('I/Q Time Domain')

plt.subplot(132)
plt.plot(signal.real, signal.imag)
plt.title('I/Q Constellation')
plt.axis('equal')

plt.subplot(133)
plt.specgram(signal, Fs=1000)
plt.title('Spectrogram')
plt.tight_layout()
plt.show()
```

**Day 3-5: UHD Architecture Deep Dive**

Study the UHD source structure:
```bash
~/uhd/host/
├── lib/
│   ├── usrp/           # Device-specific drivers
│   ├── rfnoc/          # RFNoC framework
│   ├── transport/      # USB/Ethernet/PCIe
│   └── types/          # Data types and ranges
├── include/uhd/        # Public API headers
├── utils/              # Command-line utilities
└── tests/              # Unit and integration tests
```

**Practice Exercise 1.2: Hardware-Specific Device Discovery**
```cpp
// discover_devices.cpp - Works with both USRP1 and B210
#include <uhd/utils/safe_main.hpp>
#include <uhd/device.hpp>
#include <uhd/usrp/multi_usrp.hpp>
#include <iostream>

int UHD_SAFE_MAIN(int argc, char* argv[]) {
    // Find all UHD devices
    uhd::device_addrs_t device_addrs = uhd::device::find("");
    
    if (device_addrs.empty()) {
        std::cout << "No UHD devices found" << std::endl;
        std::cout << "For USRP1: Check USB connection and permissions" << std::endl;
        std::cout << "For B210: Ensure USB 3.0 connection" << std::endl;
        return EXIT_FAILURE;
    }
    
    for (const auto& addr : device_addrs) {
        std::cout << "Found device: " << addr.to_string() << std::endl;
        
        // Create USRP object to get detailed info
        auto usrp = uhd::usrp::multi_usrp::make(addr);
        auto info = usrp->get_usrp_info();
        
        std::cout << "  Device: " << info["mboard_id"] << std::endl;
        std::cout << "  Serial: " << info["mboard_serial"] << std::endl;
        
        // Hardware-specific configuration
        if (info["mboard_id"] == "usrp1") {
            std::cout << "  USRP1 detected - FPGA: Altera Cyclone" << std::endl;
            std::cout << "  Max sample rate: 8 MS/s" << std::endl;
            
            // Check for daughterboard
            auto subdev_spec = usrp->get_rx_subdev_spec();
            auto subdev_name = usrp->get_rx_subdev_name();
            std::cout << "  RX Daughterboard: " << subdev_name << std::endl;
            
        } else if (info["mboard_id"] == "B210") {
            std::cout << "  B210 detected - FPGA: Xilinx Spartan-6" << std::endl;
            std::cout << "  Max sample rate: 61.44 MS/s" << std::endl;
            std::cout << "  Full duplex capable" << std::endl;
        }
    }
    
    return EXIT_SUCCESS;
}
```

**Hardware-Specific Setup Instructions**

For **USRP1 + RFX900**:
```bash
# Check USB permissions
lsusb | grep fffe  # Should show Ettus Research device

# Add udev rules for USRP1
sudo cp uhd/host/utils/uhd-usrp.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules

# Download FPGA images (for USRP1)
sudo uhd_images_downloader --types=fpga-usrp1

# Test connection
uhd_find_devices
uhd_usrp_probe --args="type=usrp1"
```

For **USRP B210**:
```bash
# Ensure USB 3.0 connection
lsusb -t  # Check if connected to USB 3.0 hub

# Download FPGA/firmware images
sudo uhd_images_downloader --types=b2xx

# Test connection
uhd_find_devices
uhd_usrp_probe --args="type=b200"
```
```

### Week 2: GNU Radio Block Architecture

**Day 1-3: Understanding the Runtime**

GNU Radio's scheduler and buffer management:
```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Source Block  │───▶│  Filter Block   │───▶│   Sink Block    │
│  (produces data)│    │ (transforms)    │    │ (consumes data) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
    Circular Buffer        Circular Buffer        Circular Buffer
    (thread-safe)          (thread-safe)          (thread-safe)
```

**Practice Exercise 2.1: Custom GNU Radio Block (C++)**
```cpp
// my_multiplier_impl.h
#ifndef INCLUDED_MY_MULTIPLIER_IMPL_H
#define INCLUDED_MY_MULTIPLIER_IMPL_H

#include <gnuradio/sync_block.h>

class my_multiplier_impl : public gr::sync_block {
private:
    float d_multiplier;

public:
    my_multiplier_impl(float multiplier);
    ~my_multiplier_impl();
    
    int work(int noutput_items,
             gr_vector_const_void_star &input_items,
             gr_vector_void_star &output_items);
};

// my_multiplier_impl.cc
#include "my_multiplier_impl.h"
#include <gnuradio/io_signature.h>

my_multiplier_impl::my_multiplier_impl(float multiplier)
    : gr::sync_block("my_multiplier",
                     gr::io_signature::make(1, 1, sizeof(float)),
                     gr::io_signature::make(1, 1, sizeof(float))),
      d_multiplier(multiplier) {}

int my_multiplier_impl::work(int noutput_items,
                            gr_vector_const_void_star &input_items,
                            gr_vector_void_star &output_items) {
    const float *in = (const float *) input_items[0];
    float *out = (float *) output_items[0];
    
    for (int i = 0; i < noutput_items; i++) {
        out[i] = in[i] * d_multiplier;
    }
    
    return noutput_items;
}
```

**Day 4-5: SWIG Integration**
```swig
// my_multiplier.i
%include "gnuradio.i"

%{
#include "my_multiplier_impl.h"
%}

%include "my_multiplier_impl.h"
GR_SWIG_BLOCK_MAGIC2(my, multiplier);
```

### Week 3: Hardware-Specific UHD Programming

**USRP1 Specific Considerations**
```cpp
// usrp1_config.cpp - USRP1 with RFX900 configuration
#include <uhd/usrp/multi_usrp.hpp>
#include <iostream>

class USRP1Controller {
private:
    uhd::usrp::multi_usrp::sptr usrp;
    
public:
    USRP1Controller() {
        // Create USRP1 device
        usrp = uhd::usrp::multi_usrp::make("type=usrp1");
    }
    
    void configure_for_rfx900() {
        // RFX900 specific settings
        // Frequency range: 750-1050 MHz
        double center_freq = 900e6; // 900 MHz
        double sample_rate = 4e6;   // 4 MS/s (safe for USB 2.0)
        
        // Set sample rate (limited by USB 2.0)
        usrp->set_rx_rate(sample_rate);
        usrp->set_tx_rate(sample_rate);
        
        // Set frequency (RFX900 range)
        usrp->set_rx_freq(center_freq);
        usrp->set_tx_freq(center_freq);
        
        // Set gains (RFX900 has different gain ranges)
        double rx_gain = 15.0; // 0-45 dB range
        double tx_gain = 15.0; // 0-25 dB range
        usrp->set_rx_gain(rx_gain);
        usrp->set_tx_gain(tx_gain);
        
        // Configure antenna ports
        usrp->set_rx_antenna("RX2"); // RFX900 has RX2, TX/RX
        usrp->set_tx_antenna("TX/RX");
        
        std::cout << "USRP1/RFX900 Configuration:" << std::endl;
        std::cout << "  RX Rate: " << usrp->get_rx_rate()/1e6 << " MS/s" << std::endl;
        std::cout << "  RX Freq: " << usrp->get_rx_freq()/1e6 << " MHz" << std::endl;
        std::cout << "  RX Gain: " << usrp->get_rx_gain() << " dB" << std::endl;
    }
    
    void stream_samples() {
        // Create RX streamer with appropriate buffer sizes for USB 2.0
        uhd::stream_args_t stream_args("fc32", "sc16");
        uhd::rx_streamer::sptr rx_stream = usrp->get_rx_stream(stream_args);
        
        // Smaller buffer for USRP1
        size_t samps_per_buff = rx_stream->get_max_num_samps();
        std::vector<std::complex<float>> buff(samps_per_buff);
        
        // Start streaming
        uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_START_CONTINUOUS);
        rx_stream->issue_stream_cmd(stream_cmd);
        
        // Receive samples
        uhd::rx_metadata_t md;
        for (int i = 0; i < 100; ++i) {
            size_t num_rx_samps = rx_stream->recv(&buff.front(), buff.size(), md);
            
            if (md.error_code == uhd::rx_metadata_t::ERROR_CODE_TIMEOUT) {
                std::cout << "Timeout waiting for samples" << std::endl;
                continue;
            }
            
            // Process samples
            double power = 0.0;
            for (const auto& sample : buff) {
                power += std::norm(sample);
            }
            power /= buff.size();
            
            std::cout << "Received " << num_rx_samps << " samples, Power: " 
                      << 10*log10(power) << " dBFS" << std::endl;
        }
        
        // Stop streaming
        stream_cmd.stream_mode = uhd::stream_cmd_t::STREAM_MODE_STOP_CONTINUOUS;
        rx_stream->issue_stream_cmd(stream_cmd);
    }
};
```

**B210 Specific Optimizations**
```cpp
// b210_config.cpp - B210 high-performance configuration
#include <uhd/usrp/multi_usrp.hpp>
#include <thread>

class B210Controller {
private:
    uhd::usrp::multi_usrp::sptr usrp;
    
public:
    B210Controller() {
        // Create B210 device with specific args for performance
        std::string device_args = "type=b200,num_recv_frames=128,num_send_frames=128";
        usrp = uhd::usrp::multi_usrp::make(device_args);
    }
    
    void configure_high_performance() {
        // B210 can handle much higher rates
        double sample_rate = 20e6;  // 20 MS/s
        double center_freq = 2.4e9; // 2.4 GHz (WiFi band)
        
        // Set high sample rate (possible with USB 3.0)
        usrp->set_rx_rate(sample_rate, 0);
        usrp->set_tx_rate(sample_rate, 0);
        
        // Wide frequency range available
        usrp->set_rx_freq(center_freq, 0);
        usrp->set_tx_freq(center_freq, 0);
        
        // B210 specific gain settings
        usrp->set_rx_gain(40.0, 0); // 0-76 dB range
        usrp->set_tx_gain(50.0, 0); // 0-89.8 dB range
        
        // Configure for full duplex
        usrp->set_rx_antenna("RX2", 0);
        usrp->set_tx_antenna("TX/RX", 0);
        
        std::cout << "B210 High-Performance Configuration:" << std::endl;
        std::cout << "  Sample Rate: " << usrp->get_rx_rate(0)/1e6 << " MS/s" << std::endl;
        std::cout << "  Frequency: " << usrp->get_rx_freq(0)/1e9 << " GHz" << std::endl;
        std::cout << "  RX Gain: " << usrp->get_rx_gain(0) << " dB" << std::endl;
    }
    
    void mimo_configuration() {
        // B210 supports 2x2 MIMO
        if (usrp->get_rx_num_channels() >= 2) {
            // Configure both channels
            for (size_t ch = 0; ch < 2; ++ch) {
                usrp->set_rx_rate(10e6, ch);
                usrp->set_rx_freq(2.45e9 + ch * 10e6, ch); // Slightly offset
                usrp->set_rx_gain(30.0, ch);
                usrp->set_rx_antenna("RX2", ch);
            }
            
            // Synchronize channels
            usrp->set_time_source("internal");
            usrp->set_clock_source("internal");
            usrp->set_time_now(uhd::time_spec_t(0.0));
            
            std::cout << "MIMO 2x2 configured" << std::endl;
        }
    }
    
    void full_duplex_streaming() {
        // Create streamers for simultaneous TX/RX
        uhd::stream_args_t stream_args("fc32", "sc16");
        uhd::rx_streamer::sptr rx_stream = usrp->get_rx_stream(stream_args);
        uhd::tx_streamer::sptr tx_stream = usrp->get_tx_stream(stream_args);
        
        // Buffers
        size_t samps_per_buff = 1000;
        std::vector<std::complex<float>> rx_buff(samps_per_buff);
        std::vector<std::complex<float>> tx_buff(samps_per_buff);
        
        // Generate test signal
        for (size_t i = 0; i < samps_per_buff; ++i) {
            tx_buff[i] = std::complex<float>(0.1 * cos(2*M_PI*0.1*i), 
                                           0.1 * sin(2*M_PI*0.1*i));
        }
        
        // Start RX
        uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_START_CONTINUOUS);
        rx_stream->issue_stream_cmd(stream_cmd);
        
        // Simultaneous TX/RX loop
        uhd::rx_metadata_t rx_md;
        uhd::tx_metadata_t tx_md;
        tx_md.start_of_burst = true;
        tx_md.end_of_burst = false;
        
        for (int i = 0; i < 1000; ++i) {
            // Transmit
            tx_stream->send(&tx_buff.front(), samps_per_buff, tx_md);
            tx_md.start_of_burst = false;
            
            // Receive
            size_t num_rx = rx_stream->recv(&rx_buff.front(), samps_per_buff, rx_md);
            
            if (i % 100 == 0) {
                std::cout << "Full duplex iteration " << i << std::endl;
            }
        }
        
        // Stop
        tx_md.end_of_burst = true;
        tx_stream->send(&tx_buff.front(), 0, tx_md);
        
        stream_cmd.stream_mode = uhd::stream_cmd_t::STREAM_MODE_STOP_CONTINUOUS;
        rx_stream->issue_stream_cmd(stream_cmd);
    }
};
```
```

---

## 🚀 Phase 2: Intermediate Development (Weeks 4-8)

### Week 4-5: RFNoC Framework

**Understanding RFNoC Architecture**
```text
Host Computer                           FPGA
┌─────────────────┐    PCIe/Ethernet    ┌─────────────────┐
│  GNU Radio     │◄──────────────────►│   RFNoC Blocks  │
│  Application   │                     │                 │
├─────────────────┤                     ├─────────────────┤
│  UHD Driver    │                     │  Crossbar       │
│  (RFNoC API)   │                     │  Switch         │
└─────────────────┘                     └─────────────────┘
```

**Practice Exercise 4.1: Custom RFNoC Block**
```cpp
// noc_block_gain.cpp - FPGA processing block
#include <uhd/rfnoc/noc_block_base.hpp>

class noc_block_gain : public uhd::rfnoc::noc_block_base {
public:
    UHD_RFNOC_BLOCK_CONSTRUCTOR(noc_block_gain) {
        // Register properties
        register_property(&_gain);
        
        // Configure data flow
        set_num_input_ports(1);
        set_num_output_ports(1);
    }

private:
    uhd::rfnoc::property_t<double> _gain{
        RFNOC_PROP_KEY_GAIN, 1.0, {uhd::rfnoc::res_source_info::USER}
    };
};

UHD_RFNOC_BLOCK_REGISTER_DIRECT(
    noc_block_gain, NOC_ID, "Gain", CLOCK_KEY_GRAPH, "gain"
);
```

**Corresponding Verilog Implementation**
```verilog
// noc_block_gain.v
module noc_block_gain #(
    parameter NOC_ID = 64'h1234_5678_9ABC_DEF0
)(
    // Clock and reset
    input wire bus_clk,
    input wire bus_rst,
    input wire ce_clk,
    input wire ce_rst,
    
    // AXI-Stream interfaces
    input  wire [31:0] s_axis_data_tdata,
    input  wire        s_axis_data_tlast,
    input  wire        s_axis_data_tvalid,
    output wire        s_axis_data_tready,
    
    output reg  [31:0] m_axis_data_tdata,
    output reg         m_axis_data_tlast,
    output reg         m_axis_data_tvalid,
    input  wire        m_axis_data_tready,
    
    // Settings bus
    input wire [7:0]   set_addr,
    input wire [31:0]  set_data,
    input wire         set_stb
);

// Gain register
reg [15:0] gain_reg = 16'h4000; // Default gain = 1.0 (Q1.15)

always @(posedge ce_clk) begin
    if (set_stb && set_addr == 8'd0) begin
        gain_reg <= set_data[15:0];
    end
end

// Signal processing pipeline
wire [15:0] i_in = s_axis_data_tdata[31:16];
wire [15:0] q_in = s_axis_data_tdata[15:0];

wire [31:0] i_mult = i_in * gain_reg;
wire [31:0] q_mult = q_in * gain_reg;

wire [15:0] i_out = i_mult[30:15]; // Scale back from Q1.15
wire [15:0] q_out = q_mult[30:15];

always @(posedge ce_clk) begin
    if (ce_rst) begin
        m_axis_data_tvalid <= 1'b0;
        m_axis_data_tlast  <= 1'b0;
    end else if (s_axis_data_tvalid && s_axis_data_tready) begin
        m_axis_data_tdata  <= {i_out, q_out};
        m_axis_data_tlast  <= s_axis_data_tlast;
        m_axis_data_tvalid <= 1'b1;
    end else if (m_axis_data_tready) begin
        m_axis_data_tvalid <= 1'b0;
    end
end

assign s_axis_data_tready = !m_axis_data_tvalid || m_axis_data_tready;

endmodule
```

### Week 6-7: Hardware-Specific DSP Implementation

**USRP1 Optimized DSP (Resource-Constrained)**
```cpp
// usrp1_dsp_algorithms.cpp - Optimized for limited FPGA resources
#include <uhd/usrp/multi_usrp.hpp>
#include <vector>
#include <complex>

class USRP1DSPProcessor {
private:
    uhd::usrp::multi_usrp::sptr usrp;
    
public:
    USRP1DSPProcessor() {
        usrp = uhd::usrp::multi_usrp::make("type=usrp1");
        configure_for_efficiency();
    }
    
    void configure_for_efficiency() {
        // Lower sample rates for USRP1 to ensure stable operation
        double sample_rate = 4e6; // 4 MS/s max for reliable operation
        usrp->set_rx_rate(sample_rate);
        usrp->set_tx_rate(sample_rate);
        
        // Use RFX900 optimal frequency
        usrp->set_rx_freq(915e6); // ISM band
        usrp->set_tx_freq(915e6);
        
        // Conservative gains
        usrp->set_rx_gain(20.0);
        usrp->set_tx_gain(10.0);
        
        std::cout << "USRP1 configured for efficient DSP processing" << std::endl;
        std::cout << "Sample rate: " << usrp->get_rx_rate()/1e6 << " MS/s" << std::endl;
    }
    
    // Simple but effective decimating filter
    std::vector<std::complex<float>> decimating_filter(
        const std::vector<std::complex<float>>& input, 
        int decimation_factor = 4) {
        
        // Simple boxcar filter before decimation
        std::vector<std::complex<float>> filtered;
        std::vector<std::complex<float>> output;
        
        // Apply simple moving average
        for (size_t i = decimation_factor; i < input.size(); ++i) {
            std::complex<float> sum(0, 0);
            for (int j = 0; j < decimation_factor; ++j) {
                sum += input[i - j];
            }
            filtered.push_back(sum / float(decimation_factor));
        }
        
        // Decimate
        for (size_t i = 0; i < filtered.size(); i += decimation_factor) {
            output.push_back(filtered[i]);
        }
        
        return output;
    }
    
    // Power estimation optimized for USRP1
    std::vector<float> compute_power_spectrum(
        const std::vector<std::complex<float>>& samples,
        int fft_size = 256) { // Smaller FFT for USRP1
        
        std::vector<float> power_spectrum(fft_size, 0.0f);
        
        // Simple DFT implementation (no external libraries)
        for (int k = 0; k < fft_size; ++k) {
            std::complex<float> bin_sum(0, 0);
            
            for (int n = 0; n < std::min(fft_size, (int)samples.size()); ++n) {
                float phase = -2.0f * M_PI * k * n / fft_size;
                std::complex<float> twiddle(cos(phase), sin(phase));
                bin_sum += samples[n] * twiddle;
            }
            
            power_spectrum[k] = std::norm(bin_sum);
        }
        
        return power_spectrum;
    }
};
```

**B210 Advanced DSP Implementation**
```cpp
// b210_advanced_dsp.cpp - Full-featured implementation
#include <uhd/usrp/multi_usrp.hpp>
#include <fftw3.h>
#include <liquid/liquid.h>

class B210AdvancedDSP {
private:
    uhd::usrp::multi_usrp::sptr usrp;
    
    // FFTW plans for efficient FFT
    fftwf_plan fft_plan;
    fftwf_complex* fft_in;
    fftwf_complex* fft_out;
    size_t fft_size;
    
    // Liquid DSP objects
    firfilt_crcf decimator;
    nco_crcf local_oscillator;
    
public:
    B210AdvancedDSP(size_t fft_len = 2048) : fft_size(fft_len) {
        usrp = uhd::usrp::multi_usrp::make("type=b200");
        setup_advanced_processing();
        configure_high_performance();
    }
    
    void configure_high_performance() {
        // B210 can handle much higher sample rates
        double sample_rate = 20e6; // 20 MS/s
        usrp->set_rx_rate(sample_rate, 0);
        usrp->set_tx_rate(sample_rate, 0);
        
        // Wide frequency range
        usrp->set_rx_freq(2.45e9, 0); // 2.45 GHz
        usrp->set_tx_freq(2.45e9, 0);
        
        // High dynamic range settings
        usrp->set_rx_gain(50.0, 0);
        usrp->set_tx_gain(60.0, 0);
        
        // Enable both channels for MIMO
        if (usrp->get_rx_num_channels() >= 2) {
            usrp->set_rx_rate(sample_rate, 1);
            usrp->set_rx_freq(2.45e9 + 10e6, 1); // Offset for diversity
            usrp->set_rx_gain(50.0, 1);
        }
        
        std::cout << "B210 configured for high-performance DSP" << std::endl;
        std::cout << "Sample rate: " << usrp->get_rx_rate(0)/1e6 << " MS/s" << std::endl;
        std::cout << "MIMO channels: " << usrp->get_rx_num_channels() << std::endl;
    }
    
    void setup_advanced_processing() {
        // Initialize FFTW
        fft_in = (fftwf_complex*) fftwf_malloc(sizeof(fftwf_complex) * fft_size);
        fft_out = (fftwf_complex*) fftwf_malloc(sizeof(fftwf_complex) * fft_size);
        fft_plan = fftwf_plan_dft_1d(fft_size, fft_in, fft_out, 
                                    FFTW_FORWARD, FFTW_MEASURE);
        
        // Setup liquid DSP components
        // Design anti-aliasing filter
        unsigned int h_len = 64;
        float fc = 0.25f; // Cutoff frequency
        float As = 60.0f; // Stopband attenuation
        
        firfilt_crcf_create_kaiser(h_len, fc, As, 0.0f);
        
        // Create NCO for digital mixing
        local_oscillator = nco_crcf_create(LIQUID_VCO);
        nco_crcf_set_frequency(local_oscillator, 0.1f); // 10% of sample rate
    }
    
    ~B210AdvancedDSP() {
        // Cleanup
        fftwf_destroy_plan(fft_plan);
        fftwf_free(fft_in);
        fftwf_free(fft_out);
        firfilt_crcf_destroy(decimator);
        nco_crcf_destroy(local_oscillator);
    }
    
    // High-performance channelizer
    std::vector<std::vector<std::complex<float>>> channelize_spectrum(
        const std::vector<std::complex<float>>& input,
        int num_channels = 16) {
        
        std::vector<std::vector<std::complex<float>>> channels(num_channels);
        
        // Process in chunks
        size_t chunk_size = fft_size;
        for (size_t offset = 0; offset < input.size(); offset += chunk_size) {
            size_t samples_to_process = std::min(chunk_size, input.size() - offset);
            
            // Copy to FFT input buffer
            for (size_t i = 0; i < samples_to_process; ++i) {
                fft_in[i][0] = input[offset + i].real();
                fft_in[i][1] = input[offset + i].imag();
            }
            
            // Zero pad if necessary
            for (size_t i = samples_to_process; i < fft_size; ++i) {
                fft_in[i][0] = 0.0f;
                fft_in[i][1] = 0.0f;
            }
            
            // Perform FFT
            fftwf_execute(fft_plan);
            
            // Extract channels
            int bins_per_channel = fft_size / num_channels;
            for (int ch = 0; ch < num_channels; ++ch) {
                for (int bin = 0; bin < bins_per_channel; ++bin) {
                    int fft_bin = ch * bins_per_channel + bin;
                    std::complex<float> sample(fft_out[fft_bin][0], fft_out[fft_bin][1]);
                    channels[ch].push_back(sample);
                }
            }
        }
        
        return channels;
    }
    
    // MIMO beamforming (B210 specific)
    std::vector<std::complex<float>> beamform_mimo(
        const std::vector<std::complex<float>>& ch0_samples,
        const std::vector<std::complex<float>>& ch1_samples,
        float steering_angle = 0.0f) {
        
        std::vector<std::complex<float>> beamformed;
        
        // Simple delay-and-sum beamforming
        float lambda = 3e8 / 2.45e9; // Wavelength at 2.45 GHz
        float array_spacing = lambda / 2; // Half-wavelength spacing
        
        // Calculate phase delay
        float phase_delay = 2 * M_PI * array_spacing * sin(steering_angle) / lambda;
        std::complex<float> phase_shift = std::exp(std::complex<float>(0, phase_delay));
        
        size_t min_samples = std::min(ch0_samples.size(), ch1_samples.size());
        
        for (size_t i = 0; i < min_samples; ++i) {
            std::complex<float> beam_sample = ch0_samples[i] + ch1_samples[i] * phase_shift;
            beamformed.push_back(beam_sample / 2.0f); // Normalize
        }
        
        return beamformed;
    }
    
    // Real-time spectrum analysis
    void real_time_spectrum_monitor() {
        // Create high-throughput RX streamer
        uhd::stream_args_t stream_args("fc32", "sc16");
        stream_args.args["spp"] = "2048"; // Samples per packet
        uhd::rx_streamer::sptr rx_stream = usrp->get_rx_stream(stream_args);
        
        // Buffers for continuous processing
        std::vector<std::complex<float>> buffer(fft_size);
        std::vector<float> power_spectrum(fft_size);
        
        // Start streaming
        uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_START_CONTINUOUS);
        rx_stream->issue_stream_cmd(stream_cmd);
        
        uhd::rx_metadata_t md;
        
        for (int frame = 0; frame < 1000; ++frame) {
            // Receive samples
            size_t num_rx = rx_stream->recv(&buffer.front(), buffer.size(), md);
            
            if (md.error_code != uhd::rx_metadata_t::ERROR_CODE_NONE) {
                std::cout << "RX error: " << md.strerror() << std::endl;
                continue;
            }
            
            // Apply window function
            for (size_t i = 0; i < num_rx; ++i) {
                float window = 0.5f - 0.5f * cos(2.0f * M_PI * i / (num_rx - 1)); // Hann window
                buffer[i] *= window;
            }
            
            // Compute power spectrum
            compute_power_spectrum(buffer, power_spectrum);
            
            // Find peak
            auto max_it = std::max_element(power_spectrum.begin(), power_spectrum.end());
            int peak_bin = std::distance(power_spectrum.begin(), max_it);
            float peak_freq = (peak_bin - fft_size/2) * usrp->get_rx_rate(0) / fft_size;
            
            if (frame % 100 == 0) {
                std::cout << "Frame " << frame << ": Peak at " << peak_freq/1e6 
                         << " MHz, Power: " << 10*log10(*max_it) << " dB" << std::endl;
            }
        }
        
        // Stop streaming
        stream_cmd.stream_mode = uhd::stream_cmd_t::STREAM_MODE_STOP_CONTINUOUS;
        rx_stream->issue_stream_cmd(stream_cmd);
    }
    
private:
    void compute_power_spectrum(const std::vector<std::complex<float>>& input,
                               std::vector<float>& output) {
        // Copy to FFT buffer
        for (size_t i = 0; i < std::min(input.size(), fft_size); ++i) {
            fft_in[i][0] = input[i].real();
            fft_in[i][1] = input[i].imag();
        }
        
        // Execute FFT
        fftwf_execute(fft_plan);
        
        // Compute power and apply FFT shift
        for (size_t i = 0; i < fft_size; ++i) {
            size_t shifted_i = (i + fft_size/2) % fft_size;
            float power = fft_out[i][0] * fft_out[i][0] + fft_out[i][1] * fft_out[i][1];
            output[shifted_i] = power / (fft_size * fft_size); // Normalize
        }
    }
};
```

**Comparative Performance Testing**
```python
# hardware_comparison.py - Compare USRP1 vs B210 performance
import uhd
import numpy as np
import time
import matplotlib.pyplot as plt

class HardwareComparison:
    def __init__(self):
        self.results = {}
    
    def test_usrp1_performance(self):
        """Test USRP1 + RFX900 capabilities"""
        print("Testing USRP1 + RFX900...")
        
        try:
            usrp = uhd.usrp.MultiUSRP("type=usrp1")
            
            # USRP1 limitations
            max_rate_test = [1e6, 2e6, 4e6, 8e6]  # Test up to 8 MS/s
            successful_rates = []
            
            for rate in max_rate_test:
                try:
                    usrp.set_rx_rate(rate)
                    actual_rate = usrp.get_rx_rate()
                    
                    if abs(actual_rate - rate) < 1e3:  # Within 1 kHz
                        successful_rates.append(rate)
                        print(f"  ✓ {rate/1e6:.1f} MS/s achieved")
                    else:
                        print(f"  ✗ {rate/1e6:.1f} MS/s failed (got {actual_rate/1e6:.1f} MS/s)")
                        break
                except Exception as e:
                    print(f"  ✗ {rate/1e6:.1f} MS/s error: {e}")
                    break
            
            # Frequency range test (RFX900)
            freq_range = usrp.get_rx_freq_range()
            print(f"  Frequency range: {freq_range.start()/1e6:.1f} - {freq_range.stop()/1e6:.1f} MHz")
            
            # Gain range test
            gain_range = usrp.get_rx_gain_range()
            print(f"  RX gain range: {gain_range.start():.1f} - {gain_range.stop():.1f} dB")
            
            self.results['usrp1'] = {
                'max_rate': max(successful_rates),
                'freq_range': (freq_range.start(), freq_range.stop()),
                'gain_range': (gain_range.start(), gain_range.stop()),
                'fpga': 'Altera Cyclone EP1C12 (12k LEs)'
            }
            
        except Exception as e:
            print(f"USRP1 test failed: {e}")
            self.results['usrp1'] = None
    
    def test_b210_performance(self):
        """Test B210 capabilities"""
        print("\nTesting B210...")
        
        try:
            usrp = uhd.usrp.MultiUSRP("type=b200")
            
            # B210 can handle much higher rates
            max_rate_test = [5e6, 10e6, 20e6, 30e6, 50e6, 61.44e6]
            successful_rates = []
            
            for rate in max_rate_test:
                try:
                    usrp.set_rx_rate(rate)
                    actual_rate = usrp.get_rx_rate()
                    
                    if abs(actual_rate - rate) < 1e4:  # Within 10 kHz
                        successful_rates.append(rate)
                        print(f"  ✓ {rate/1e6:.1f} MS/s achieved")
                    else:
                        print(f"  ✗ {rate/1e6:.1f} MS/s failed (got {actual_rate/1e6:.1f} MS/s)")
                        break
                except Exception as e:
                    print(f"  ✗ {rate/1e6:.1f} MS/s error: {e}")
                    break
            
            # Wide frequency range
            freq_range = usrp.get_rx_freq_range()
            print(f"  Frequency range: {freq_range.start()/1e6:.1f} - {freq_range.stop()/1e6:.1f} MHz")
            
            # High dynamic range
            gain_range = usrp.get_rx_gain_range()
            print(f"  RX gain range: {gain_range.start():.1f} - {gain_range.stop():.1f} dB")
            
            # Test MIMO capability
            num_channels = usrp.get_rx_num_channels()
            print(f"  MIMO channels: {num_channels}")
            
            self.results['b210'] = {
                'max_rate': max(successful_rates),
                'freq_range': (freq_range.start(), freq_range.stop()),
                'gain_range': (gain_range.start(), gain_range.stop()),
                'mimo_channels': num_channels,
                'fpga': 'Xilinx Spartan-6 XC6SLX150 (147k LUTs)'
            }
            
        except Exception as e:
            print(f"B210 test failed: {e}")
            self.results['b210'] = None
    
    def latency_comparison(self):
        """Compare end-to-end latency"""
        print("\nLatency Comparison:")
        
        for hw_name in ['usrp1', 'b210']:
            if self.results.get(hw_name) is None:
                continue
                
            try:
                device_args = f"type={'usrp1' if hw_name == 'usrp1' else 'b200'}"
                usrp = uhd.usrp.MultiUSRP(device_args)
                
                # Configure for latency test
                test_rate = 1e6  # 1 MS/s for fair comparison
                usrp.set_rx_rate(test_rate)
                usrp.set_tx_rate(test_rate)
                
                if hw_name == 'usrp1':
                    usrp.set_rx_freq(915e6)
                    usrp.set_tx_freq(915e6)
                else:
                    usrp.set_rx_freq(2.45e9)
                    usrp.set_tx_freq(2.45e9)
                
                # Latency measurement
                latencies = []
                for _ in range(10):
                    start_time = time.perf_counter()
                    
                    # Quick loopback test
                    tx_samples = np.array([1.0 + 1.0j], dtype=np.complex64)
                    rx_samples = np.zeros(1, dtype=np.complex64)
                    
                    # This is simplified - real latency measurement is more complex
                    time.sleep(0.001)  # Simulate processing time
                    
                    end_time = time.perf_counter()
                    latencies.append((end_time - start_time) * 1e6)  # Convert to microseconds
                
                avg_latency = np.mean(latencies)
                std_latency = np.std(latencies)
                
                print(f"  {hw_name.upper()}: {avg_latency:.1f} ± {std_latency:.1f} μs")
                self.results[hw_name]['latency'] = avg_latency
                
            except Exception as e:
                print(f"  {hw_name.upper()}: Latency test failed - {e}")
    
    def generate_comparison_report(self):
        """Generate comprehensive comparison report"""
        print("\n" + "="*60)
        print("HARDWARE COMPARISON REPORT")
        print("="*60)
        
        if self.results.get('usrp1') and self.results.get('b210'):
            usrp1 = self.results['usrp1']
            b210 = self.results['b210']
            
            print(f"{'Metric':<25} {'USRP1 + RFX900':<20} {'B210':<20}")
            print("-" * 65)
            print(f"{'Max Sample Rate':<25} {usrp1['max_rate']/1e6:.1f} MS/s{'':<12} {b210['max_rate']/1e6:.1f} MS/s")
            print(f"{'Frequency Range':<25} {usrp1['freq_range'][0]/1e6:.0f}-{usrp1['freq_range'][1]/1e6:.0f} MHz{'':<6} {b210['freq_range'][0]/1e6:.0f}-{b210['freq_range'][1]/1e6:.0f} MHz")
            print(f"{'RX Gain Range':<25} {usrp1['gain_range'][0]:.0f}-{usrp1['gain_range'][1]:.0f} dB{'':<10} {b210['gain_range'][0]:.0f}-{b210['gain_range'][1]:.0f} dB")
            print(f"{'MIMO Channels':<25} 1{'':<19} {b210.get('mimo_channels', 'N/A')}")
            
            if 'latency' in usrp1 and 'latency' in b210:
                print(f"{'End-to-End Latency':<25} {usrp1['latency']:.1f} μs{'':<12} {b210['latency']:.1f} μs")
            
            print(f"{'FPGA':<25} {usrp1['fpga']:<20} {b210['fpga']}")
            
            print("\nRecommendations:")
            print("• USRP1 + RFX900: Best for learning, cost-effective, ISM band applications")
            print("• B210: Best for wide-band applications, MIMO, high sample rates")
            
        else:
            print("Incomplete test results - ensure both devices are connected")

if __name__ == "__main__":
    comparison = HardwareComparison()
    comparison.test_usrp1_performance()
    comparison.test_b210_performance()
    comparison.latency_comparison()
    comparison.generate_comparison_report()
```
```cpp
// fir_filter.cpp
#include <vector>
#include <complex>

class FIRFilter {
private:
    std::vector<float> taps;
    std::vector<std::complex<float>> delay_line;
    size_t delay_index;

public:
    FIRFilter(const std::vector<float>& coefficients) 
        : taps(coefficients), 
          delay_line(coefficients.size(), {0, 0}),
          delay_index(0) {}
    
    std::complex<float> process(std::complex<float> input) {
        // Insert new sample
        delay_line[delay_index] = input;
        
        // Compute output
        std::complex<float> output(0, 0);
        for (size_t i = 0; i < taps.size(); ++i) {
            size_t tap_index = (delay_index + i) % taps.size();
            output += taps[i] * delay_line[tap_index];
        }
        
        // Update delay index
        delay_index = (delay_index > 0) ? delay_index - 1 : taps.size() - 1;
        
        return output;
    }
};
```

Optimized Verilog Implementation:
```verilog
// fir_filter.v - Systolic array implementation
module fir_filter #(
    parameter WIDTH = 16,
    parameter TAPS = 64
)(
    input wire clk,
    input wire rst,
    input wire signed [WIDTH-1:0] data_i,
    input wire signed [WIDTH-1:0] data_q,
    input wire data_valid,
    output reg signed [WIDTH-1:0] filt_i,
    output reg signed [WIDTH-1:0] filt_q,
    output reg filt_valid
);

// Coefficient memory
reg signed [WIDTH-1:0] coeffs [0:TAPS-1];
initial $readmemh("fir_coeffs.hex", coeffs);

// Shift register for input samples
reg signed [WIDTH-1:0] shift_reg_i [0:TAPS-1];
reg signed [WIDTH-1:0] shift_reg_q [0:TAPS-1];

// Multiply-accumulate chain
wire signed [2*WIDTH-1:0] mac_i [0:TAPS-1];
wire signed [2*WIDTH-1:0] mac_q [0:TAPS-1];

genvar i;
generate
for (i = 0; i < TAPS; i = i + 1) begin : mac_array
    if (i == 0) begin
        assign mac_i[i] = shift_reg_i[i] * coeffs[i];
        assign mac_q[i] = shift_reg_q[i] * coeffs[i];
    end else begin
        assign mac_i[i] = mac_i[i-1] + (shift_reg_i[i] * coeffs[i]);
        assign mac_q[i] = mac_q[i-1] + (shift_reg_q[i] * coeffs[i]);
    end
end
endgenerate

// Pipeline registers
reg [2:0] valid_delay;

always @(posedge clk) begin
    if (rst) begin
        valid_delay <= 3'b0;
        filt_valid <= 1'b0;
    end else begin
        // Shift register update
        if (data_valid) begin
            shift_reg_i[0] <= data_i;
            shift_reg_q[0] <= data_q;
            for (int j = 1; j < TAPS; j = j + 1) begin
                shift_reg_i[j] <= shift_reg_i[j-1];
                shift_reg_q[j] <= shift_reg_q[j-1];
            end
        end
        
        // Output pipeline
        valid_delay <= {valid_delay[1:0], data_valid};
        filt_valid <= valid_delay[2];
        
        if (valid_delay[2]) begin
            filt_i <= mac_i[TAPS-1][2*WIDTH-2:WIDTH-1]; // Scale output
            filt_q <= mac_q[TAPS-1][2*WIDTH-2:WIDTH-1];
        end
    end
end

endmodule
```

### Week 8: Performance Optimization

**Memory Management and Zero-Copy Techniques**
```cpp
// zero_copy_example.cpp
#include <uhd/types/metadata.hpp>
#include <uhd/stream.hpp>

class ZeroCopyStreamer {
private:
    uhd::rx_streamer::sptr rx_stream;
    static constexpr size_t MAX_SAMPS_PER_PACKET = 1000;

public:
    void efficient_receive() {
        // Allocate managed buffers
        std::vector<std::complex<float>*> buff_ptrs;
        std::vector<uhd::rx_streamer::buffs_type> buff_containers;
        
        // Get managed receive buffers (zero-copy when possible)
        auto managed_buffs = rx_stream->get_recv_buffs(0.1);
        
        if (managed_buffs.size() > 0) {
            // Direct access to hardware buffers
            for (auto& buff : managed_buffs) {
                auto* samples = buff->cast<std::complex<float>*>();
                // Process samples in-place
                process_samples_inplace(samples, buff->size());
            }
        }
    }
    
private:
    void process_samples_inplace(std::complex<float>* samples, size_t count) {
        // SIMD-optimized processing
        #pragma omp simd
        for (size_t i = 0; i < count; ++i) {
            // Apply processing without copying
            samples[i] *= std::complex<float>(0.5f, 0.0f);
        }
    }
};
```

---

### Week 9-10: Hardware-Specific FPGA Toolchain Setup

**USRP1 Development Environment (Altera/Intel Quartus)**
```bash
# setup_usrp1_dev.sh
#!/bin/bash

echo "Setting up USRP1 development environment..."

# Install Quartus II 13.0sp1 (last version supporting Cyclone)
# Download from Intel FPGA website
wget https://download.altera.com/akdlm/software/acdsinst/13.0sp1/232/ib_installers/QuartusSetup-13.0.1.232.run

# Install
chmod +x QuartusSetup-13.0.1.232.run
sudo ./QuartusSetup-13.0.1.232.run

# Set environment
export QUARTUS_ROOTDIR=/opt/altera/13.0sp1/quartus
export PATH=$QUARTUS_ROOTDIR/bin:$PATH

# Clone USRP1 FPGA source
git clone https://github.com/EttusResearch/fpga.git
cd fpga/usrp1/toplevel/usrp_std

echo "USRP1 development environment ready"
echo "FPGA: Altera Cyclone EP1C12Q240C8"
echo "Resources: 12,060 LEs, 52 M4K RAM blocks"
```

**B210 Development Environment (Xilinx ISE)**
```bash
# setup_b210_dev.sh
#!/bin/bash

echo "Setting up B210 development environment..."

# Install Xilinx ISE 14.7 (supports Spartan-6)
# Download from Xilinx website (requires free account)
wget https://xilinx-ax-dl.entitlenow.com/dl/ul/2014/11/24/R208947123/Xilinx_ISE_DS_Lin_14.7_1015_1.tar

# Extract and install
tar -xvf Xilinx_ISE_DS_Lin_14.7_1015_1.tar
cd Xilinx_ISE_DS_Lin_14.7_1015_1
sudo ./xsetup

# Set environment
source /opt/Xilinx/14.7/ISE_DS/settings64.sh

# Clone B200 FPGA source
git clone --branch uhd-3.15 https://github.com/EttusResearch/fpga.git
cd fpga/usrp3/top/b200

echo "B210 development environment ready"
echo "FPGA: Xilinx Spartan-6 XC6SLX150-3FGG484"
echo "Resources: 147,443 LUTs, 4.8 Mb Block RAM"
```

**Hardware-Specific Project Templates**

USRP1 Project Template:
```tcl
# usrp1_project_template.tcl
# Create new USRP1 project

# Project settings for EP1C12
project_new usrp1_custom -overwrite

# Device settings
set_global_assignment -name FAMILY "Cyclone"
set_global_assignment -name DEVICE EP1C12Q240C8
set_global_assignment -name TOP_LEVEL_ENTITY usrp_std
set_global_assignment -name ORIGINAL_QUARTUS_VERSION 13.0
set_global_assignment -name PROJECT_CREATION_TIME_DATE "$(date)"

# Clock settings (USRP1 uses 64 MHz master clock)
set_global_assignment -name FMAX_REQUIREMENT "64 MHz" -section_id clk64
create_clock -name {clk64} -period 15.625 -waveform {0.000 7.813} [get_ports {master_clk}]

# Pin assignments for USRP1
set_location_assignment PIN_28 -to master_clk
set_location_assignment PIN_29 -to SCLK
set_location_assignment PIN_30 -to SDI
set_location_assignment PIN_33 -to SDO
set_location_assignment PIN_34 -to SEN_FPGA

# I/O standards
set_instance_assignment -name IO_STANDARD "3.3-V LVTTL" -to master_clk
set_instance_assignment -name IO_STANDARD "3.3-V LVTTL" -to SCLK

# Add source files
set_global_assignment -name VERILOG_FILE usrp_std.v
set_global_assignment -name VERILOG_FILE usrp1_custom_dsp.v
set_global_assignment -name SDC_FILE usrp_std.sdc

# Memory settings (limited on EP1C12)
set_global_assignment -name OPTIMIZE_HOLD_TIMING "ALL PATHS"
set_global_assignment -name OPTIMIZE_MULTI_CORNER_TIMING ON
set_global_assignment -name FITTER_EFFORT "STANDARD FIT"

project_close
```

B210 Project Template:
```tcl
# b210_project_template.tcl
# ISE project for B210

# Create project
project new b200.xise

# Device settings for Spartan-6
project set family "Spartan6"
project set device "xc6slx150"
project set package "fgg484"
project set speed "-3"

# Add source files
xfile add "b200.v" -top
xfile add "b200_core.v"
xfile add "b210_advanced_dsp.v"
xfile add "axi_wrapper.v"

# Add constraints
xfile add "b200.ucf"
xfile add "b200_timing.ucf"

# Clock settings (B210 uses multiple clock domains)
# 40 MHz reference clock
# 200 MHz bus clock  
# Variable radio clock

# Synthesis settings
project set "Synthesis Tool" "XST (VHDL/Verilog)"
project set "Use DSP Block" "Auto"
project set "Pack I/O Registers into IOBs" "Auto"

# Implementation settings
project set "Place & Route Effort Level (Overall)" "High"
project set "Use Timing Constraints" "true"
project set "Create Binary Configuration File" "true"

project close
```

**Resource Utilization Guidelines**

USRP1 Resource Management:
```verilog
// usrp1_resource_budget.v
// Resource budget for EP1C12 (12,060 LEs total)

/*
Recommended resource allocation for USRP1:
- Control logic: ~1,000 LEs (8%)
- Interface logic: ~1,500 LEs (12%)
- DSP processing: ~8,000 LEs (66%)
- User logic: ~1,500 LEs (12%)
- Spare: ~60 LEs (2%)

Memory blocks (52 M4K blocks total):
- FIR filter coefficients: 4-8 blocks
- Buffer memory: 8-16 blocks
- User memory: 24-36 blocks
- System: 4-8 blocks
*/

module usrp1_resource_monitor (
    input wire clk,
    input wire reset,
    output reg [15:0] le_usage_percent,
    output reg [15:0] mem_usage_percent
);

// Approximate resource counting
// In real design, this would be reported by Quartus
parameter TOTAL_LES = 12060;
parameter TOTAL_M4K = 52;

// Example usage tracking
reg [13:0] estimated_le_usage;
reg [5:0] estimated_m4k_usage;

always @(posedge clk) begin
    if (reset) begin
        estimated_le_usage <= 14'd0;
        estimated_m4k_usage <= 6'd0;
    end else begin
        // Update based on enabled features
        // This is a simplified example
        le_usage_percent <= (estimated_le_usage * 100) / TOTAL_LES;
        mem_usage_percent <= (estimated_m4k_usage * 100) / TOTAL_M4K;
    end
end

endmodule
```

B210 Resource Management:
```verilog
// b210_resource_budget.v
// Resource budget for XC6SLX150 (147,443 LUTs total)

/*
Recommended resource allocation for B210:
- Control and interface: ~20,000 LUTs (14%)
- DSP processing: ~100,000 LUTs (68%)
- User applications: ~25,000 LUTs (17%)
- Spare: ~2,443 LUTs (1%)

DSP48A1 slices (180 total):
- DDC/DUC chains: 40-60 slices
- User DSP: 80-120 slices
- System/misc: 20-40 slices

Block RAM (4.8 Mb total):
- Sample buffers: 1-2 Mb
- Filter coefficients: 0.5 Mb
- User memory: 2-3 Mb
- System: 0.3 Mb
*/

module b210_resource_monitor (
    input wire clk,
    input wire reset,
    output reg [15:0] lut_usage_percent,
    output reg [15:0] dsp_usage_percent,
    output reg [15:0] bram_usage_percent
);

parameter TOTAL_LUTS = 147443;
parameter TOTAL_DSP48 = 180;
parameter TOTAL_BRAM_18K = 268; // 4.8 Mb / 18Kb each

// Resource tracking
reg [17:0] estimated_lut_usage;
reg [7:0] estimated_dsp_usage;
reg [8:0] estimated_bram_usage;

always @(posedge clk) begin
    if (reset) begin
        estimated_lut_usage <= 18'd0;
        estimated_dsp_usage <= 8'd0;
        estimated_bram_usage <= 9'd0;
    end else begin
        lut_usage_percent <= (estimated_lut_usage * 100) / TOTAL_LUTS;
        dsp_usage_percent <= (estimated_dsp_usage * 100) / TOTAL_DSP48;
        bram_usage_percent <= (estimated_bram_usage * 100) / TOTAL_BRAM_18K;
    end
end

endmodule
```

### Week 11-12: Platform-Specific Advanced DSP

**USRP1 Optimized FFT (Resource Constrained)**
```verilog
// usrp1_efficient_fft.v
// Memory-efficient FFT for limited FPGA resources
module usrp1_fft_64 (
    input wire clk64,
    input wire reset,
    input wire [15:0] data_i,
    input wire [15:0] data_q,
    input wire data_valid,
    output reg [15:0] fft_i,
    output reg [15:0] fft_q,
    output reg fft_valid
);

// 64-point FFT using radix-2 decimation-in-time
// Optimized for EP1C12 resource constraints

parameter FFT_SIZE = 64;
parameter STAGES = 6; // log2(64)

// Single memory block for ping-pong buffering
reg [31:0] fft_memory [0:63]; // Use one M4K block
reg memory_select;
reg [5:0] input_counter;
reg [2:0] stage_counter;

// Twiddle factor ROM (reduced precision)
reg [15:0] twiddle_cos [0:31];
reg [15:0] twiddle_sin [0:31];

// Initialize twiddle factors
initial begin
    integer i;
    for (i = 0; i < 32; i = i + 1) begin
        twiddle_cos[i] = $rtoi(16383 * $cos(-2 * 3.14159 * i / 64));
        twiddle_sin[i] = $rtoi(16383 * $sin(-2 * 3.14159 * i / 64));
    end
end

// State machine
reg [2:0] state;
localparam IDLE = 3'd0, INPUT = 3'd1, COMPUTE = 3'd2, OUTPUT = 3'd3;

always @(posedge clk64) begin
    if (reset) begin
        state <= IDLE;
        input_counter <= 6'd0;
        stage_counter <= 3'd0;
        fft_valid <= 1'b0;
        memory_select <= 1'b0;
    end else begin
        case (state)
            IDLE: begin
                if (data_valid) begin
                    state <= INPUT;
                    input_counter <= 6'd0;
                end
            end
            
            INPUT: begin
                if (data_valid) begin
                    fft_memory[input_counter] <= {data_q, data_i};
                    input_counter <= input_counter + 1;
                    
                    if (input_counter == FFT_SIZE - 1) begin
                        state <= COMPUTE;
                        stage_counter <= 3'd0;
                    end
                end
            end
            
            COMPUTE: begin
                // Simplified butterfly computation
                // In real implementation, this would be pipelined
                stage_counter <= stage_counter + 1;
                
                if (stage_counter == STAGES - 1) begin
                    state <= OUTPUT;
                    input_counter <= 6'd0;
                end
            end
            
            OUTPUT: begin
                fft_i <= fft_memory[input_counter][15:0];
                fft_q <= fft_memory[input_counter][31:16];
                fft_valid <= 1'b1;
                input_counter <= input_counter + 1;
                
                if (input_counter == FFT_SIZE - 1) begin
                    state <= IDLE;
                    fft_valid <= 1'b0;
                end
            end
        endcase
    end
end

endmodule
```

**B210 High-Performance FFT Pipeline**
```verilog
// b210_streaming_fft.v
// High-throughput streaming FFT using Xilinx IP
module b210_streaming_fft_2048 (
    input wire clk,
    input wire reset,
    
    // Input stream
    input wire [31:0] s_axis_data_tdata,
    input wire s_axis_data_tvalid,
    input wire s_axis_data_tlast,
    output wire s_axis_data_tready,
    
    // Output stream
    output wire [31:0] m_axis_data_tdata,
    output wire m_axis_data_tvalid,
    output wire m_axis_data_tlast,
    input wire m_axis_data_tready,
    
    // Configuration
    input wire [4:0] fft_size_log2, // 6-11 for 64-2048 point FFT
    input wire fft_direction,       // 0=forward, 1=inverse
    input wire [1:0] scaling_mode   // 0=none, 1=unscaled, 2=scaled
);

// Xilinx FFT IP core (optimized for Spartan-6)
xfft_v9_1 fft_core (
    .aclk(clk),
    .aresetn(~reset),
    
    // Configuration channel
    .s_axis_config_tdata({
        8'b0,           // Reserved
        scaling_mode,   // Scaling schedule
        1'b0,           // Reserved
        fft_direction,  // Forward/inverse
        6'b0,           // Reserved
        fft_size_log2   // Transform length
    }),
    .s_axis_config_tvalid(1'b1),
    .s_axis_config_tready(),
    
    // Data input
    .s_axis_data_tdata(s_axis_data_tdata),
    .s_axis_data_tvalid(s_axis_data_tvalid),
    .s_axis_data_tready(s_axis_data_tready),
    .s_axis_data_tlast(s_axis_data_tlast),
    
    // Data output
    .m_axis_data_tdata(m_axis_data_tdata),
    .m_axis_data_tvalid(m_axis_data_tvalid),
    .m_axis_data_tready(m_axis_data_tready),
    .m_axis_data_tlast(m_axis_data_tlast),
    
    // Status outputs
    .event_frame_started(),
    .event_tlast_unexpected(),
    .event_tlast_missing(),
    .event_status_channel_halt(),
    .event_data_in_channel_halt(),
    .event_data_out_channel_halt()
);

endmodule

// Spectral analysis engine using the FFT
module b210_spectrum_analyzer (
    input wire clk,
    input wire reset,
    
    // Sample input
    input wire [31:0] sample_data,
    input wire sample_valid,
    
    // Spectrum output
    output reg [31:0] spectrum_magnitude,
    output reg [10:0] spectrum_bin,
    output reg spectrum_valid,
    
    // Control
    input wire [10:0] fft_size,
    input wire [15:0] averaging_factor
);

// Window function ROM
reg [15:0] window_rom [0:2047];
reg [10:0] window_addr;

// Initialize with Blackman-Harris window
initial begin
    integer i;
    real a0 = 0.35875;
    real a1 = 0.48829;
    real a2 = 0.14128;
    real a3 = 0.01168;
    
    for (i = 0; i < 2048; i = i + 1) begin
        real n = i;
        real N = 2048;
        real window_val = a0 - a1*$cos(2*3.14159*n/(N-1)) + 
                         a2*$cos(4*3.14159*n/(N-1)) - 
                         a3*$cos(6*3.14159*n/(N-1));
        window_rom[i] = $rtoi(16383 * window_val);
    end
end

// Sample buffer with windowing
reg [31:0] windowed_samples [0:2047];
reg [10:0] sample_count;
reg windowing_complete;

// Apply window function
wire [15:0] sample_i = sample_data[15:0];
wire [15:0] sample_q = sample_data[31:16];
wire [15:0] window_coeff = window_rom[sample_count];

wire [31:0] windowed_i = (sample_i * window_coeff) >>> 14;
wire [31:0] windowed_q = (sample_q * window_coeff) >>> 14;

always @(posedge clk) begin
    if (reset) begin
        sample_count <= 11'd0;
        windowing_complete <= 1'b0;
    end else if (sample_valid && sample_count < fft_size) begin
        windowed_samples[sample_count] <= {windowed_q[15:0], windowed_i[15:0]};
        sample_count <= sample_count + 1;
        
        if (sample_count == fft_size - 1) begin
            windowing_complete <= 1'b1;
            sample_count <= 11'd0;
        end
    end else begin
        windowing_complete <= 1'b0;
    end
end

// FFT processing
wire [31:0] fft_result;
wire fft_result_valid;
wire fft_tlast;

b210_streaming_fft_2048 fft_engine (
    .clk(clk),
    .reset(reset),
    .s_axis_data_tdata(windowed_samples[sample_count]),
    .s_axis_data_tvalid(windowing_complete),
    .s_axis_data_tlast(sample_count == fft_size - 1),
    .s_axis_data_tready(),
    .m_axis_data_tdata(fft_result),
    .m_axis_data_tvalid(fft_result_valid),
    .m_axis_data_tlast(fft_tlast),
    .m_axis_data_tready(1'b1),
    .fft_size_log2(11), // 2048-point
    .fft_direction(1'b0), // Forward
    .scaling_mode(2'b10) // Scaled
);

// Magnitude calculation and averaging
reg [31:0] magnitude_accumulator [0:2047];
reg [15:0] average_count;
reg [10:0] output_bin_counter;

always @(posedge clk) begin
    if (reset) begin
        average_count <= 16'd0;
        output_bin_counter <= 11'd0;
        spectrum_valid <= 1'b0;
    end else if (fft_result_valid) begin
        // Calculate magnitude squared
        wire [15:0] real_part = fft_result[15:0];
        wire [15:0] imag_part = fft_result[31:16];
        wire [31:0] magnitude_sq = real_part * real_part + imag_part * imag_part;
        
        // Accumulate for averaging
        magnitude_accumulator[output_bin_counter] <= 
            magnitude_accumulator[output_bin_counter] + magnitude_sq;
        
        output_bin_counter <= output_bin_counter + 1;
        
        if (fft_tlast) begin
            average_count <= average_count + 1;
            output_bin_counter <= 11'd0;
            
            // Output averaged spectrum
            if (average_count >= averaging_factor) begin
                spectrum_valid <= 1'b1;
                average_count <= 16'd0;
            end
        end
    end else if (spectrum_valid) begin
        // Output spectrum bins
        spectrum_magnitude <= magnitude_accumulator[spectrum_bin] / averaging_factor;
        spectrum_bin <= spectrum_bin + 1;
        
        if (spectrum_bin == fft_size - 1) begin
            spectrum_valid <= 1'b0;
            spectrum_bin <= 11'd0;
            
            // Clear accumulator for next averaging cycle
            for (int i = 0; i < 2048; i = i + 1) begin
                magnitude_accumulator[i] <= 32'd0;
            end
        end
    end
end

endmodule
```

### Week 13-14: Hardware-Specific Timing and Optimization

**USRP1 Timing Constraints (Quartus SDC)**
```sdc
# usrp1_timing.sdc
# Timing constraints for USRP1 EP1C12

# Define clocks
create_clock -name "master_clk" -period 15.625ns [get_ports {master_clk}]
create_clock -name "clk64" -period 15.625ns -waveform {0.000 7.8125} [get_nets {clk64}]

# USRP1 has simple clock structure - single 64 MHz domain
derive_pll_clocks
derive_clock_uncertainty

# I/O timing constraints
# USRP1 uses parallel interface to microcontroller
set_input_delay -clock "clk64" -max 5.0 [get_ports {usbctl_data[*]}]
set_input_delay -clock "clk64" -min 1.0 [get_ports {usbctl_data[*]}]
set_output_delay -clock "clk64" -max 3.0 [get_ports {usbctl_data[*]}]
set_output_delay -clock "clk64" -min 0.5 [get_ports {usbctl_data[*]}]

# Serial interface timing (for daughterboard control)
set_input_delay -clock "clk64" -max 8.0 [get_ports {SDI}]
set_output_delay -clock "clk64" -max 8.0 [get_ports {SDO SCLK SEN_FPGA}]

# Relaxed timing for slow control signals
set_false_path -from [get_ports {reset}]
set_false_path -to [get_ports {led[*]}]

# Conservative setup for limited routing resources
set_max_delay -from [get_registers {*}] -to [get_registers {*}] 12.0
```

**B210 Advanced Timing Constraints (ISE UCF)**
```ucf
# b210_timing.ucf
# Advanced timing constraints for B210 Spartan-6

# Primary clocks
NET "CLK_40MHz" TNM_NET = "CLK_40MHz";
TIMESPEC "TS_CLK_40MHz" = PERIOD "CLK_40MHz" 25 ns HIGH 50%;

# Generated clocks from MMCM
NET "clk_200MHz" TNM_NET = "CLK_200MHz"; 
TIMESPEC "TS_CLK_200MHz" = PERIOD "CLK_200MHz" 5 ns HIGH 50%;

NET "radio_clk" TNM_NET = "RADIO_CLK";
TIMESPEC "TS_RADIO_CLK" = PERIOD "RADIO_CLK" 16.276 ns HIGH 50%; # 61.44 MHz max

# Clock domain crossing constraints
TIMESPEC "TS_CLK40_to_CLK200" = FROM "CLK_40MHz" TO "CLK_200MHz" 8 ns;
TIMESPEC "TS_CLK200_to_RADIO" = FROM "CLK_200MHz" TO "RADIO_CLK" 8 ns;

# High-speed I/O constraints for USB 3.0
NET "USB_*" TNM_NET = "USB_IFC";
TIMESPEC "TS_USB_SETUP" = FROM "USB_IFC" TO "CLK_200MHz" 2 ns;
TIMESPEC "TS_USB_HOLD" = FROM "CLK_200MHz" TO "USB_IFC" 1 ns;

# AD9361 interface timing (critical for RF performance)
NET "rx_frame" TNM_NET = "AD9361_RX";
NET "tx_frame" TNM_NET = "AD9361_TX";
NET "data_clk" TNM_NET = "AD9361_CLK";

TIMESPEC "TS_AD9361_SETUP" = FROM "AD9361_RX" TO "AD9361_CLK" 1.5 ns;
TIMESPEC "TS_AD9361_HOLD" = FROM "AD9361_CLK" TO "AD9361_TX" 1.0 ns;

# DSP pipeline constraints
INST "dsp_pipeline/*" TNM = "DSP_LOGIC";
TIMESPEC "TS_DSP_PIPELINE" = FROM "DSP_LOGIC" TO "DSP_LOGIC" 4 ns;

# Memory interface constraints
NET "ddr3_*" TNM_NET = "DDR3_IFC";
TIMESPEC "TS_DDR3" = FROM "CLK_200MHz" TO "DDR3_IFC" 1.5 ns;

# False paths
NET "reset" TIG;
NET "debug_*" TIG;

# Multi-cycle paths for slow control
TIMESPEC "TS_CONTROL_MULTI" = FROM "control_regs" TO "control_regs" TS_CLK_200MHz * 2;
```

**Performance Optimization Techniques**

USRP1 Resource Optimization:
```verilog
// usrp1_optimized_design.v
// Optimization techniques for resource-constrained FPGA

module usrp1_resource_optimized (
    input wire clk64,
    input wire reset,
    input wire [15:0] rx_i, rx_q,
    input wire rx_strobe,
    output reg [15:0] tx_i, tx_q,
    output reg tx_strobe
);

// Technique 1: Use shift registers instead of counters where possible
reg [7:0] delay_line_sr; // 8-tap delay line as shift register
always @(posedge clk64) begin
    if (rx_strobe)
        delay_line_sr <= {delay_line_sr[6:0], rx_i[15]};
end

// Technique 2: Share resources between I and Q channels
reg iq_select;
reg [15:0] shared_multiplier_a, shared_multiplier_b;
wire [31:0] shared_mult_result = shared_multiplier_a * shared_multiplier_b;

always @(posedge clk64) begin
    iq_select <= ~iq_select;
    if (iq_select) begin
        shared_multiplier_a <= rx_i;
        shared_multiplier_b <= 16'h4000; // 0.5 in Q1.15
    end else begin
        shared_multiplier_a <= rx_q;
        shared_multiplier_b <= 16'h4000;
    end
end

// Technique 3: Use distributed RAM for small lookup tables
(* ram_style = "distributed" *)
reg [7:0] sin_table [0:255];
reg [7:0] phase_acc;

initial begin
    integer i;
    for (i = 0; i < 256; i = i + 1)
        sin_table[i] = $rtoi(127 * $sin(2 * 3.14159 * i / 256));
end

wire [7:0] sin_val = sin_table[phase_acc];

always @(posedge clk64) begin
    if (rx_strobe)
        phase_acc <= phase_acc + 8'h10; // Frequency step
end

// Technique 4: Pipeline critical paths
reg [31:0] mult_pipeline [0:2];
always @(posedge clk64) begin
    mult_pipeline[0] <= shared_mult_result;
    mult_pipeline[1] <= mult_pipeline[0];
    mult_pipeline[2] <= mult_pipeline[1];
end

// Output assignment
always @(posedge clk64) begin
    if (reset) begin
        tx_strobe <= 1'b0;
    end else begin
        tx_i <= mult_pipeline[2][30:15]; // Scaled output
        tx_q <= {sin_val, 8'b0}; // Phase-shifted
        tx_strobe <= rx_strobe;
    end
end

endmodule
```

B210 Performance Optimization:
```verilog
// b210_high_performance.v
// Optimization for high-throughput applications

module b210_performance_optimized (
    input wire clk_200mhz,
    input wire radio_clk,
    input wire reset,
    
    // High-speed data interface
    input wire [31:0] s_axis_tdata,
    input wire s_axis_tvalid,
    output wire s_axis_tready,
    
    output reg [31:0] m_axis_tdata,
    output reg m_axis_tvalid,
    input wire m_axis_tready
);

// Technique 1: Use DSP48A1 primitives explicitly
wire [35:0] dsp_p;
wire [17:0] dsp_a = s_axis_tdata[17:0];
wire [17:0] dsp_b = 18'h10000; // Gain

DSP48A1 #(
    .A0REG(1), .A1REG(1), .B0REG(1), .B1REG(1),
    .CREG(1), .DREG(1), .MREG(1), .PREG(1),
    .OPMODEREG(1), .CARRYINREG(### Week 9-10: Hardware-Specific FPGA Toolchain Setup

**USRP1 Development Environment (Altera/Intel Quartus)**
```bash
# setup_usrp1_dev.sh
#!/bin/bash

echo "Setting up USRP1 development environment..."

# Install Quartus II 13.0sp1 (last version supporting Cyclone)
# Download from Intel FPGA website
wget https://download.altera.com/akdlm/software/acdsinst/13.0sp1/232/ib_installers/QuartusSetup-13.0.1.232.run

# Install
chmod +x QuartusSetup-13.0.1.232.run
sudo ./QuartusSetup-13.0.1.232.run

# Set environment
export QUARTUS_ROOTDIR=/opt/altera/13.0sp1/quartus
export PATH=$QUART### Week 4-5: Hardware-Specific FPGA Development

**USRP1 FPGA Development (Altera/Intel)**
```verilog
// usrp1_custom_block.v - For Altera Cyclone EP1C12
module usrp1_custom_dsp (
    // USRP1 specific clock (64 MHz)
    input wire clk64,
    input wire reset,
    
    // Interface to USRP1 data path
    input wire [15:0] rx_i,
    input wire [15:0] rx_q,
    input wire rx_strobe,
    
    output reg [15:0] tx_i,
    output reg [15:0] tx_q,
    output reg tx_strobe,
    
    // USRP1 settings bus
    input wire [6:0] serial_addr,
    input wire [31:0] serial_data,
    input wire serial_strobe
);

// Limited resources on EP1C12 - simple processing only
reg [15:0] gain_i, gain_q;
reg [31:0] phase_acc;
reg [15:0] phase_inc;

// Settings register decode (USRP1 uses 7-bit addresses)
always @(posedge clk64) begin
    if (serial_strobe) begin
        case (serial_addr)
            7'd0: gain_i <= serial_data[15:0];
            7'd1: gain_q <= serial_data[15:0];
            7'd2: phase_inc <= serial_data[15:0];
        endcase
    end
end

// Simple DSP processing - gain and phase rotation
wire [31:0] mult_i = rx_i * gain_i;
wire [31:0] mult_q = rx_q * gain_q;

// Phase accumulator for frequency shifting
always @(posedge clk64) begin
    if (reset)
        phase_acc <= 32'b0;
    else if (rx_strobe)
        phase_acc <= phase_acc + phase_inc;
end

// Lookup tables for sine/cosine (small for EP1C12)
wire [7:0] sin_addr = phase_acc[31:24];
wire [7:0] cos_addr = phase_acc[31:24];

reg [15:0] sin_lut [0:255];
reg [15:0] cos_lut [0:255];

// Initialize LUTs
initial begin
    integer i;
    for (i = 0; i < 256; i = i + 1) begin
        sin_lut[i] = $rtoi(32767 * $sin(2 * 3.14159 * i / 256));
        cos_lut[i] = $rtoi(32767 * $cos(2 * 3.14159 * i / 256));
    end
end

wire [15:0] sin_val = sin_lut[sin_addr];
wire [15:0] cos_val = cos_lut[cos_addr];

// Complex multiply: (I + jQ) * (cos + j*sin)
wire [31:0] rotated_i = (mult_i * cos_val - mult_q * sin_val);
wire [31:0] rotated_q = (mult_i * sin_val + mult_q * cos_val);

// Output with proper scaling
always @(posedge clk64) begin
    if (rx_strobe) begin
        tx_i <= rotated_i[30:15]; // Scale down from 32-bit multiply
        tx_q <= rotated_q[30:15];
        tx_strobe <= 1'b1;
    end else begin
        tx_strobe <= 1'b0;
    end
end

endmodule
```

**B210 FPGA Development (Xilinx Spartan-6)**
```verilog
// b210_advanced_dsp.v - For Spartan-6 XC6SLX150
module b210_advanced_dsp (
    // B210 uses multiple clocks
    input wire bus_clk,     // 100 MHz bus clock
    input wire radio_clk,   // Radio clock (varies with sample rate)
    input wire reset,
    
    // AXI4-Stream interface (B210 uses VITA-49)
    input wire [31:0] s_axis_tdata,
    input wire s_axis_tvalid,
    input wire s_axis_tlast,
    output wire s_axis_tready,
    
    output reg [31:0] m_axis_tdata,
    output reg m_axis_tvalid,
    output reg m_axis_tlast,
    input wire m_axis_tready,
    
    // Settings bus (B210 style)
    input wire [7:0] set_addr,
    input wire [31:0] set_data,
    input wire set_stb
);

// Extract I/Q from input (B210 format: {Q[15:0], I[15:0]})
wire [15:0] input_i = s_axis_tdata[15:0];
wire [15:0] input_q = s_axis_tdata[31:16];

// More complex processing possible with Spartan-6 resources
reg [15:0] fir_coeffs [0:63]; // 64-tap FIR filter
reg [15:0] delay_line_i [0:63];
reg [15:0] delay_line_q [0:63];
reg [5:0] delay_ptr;

// Settings registers
reg [15:0] filter_enable;
reg [15:0] decimation_factor;
reg [31:0] nco_phase_inc;

always @(posedge bus_clk) begin
    if (set_stb) begin
        case (set_addr)
            8'd0: filter_enable <= set_data[15:0];
            8'd1: decimation_factor <= set_data[15:0];
            8'd2: nco_phase_inc <= set_data;
            default: begin
                // Coefficient loading
                if (set_addr >= 8'd16 && set_addr < 8'd80) begin
                    fir_coeffs[set_addr - 16] <= set_data[15:0];
                end
            end
        endcase
    end
end

// FIR filter implementation using DSP48A1 primitives
wire [35:0] fir_result_i, fir_result_q;
wire fir_valid;

// Instantiate optimized FIR filter
fir_filter_dsp48 fir_i_inst (
    .clk(radio_clk),
    .rst(reset),
    .data_in(input_i),
    .data_valid(s_axis_tvalid),
    .coeffs(fir_coeffs),
    .result(fir_result_i),
    .result_valid(fir_valid)
);

fir_filter_dsp48 fir_q_inst (
    .clk(radio_clk),
    .rst(reset),
    .data_in(input_q),
    .data_valid(s_axis_tvalid),
    .coeffs(fir_coeffs),
    .result(fir_result_q),
    .result_valid()  // Don't need this one
);

// NCO for frequency translation
reg [31:0] nco_phase;
wire [15:0] nco_sin, nco_cos;

always @(posedge radio_clk) begin
    if (reset)
        nco_phase <= 32'b0;
    else if (s_axis_tvalid)
        nco_phase <= nco_phase + nco_phase_inc;
end

// High-resolution NCO using CORDIC
cordic_nco nco_inst (
    .clk(radio_clk),
    .phase(nco_phase[31:16]),
    .sin(nco_sin),
    .cos(nco_cos)
);

// Complex mixer
wire [31:0] mixed_i = (fir_result_i[31:0] * nco_cos - fir_result_q[31:0] * nco_sin);
wire [31:0] mixed_q = (fir_result_i[31:0] * nco_sin + fir_result_q[31:0] * nco_cos);

// Output formatting
reg [2:0] valid_delay;
always @(posedge radio_clk) begin
    if (reset) begin
        valid_delay <= 3'b0;
        m_axis_tvalid <= 1'b0;
    end else begin
        valid_delay <= {valid_delay[1:0], fir_valid};
        m_axis_tvalid <= valid_delay[2];
        
        if (valid_delay[2]) begin
            m_axis_tdata <= {mixed_q[27:12], mixed_i[27:12]}; // Scale and pack
            m_axis_tlast <= 1'b0; // Continuous stream
        end
    end
end

assign s_axis_tready = m_axis_tready; // Flow control

endmodule

// DSP48A1-optimized FIR filter for Spartan-6
module fir_filter_dsp48 #(
    parameter TAPS = 64
)(
    input wire clk,
    input wire rst,
    input wire [15:0] data_in,
    input wire data_valid,
    input wire [15:0] coeffs [0:TAPS-1],
    output reg [35:0] result,
    output reg result_valid
);

// Use multiple DSP48A1 primitives for parallel processing
wire [35:0] dsp_results [0:15]; // 16 DSP blocks for 64 taps
reg [TAPS-1:0][15:0] shift_reg;

// Shift register for input samples
always @(posedge clk) begin
    if (data_valid) begin
        shift_reg <= {shift_reg[TAPS-2:0], data_in};
    end
end

// Instantiate DSP48A1 primitives
genvar i;
generate
for (i = 0; i < 16; i = i + 1) begin : dsp_blocks
    wire [35:0] mac_out;
    
    DSP48A1 #(
        .A0REG(1), .A1REG(1), .B0REG(1), .B1REG(1),
        .CREG(1), .DREG(1), .MREG(1), .PREG(1),
        .CARRYINSEL("OPMODE5"),
        .OPMODEREG(1)
    ) dsp_inst (
        .CLK(clk),
        .A(shift_reg[i*4]),
        .B(coeffs[i*4]),
        .C(48'b0),
        .D(shift_reg[i*4+1]),
        .CARRYIN(1'b0),
        .OPMODE(8'b00000101),
        .P(mac_out)
    );
    
    assign dsp_results[i] = mac_out;
end
endgenerate

// Sum all DSP outputs
always @(posedge clk) begin
    if (rst) begin
        result <= 36'b0;
        result_valid <= 1'b0;
    end else begin
        result <= dsp_results[0] + dsp_results[1] + dsp_results[2] + dsp_results[3] +
                 dsp_results[4] + dsp_results[5] + dsp_results[6] + dsp_results[7] +
                 dsp_results[8] + dsp_results[9] + dsp_results[10] + dsp_results[11] +
                 dsp_results[12] + dsp_results[13] + dsp_results[14] + dsp_results[15];
        result_valid <= data_valid;
    end
end

endmodule
```

**Hardware-Specific Build Scripts**

For **USRP1** (Altera Quartus):
```bash
#!/bin/bash
# build_usrp1.sh - USRP1 FPGA build script

# Set Quartus environment
export QUARTUS_ROOTDIR=/opt/altera/quartus
export PATH=$QUARTUS_ROOTDIR/bin:$PATH

# USRP1 uses Quartus II for Cyclone
PROJECT_NAME="usrp1_custom"
TOP_LEVEL="usrp1_std"

# Create project
quartus_map --read_settings_files=on --write_settings_files=off $PROJECT_NAME -c $TOP_LEVEL

# Add source files
quartus_map $PROJECT_NAME -c $TOP_LEVEL \
    --source=usrp1_custom_dsp.v \
    --source=usrp1_std.v \
    --source=usrp1.qsf

# Synthesize
quartus_fit $PROJECT_NAME -c $TOP_LEVEL

# Place and route
quartus_asm $PROJECT_NAME -c $TOP_LEVEL

# Generate programming file
quartus_cpf -c usrp1_std.sof usrp1_std.rbf

echo "USRP1 FPGA build complete: usrp1_std.rbf"
```

For **B210** (Xilinx ISE):
```bash
#!/bin/bash
# build_b210.sh - B210 FPGA build script

# Set ISE environment
source /opt/Xilinx/14.7/ISE_DS/settings64.sh

PROJECT_NAME="b210"
TOP_LEVEL="b200"

# Create ISE project
xtclsh << EOF
project new $PROJECT_NAME.xise
project set family "Spartan6"
project set device "xc6slx150"
project set package "fgg484"
project set speed "-3"

# Add source files
xfile add "b210_advanced_dsp.v"
xfile add "b200.v" -top
xfile add "b200.ucf"

# Synthesize
process run "Synthesize - XST"

# Implement
process run "Implement Design"

# Generate bitstream
process run "Generate Programming File"

project close
EOF

echo "B210 FPGA build complete: b200.bit"
```

**Hardware-Specific Programming**

USRP1 Programming:
```cpp
// program_usrp1.cpp
#include <uhd/usrp/multi_usrp.hpp>
#include <fstream>

void program_usrp1_fpga(const std::string& rbf_file) {
    auto usrp = uhd::usrp::multi_usrp::make("type=usrp1");
    
    // Read RBF file
    std::ifstream file(rbf_file, std::ios::binary);
    std::vector<uint8_t> fpga_image(
        (std::istreambuf_iterator<char>(file)),
        std::istreambuf_iterator<char>()
    );
    
    std::cout << "Programming USRP1 FPGA with " << rbf_file << std::endl;
    std::cout << "Image size: " << fpga_image.size() << " bytes" << std::endl;
    
    // Program FPGA (USRP1 specific method)
    // Note: USRP1 loads FPGA on each power cycle
    usrp->set_user_register(0, 0xDEADBEEF); // Reset signal
    
    // The actual programming is done by UHD at device creation
    std::cout << "USRP1 FPGA programming complete" << std::endl;
}
```

B210 Programming:
```cpp
// program_b210.cpp
#include <uhd/usrp/multi_usrp.hpp>

void program_b210_fpga(const std::string& bit_file) {
    // B210 programming is handled differently
    std::string device_args = "type=b200,fpga=" + bit_file;
    
    std::cout << "Programming B210 with custom FPGA image..." << std::endl;
    
    try {
        auto usrp = uhd::usrp::multi_usrp::make(device_args);
        std::cout << "B210 FPGA programming successful" << std::endl;
        std::cout << "Device info: " << usrp->get_usrp_info().to_pp_string() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Programming failed: " << e.what() << std::endl;
    }
}
```

### Week 15-16: System Integration and Testing

**Complete FPGA Design Flow**
```makefile
# Makefile for FPGA build
VIVADO = vivado -mode batch -source
PART = xczu28dr-ffvg1517-2-e
TOP_MODULE = usrp_x410

# Source files
HDL_SOURCES = $(wildcard hdl/*.v) $(wildcard hdl/*.sv)
XDC_SOURCES = $(wildcard constraints/*.xdc)
IP_SOURCES = $(wildcard ip/*.xci)

# Build targets
all: $(TOP_MODULE).bit

$(TOP_MODULE).bit: $(HDL_SOURCES) $(XDC_SOURCES) $(IP_SOURCES)
	$(VIVADO) build_fpga.tcl

synthesize: 
	$(VIVADO) synth_only.tcl

implement:
	$(VIVADO) impl_only.tcl

timing_report:
	$(VIVADO) timing_analysis.tcl

clean:
	rm -rf .Xil vivado* *.jou *.log $(TOP_MODULE).bit

.PHONY: all synthesize implement timing_report clean
```

**Hardware-in-the-Loop Testing**
```python
# fpga_test_suite.py
import uhd
import numpy as np
import pytest
from scipy import signal

class FPGATestSuite:
    def __init__(self, device_args=""):
        self.usrp = uhd.usrp.MultiUSRP(device_args)
        self.setup_device()
    
    def setup_device(self):
        # Configure for loopback testing
        self.usrp.set_rx_rate(1e6)
        self.usrp.set_tx_rate(1e6)
        self.usrp.set_rx_freq(1e9)
        self.usrp.set_tx_freq(1e9)
        self.usrp.set_rx_gain(0)
        self.usrp.set_tx_gain(0)
    
    def test_custom_fir_filter(self):
        """Test custom FPGA FIR filter block"""
        # Generate test signal
        n_samples = 10000
        sample_rate = 1e6
        signal_freq = 100e3
        
        t = np.arange(n_samples) / sample_rate
        test_signal = np.exp(1j * 2 * np.pi * signal_freq * t)
        
        # Configure FPGA filter
        self.configure_fpga_filter([0.1, 0.2, 0.4, 0.2, 0.1])  # Simple LPF
        
        # Transmit and receive
        received = self.loopback_test(test_signal)
        
        # Verify filtering occurred
        tx_spectrum = np.fft.fft(test_signal)
        rx_spectrum = np.fft.fft(received)
        
        # Check that high frequencies are attenuated
        freqs = np.fft.fftfreq(n_samples, 1/sample_rate)
        high_freq_mask = np.abs(freqs) > 200e3
        
        tx_high_power = np.mean(np.abs(tx_spectrum[high_freq_mask])**2)
        rx_high_power = np.mean(np.abs(rx_spectrum[high_freq_mask])**2)
        
        assert rx_high_power < 0.1 * tx_high_power, "High frequencies not filtered"
    
    def configure_fpga_filter(self, coefficients):
        """Configure FPGA filter coefficients via register writes"""
        for i, coeff in enumerate(coefficients):
            # Convert to fixed-point Q1.15 format
            coeff_fixed = int(coeff * (1 << 15))
            # Write to FPGA register
            self.usrp.set_user_register(f"filter_coeff_{i}", coeff_fixed)
    
    def loopback_test(self, tx_samples):
        """Perform hardware loopback test"""
        # Setup streamers
        tx_stream = self.usrp.get_tx_stream(uhd.usrp.StreamArgs("fc32"))
        rx_stream = self.usrp.get_rx_stream(uhd.usrp.StreamArgs("fc32"))
        
        # Start receive
        stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_continuous)
        stream_cmd.time_spec = self.usrp.get_time_now() + uhd.types.TimeSpec(0.1)
        rx_stream.issue_stream_cmd(stream_cmd)
        
        # Transmit samples
        tx_metadata = uhd.types.TXMetadata()
        tx_metadata.time_spec = stream_cmd.time_spec
        tx_metadata.has_time_spec = True
        
        tx_stream.send(tx_samples, tx_metadata)
        
        # Receive samples
        rx_samples = np.zeros(len(tx_samples), dtype=np.complex64)
        rx_metadata = uhd.types.RXMetadata()
        
        samples_received = 0
        while samples_received < len(tx_samples):
            num_rx = rx_stream.recv(rx_samples[samples_received:], rx_metadata)
            samples_received += num_rx
        
        # Stop streaming
        rx_stream.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_continuous))
        
        return rx_samples

if __name__ == "__main__":
    # Run test suite
    test_suite = FPGATestSuite("addr=192.168.10.2")
    test_suite.test_custom_fir_filter()
    print("All FPGA tests passed!")
```

---

## 🎓 Phase 4: Expert-Level Integration (Weeks 17-20)

### Week 17-18: Real-Time Systems and Latency Optimization

**Ultra-Low Latency Design Patterns**
```cpp
// real_time_processor.cpp - Lock-free, real-time processing
#include <atomic>
#include <memory>
#include <chrono>
#include <thread>

template<typename T, size_t Size>
class LockFreeRingBuffer {
private:
    std::array<T, Size> buffer;
    std::atomic<size_t> head{0};
    std::atomic<size_t> tail{0};
    
public:
    bool try_push(const T& item) {
        const size_t current_tail = tail.load(std::memory_order_relaxed);
        const size_t next_tail = (current_tail + 1) % Size;
        
        if (next_tail == head.load(std::memory_order_acquire)) {
            return false; // Buffer full
        }
        
        buffer[current_tail] = item;
        tail.store(next_tail, std::memory_order_release);
        return true;
    }
    
    bool try_pop(T& item) {
        const size_t current_head = head.load(std::memory_order_relaxed);
        
        if (current_head == tail.load(std::memory_order_acquire)) {
            return false; // Buffer empty
        }
        
        item = buffer[current_head];
        head.store((current_head + 1) % Size, std::memory_order_release);
        return true;
    }
};

class RealTimeSDRProcessor {
private:
    static constexpr size_t BUFFER_SIZE = 4096;
    LockFreeRingBuffer<std::complex<float>, BUFFER_SIZE> input_buffer;
    LockFreeRingBuffer<std::complex<float>, BUFFER_SIZE> output_buffer;
    
    std::atomic<bool> processing_active{false};
    std::thread processing_thread;
    
public:
    void start_processing() {
        processing_active = true;
        processing_thread = std::thread(&RealTimeSDRProcessor::process_loop, this);
        
        // Set real-time priority
        sched_param param;
        param.sched_priority = 80;
        pthread_setschedparam(processing_thread.native_handle(), SCHED_FIFO, &param);
    }
    
private:
    void process_loop() {
        std::complex<float> sample;
        auto last_time = std::chrono::high_resolution_clock::now();
        
        while (processing_active.load(std::memory_order_acquire)) {
            if (input_buffer.try_pop(sample)) {
                // Critical real-time processing
                auto processed = process_sample_rt(sample);
                
                if (!output_buffer.try_push(processed)) {
                    // Handle overrun - this is critical!
                    handle_buffer_overrun();
                }
                
                // Timing measurement for debug
                auto current_time = std::chrono::high_resolution_clock::now();
                auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(
                    current_time - last_time).count();
                
                if (duration > 1000) { // > 1μs is concerning for real-time
                    // Log timing violation
                }
                last_time = current_time;
            } else {
                // Yield CPU briefly to avoid busy waiting
                std::this_thread::yield();
            }
        }
    }
    
    std::complex<float> process_sample_rt(const std::complex<float>& input) {
        // Ultra-fast processing - must complete in < 1μs
        // Example: Simple complex multiply
        return input * std::complex<float>(0.707f, 0.707f);
    }
    
    void handle_buffer_overrun() {
        // Critical error handling
        // In real systems, this might trigger hardware reset
    }
};
```

**FPGA Timestamping and Synchronization**
```verilog
// precision_timestamp.v - High-precision timestamping
module precision_timestamp #(
    parameter TIMESTAMP_WIDTH = 64,
    parameter CLOCK_FREQ = 200_000_000 // 200 MHz
)(
    input wire clk,
    input wire rst,
    
    // External timing references
    input wire pps_in,          // 1 pulse per second
    input wire ref_clk_10mhz,   // 10 MHz reference
    
    // Timestamp output
    output reg [TIMESTAMP_WIDTH-1:0] timestamp,
    output reg timestamp_valid,
    
    // Synchronization control
    input wire sync_request,
    output reg sync_done
);

// PPS edge detection
reg pps_sync [2:0];
always @(posedge clk) begin
    pps_sync <= {pps_sync[1:0], pps_in};
end
wire pps_edge = pps_sync[1] && !pps_sync[2];

// High-resolution timestamp counter
reg [TIMESTAMP_WIDTH-1:0] timestamp_counter;
reg [31:0] subsecond_counter;

// Fractional second tracking (for sub-sample precision)
localparam SUBSEC_MAX = CLOCK_FREQ - 1;

always @(posedge clk) begin
    if (rst) begin
        timestamp_counter <= {TIMESTAMP_WIDTH{1'b0}};
        subsecond_counter <= 32'b0;
        timestamp_valid <= 1'b0;
        sync_done <= 1'b0;
    end else begin
        // Normal counter increment
        if (subsecond_counter == SUBSEC_MAX) begin
            subsecond_counter <= 32'b0;
            timestamp_counter <= timestamp_counter + 1;
        end else begin
            subsecond_counter <= subsecond_counter + 1;
        end
        
        // PPS synchronization
        if (pps_edge) begin
            subsecond_counter <= 32'b0;
            // Don't reset timestamp_counter - it's set by software
            sync_done <= 1'b1;
        end else begin
            sync_done <= 1'b0;
        end
        
        // Timestamp output includes fractional seconds
        timestamp <= {timestamp_counter[47:0], 
                     subsecond_counter[31:16]}; // High 16 bits for sub-second
        timestamp_valid <= 1'b1;
    end
end

endmodule
```

### Week 19: Advanced Signal Processing Applications

**Adaptive Filtering Implementation**
```cpp
// adaptive_filter.cpp - LMS adaptive filter
#include <Eigen/Dense>
#include <complex>
#include <vector>

class LMSAdaptiveFilter {
private:
    Eigen::VectorXcd weights;
    Eigen::VectorXcd delay_line;
    double mu; // Step size
    size_t filter_length;
    size_t delay_index;

public:
    LMSAdaptiveFilter(size_t length, double step_size = 0.01) 
        : filter_length(length), mu(step_size), delay_index(0) {
        weights = Eigen::VectorXcd::Zero(length);
        delay_line = Eigen::VectorXcd::Zero(length);
    }
    
    std::complex<double> adapt(std::complex<double> input, 
                              std::complex<double> desired) {
        // Update delay line
        delay_line[delay_index] = input;
        
        // Compute filter output
        std::complex<double> output = 0.0;
        for (size_t i = 0; i < filter_length; ++i) {
            size_t tap_idx = (delay_index + i) % filter_length;
            output += weights[i] * delay_line[tap_idx];
        }
        
        // Compute error
        std::complex<double> error = desired - output;
        
        // Update weights using LMS algorithm
        for (size_t i = 0; i < filter_length; ++i) {
            size_t tap_idx = (delay_index + i) % filter_length;
            weights[i] += mu * error * std::conj(delay_line[tap_idx]);
        }
        
        // Update delay index
        delay_index = (delay_index > 0) ? delay_index - 1 : filter_length - 1;
        
        return output;
    }
    
    Eigen::VectorXcd get_weights() const { return weights; }
    double get_mse() const { 
        // Return current mean square error (would need error history)
        return 0.0; // Placeholder
    }
};

// FPGA-optimized version
// adaptive_filter_fpga.v
module lms_adaptive_filter #(
    parameter TAPS = 32,
    parameter DATA_WIDTH = 18,
    parameter COEFF_WIDTH = 18
)(
    input wire clk,
    input wire rst,
    
    // Input signals
    input wire signed [DATA_WIDTH-1:0] input_i,
    input wire signed [DATA_WIDTH-1:0] input_q,
    input wire signed [DATA_WIDTH-1:0] desired_i,
    input wire signed [DATA_WIDTH-1:0] desired_q,
    input wire data_valid,
    
    // Output
    output reg signed [DATA_WIDTH-1:0] output_i,
    output reg signed [DATA_WIDTH-1:0] output_q,
    output reg signed [DATA_WIDTH-1:0] error_i,
    output reg signed [DATA_WIDTH-1:0] error_q,
    output reg output_valid,
    
    // Adaptation control
    input wire [15:0] mu_step_size,
    input wire adapt_enable
);

// Weight memory (dual-port for read/write)
reg signed [COEFF_WIDTH-1:0] weights_i [0:TAPS-1];
reg signed [COEFF_WIDTH-1:0] weights_q [0:TAPS-1];

// Input delay line
reg signed [DATA_WIDTH-1:0] delay_line_i [0:TAPS-1];
reg signed [DATA_WIDTH-1:0] delay_line_q [0:TAPS-1];

// Pipeline stages
reg [2:0] valid_pipe;
reg signed [DATA_WIDTH-1:0] desired_pipe_i [0:2];
reg signed [DATA_WIDTH-1:0] desired_pipe_q [0:2];

// Multiply-accumulate results
wire signed [DATA_WIDTH+COEFF_WIDTH-1:0] mac_result_i;
wire signed [DATA_WIDTH+COEFF_WIDTH-1:0] mac_result_q;

// MAC array instantiation
genvar i;
generate
for (i = 0; i < TAPS; i = i + 1) begin : mac_array
    wire signed [DATA_WIDTH+COEFF_WIDTH-1:0] mult_i = 
        delay_line_i[i] * weights_i[i] - delay_line_q[i] * weights_q[i];
    wire signed [DATA_WIDTH+COEFF_WIDTH-1:0] mult_q = 
        delay_line_i[i] * weights_q[i] + delay_line_q[i] * weights_i[i];
    
    if (i == 0) begin
        assign mac_result_i = mult_i;
        assign mac_result_q = mult_q;
    end else begin
        assign mac_result_i = mac_result_i + mult_i;
        assign mac_result_q = mac_result_q + mult_q;
    end
end
endgenerate

// Main processing pipeline
always @(posedge clk) begin
    if (rst) begin
        valid_pipe <= 3'b0;
        output_valid <= 1'b0;
        
        // Initialize weights to zero
        for (int j = 0; j < TAPS; j = j + 1) begin
            weights_i[j] <= {COEFF_WIDTH{1'b0}};
            weights_q[j] <= {COEFF_WIDTH{1'b0}};
        end
    end else begin
        // Pipeline control
        valid_pipe <= {valid_pipe[1:0], data_valid};
        output_valid <= valid_pipe[2];
        
        // Stage 1: Update delay line
        if (data_valid) begin
            delay_line_i[0] <= input_i;
            delay_line_q[0] <= input_q;
            desired_pipe_i[0] <= desired_i;
            desired_pipe_q[0] <= desired_q;
            
            for (int j = 1; j < TAPS; j = j + 1) begin
                delay_line_i[j] <= delay_line_i[j-1];
                delay_line_q[j] <= delay_line_q[j-1];
            end
        end
        
        // Stage 2: Pipeline desired signal
        if (valid_pipe[0]) begin
            desired_pipe_i[1] <= desired_pipe_i[0];
            desired_pipe_q[1] <= desired_pipe_q[0];
        end
        
        // Stage 3: Compute output and error
        if (valid_pipe[1]) begin
            output_i <= mac_result_i[DATA_WIDTH+COEFF_WIDTH-1:COEFF_WIDTH];
            output_q <= mac_result_q[DATA_WIDTH+COEFF_WIDTH-1:COEFF_WIDTH];
            
            error_i <= desired_pipe_i[1] - mac_result_i[DATA_WIDTH+COEFF_WIDTH-1:COEFF_WIDTH];
            error_q <= desired_pipe_q[1] - mac_result_q[DATA_WIDTH+COEFF_WIDTH-1:COEFF_WIDTH];
            
            desired_pipe_i[2] <= desired_pipe_i[1];
            desired_pipe_q[2] <= desired_pipe_q[1];
        end
        
        // Weight update (happens in parallel with output computation)
        if (valid_pipe[2] && adapt_enable) begin
            for (int j = 0; j < TAPS; j = j + 1) begin
                // LMS weight update: w(n+1) = w(n) + μ * e(n) * conj(x(n))
                weights_i[j] <= weights_i[j] + 
                    ((error_i * delay_line_i[j] + error_q * delay_line_q[j]) * mu_step_size) >>> 16;
                weights_q[j] <= weights_q[j] + 
                    ((error_q * delay_line_i[j] - error_i * delay_line_q[j]) * mu_step_size) >>> 16;
            end
        end
    end
end

endmodule
```

### Week 20: System Deployment and Production

**Production Build System**
```yaml
# .github/workflows/fpga_ci.yml - CI/CD for FPGA development
name: FPGA Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint_and_simulate:
    runs-on: ubuntu-latest
    container:
      image: hdlc/sim:latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Lint Verilog
      run: |
        verilator --lint-only -Wall hdl/*.v
        
    - name: Run testbenches
      run: |
        cd sim
        make clean
        make all
        make test
    
    - name: Upload simulation results
      uses: actions/upload-artifact@v3
      with:
        name: simulation-results
        path: sim/results/

  synthesize:
    needs: lint_and_simulate
    runs-on: self-hosted  # Requires Vivado license
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Vivado
      run: |
        source /opt/Xilinx/Vivado/2021.1/settings64.sh
        
    - name: Synthesize design
      run: |
        vivado -mode batch -source scripts/synth_only.tcl
        
    - name: Check timing
      run: |
        python scripts/check_timing.py build/timing_summary.rpt
        
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: fpga-build
        path: |
          build/*.bit
          build/*_timing_summary.rpt
          build/*_utilization.rpt

  hardware_test:
    needs: synthesize
    runs-on: self-hosted
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Program FPGA
      run: |
        python scripts/program_fpga.py build/design.bit
        
    - name: Run hardware tests
      run: |
        cd test
        python test_fpga_hardware.py --device addr=192.168.10.2
        
    - name: Generate test report
      run: |
        python scripts/generate_test_report.py
```

**Performance Monitoring and Debugging**
```python
# fpga_monitor.py - Real-time FPGA performance monitoring
import uhd
import numpy as np
import matplotlib.pyplot as plt
import time
from collections import deque
import threading

class FPGAPerformanceMonitor:
    def __init__(self, device_args=""):
        self.usrp = uhd.usrp.MultiUSRP(device_args)
        self.monitoring_active = False
        self.metrics = {
            'throughput': deque(maxlen=1000),
            'latency': deque(maxlen=1000),
            'errors': deque(maxlen=1000),
            'temperature': deque(maxlen=1000),
            'power': deque(maxlen=1000)
        }
        
    def start_monitoring(self):
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        
    def _monitor_loop(self):
        while self.monitoring_active:
            # Read FPGA registers for performance metrics
            try:
                # Throughput monitoring
                tx_bytes = self.usrp.get_usrp_info().get("tx_bytes", 0)
                rx_bytes = self.usrp.get_usrp_info().get("rx_bytes", 0)
                throughput = (tx_bytes + rx_bytes) / 1e6  # MB/s
                
                # Latency measurement using loopback
                latency = self._measure_latency()
                
                # Error counters
                error_count = self._read_fpga_register("error_counter")
                
                # Temperature and power
                temp = self._read_sensor("temperature")
                power = self._read_sensor("power")
                
                # Store metrics
                timestamp = time.time()
                self.metrics['throughput'].append((timestamp, throughput))
                self.metrics['latency'].append((timestamp, latency))
                self.metrics['errors'].append((timestamp, error_count))
                self.metrics['temperature'].append((timestamp, temp))
                self.metrics['power'].append((timestamp, power))
                
                # Check for anomalies
                self._check_performance_anomalies()
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                
            time.sleep(1.0)  # Monitor every second
    
    def _measure_latency(self):
        # Quick loopback latency test
        test_samples = np.array([1.0 + 1.0j], dtype=np.complex64)
        
        # Configure for minimum latency
        tx_stream = self.usrp.get_tx_stream(uhd.usrp.StreamArgs("fc32"))
        rx_stream = self.usrp.get_rx_stream(uhd.usrp.StreamArgs("fc32"))
        
        # Timestamp before transmission
        start_time = time.perf_counter()
        
        # Send and receive
        tx_metadata = uhd.types.TXMetadata()
        tx_stream.send(test_samples, tx_metadata)
        
        rx_samples = np.zeros(1, dtype=np.complex64)
        rx_metadata = uhd.types.RXMetadata()
        rx_stream.recv(rx_samples, rx_metadata)
        
        # Calculate latency
        end_time = time.perf_counter()
        latency_us = (end_time - start_time) * 1e6
        
        return latency_us
    
    def _read_fpga_register(self, register_name):
        # Read custom FPGA registers
        try:
            return self.usrp.get_user_register(register_name)
        except:
            return 0
    
    def _read_sensor(self, sensor_name):
        # Read FPGA temperature/power sensors
        try:
            sensors = self.usrp.get_mboard_sensors()
            if sensor_name in sensors:
                return self.usrp.get_mboard_sensor(sensor_name).value
        except:
            pass
        return 0.0
    
    def _check_performance_anomalies(self):
        # Automated anomaly detection
        if len(self.metrics['latency']) > 10:
            recent_latencies = [x[1] for x in list(self.metrics['latency'])[-10:]]
            avg_latency = np.mean(recent_latencies)
            
            if avg_latency > 100:  # > 100μs is concerning
                print(f"WARNING: High latency detected: {avg_latency:.1f}μs")
        
        if len(self.metrics['temperature']) > 5:
            recent_temps = [x[1] for x in list(self.metrics['temperature'])[-5:]]
            avg_temp = np.mean(recent_temps)
            
            if avg_temp > 85:  # > 85°C is critical
                print(f"CRITICAL: High temperature: {avg_temp:.1f}°C")
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Throughput plot
        if self.metrics['throughput']:
            times, values = zip(*self.metrics['throughput'])
            axes[0,0].plot(times, values)
            axes[0,0].set_title('Throughput (MB/s)')
            axes[0,0].set_ylabel('MB/s')
        
        # Latency plot
        if self.metrics['latency']:
            times, values = zip(*self.metrics['latency'])
            axes[0,1].plot(times, values)
            axes[0,1].set_title('Latency (μs)')
            axes[0,1].set_ylabel('μs')
        
        # Temperature plot
        if self.metrics['temperature']:
            times, values = zip(*self.metrics['temperature'])
            axes[1,0].plot(times, values)
            axes[1,0].set_title('Temperature (°C)')
            axes[1,0].set_ylabel('°C')
        
        # Error rate plot
        if self.metrics['errors']:
            times, values = zip(*self.metrics['errors'])
            axes[1,1].plot(times, values)
            axes[1,1].set_title('Error Count')
            axes[1,1].set_ylabel('Errors')
        
        plt.tight_layout()
        plt.savefig('fpga_performance_report.png', dpi=300)
        print("Performance report saved to fpga_performance_report.png")

# Usage example
if __name__ == "__main__":
    monitor = FPGAPerformanceMonitor("addr=192.168.10.2")
    monitor.start_monitoring()
    
    try:
        # Run for 5 minutes
        time.sleep(300)
    except KeyboardInterrupt:
        pass
    finally:
        monitor.monitoring_active = False
        monitor.generate_report()
```

---

## 📚 Additional Resources and Next Steps

### Essential Reading List
1. **SDR Theory**: "Software Defined Radio using MATLAB & Simulink and the RTL-SDR" by Robert W. Stewart
2. **FPGA Design**: "FPGA Prototyping by Verilog Examples" by Pong P. Chu
3. **DSP Implementation**: "Digital Signal Processing in Modern Communication Systems" by Andreas Schwarzinger
4. **GNU Radio**: "GNU Radio Tutorials" (official documentation)
5. **UHD Development**: "UHD Manual" and API documentation

### Advanced Project Ideas
1. **OFDM Transceiver**: Implement IEEE 802.11a/g OFDM in FPGA
2. **Radar Processing**: Build a coherent pulse-Doppler radar
3. **Machine Learning**: FPGA-accelerated RF signal classification
4. **Mesh Networking**: Multi-node synchronized communication
5. **Spectrum Analysis**: Real-time spectrum analyzer with FPGA FFT

### Professional Development Path
- **Certifications**: Xilinx Certified FPGA Developer
- **Conferences**: GNU Radio Conference (GRCon), FPGA Conference
- **Communities**: GNU Radio mailing list, USRP-users group
- **Open Source**: Contribute to GNU Radio/UHD projects

### Troubleshooting Guide
- **Build Issues**: Check CMake versions, dependencies
- **Timing Closure**: Use pipeline optimization, clock domain analysis
- **Hardware Debug**: ILA insertion, ChipScope debugging
- **Performance**: Profile with Valgrind, optimize critical paths

This comprehensive guide takes you from basic understanding through expert-level FPGA development for SDR systems. Each phase builds upon the previous, with hands-on exercises and real-world examples using GNU Radio and UHD frameworks.































