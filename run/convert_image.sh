source $HOME/capstone/Break12306Captcha/run/common.sh
mkdir -p $DATA_PATH/tmp_captcha2txt

python $SRC_PATH/image_hash/captcha_mapper.py \
  $DATA_PATH/filelist.txt \
  $CAPTCHA_IMAGE \
  $DATA_PATH/tmp_captcha2txt \
  24

cat $DATA_PATH/tmp_captcha2txt/*.txt > $CAPTCHA_TEXT
rm -r $DATA_PATH/tmp_captcha2txt
