# How to install UHD GNURadio and RFNoC on Ubuntu?

## for UHD4.0~4.4, GNURadio 3.8 and RFNoC on Ubuntu (18.04.2, 20.04.6, 22.04.2) 

-   [RFNoC 4 Workshop - GRCon 2020](https://www.youtube.com/watch?v=M9ntwQie9vs)

**Errata:**
- Part 2 Slide 4 "Getting RFNoC", UHD 4.2 has been released since this video was created and can be used by checking out the "UHD-4.2" branch instead of "UHD-4.0". When using UHD 4.2, check out the "master" branch of gr-ettus as the "maint3.8-uhd4.0" branch only works with UHD 4.0 & 4.1.
- When using uhd_usrp_probe, OOT module blocks will show up with the generic name "Block#0", "Block#1", etc. This is a known issue. One workaround is to use LD_PRELOAD. For example, for the rfnoc-tutorial OOT module from this tutorial, use: LD_PRELOAD=/usr/lib/librfnoc-tutorial.so uhd_usrp_probe


**Slides**
-   [rfnoc4_workshop_slides_2020_part_1.pdf](https://grcon.s3.us-west-1.amazonaws.com/GRC2020/rfnoc4_workshop_slides_2020_part_1.pdf)

-   [rfnoc4_workshop_slides_2020_part_2.pdf](https://grcon.s3.us-west-1.amazonaws.com/GRC2020/rfnoc4_workshop_slides_2020_part_2.pdf)


## Ubuntu preparation

- update and upgrade

```
sudo apt update && sudo apt upgrade
```

-   displays LSB (Linux Standard Base) information about the Linux distribution.
```
lsb_release -a
```

or

```
cat /etc/os-release
```

-   Checking Size and Availability of RAM

```
free -h
```

or

```
sudo dmidecode --type memory | less
```

-   Disk space usage

```
df -h
```

##  Install Vivado 2019.1 on Ubuntu

-   [Installing Vivado, Vitis, & PetaLinux 2021.2 on Ubuntu 18.04](https://www.hackster.io/whitney-knitter/installing-vivado-vitis-petalinux-2021-2-on-ubuntu-18-04-0d0fdf)

-   [I'm trying to install SDK 2019.1. But it seems obsolete. Where could I get the full size image?](https://support.xilinx.com/s/question/0D54U00006sZZTlSAO/im-trying-to-install-sdk-20191-but-it-seems-obsoletewhere-could-i-get-the-full-size-image?language=en_US)

-   [Running Vivado on Linux (Ubuntu)](https://mboers.github.io/zynq-notes/3-running-vivado/)

**Getting ready for Vivado 2019.1 to work in Ubuntu 20.04:**

(If you are using Vivado 2019.1 on Ubuntu 20.04, you'll need to install the follwing two additional ibraries:)

```
sudo apt install libtinfo5 libncurses5 
```

## Dependencies for Ubuntu (18.04.2, 20.04.6 and 22.04.2)

**Ubuntu 20.04 Dependencies:**

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

##  Install UHD4.0 (4.4) GNURadio 3.8 and RFNoC on Ubuntu (18.04.2, 20.046 and 22.04.2):

**UHD 4.0:**
```
git clone --branch UHD-4.0 https://github.com/ettusresearch/uhd.git uhd
```

**UHD 4.4:**
```
git clone --branch UHD-4.4 https://github.com/ettusresearch/uhd.git uhd
```

-   **Install**

```
mkdir uhd/host/build; cd uhd/host/build; cmake ..
```
```
make -j4; sudo make install
```

-   **Verify the UHD installed**

```
sudo ldconfig
```
```
sudo /usr/local/lib/uhd/utils/uhd_images_downloader.py
```
```
sudo uhd_usrp_probe
```


```
sudo uhd_find_device
```

**GNU Radio 3.8:**

```
git clone --branch maint-3.8 --recursive https://github.com/gnuradio/gnuradio.git gnuradio
```

```
mkdir gnuradio/build; cd gnuradio/build; cmake ..
```

**Note to install on raspberry:** you can limit the number of threads used by the "make" utility by specifying the maximum number of jobs (or threads) to be used with the "-j" option. For example, you can use the command "make -j2" to limit the number of threads used to 2.

```
make -j4; sudo make install
```

-   **Verify GNU Radio 3.8 installed**

```
export PYTHONPATH=/usr/local/lib/python3/dist-packages/:$PYTHONPATH
```

```
sudo ldconfig
gnuradio-companion
```

**gr-ettus:**

```
git clone --branch maint-3.8-uhd4.0 https://github.com/ettusresearch/gr-ettus.git gr-ettus
```

```
mkdir gr-ettus/build; cd gr-ettus/build; cmake -DENABLE_QT=True ..
```

```
make -j4; sudo make install
```

-   **Verify gr-ettus: installed**

```
export PYTHONPATH=/usr/local/lib/python3/dist-packages/:$PYTHONPATH
```

```
sudo ldconfig
rfnocmodtool help
```

**Note: to install softwares on raspberry**  

```
make -j2; sudo make install
```

you can limit the number of threads used by the "make" utility by specifying the maximum number of jobs (or threads) to be used with the "-j" option. For example, you can use the command "make -j2" to limit the number of threads used to 2.

By limiting the number of threads, you can reduce the CPU load during the build process, which can be especially helpful on systems with limited resources or when you need to run other processes simultaneously. However, it's important to note that limiting the number of threads may also increase the time needed to compile the program, since fewer threads will be available to perform the build tasks.

The optimal number of threads to use depends on various factors, such as the size of the program being built, the available system resources, and the number of CPU cores in the system. It's generally recommended to use a number of threads that matches the number of CPU cores or slightly higher, and adjust it based on the performance of your specific system.


