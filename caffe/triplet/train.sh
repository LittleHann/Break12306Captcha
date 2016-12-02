#!/bin/sh

TOOLS=/home/haonans/software/caffe-video_triplet/build/tools
$TOOLS/caffe train --solver=solver.prototxt --gpu=2,3 

