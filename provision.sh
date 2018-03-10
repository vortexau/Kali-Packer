#!/bin/bash

# This script is executed by packer, over SSH, after the first reboot.
# Provision some basic settings inside the Kali box file.

# Updating the package list happens automatically on first boot
echo "Waiting on existing apt-get lock to be removed... "
while fuser /var/lib/dpkg/lock >/dev/null 2>&1 ;
do
    echo -n "."
    sleep 1
done

echo -n "Lock released!"

# Upgrade all packages
export DEBIAN_FRONTEND=noninteractive 

apt-get dist-upgrade -y --force-yes

# Required for virtual box tools.
apt-get install -y linux-headers-$(uname -r)
apt-get install -y gcc make

# Install things our PTs like on their VMs

# i3
# Terminator
# tmux
apt-get install -y i3 terminator tmux empire bloodhound

# CyberChef - Likely to be a manual install process

# Install python libraries

# Make sure SSH is enabled.
systemctl enable ssh

apt-get auto-remove -y
apt-get clean
apt-get autoclean
