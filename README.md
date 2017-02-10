This project is the implementation of _Discovering Sematic Meaning with Unsupervised Learning_. The task is to break the captcha from [China Railway Official Website](http://www.12306.cn). 

We construct a graph and run label propagation on it. The graph from a single vertex's (an image) view is illustrated below:

![](instructions/graph.png)


With the image-image and image-label co-occurrence information, we construct a graph, and run label propagation on it to link codes and images.



![](instructions/DATA_FLOW.png)

The detailed documentation of data flow and files is [here](https://github.com/normanyahq/Break12306Captcha/blob/master/instructions/instruction.md).




