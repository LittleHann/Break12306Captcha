About PBS
---

- For training triplet, 40k - 60k iterations are probably enough.
- 24 hours walltime is enought (default is 4 hours)

How to start a new training process
---

[Official wiki for solver.prototxt](https://github.com/BVLC/caffe/wiki/Solver-Prototxt)

- Copy you data around all compute nodes to every `/ssd` folder and change the source dir inside the `imagenet_train.prototxt`.
- In the imagenet_train.prototxt, change you hyperparameters (rand_ and hard_ ratio) and margin.
- In solver.prototxt, change the snapshot_prefix according to current values of margin and hard_ratio or you can create a directory for current settings in `train.sh`. (Besides, change the max_iter to 60000, snapshot iterval to 2000)
- In train.pbs, change the margin value and hard ratio variables accordingly
