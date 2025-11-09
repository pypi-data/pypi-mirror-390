from model_load import model, DEVICE
import re
import torch
from tokenizer import encode_token, decode_token, char2idx, EOS, SOS

def predict(word, max_len=30):
    with torch.no_grad():

        src = torch.tensor([encode_token(word)]).to(DEVICE)
        encoder_outputs, hidden, cell = model.encoder(src)

        input = torch.tensor([char2idx[SOS]]).to(DEVICE)
        decoded_indices = []

        for _ in range(max_len):
            out, hidden, cell = model.decoder(input, hidden, cell, encoder_outputs)
            top1 = out.argmax(1)
            if top1.item() == char2idx[EOS]:
                break
            decoded_indices.append(top1.item())
            input = top1

        return decode_token(decoded_indices)


class TamilLemmatizer:
    def __init__(self):
        pass
    
    def lemmatize(self,word):
        if word:
            return self.get_tamil_lemma(tamil_word=word)
        else:
            return "No word"
    
    def is_tamil(self,word):
        return bool(re.fullmatch(r'[\u0B80-\u0BFF]+', word))
        
        
    def get_tamil_lemma(self,tamil_word):
        tamil_list = tamil_word.split(" ")
        result = []
        for w in tamil_list:
            if self.is_tamil(w):
                lemma = predict(w, model)
                result.append(lemma)
            else:
                result.append(lemma)
        return result