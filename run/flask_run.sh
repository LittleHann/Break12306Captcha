#!/usr/bin/env bash
source ./common.sh
python ../image_searcher/app.py \
    /home/haonans/share/rgb_key_2_hashes.pickle \
    /home/haonans/share/hash_2_sources.pickle \
    --host 0.0.0.0 \
    --port 8000 &
