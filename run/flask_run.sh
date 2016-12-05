#!/usr/bin/env bash
source ./common.sh
python ../image_searcher/app.py \
    /data2/haonans/rgb_key_2_hashes.pickle \
    /data2/haonans/hash_2_sources.pickle \
    --host 0.0.0.0 \
    --port 8000 &
