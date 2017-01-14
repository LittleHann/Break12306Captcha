# HOWTO

How To Extract fc7 vectors of images
---

The extractor is `multiprocess_fc7_extractor.py` and it needs to be run on compute nodes with GPU.
It needs three input arguments.
- `num_worker` How many parallel processes in total you want to extract fc7 because feature extractor can be run different nodes at the same time.
- `i_start` and `i_end`. On a specific node, what range of workers do you want to run.

For example, you want to run fc7 feature extractor on compute-1-1, compute-1-3, compute-1-5.

```
# On compute-1-1, you run
python multiprocess_fc7_extractor.py 48 0 15

# On compute-1-3, you run
python multiprocess_fc7_extractor.py 48 0 15

# On compute-1-5, you run
python multiprocess_fc7_extractor.py 48 0 15

```

Sample PBS script
```
#PBS -S /bin/bash
#
##PBS -j oe
#
#
#PBS -l nodes=compute-1-1:ppn=4
#PBS -l walltime=120:00:00
#

pushd .

. activate caffe

cd /home/haonans/
. config-caffe_latest.sh


cd /home/haonans/capstone/Break12306Captcha/image_hash
python multiprocess_fc7_extractor.py 48 0 15&> /home/haonans/capstone/log/worker_1_1.log

popd
```

All computed fc7 features are stored in `/ssd/haonans/text_db_worker_{}.txt`. You can change the directory inside as you like.
In the end, you can just concatinate all files together.



Two pre-computed files are needed in advance:
- `txt_captchas.txt`
> Each line of this file is pre-computed gray-scale and RGB perceptual hash values
- `mappings.txt`
> Find the RGB hash ID (unique) given a RGB perceptual hash value
