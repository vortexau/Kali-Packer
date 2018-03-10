#!/bin/bash

./python gen-kali-template.py
packer build kali-template.json
