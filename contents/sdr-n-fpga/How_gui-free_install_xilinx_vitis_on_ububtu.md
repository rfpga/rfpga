# Installing Xilinx Vitis 2020.2 on Ubuntu (Headless or GUI-Free)

This guide walks through installing the Xilinx Vitis Unified Software Platform on Ubuntu using the `.tar.gz` offline installer in **batch mode** (no GUI).

---

## 1. Prerequisites

### Install Required Dependencies:

```bash
sudo apt update && sudo apt install -y \
  libgtk2.0-0 libcanberra-gtk-module libcanberra-gtk3-module \
  libxrender1 libxtst6 libxi6 libnss3 libncurses5 libstdc++6 \
  libsm6 libxext6 libx11-6 libxcb1 libxau6 libxdmcp6
```

---

## 2. Extract Installer

```bash
tar -xvzf Xilinx_Unified_2020.2_1118_1232.tar.gz
cd Xilinx_Unified_2020.2_1118_1232
chmod +x xsetup
```

---

## 3. Generate Config File (Batch Mode)

```bash
sudo ./xsetup -b ConfigGen
```

When prompted:

- Select: `1` for Vitis
- A config file will be created at: `/root/.Xilinx/install_config.txt`

Copy it for editing:

```bash
sudo cp /root/.Xilinx/install_config.txt ./install_config.txt
sudo chown $USER:$USER install_config.txt
```

---

## 4. Edit `install_config.txt`

Ensure it contains the following minimum fields:

```ini
Edition=Vitis Unified Software Platform
Product=Vitis
Destination=/tools/Xilinx
EnableWebTalk=0
Modules=DocNav:1,Vitis:1,Vivado:1,Artix-7:1,Kintex-7:1,Spartan-7:1,Zynq-7000:1,Zynq UltraScale+ MPSoC:1
CreateProgramGroupShortcuts=1
CreateShortcutsForAllUsers=0
CreateDesktopShortcuts=1
CreateFileAssociation=1
EnableDiskUsageOptimization=1
```

Note:

- **EnableWebTalk** must use capital "T"
- Adjust `Modules=` list to your device needs

---

## 5. Run Installer

```bash
sudo ./xsetup -a XilinxEULA,3rdPartyEULA,WebTalkTerms \
  -b Install \
  -c install_config.txt
```

> Ignore the warning: `EnableWebTalk is unknown and will be ignored.` The flag still prevents prompts.

Installation log will be saved to:

```
/tools/Xilinx/.xinstall/Vitis_2020.2/xinstall.log
```

---

## 6. Post-Install: Setup Environment

Add to your `.bashrc` or run manually:

```bash
source /tools/Xilinx/Vitis/2020.2/settings64.sh
```

To verify:

```bash
which vivado   # Should return Vivado binary path if installed
which xsct     # Should return XSCT binary path

vivado &       # Launch Vivado GUI
vitis &        # Launch Vitis GUI
xsct           # Launch XSCT TCL console
```

> If `xsct` warns about `rlwrap` and `$TERM`, you can ignore it — XSCT still works.

---

## 7. (Optional) Run installLibs.sh for Versal Tools

If you are using Versal ACAP tools, run the following script with root privilege:

```bash
sudo /tools/Xilinx/Vitis/2020.2/scripts/installLibs.sh
```

---

## ✅ Done

You’ve now installed Vitis (and optionally Vivado) on Ubuntu without needing GUI mode, but GUI tools can still be used on Ubuntu Desktop.

Let me know if you want to trim modules for a lighter install!

