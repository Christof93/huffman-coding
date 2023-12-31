import math
Node = tuple[tuple[str, int], tuple[str, int], tuple[str, int]]

class HuffmanTree():
    def __init__(self) -> None:
        self.header = "110"
        self.paths = {}
        self.freq_dist = {}
        self.sequence = ""
        self.tree = []

    def get_frequencies(self, seq: str) -> dict:
        self.freq_dist = {}
        for symbol in seq:
            self.freq_dist[symbol] = self.freq_dist.get(symbol, 0) + 1
        return self.freq_dist
    
    def make_tree(self, probabilities: dict):
        self.paths = {}
        remaining = [((s,p),) for s,p in probabilities.items()]
        while len(remaining)>1:
            # sort by probability
            remaining = sorted(remaining, key=lambda x:(x[0][1], x[0][0]))
            # remove first two nodes
            first=remaining.pop(0)
            second=remaining.pop(0)
            # merge the nodes and sum their probabilities
            new_node = self.merge_nodes(first, second)
            # add it back into the queue
            remaining.append(new_node)
        self.tree=remaining.pop(0)
        return self.paths

    def merge_nodes(self, node_a: Node , node_b: Node):
        # extend all paths on the left
        for s in node_a[0][0]:
            self.paths[s]="0"+self.paths.get(s, "")
        # extend all paths on the right
        for s in node_b[0][0]:
            self.paths[s]="1"+self.paths.get(s, "")
        return (tuple(a+b for a,b in zip(node_a[0], node_b[0])), node_a, node_b)

    def calculate_paths(self, tree, current_path=""):
        for i, node in enumerate(tree[1:]):
            if len(node)==1:
                self.paths[node[0][0]] = current_path + str(i)
            else:
                self.calculate_paths(node, current_path + str(i))
    
    def encode(self, sequence: str) -> str:
        self.sequence = sequence
        self.probabilities = self.get_frequencies(sequence)
        self.paths = self.make_tree(self.probabilities)
        self.canonicalize()
        return "".join(self.paths[s] for s in self.sequence)
    
    def form_canon_path(self, path, new_length):
        if path == 0:
            path = "0"*new_length
        else:                    
            path = format(int(path, 2) + 1 , 'b').rjust(
                len(path), "0" # fill back 0s on the left lost in int conversion
            ).ljust(
                new_length, "0" # fill 0s on the right according to bit length required
            )
        return path
    
    def canonicalize(self):
        # sort paths by length and then alphabetically by their leaf node
        sorted_paths = sorted(self.paths.items(), key=lambda x:(len(x[1]), x[0]))
        # initialize the canonical path as a string of 0s lengths of the shortest path
        canon_path = 0
        for symbol, path in sorted_paths:
            # add one to previous code
            canon_path = self.form_canon_path(canon_path, len(path))
            self.paths[symbol] = canon_path
    
    
    def get_compressed_tree(self):
        all_symbols, all_paths = map(
            list, 
            zip(*sorted(self.paths.items(), key=lambda x:(len(x[1]), x[0])))
        )
        bit_lens = [0 for _ in range(max([len(p) for p in all_paths]))]
        for path in all_paths:
            bit_lens[len(path)-1]+=1
        return "".join([
            "".join(
                [format(bl,'b').zfill(7) for bl in [len(bit_lens)]+bit_lens]
            ), 
            "".join(
                [format(len(all_symbols),'b').zfill(7)]+
                [format(ord(s),'b').zfill(7) for s in all_symbols]
            )
        ])
    
    def recover_treeinfo_from_binary(self, ct):
        self.num_bins=int(ct[:7], 2)
        ct = ct[7:]
        bit_nums=[int(ct[i:i+7], 2) for i in range(0, self.num_bins*7, 7)]
        ct = ct[self.num_bins*7:]
        self.num_symbols = int(ct[:7], 2)
        ct = ct[7:]
        symbolstack = [chr(int(ct[i:i+7], 2)) for i in range(0, self.num_symbols*7, 7)]
        ct=None
        return bit_nums, symbolstack
        
    def decompress_tree(self, ct):
        # get the unique symbols and the code length bins
        bit_nums, symbolstack = self.recover_treeinfo_from_binary(ct)
        self.paths = {}
        path = 0
        for i, nums in enumerate(bit_nums):
            code_len = i+1
            for _ in range(nums):
                # pop as many symbols as there are of the same code length
                symbol = symbolstack.pop(0)
                # use the same canonicalization algorithm to recover the tree 
                path = self.form_canon_path(path, code_len)
                self.paths[symbol] = path

    def decode(self, encoded):
        string=""
        code_to_symbol = {b:a for a,b in self.paths.items()}
        code=""
        for bit in encoded:
            code+=bit
            try:
                string+=code_to_symbol[code]
                code=""
            except KeyError:
                continue
        self.sequence = string
        self.probabilities = self.get_frequencies(self.sequence)
        return string

    def compress(self, sequence: str) -> str:
        encoded = self.encode(sequence)
        compressed_tree = self.get_compressed_tree()
        return self.header + compressed_tree + encoded
    
    def decompress(self, compressed_bitstream):
        self.decompress_tree(compressed_bitstream[3:])
        bitlen_tree = 7*self.num_bins+7*self.num_symbols+(2*7)
        decoded = self.decode(compressed_bitstream[3+bitlen_tree:])
        return decoded

    def get_weighted_pathlength(self):
        len_seq = len(self.sequence)
        return sum(
            [
                len(self.paths[s]) * (self.freq_dist[s] / len_seq) 
                for s in set(self.sequence)
            ]
        )

