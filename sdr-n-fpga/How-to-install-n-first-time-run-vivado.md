How to install and lauch vivado first time?

-   **Xilinx Download**

-   https://www.xilinx.com/support/download.html

-   **Getting ready for Vivado 2019.1 to work in Ubuntu 20.04:**

(If you are using Vivado 2019.1 on Ubuntu 20.04, you'll need to install the follwing two additional ibraries:)

```
sudo apt install libtinfo5 libncurses5 
```

```
sudo apt update && sudo apt upgrade
```

```
sudo apt update
sudo apt install libncurses5 -y
sudo apt install make
sudo apt-get install build-essential
sudo apt install net-tools
```

```
sudo apt install git cmake g++ libboost-all-dev libgmp-dev swig \
python3-numpy python3-mako python3-sphinx python3-lxml \
doxygen libfftw3-dev libsdl1.2-dev libgsl-dev libqwt-qt5-dev \
libqt5opengl5-dev python3-pyqt5 liblog4cpp5-dev libzmq3-dev \
python3-yaml python3-click python3-click-plugins python3-zmq \
python3-scipy python3-gi python3-gi-cairo gobject-introspection \
gir1.2-gtk-3.0 build-essential libusb-1.0-0-dev python3-docutils \
python3-setuptools python3-ruamel.yaml python-is-python3
```

-   **install Vivado**

If using the Linux self-extracting web installer (e.g. Vivado HLx 2019.1: WebPACK and Editions - Linux Self Extracting Web Installer), give it the appropriate permissions to make it executable and run it:

```
sudo chmod 777 ./Downloads/Xilinx_Vivado_SDK_Web_2019.1_0524_1430_Lin64.bin
```
```
sudo ./Downloads/Xilinx_Vivado_SDK_Web_2019.1_0524_1430_Lin64.bin
```

-   **First time to launch vivado**
```
sudo apt install libtinfo5 libncurses5
```

```
cd /tools/Xilinx/Vivado/2019.1
```
```
source ./settings64.sh
```
```
cd ~
```
```
vivado &
```

-   **Hardware is not open**

```
cd /tools/Xilinx/Vivado/2019.1/data/xicom/cable_drivers/lin64/install_script/install_drivers/

sudo ./install_drivers
```