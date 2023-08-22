# huffman-coding
Ever wondered how modern compression algorithms as in gzip, zip or zlib work? Well, I have recently and to get a better understanding I decided to reproduce the huffman encoding algorithm which all these programs have in common in Python (without the help of ChatGPT).

Conventional, fixed-length encoding assigns the same number of bits to each character, leading to inefficient representation. Huffman encoding, created by David A. Huffman in 1952, employs a variable-length code system that assigns shorter codes to frequently occurring characters and longer codes to less common ones. This results in a more compact representation and significant data compression.
Together with the LZ77 algorithm which replaces duplicate strings with pointers, the huffman coding is the main component of the DEFLATE algorithm used to compress among other things PDF streams and HTTP requests.

The tricky part of any variable length encoding is to recover the boundaries between the individual codes which represent the symbols. This is mainly what the huffman tree allows us to do if we can obtain it. There is a so called static huffman tree which is a standardized tree which should be obtainable on the web and the dynamic huffman tree which is computed during compression and stored alongside the encoded data so it can be used to decompress later on.

A static huffman tree will not be optimal as it is not adapted to the actual data which is compressed. However, if the length of the original data is short the non-optimal encoding can still be more compact since we can leave away the representation of the computed huffman tree from the final encoding.
In most practical cases however, a dynamically computed tree will be the more efficient choice.

The first step to create out huffman tree will be to establish the character frequencies which will be strictly proportional to the probability of reading said symbol in the data.

```python
def get_frequencies(self, seq: str) -> dict:
    self.freq_dist = {}
    for symbol in seq:
        self.freq_dist[symbol] = self.freq_dist.get(symbol, 0) + 1
    return self.freq_dist

```
To generate the binary huffman tree from symbols and symbol probabilities we follow this algorithm:

1. Create a leaf node for each symbol and add it to a queue.
2. While there is more than one node in the queue:
    - Remove the two nodes with the lowest probability from the queue
    - Create a new internal node with these two nodes as children and with probability equal to the sum of the two nodes' probabilities.
    - Add the new node to the queue.
3. The remaining node is the root node and the tree is complete.

In Python we store the tree as a dictionary of symbols and the corresponding paths to the leaf node representing that symbol. These paths will act as codes for the symbols with more frequent symbols getting shorter paths and less frequent symbols the longer paths. The paths are recorded as the tree is constructed according to the above algorithm.

```python
def make_tree(self, probabilities: dict):
    self.paths = {}
    remaining = [((s,p),) for s,p in probabilities.items()]
    while len(remaining)>1:
        remaining = sorted(remaining, key=lambda x:(x[0][1], x[0][0]))
        first=remaining.pop(0)
        second=remaining.pop(0)
        new_node = self.merge_nodes(first, second)
        remaining.append(new_node)
    self.tree=remaining.pop(0)
    return self.paths

def merge_nodes(self, node_a: Node , node_b: Node):
    for s in node_a[0][0]:
        self.paths[s]="0"+self.paths.get(s, "")
    for s in node_b[0][0]:
        self.paths[s]="1"+self.paths.get(s, "")
    return (tuple(a+b for a,b in zip(node_a[0], node_b[0])), node_a, node_b)
```
If we decode a compressed bitsequence with the help of a huffman tree we read the individual bits from left to right. According to the bit currently read we follow the tree and print the symbol as soon as we reach a leaf node. Then, we start again at the root of the tree.

### How do we encode the huffman tree?
A huffman tree with large number of unique symbols might utilise considerable amounts of space if not also encoded a bit more cleverly. To achieve this a canonical Huffman coding was introduced which restructures the path values assigned to symbols such that all symbols with codes of a given length are assigned their values sequentially (alphabetically in the case of strings). In this case it is suffient to just transmit the number of bits for each symbol in sequential order. If the number of unique symbols is smaller than the whole alphabet it might be better to store the symbols and how many of the symbols share the same length encoding. From both of these methods we are able to reconstruct the canonical Huffman tree.

```python
def canonicalize(self):
    sorted_paths = sorted(self.paths.items(), key=lambda x:(len(x[1]), x[0]))
    canon_path = len(sorted_paths[0][1]) * "0"
    self.paths[sorted_paths[0][0]] = canon_path
    for symbol, path in sorted_paths[1:]:
        # add one to previous code
        canon_path = format(int(canon_path, 2) + 1 , 'b').rjust(
            len(canon_path), "0"  # fill back 0s on the left lost in int conversion
        ).ljust(
            len(path), "0" # fill 0s on the right according to bit length required
        )
        self.paths[symbol] = canon_path
        
def decompress_tree(self, ct):
    bit_nums, symbolstack = self.recover_treeinfo_from_binary(ct)
    self.paths = {}
    path = 0
    for i, nums in enumerate(bit_nums):
        code_len = i+1
        for _ in range(nums):
            symbol = symbolstack.pop(0)
            if path == 0:
                path = "0"*code_len
            else:                    
                path = format(int(path, 2) + 1 , 'b').rjust(
                    len(path), "0" # fill back 0s on the left lost in int conversion
                ).ljust(
                    code_len, "0" # fill 0s on the right according to bit length required
                )

            self.paths[symbol] = path
```
In the code example we canonicalize (encode) and decompress (decode) the tree from the representation encoded according to the second strategy.
Finally we put all this together and test it on a few paragraphs of "Lorem ipsum...".

```python
    uncompressed = ''.join([format(ord(c),'b') for c in string])
    print(f"uncompressed length: {len(uncompressed)}")
    ht = HuffmanTree()
    compressed = ht.compress(string)
    old_paths = ht.paths

    print(f"compressed length: {len(compressed)}")
    print(f"longest path length: {max([len(e) for e in ht.paths.values()])}")
    print(f"weighted path length: {ht.get_weighted_pathlength():.4f}")
    print(f"shannon entropy: {calculate_entropy(string, ht.freq_dist):.4f}")
    ## reset the object
    ht = HuffmanTree()
    decompressed = ht.decompress(compressed)
    assert old_paths==ht.paths
    assert string==decompressed
```

Running this code we see that we achieve a considerable compression of ~40% on the relatively short text and that the sum of the path lengths of the symbols weighted by their probability nears the theoretical limit of optimal compression set by the Shannon entropy of 4.2161.
```
uncompressed length: 26485
compressed length: 16929
longest path length: 12
weighted path length: 4.2537
shannon entropy: 4.2161
```

Learn more about Huffmann Codes on [Wikipedia](https://en.wikipedia.org/wiki/Huffman_coding).


