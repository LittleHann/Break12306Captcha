import os

cwd = os.getcwd()

with open('trainlist.txt', 'w') as writer:
    for cur_fname in os.listdir('data'):
#        print cur_fname
        cur_label_num = int(cur_fname.split('-')[0].split('_')[-1])
        cur_abs_path = os.path.join(cwd, 'data', cur_fname)
        assert os.path.exists(cur_abs_path)
        writer.write(cur_abs_path + ' ' + str(cur_label_num) + '\n')


