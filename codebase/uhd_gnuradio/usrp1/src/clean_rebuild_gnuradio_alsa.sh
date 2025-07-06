#!/bin/bash
# clean_rebuild_gnuradio_alsa.sh
# This script completely cleans and rebuilds GNU Radio with ALSA audio backend support

set -e

# Step 1: Remove all old OSS-linked GNU Radio components
sudo rm -rf /usr/local/lib/libgnuradio*
sudo rm -rf /usr/local/lib64/libgnuradio*
sudo rm -rf /usr/local/lib/cmake/gnuradio
sudo find /usr/local -name "*audio_oss_sink*" -exec rm -v {} \;
sudo ldconfig

# Step 2: Set build directory
cd ~/src/gnuradio || { echo "GNU Radio source not found in ~/src/gnuradio"; exit 1; }
rm -rf build
mkdir build && cd build

# Step 3: Configure with ALSA
cmake .. \
  -DENABLE_GR_UHD=ON \
  -DENABLE_GR_ANALOG=ON \
  -DENABLE_GR_BLOCKS=ON \
  -DENABLE_GR_QTGUI=ON \
  -DENABLE_GRC=ON \
  -DENABLE_GR_AUDIO=ON \
  -DAUDIO_BACKEND=alsa \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DCMAKE_INSTALL_LIBDIR=lib \
  -DPYTHON_EXECUTABLE=$(which python3)

# Step 4: Build and install
make -j$(nproc)
sudo make install
sudo ldconfig

# Step 5: Verify
python3 -c "from gnuradio import audio; print('✅ Audio sink is:', audio.sink)"

echo "\n🎉 GNU Radio has been rebuilt with ALSA backend and installed cleanly."
echo "You can now run: python3 fm_tx_rx_usrp_1.py --mic or --rx"
