# How to fix dependency issues on Linux

## Prerequisites

When installing on linux, you'll need the 32-bit libraries specified on the [valvesoftware](https://developer.valvesoftware.com/wiki/SteamCMD#32-bit_libraries_on_64-bit_Linux_systems) website.

Ubuntu
```
sudo apt-get install lib32stdc++6
sudo apt-get install build-essential
sudo apt-get install libx11-xcb-dev libglu1-mesa-dev
```
If you get an error for missing dependencies or broken packages, run the following
```
 dpkg --add-architecture i386
 apt-get update
 apt-get install lib32gcc1
```
RHEL, Fedora, CentOS, etc.
```
yum install glibc.i686 libstdc++.i686
```
Arch Linux

Enable the [multilib repository](https://wiki.archlinux.org/title/Official_repositories#multilib)
```
pacman -S lib32-gcc-libs
```
