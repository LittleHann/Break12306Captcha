The RGB pHash value has 8 * 8 * 3 = 192 bits and the gray-scale pHash values has 8 * 8 = 64 bits values.
math.log10(2 ** 192) == 57, math.log10(2 ** 64) == 19.

In python, the size of each sub-image is roughly 64 bytes (you can use `sys.getsizeof`). There are three options for us
to represent the pHash value:
1. use binary strings.
2. use integer strings.
3. use hex number strings.

On average, the hex number string is shorted but in fact pHash will probably not shrink the size of our database because
the base size of python string type is 37 bytes (sys.getsizeof('') == 37).

But I don't know implementation details of Redis or DynamoDB.

Any question is how to calc hamming distance of two pHash values quickly? (Pre-calculated?)