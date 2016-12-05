source $HOME/capstone/Break12306Captcha/run/common.sh
cat $EDGE_LIST | python $SRC_PATH/tools/weights_to_adj_list.py \
    > $EDGE_ADJLIST