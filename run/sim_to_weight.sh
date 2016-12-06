source $HOME/capstone/Break12306Captcha/run/common.sh
python $SRC_PATH/tools/cos_to_weight.py \
    $COSINE_SIM \
    $IMAGE_COOCCUR_DICT \
    0.001 \
    $EDGE_LIST