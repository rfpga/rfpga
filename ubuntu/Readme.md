# Ubuntu 22.04.2

## vboxuser is not in the sudoers file this incident will be reported

```
sudo apt update && sudo apt upgrade
```

```
su
```

```
apt install sudo
```

```
usermod -aG sudo username
```

## Download and install the latest version of VBoxGuestAdditions

-   [7.0.8 is the latest version of VBoxGuestAdditions](https://w0.dk/~chlor/vboxguestadditions/)

```
cd /media/rfpga/VBox_GAs_7.0.8
sudo bash VBoxLinuxAdditions.run
```


## Share files

-   [How to Install VirtualBox on MacOS](https://tecadmin.net/how-to-install-virtualbox-on-macos/)

-   [Share folder between MacOS and Ubuntu](https://medium.com/macoclock/share-folder-between-macos-and-ubuntu-4ce84fb5c1ad)

-   [How can I access the host OS when using Ubuntu 22.04 or 22.10 with VM Tools Installed?](https://askubuntu.com/questions/1452608/how-can-i-access-the-host-os-when-using-ubuntu-22-04-or-22-10-with-vm-tools-inst)