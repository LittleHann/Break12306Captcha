source $HOME/capstone/Break12306Captcha/run/common.sh
python $SRC_PATH/tools/count_cooccurrence.py \
  $CAPTCHA_TEXT \
  $MAPPING_DICT \
  $IMAGE_COOCCUR_DICT
