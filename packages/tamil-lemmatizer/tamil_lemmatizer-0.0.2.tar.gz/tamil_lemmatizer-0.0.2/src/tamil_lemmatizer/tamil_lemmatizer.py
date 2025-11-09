from tamil_lemmatizer.model import Encoder, Decoder ,Seq2Seq,EMBED_SIZE,HIDDEN_SIZE
import re
import torch
from tamil_lemmatizer.tokenizer import encode_token, decode_token, char2idx, EOS, SOS,VOCAB_SIZE
from huggingface_hub import hf_hub_download

REPO_ID = "Hemanth-thunder/lemma"
FILENAME = "model.pt"
#CACHE_DIR = "asset" 

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
 

class TamilLemmatizer:
 
    def __init__(self):
        self.asset = self._load_asset()

        encoder = Encoder(VOCAB_SIZE, EMBED_SIZE, HIDDEN_SIZE).to(DEVICE)
        decoder = Decoder(VOCAB_SIZE, EMBED_SIZE, HIDDEN_SIZE).to(DEVICE)
        self.model = Seq2Seq(encoder, decoder).to(DEVICE)
        self.model.load_state_dict(torch.load(self.asset,map_location=DEVICE))
 
        self.model.eval()
        self.max_len = 30
 
    def _load_asset(self):
        return hf_hub_download(repo_id=REPO_ID, 
                               filename=FILENAME)
    
    def lemmatize(self,word):
        if word:
            return self.get_tamil_lemma(tamil_word=word)
        else:
            return "No word"
    
    def is_tamil(self,word):
        return bool(re.fullmatch(r'[\u0B80-\u0BFF]+', word))
    
    
    def predict(self,word):
        with torch.no_grad():

            src = torch.tensor([encode_token(word)]).to(DEVICE)
            encoder_outputs, hidden, cell = self.model.encoder(src)

            input = torch.tensor([char2idx[SOS]]).to(DEVICE)
            decoded_indices = []

            for _ in range(self.max_len):
                out, hidden, cell = self.model.decoder(input, hidden, cell, encoder_outputs)
                top1 = out.argmax(1)
                if top1.item() == char2idx[EOS]:
                    break
                decoded_indices.append(top1.item())
                input = top1

            return decode_token(decoded_indices)        
        
    def get_tamil_lemma(self,tamil_word):
        if self.is_tamil(tamil_word):
            lemma = self.predict(word= tamil_word)
            return lemma
        else:
            return tamil_word
 