source $HOME/capstone/Break12306Captcha/run/common.sh
python $SRC_PATH/imageprocess/label_mapper.py \
  $MODEL \
  $FILE_LIST \
  $CAPTCHA_IMAGE \
  $LABEL_PROB \
  8
