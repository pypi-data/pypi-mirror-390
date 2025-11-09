
from tamil_lemmatizer.vocab import char2idx 
  
  
VOCAB_SIZE = len(char2idx)

PAD, SOS, EOS = "<PAD>", "<SOS>", "<EOS>"

char2idx[PAD] = 0
char2idx[SOS] = 1
char2idx[EOS] = 2
idx2char = {i: c for c, i in char2idx.items()}


class CharTokenizer:
    def __init__(self, char2idx):
        self.char2id = char2idx
        self.id2char = {idx: ch for ch, idx in char2idx.items()}
    def encode(self, text):
        return [self.char2id.get(ch, 0) for ch in text]
    def decode(self, ids):
        return "".join([self.id2char.get(i, "") for i in ids if i != 0])

tokenizer = CharTokenizer(char2idx)

def encode_token(word):
    return [char2idx[SOS]] + [char2idx[c] for c in word] + [char2idx[EOS]]

def decode_token(indices):
    return "".join(idx2char[i] for i in indices if i > 2)