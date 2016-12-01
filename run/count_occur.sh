source $HOME/tfenv/before_run.sh
export PYTHONPATH=$PYTHONPATH:/home/heqingy/capstone/Break12306Captcha
python /home/heqingy/capstone/Break12306Captcha/tools/count_cooccurrence.py /home/heqingy/capstone/new_captcha2txt/captchas.txt /home/heqingy/capstone/Break12306Captcha/tools/mapping.json /home/heqingy/capstone/Break12306Captcha/tools/image_coccur.pickle
