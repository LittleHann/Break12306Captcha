source $HOME/capstone/Break12306Captcha/run/common.sh
mkdir -p $DATA_PATH/tmp_label_prob
python $SRC_PATH/imageprocess/label_mapper.py \
  $MODEL \
  $FILE_LIST \
  $CAPTCHA_IMAGE \
  $DATA_PATH/tmp_label_prob \
  8

cat $DATA_PATH/tmp_label_prob/*.txt > $LABEL_PROB
rm -r $DATA_PATH/tmp_label_prob
