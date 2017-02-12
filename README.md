This project is the implementation of _Discovering Sematic Meaning with Unsupervised Learning_. The task is to break the captcha from [China Railway Official Website](http://www.12306.cn). 

We construct a graph with image count and co-occurrence information and run label propagation on it. The data flow and graph from a vertex's (image) view is illustrated below:

<img src='instructions/DATA_FLOW.png' width=500 />
<img src='instructions/graph.png' width=350 />

The detailed explanation of data flow and code files is [here](https://github.com/normanyahq/Break12306Captcha/blob/master/instructions/instruction.md).

Some example results are shown below:

![](instructions/final1.png)
![](instructions/final2.png)

