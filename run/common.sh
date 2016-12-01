source $HOME/tfenv/before_run.sh

export SRC_PATH=$HOME/capstone/Break12306Captcha
export DATA_PATH=$HOME/capstone/data/
export PYTHONPATH=$PYTHONPATH:$SRC_PATH

export MODEL=$DATA_PATH/model_0.8acc.ckpt
export CAPTCHA_IMAGE=$DATA_PATH/captchas/
export CAPTCHA_TEXT=$DATA_PATH/txt_captchas.txt
export LABEL_PROB=$DATA_PATH/label_prob.txt
export FILE_LIST=$DATA_PATH/filelist.txt
export SMALL_FILE_LIST=$DATA_PATH/small_filelist.txt
export MAPPING_DICT=$DATA_PATH/mapping.json
export IMAGE_COOCCUR_DICT=$DATA_PATH/image_cooccur.pickle
