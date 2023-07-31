from typing import Tuple
import math

class HuffmanTree():
    def __init__(self) -> None:
        self.paths = {}
        self.freq_dist = {}
        self.sequence = ""

    def get_frequencies(self, seq: str) -> dict:
        self.freq_dist = {}
        for symbol in seq:
            self.freq_dist[symbol] = self.freq_dist.get(symbol, 0) + 1
        return self.freq_dist
    
    def make_tree(self, probabilities):
        self.paths = {}
        remaining = probabilities.items()
        while len(remaining)>1:
            remaining = sorted(remaining, key=lambda x:x[1])
            first=remaining.pop(0)
            second=remaining.pop(0)
            new_node = self.merge_nodes(first, second)
            remaining.append(new_node)
        return self.paths
    
    def merge_nodes(self, node_a: Tuple[str, int], node_b: Tuple[str, int]):
        for s in node_a[0]:
            self.paths[s] = self.paths.get(s, "") + "0"
        for s in node_b[0]:
            self.paths[s] = self.paths.get(s, "") + "1"
        return tuple(a+b for a,b in zip(node_a, node_b))
    
    def encode(self, sequence: str) -> str:
        self.sequence = sequence
        self.probabilities = self.get_frequencies(sequence)
        self.paths = self.make_tree(self.probabilities)
        self.canonicalize()
        return [self.paths[s] for s in self.sequence]
    
    def canonicalize(self):
        sorted_paths = sorted(self.paths.items(), key=lambda x:(len(x[1]), x[0]))
        canon_path = "0"
        self.paths[sorted_paths[0][0]] = canon_path * len(sorted_paths[0][1])
        for symbol, path in sorted_paths[1:]:
            canon_path = format(int(canon_path, 2) + 1, 'b')
            canon_path = format(int(canon_path, 2) << (len(path) - len(canon_path)), 'b')
            self.paths[symbol] = canon_path

    def get_compressed_path(self):
        all_symbols = sorted(self.paths.items(), key=lambda x:(len(x[1]), x[0]))
        bit_lens = [0 for l in range(max([len(p) for p in self.paths.values()])+1)]
        for s, path in all_symbols:
            bit_lens[len(path)]+=1
        return (bit_lens, [s for s,_ in all_symbols])
    
    def from_compressed_path(self, bit_nums, symbols):
        self.paths = {}
        symbolstack = symbols.copy()
        path = 0
        for i, nums in enumerate(bit_nums):
            for _ in range(nums):
                symbol = symbolstack.pop(0)
                if path == 0:
                    path = "0"*i
                else:
                    path = format(int(path, 2) + 1, 'b')
                    path = format(int(path, 2) << (i - len(path)), 'b')
                self.paths[symbol] = path


    def decode(self, codes, bit_lengths=None, symbols=None):
        string=""
        if bit_lengths is not None and symbols is not None:
            self.from_compressed_path(bit_lengths, symbols)
        code_to_symbol = {b:a for a,b in self.paths.items()}
        for code in codes:
            string+=code_to_symbol[code]
        return string

    def get_weighted_pathlength(self):
        len_seq = len(self.sequence)
        return sum(
            [
                len(self.paths[s]) * (self.freq_dist[s] / len_seq) 
                for s in self.sequence
            ]
        )

def calculate_entropy(sequence, freq_dist):
    len_seq = len(sequence)
    return sum(
            [
                (freq_dist[s] / len_seq) * math.log((freq_dist[s] / len_seq), 2) 
                for s in sequence
            ]
        ) * -1
    
if __name__=="__main__":
    string = "hello world."
    ht = HuffmanTree()
    encoded = ht.encode(string)
    print(encoded)
    bitsize_freqs, symbols = ht.get_compressed_path()
    ht.from_compressed_path(bitsize_freqs, symbols)
    decoded = ht.decode(encoded, bitsize_freqs, symbols)
    print(decoded)
    print("longest path length:", max([len(e) for e in encoded]))
    print(f"weighted path length:{ht.get_weighted_pathlength():.4f}")
    print(f"shannon entropy: {calculate_entropy(string, ht.freq_dist):.4f}")