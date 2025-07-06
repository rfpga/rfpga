# Complete SDR Learning Guide: UHD, GNU Radio & FPGA Development

## 📋 Learning Path Overview

This guide takes you from C++/Python basics through advanced FPGA development for software-defined radio systems.

### Prerequisites Checklist
- ✅ C++ proficiency (classes, templates, memory management)
- ✅ Python proficiency (modules, NumPy, SciPy)
- ✅ Basic Linux command line
- ⬜ Digital Signal Processing fundamentals
- ⬜ FPGA development (we'll cover this)

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

**Practice Exercise 1.2: UHD Device Discovery**
```cpp
// discover_devices.cpp
#include <uhd/utils/safe_main.hpp>
#include <uhd/device.hpp>
#include <iostream>

int UHD_SAFE_MAIN(int argc, char* argv[]) {
    // Find all USRP devices
    uhd::device_addrs_t device_addrs = uhd::device::find("");
    
    if (device_addrs.empty()) {
        std::cout << "No UHD devices found" << std::endl;
        return EXIT_FAILURE;
    }
    
    for (const auto& addr : device_addrs) {
        std::cout << "Found device: " << addr.to_string() << std::endl;
    }
    
    return EXIT_SUCCESS;
}
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

### Week 3: Advanced UHD Programming

**Multi-Channel Operations**
```cpp
// multi_rx_example.cpp
#include <uhd/usrp/multi_usrp.hpp>
#include <thread>

int main() {
    // Create multi-USRP for synchronized operation
    uhd::usrp::multi_usrp::sptr usrp = 
        uhd::usrp::multi_usrp::make("addr0=192.168.10.2,addr1=192.168.10.3");
    
    // Configure both channels
    usrp->set_rx_rate(1e6, 0);  // Channel 0
    usrp->set_rx_rate(1e6, 1);  // Channel 1
    usrp->set_rx_freq(100e6, 0);
    usrp->set_rx_freq(200e6, 1);
    
    // Set time reference for synchronization
    usrp->set_time_source("gpsdo");
    usrp->set_clock_source("gpsdo");
    
    // Create RX streamers
    uhd::stream_args_t stream_args("fc32", "sc16");
    stream_args.channels = {0, 1};
    uhd::rx_streamer::sptr rx_stream = usrp->get_rx_stream(stream_args);
    
    // Start synchronized streaming
    uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_START_CONTINUOUS);
    stream_cmd.time_spec = usrp->get_time_now() + uhd::time_spec_t(0.1);
    rx_stream->issue_stream_cmd(stream_cmd);
    
    return 0;
}
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

### Week 6-7: DSP Algorithm Implementation

**Practice Exercise 6.1: Digital Filter in C++ and Verilog**

C++ Reference Implementation:
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

## 🔬 Phase 3: Advanced FPGA Development (Weeks 9-16)

### Week 9-10: Vivado and FPGA Toolchain

**Setting up Development Environment**
```bash
# Install Xilinx Vivado (version depends on USRP model)
# For USRP N310/N320: Vivado 2019.1
# For USRP X410: Vivado 2021.1

# Set up environment
source /opt/Xilinx/Vivado/2021.1/settings64.sh

# Clone FPGA source
git clone --recursive https://github.com/EttusResearch/fpga.git
cd fpga

# Build USRP FPGA image
cd usrp3/top/x410
make X410_HG_200  # High-grade version with 200 MHz fabric clock
```

**Practice Exercise 9.1: Custom FPGA Block Integration**
```tcl
# custom_block.tcl - Vivado TCL script
# Create custom IP block
create_project -force custom_dsp ./custom_dsp_proj -part xczu28dr-ffvg1517-2-e

# Add source files
add_files {
    ../hdl/custom_dsp.v
    ../hdl/custom_dsp_wrapper.v
}

# Set top module
set_property top custom_dsp_wrapper [current_fileset]

# Package IP
ipx::package_project -root_dir ./custom_dsp_ip -vendor ettus -library user -taxonomy /UserIP

# Set IP properties
set_property name custom_dsp [ipx::current_core]
set_property display_name "Custom DSP Block" [ipx::current_core]
set_property description "Custom DSP processing block" [ipx::current_core]

# Save IP
ipx::save_core [ipx::current_core]
```

### Week 11-12: Advanced DSP Implementation

