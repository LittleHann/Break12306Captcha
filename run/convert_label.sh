source $HOME/tfenv/before_run.sh
export PYTHONPATH=$PYTHONPATH:/home/heqingy/capstone/Break12306Captcha
python /home/heqingy/capstone/Break12306Captcha/imageprocess/label_mapper.py /home/heqingy/capstone/model_0.8acc.ckpt /home/heqingy/capstone/filelist.txt /home/heqingy/captchas/ /home/heqingy/capstone/label_prob/ 8
