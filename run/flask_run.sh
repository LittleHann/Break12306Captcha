#!/usr/bin/env bash
source ./common.sh
export DATA_PATH=/data2/haonans
python ../image_searcher/app.py \
    $DATA_PATH/rgb_key_2_hashes.pickle \
    $DATA_PATH/hash_2_sources.pickle \
    --host 0.0.0.0 \
    --port 8000 &
