#!/usr/bin/env python

import json, requests, gnupg

# CPU Count
kali_cpu_count = 2
# Disk Size allocated
kali_disk_size = 16 #GB
# RAM allocated
kali_ram_allocated = 6 #GB

# baseurl
baseurl = "http://cdimage.kali.org/current/"

# Get the SHA256SUMs for the latest ISOs
sha256sum_url = baseurl + "SHA256SUMS"
sha256sum_sig = baseurl + "SHA256SUMS.gpg"

print "Getting Kali public signing key"

gpg = gnupg.GPG()

# Kali signing key file
kali_signing_key = "https://www.kali.org/archive-key.asc"

# Get the key file content
key = requests.get(kali_signing_key)
if key.status_code is 200:
    key_import = gpg.import_keys(key.text)
    if key_import.count is 1:
        print "Key imported!"
    else:
        raise ValueError("Key import failed.")
else:
    raise ValueError("Key download failed!")

shasums = requests.get(sha256sum_url)
with open('SHA256SUMS', 'w') as f:
    f.write(shasums.text)

shasums_sig = requests.get(sha256sum_sig)
with open('SHA256SUMS.gpg', 'w') as f:
    f.write(shasums_sig.text)

shasums = open('SHA256SUMS.gpg', 'r')
verify = gpg.verify_file(shasums, 'SHA256SUMS')

if not verify:
    raise ValueError("Failed to verify SHA256SUM data..")
else:
    print "SHA256SUM Files validated."

# Rebuild the following so that we get the ISO name from the verified sha256sums file
with open('SHA256SUMS', 'r') as allsums:
    image_and_sum = allsums.readline()

items = image_and_sum.split("  ")

kali_iso_hash = items[0]
kali_iso_url = baseurl + items[1].strip()




variables = {}
variables["disk_size"] = "{disk}".format(disk = kali_disk_size * 1000)

builders = []
vb_builder = {}
vb_builder["type"] = "virtualbox-iso"
vb_builder["guest_os_type"] = "Debian_64"
vb_builder["iso_url"] = "{kali_iso}".format(kali_iso=kali_iso_url)
vb_builder["iso_checksum"] = "{hash}".format(hash=kali_iso_hash)
vb_builder["iso_checksum_type"] = "sha256"
vb_builder["ssh_username"] = "vagrant"
vb_builder["ssh_password"] = "vagrant"
vb_builder["boot_wait"] = "5s"
vb_builder["ssh_wait_timeout"] = "90m"
vb_builder["shutdown_command"] = "echo 'vagrant' | sudo -S shutdown -P now"
#vb_builder["disk_size"] = "{disk_size}".format(disk_size=kali_disk_size * 1000)
vb_builder["http_directory"] = "."
vb_builder["ssh_pty"] = "true"

vboxmanage = []

cpus = []
cpus.append("modifyvm")
cpus.append("{{.Name}}")
cpus.append("--cpus")
cpus.append("{cpus}".format(cpus=kali_cpu_count))
vboxmanage.append(cpus)

memory = []
memory.append("modifyvm")
memory.append("{{.Name}}")
memory.append("--memory")
memory.append("{ram}".format(ram=kali_ram_allocated * 1000))
vboxmanage.append(memory)

vram = []
vram.append("modifyvm")
vram.append("{{.Name}}")
vram.append("--vram")
vram.append("256")
vboxmanage.append(vram)

vb_builder["vboxmanage"] = []
vb_builder["vboxmanage"].append(cpus)
vb_builder["vboxmanage"].append(memory)
vb_builder["vboxmanage"].append(vram)


boot_command = []
boot_command.append("<esc><wait>")
boot_command.append(".linux /install/vmlinuz")
boot_command.append(" net.ifnames=0")
boot_command.append(" ---")
boot_command.append(" quiet")
boot_command.append(" initrd=/install/initrd.gz")
boot_command.append(" auto")
boot_command.append(" debian-installer=en_US")
boot_command.append(" locale=en_US")
boot_command.append(" kbd-chooser/method=us")
boot_command.append(" keymap=us")
boot_command.append(" hostname=kali")
boot_command.append(" domain=unassigned-domain")
boot_command.append(" url=http://{{ .HTTPIP }}:{{ .HTTPPort }}/preseed.cfg")
boot_command.append(" DEBCONF_DEBUG=5")
boot_command.append("<enter>")

vb_builder["boot_command"] = boot_command

builders.append(vb_builder)

provisioners = []
#puppet_provisioner = {}
#puppet_provisioner["type"] = "puppet"
#provisioners.append(puppet_provisioner)

shell_provisioner = {}
shell_provisioner["type"] = "shell"
# One or the other...
#shell_provisioner["inline"] = []
#shell_provisioner["inline"].append("echo foo")

shell_provisioner["execute_command"] = "echo vagrant | sudo -S bash {{.Path}}"
shell_provisioner["script"] = "provision.sh"
shell_provisioner["start_retry_timeout"] = "15m"

provisioners.append(shell_provisioner)
# Scripts to install/setup Burp Pro, Nessus, CyberChef etc.


post_processors = []
vagrant_post_processor = {}
vagrant_post_processor["type"] = "vagrant"
vagrant_post_processor["compression_level"] = 1

post_processors.append(vagrant_post_processor)

doc = {}
doc["variables"] = variables
doc["builders"] = builders
doc["provisioners"] = provisioners
doc["post-processors"] = post_processors

json_data = json.dumps(doc, indent=4, separators=(',', ': '))

fh = open("kali-template.json", "w")
fh.write(json_data)
fh.close()

print"Template written!"

