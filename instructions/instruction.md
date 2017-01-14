Project Introduction
========

Data Flow
----
![](DATA_FLOW.png)

**Note:**

(0) The Chinese labels are mapped into numbers according to the order in `labelgenerator/labels.txt` , starting from 0.


(1) Methods are defined in `imageprocess/utils.py`. For usage, check `imageprocess/label_mapper.py` as reference.
  
(2) Methods are defined in `image_hash/__init__.py`. 

(3) The pre-trained classifier is `classifier/model_0.8acc.ckpt`. To train the model, check the other files in this directory. To reduce the cost of storage and calculation, we convert the label probability distribution vector into sparse vector with a threshold, and you can check `imageprocess/label_mapper.py` for more information. 

(4) Methods are defined in `image_hash/__init__.py`. For usage, check `image_hash/captcha_mapper.py` as reference. There are three types of Hash in our program: grayscale phash, initial RGB phash, final RGB phash. Refer to slides for more details.

(5) Methods are defined in `image_hash/multiprocess_fc7_extractor.py`  
Pre-trained AlexNet Model: [Download Page](https://github.com/BVLC/caffe/tree/master/models/bvlc_reference_caffenet)

(6) To speed-up the calculation and reduce memory cost, for each FC7 vector, we only reserve 10% largest values and convert it into sparse vector. The calculation is done on AWS Spark Cluster. The AWS configuration can be found in __graph_partition/cosine`similarity.aws.cli` 

(7) To eliminate the number of total edges, we generate edge if and only if an image pair has appeared together in at least 1 CAPTCHA.

(8) This is the number of ID (final RGB Phash). 

(9) For 3.5M unique images, it consumes about 170G memory. We ran on AWS, and it takes about 1h to run. I tried to write a parallelized version (Spark, multi-thread), but it doesn't seem to be simple. Considering the cost it not too high, I gave up.

(10) This is the probability with only image-label co-occurrence information. Without label propagation, the accuracy for images appearing only a few times is relatively low.

Set-Up Steps
---
_Note: Variable names with `$` are environment variables, and are mostly defined in `run/common.sh`_

1. __Library__ Install all related libraries (with import error message). Tensorflow configuration on cluster can be found here: [CNBC Wiki - tensorflow](https://github.com/leelabcnbc/lab-wiki/wiki/how-to-use-CNBC-cluster#theano--tensorflow)
2. __Data__ Set the data path in `run/common.sh` and run.   
The command `source $HOME/tfenv/before_run.sh` is for activating Tensorflow environment
3. __Get Text CAPTCHA__ Run `run/convert_image.sh` to convert raw CAPTCHA images into text format: 
`filename, gray_phash1, rgb_phash1, gray_phash2, rgb_phash2, ...`, separated by __'\t'__. Note that the `rgb_phash` here is initial RGB phash, which will be mapped into final RGB phase.
The output file is named `$CAPTCHA_TEXT`.
4. __Get Label Prediction__ Run `run/convert_label.sh` to get label prediction for each CAPTCHA. The output file is named `$LABEL_PROB` in following format:
`filename, index1:prob1, index2:prob2, ...`, separated by __'\t'__.
5. __Generate Image to Final RGB Mapping__ Run `run/count_unique.sh` to generate `$MAPPING_DICT`, which contains following values and mapping dictionaries:  
    * buckets: Grayscale RGB -> Final RGB Value, *dictionary*
    * rgb2final: Initial RGB Value -> Final RGB Value, *dictionary*
    * image_occurrence: Count of images, *dictionary*
    * unique_count: Count of final RGB values, *value*
    * dist: Difference threshold used for this mapping file, *value*
6. __Get Initial Label Probability Distribution__ Run `run/get_image_prob.sh` to generate initial label probability distribution file `$IMAGE_PROB` with image-label co-occurrence.
7. __Get Co-occurrence Dictionary__ Run `run/count_coocur.sh` to generate edge list using `$CAPTCHA_TEXT` and `$MAPPING_DICT`, and output is `$IMAGE_COOCCUR_DICT`. The key of this dictionary is a pair of final RGB Phash value, and the value is the count of this pair.   
For a tuple `(phash1, phash2)`, we assume `phash1 < phash2` so that we can save some space
8. __Get Queries for Cosine Similarity__ Run `run/generate_query.sh` to generate queries for cosine similarity. The output is stored in `$QUERY`.
9. __Get Cosine Similarity__ Submit `graph_partition/cosine_similarity.py` to Spark cluster to get a list of 3-element tuple for each image. Each line is in following format
`(final_rgb_i, [(final_rgb_j1, FC7_cosine_sim_ij1, cooccur_count_ij1), ...])`  
The output is stored in `$COSINE_SIM`.
10. __Get Edge Weight__ Run `run/sim_to_weight.sh` to generate the edge list. It is separated from previous step so that we can easily tune the parameters of how we combine `FC7 Similarity` and `Co-occurrence`.
11. __Label Propagation__ Run `tools/hf_predict.py` to do label propagation. Check `tools/hf_predict.py -h` for more information. The command I used is  
`time python hf_predict.py --iter 5 --cn /ssd/heqingy/prediction_prob.pickle /ssd/heqingy/mapping.json /ssd/heqingy/cosine_sim.txt > predict_hf.txt`



How To Extract FC7 vectors of images
---

The extractor is `image_hash/multiprocess_fc7_extractor.py` and it needs to be run on compute nodes with GPUs.
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
In the end, you can just concatenate all files together.



Two pre-computed files are needed in advance:

* `txt_captchas.txt`  
> Each line of this file is pre-computed gray-scale and RGB perceptual hash values  

* `mappings.txt`  
> Find the RGB hash ID (unique) given a RGB perceptual hash value


Some Tools
--------
* __Image Searcher__ Download CAPTCHAs from AWS-S3 containing images with queried final RGB Phash value. Check `image_searcher` directory and `run/flask_run.sh`.
* __Human Recognition__ Check `tools/ruokuai.py` as a coding example for Ruokuai.com