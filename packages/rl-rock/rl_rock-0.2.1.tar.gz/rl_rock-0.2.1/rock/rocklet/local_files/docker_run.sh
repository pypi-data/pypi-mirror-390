#!/bin/bash
set -o errexit

if [ ! -f /etc/alpine-release ]; then
    # Not Alpine Linux system
    # Run rocklet
    /tmp/miniforge/bin/rocklet

else
    echo "Alpine Linux system is not supported yet"
fi
