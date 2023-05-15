# Raspberry Pi

-   [SSH with the Pi](http://learn.adafruit.com/adafruits-raspberry-pi-lesson-6-using-ssh)

-   [How to install Ubuntu Desktop on Raspberry Pi 4](https://ubuntu.com/tutorials/how-to-install-ubuntu-desktop-on-raspberry-pi-4#1-overview)

-   [Want the Ubuntu Desktop 22.04.2 on Raspberry Pi 4 run Gnuradio](../sdr-n-fpga/How-to-install-uhd-gnuradio-n-rfnoc-on-ubuntu.md)

-   [Visual Studio Code on Linux](https://code.visualstudio.com/docs/setup/linux)

-   [Setting up SSH key with GitHub for Ubuntu](https://medium.com/featurepreneur/setting-up-ssh-key-with-github-for-ubuntu-cd8f2fabf25b)

**Note: limit the number of threads to install softwares on raspberry**  

```
make -j2; sudo make install
```

You can limit the number of threads used by the "make" utility by specifying the maximum number of jobs (or threads) to be used with the "-j" option. For example, you can use the command `make -j2` to limit the number of threads used to 2.

By limiting the number of threads, you can reduce the CPU load during the build process, which can be especially helpful on systems with limited resources or when you need to run other processes simultaneously. However, it's important to note that limiting the number of threads may also increase the time needed to compile the program, since fewer threads will be available to perform the build tasks.

The optimal number of threads to use depends on various factors, such as the size of the program being built, the available system resources, and the number of CPU cores in the system. It's generally recommended to use a number of threads that matches the number of CPU cores or slightly higher, and adjust it based on the performance of your specific system.

