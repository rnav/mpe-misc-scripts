#!/bin/bash

if [[ -z "$1" ]]; then
    echo "Usage: $0 <message id>" >&2
    exit 1
fi

wget -O "${1}.mbox" "https://lore.kernel.org/lkml/$1/raw"