def calculate_entropy(sequence, freq_dist):
    len_seq = len(sequence)
    return sum(
            [
                (freq_dist[s] / len_seq) * math.log((freq_dist[s] / len_seq), 2) * -1
                for s in set(sequence)
            ]
        )

def test_hufftree():
    string = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce rutrum at velit quis sodales. Sed scelerisque sit amet ex at mattis. Cras vestibulum ultricies massa eget pulvinar. Aliquam pharetra eget sem eget sodales. Cras dapibus turpis ante, a aliquet orci porttitor et. Fusce posuere urna ante, non maximus nulla sollicitudin et. Donec faucibus urna vel metus tincidunt lobortis. Donec maximus risus diam, at venenatis eros posuere eget. Vivamus ac ante viverra, sollicitudin elit ut, blandit enim. Fusce cursus ligula vel nisl elementum, a ullamcorper mauris placerat. Cras ornare egestas justo, eu imperdiet risus consequat a. Sed sagittis lectus vel lectus ultricies, eu lobortis quam accumsan. Phasellus euismod, neque eu viverra tempus, ligula dolor ultricies nisl, ac lobortis enim massa in felis. Proin laoreet hendrerit erat ut posuere.

Quisque tincidunt dolor rutrum turpis semper, sed pulvinar diam scelerisque. Aliquam mattis, tellus vitae ornare gravida, ipsum eros pellentesque libero, ut convallis ante nulla iaculis felis. Curabitur quis lectus non felis congue lobortis. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Duis non nunc auctor, rhoncus leo at, pulvinar elit. Integer condimentum egestas mollis. Maecenas augue turpis, fringilla ac suscipit sed, malesuada lacinia lacus. Fusce gravida convallis lorem nec consequat. Pellentesque at risus lacus. Morbi rutrum, nisl et iaculis tincidunt, nisi elit posuere purus, ac consequat turpis nibh non magna. Vivamus in lacus iaculis, euismod velit sit amet, placerat sapien.

Aenean nunc odio, interdum eu dapibus sit amet, suscipit sit amet orci. Morbi condimentum tellus vitae massa ultrices dapibus. Nulla ac odio tristique, auctor nunc euismod, imperdiet est. Nam tempus urna et diam vulputate imperdiet. Nullam sit amet malesuada elit. Sed semper arcu metus, in interdum mi convallis eu. Praesent ut feugiat urna. Phasellus eu porttitor metus. Suspendisse tempor malesuada velit quis sagittis. Nunc velit massa, vestibulum molestie feugiat quis, suscipit euismod eros. Mauris pulvinar dui elit, et ornare ex mollis ut. Fusce mauris ipsum, dapibus id vestibulum viverra, congue at nisl. Ut elementum commodo varius.

Sed a ligula maximus, hendrerit turpis nec, dictum neque. Cras dictum augue at turpis fermentum, nec dictum dui aliquam. In sit amet nunc molestie, maximus nunc vitae, molestie lorem. Aenean vestibulum vel tortor quis ornare. Nam suscipit, felis ac aliquam sagittis, ligula ipsum tincidunt velit, a dapibus diam enim sit amet lectus. Interdum et malesuada fames ac ante ipsum primis in faucibus. Vivamus sagittis, purus pretium aliquet porttitor, enim dui convallis eros, nec ullamcorper sem urna a felis. Quisque at ex a velit imperdiet scelerisque. Fusce non nulla condimentum, aliquet nisl in, viverra dui. Etiam accumsan iaculis egestas. Etiam luctus sit amet ex euismod volutpat. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Nulla ante nibh, tristique congue arcu vel, faucibus ultricies eros. Aliquam aliquam fringilla purus quis pulvinar. Curabitur sed ligula nunc.

Curabitur finibus nisl nec auctor dignissim. Maecenas iaculis nisl felis, nec laoreet tellus consectetur sit amet. Donec eu euismod dolor. Quisque in blandit mauris, a lacinia nisi. Pellentesque congue nunc at tortor fringilla pharetra. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Cras placerat dui in volutpat vulputate. Nullam nulla ligula, pharetra a varius luctus, mollis vel nibh. Sed tristique venenatis ultricies. Pellentesque nisi elit, lacinia eget ultrices sed, sagittis vel urna. Ut ac ex id augue finibus bibendum non vitae eros. Donec sodales semper felis, eu gravida quam interdum ut.
"""
    # string = "hello world."
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

if __name__=="__main__":
    test_hufftree()