**High-Performance FFT Implementation**
```verilog
// streaming_fft.v - Pipelined streaming FFT
module streaming_fft #(
    parameter FFT_SIZE = 1024,
    parameter DATA_WIDTH = 16
)(
    input wire clk,
    input wire rst,
    
    // Input stream
    input wire signed [DATA_WIDTH-1:0] s_axis_data_tdata_i,
    input wire signed [DATA_WIDTH-1:0] s_axis_data_tdata_q,
    input wire s_axis_data_tvalid,
    input wire s_axis_data_tlast,
    output wire s_axis_data_tready,
    
    // Output stream
    output wire signed [DATA_WIDTH-1:0] m_axis_data_tdata_i,
    output wire signed [DATA_WIDTH-1:0] m_axis_data_tdata_q,
    output wire m_axis_data_tvalid,
    output wire m_axis_data_tlast,
    input wire m_axis_data_tready,
    
    // Configuration
    input wire [7:0] fft_size_log2,
    input wire fft_direction // 0 = forward, 1 = inverse
);

localparam LOG2_SIZE = $clog2(FFT_SIZE);

// Xilinx FFT IP instantiation
xfft_0 fft_core (
    .aclk(clk),
    .aresetn(!rst),
    
    // Configuration
    .s_axis_config_tdata({1'b0, fft_direction, 6'b0, fft_size_log2}),
    .s_axis_config_tvalid(1'b1),
    .s_axis_config_tready(),
    
    // Input data
    .s_axis_data_tdata({s_axis_data_tdata_q, s_axis_data_tdata_i}),
    .s_axis_data_tvalid(s_axis_data_tvalid),
    .s_axis_data_tready(s_axis_data_tready),
    .s_axis_data_tlast(s_axis_data_tlast),
    
    // Output data
    .m_axis_data_tdata({m_axis_data_tdata_q, m_axis_data_tdata_i}),
    .m_axis_data_tvalid(m_axis_data_tvalid),
    .m_axis_data_tready(m_axis_data_tready),
    .m_axis_data_tlast(m_axis_data_tlast),
    
    // Status
    .event_frame_started(),
    .event_tlast_unexpected(),
    .event_tlast_missing(),
    .event_status_channel_halt(),
    .event_data_in_channel_halt(),
    .event_data_out_channel_halt()
);

endmodule
```

### Week 13-14: Timing Closure and Optimization

**Advanced Timing Constraints**
```tcl
# timing_constraints.xdc
# Clock definitions
create_clock -period 5.000 [get_ports clk_200mhz]
create_clock -period 8.000 [get_ports clk_125mhz]

# Clock domain crossing constraints
set_clock_groups -asynchronous \
    -group [get_clocks clk_200mhz] \
    -group [get_clocks clk_125mhz]

# Input/Output delays
set_input_delay -clock clk_200mhz -max 2.0 [get_ports data_in*]
set_input_delay -clock clk_200mhz -min 0.5 [get_ports data_in*]
set_output_delay -clock clk_200mhz -max 1.5 [get_ports data_out*]
set_output_delay -clock clk_200mhz -min 0.2 [get_ports data_out*]

# False paths
set_false_path -from [get_ports rst]
set_false_path -to [get_ports led*]

# Multi-cycle paths for slow control signals
set_multicycle_path -setup 2 -from [get_clocks clk_125mhz] -to [get_clocks clk_200mhz]
set_multicycle_path -hold 1 -from [get_clocks clk_125mhz] -to [get_clocks clk_200mhz]
```

**Pipeline Optimization Techniques**
```verilog
// optimized_pipeline.v
module optimized_pipeline #(
    parameter STAGES = 4,
    parameter WIDTH = 18
)(
    input wire clk,
    input wire rst,
    input wire signed [WIDTH-1:0] data_in,
    input wire data_valid_in,
    output reg signed [WIDTH-1:0] data_out,
    output reg data_valid_out
);

// Pipeline registers with optimal placement
(* ASYNC_REG = "TRUE" *) reg [STAGES-1:0] valid_pipe;
(* shreg_extract = "no" *) reg signed [WIDTH-1:0] data_pipe [0:STAGES-1];

// DSP48 primitive inference for multiply-accumulate
(* use_dsp = "yes" *) reg signed [2*WIDTH-1:0] mult_result;
(* use_dsp = "yes" *) reg signed [2*WIDTH-1:0] acc_result;

always @(posedge clk) begin
    if (rst) begin
        valid_pipe <= {STAGES{1'b0}};
        data_valid_out <= 1'b0;
        acc_result <= {2*WIDTH{1'b0}};
    end else begin
        // Pipeline advancement
        valid_pipe <= {valid_pipe[STAGES-2:0], data_valid_in};
        data_valid_out <= valid_pipe[STAGES-1];
        
        // Data pipeline with processing
        data_pipe[0] <= data_in;
        for (int i = 1; i < STAGES; i++) begin
            data_pipe[i] <= data_pipe[i-1];
        end
        
        // Processing stages
        if (valid_pipe[0]) begin
            mult_result <= data_pipe[0] * data_pipe[0]; // Square
        end
        
        if (valid_pipe[1]) begin
            acc_result <= acc_result + mult_result; // Accumulate
        end
        
        if (valid_pipe[STAGES-1]) begin
            data_out <= acc_result[WIDTH-1:0]; // Output scaled result
        end
    end
end

endmodule
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