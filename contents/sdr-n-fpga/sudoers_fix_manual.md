# Fixing "rfnoc is not in the sudoers file" Error on Ubuntu

## Overview
This guide explains how to resolve the error:

```
rfnoc is not in the sudoers file. This incident will be reported.
```

This occurs when the user `rfnoc` attempts to run a command with `sudo`, but does not have the required privileges.

## Prerequisites
- Access to the VM's console (e.g., VirtualBox GUI)
- Ubuntu installed (e.g., 22.04.5 LTS)
- Either root password or access to recovery mode

## Cause
Ubuntu restricts `sudo` usage to users in the `sudo` group. If `rfnoc` is not in that group, `sudo` commands will be denied.

## Step-by-Step Solution (Using Recovery Mode)

### Step 1: Reboot into Recovery Mode
1. Restart the VM.
2. Hold the `Shift` key (or `Esc` for UEFI) to access the GRUB menu.
3. Select `Advanced options for Ubuntu`.
4. Choose the entry with `(recovery mode)`.

### Step 2: Drop to Root Shell
1. In the recovery menu, choose `root - Drop to root shell prompt`.
2. At the root prompt, remount the filesystem as writable:
   ```bash
   mount -o remount,rw /
   ```

### Step 3: Add `rfnoc` to the `sudo` Group
```bash
usermod -aG sudo rfnoc
```

### Step 4: Reboot
```bash
reboot
```

Now log in as `rfnoc` and test with:
```bash
sudo whoami
```
Expected output:
```
root
```

## Alternative: Use Root Account (if enabled)
If you have the root password, you can log in directly:
```bash
su -
usermod -aG sudo rfnoc
```

## Notes
- This method assumes you have full control over the VM.
- On new installs, only the first user created during setup is in the `sudo` group.
- If you’re locked out entirely, you may need to create a new admin user from recovery.

## Security Advice
- Only grant sudo to trusted users.
- Avoid editing `/etc/sudoers` directly; use `visudo` for syntax-checked editing.

## Summary
- The error occurs because `rfnoc` lacks sudo rights.
- Reboot into recovery mode to add `rfnoc` to the `sudo` group.
- After reboot, `sudo` should work as expected.

