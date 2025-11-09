import torch
import torch.nn as nn
 
from tamil_lemmatizer.tokenizer import VOCAB_SIZE, char2idx, PAD
 


EMBED_SIZE = 512
HIDDEN_SIZE = 1024

 
        
 

#############################################
# Encoder
#############################################
class Encoder(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=char2idx[PAD])
        self.rnn = nn.LSTM(embed_size, hidden_size, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, hidden_size)

    def forward(self, x):
        emb = self.embedding(x)
        out, (h, c) = self.rnn(emb)
        h = torch.tanh(self.fc(torch.cat((h[0], h[1]), dim=1))).unsqueeze(0)
        c = torch.tanh(self.fc(torch.cat((c[0], c[1]), dim=1))).unsqueeze(0)
        return out, h, c
    
    

#############################################
# Attention
#############################################
class Attention(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.attn = nn.Linear(hidden_size * 3, hidden_size)
        self.v = nn.Linear(hidden_size, 1, bias=False)

    def forward(self, hidden, encoder_outputs):
        batch_size, seq_len, _ = encoder_outputs.size()
        hidden = hidden.permute(1, 0, 2).repeat(1, seq_len, 1)
        combined = torch.cat((hidden, encoder_outputs), dim=2)
        energy = torch.tanh(self.attn(combined))
        attn_scores = self.v(energy).squeeze(2)
        return torch.softmax(attn_scores, dim=1)

#############################################
# Decoder
#############################################
class Decoder(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=char2idx[PAD])
        self.rnn = nn.LSTM(embed_size + hidden_size * 2, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)
        self.attention = Attention(hidden_size)

    def forward(self, input, hidden, cell, encoder_outputs):
        input = input.unsqueeze(1)
        emb = self.embedding(input)
        attn_weights = self.attention(hidden, encoder_outputs)
        context = torch.bmm(attn_weights.unsqueeze(1), encoder_outputs)
        rnn_input = torch.cat((emb, context), dim=2)
        output, (hidden, cell) = self.rnn(rnn_input, (hidden, cell))
        logits = self.fc(output.squeeze(1))
        return logits, hidden, cell

#############################################
# Seq2Seq Model
#############################################
class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder

    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        encoder_outputs, hidden, cell = self.encoder(src)
        batch_size, trg_len = trg.size()
        outputs = torch.zeros(batch_size, trg_len - 1, VOCAB_SIZE).to(DEVICE)

        input = trg[:, 0]  # <SOS>
        for t in range(1, trg_len):
            out, hidden, cell = self.decoder(input, hidden, cell, encoder_outputs)
            outputs[:, t - 1, :] = out

            teacher_force = torch.rand(1).item() < teacher_forcing_ratio
            top1 = out.argmax(1)
            input = trg[:, t] if teacher_force else top1

        return outputs

 

 


