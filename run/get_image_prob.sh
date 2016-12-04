source $HOME/capstone/Break12306Captcha/run/common.sh
python $SRC_PATH/tools/image_label_prob.py \
  $LABEL_PROB \
  $CAPTCHA_TEXT \
  $MAPPING_DICT \
  $IMAGE_PROB
