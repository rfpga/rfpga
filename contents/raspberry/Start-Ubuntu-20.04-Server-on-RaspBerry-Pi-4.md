# How to install Ubuntu 20.04 Desktop on RaspBerry Pi

**Default Login Details for Ubuntu Server on the Pi**

There never was a specific desktop version of Ubuntu 20.04 for Raspberry Pi. Instead, you have to install the server version of Ubuntu 20.04, and when that is installed, you install the desktop environment with this command:

```
sudo apt-get install ubuntu-desktop
```

To login to your new installation, you will need to use the default login details. 
-   The default username is `ubuntu`. 
-   The default password is `ubuntu`.

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