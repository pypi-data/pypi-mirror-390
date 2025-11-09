# Tamil Lemmatizer

**Tamil Lemmatizer** is a character-level lemmatization library for Tamil text.  
It normalizes inflected Tamil word forms and maps them to their base lemma using a deep learning model (PyTorch).

---

## ✨ Features

- ✅ Lemmatizes Tamil words to their base form
- ✅ Handles unseen words using a character-level sequence model
- ✅ Simple Python API
- ✅ Supports batch inference
- ✅ Open-source and extensible

---

## 📦 Installation

```bash
pip install tamil-lemmatizer
````

---

## 🚀 Quick Start

```python
from tamil_lemmatizer import TamilLemmatizer

lemmatizer = TamilLemmatizer()

word = "சென்றார்கள்"
lemma = lemmatizer.lemmatize(word)

print(lemma)   # Output: செல்
```

### Batch input

```python
words = ["பாடுகிறது", "வந்தார்கள்", "சென்றேன்"]
print(lemmatizer.lemmatize_batch(words))
```

---

## 📚 Description

Tamil is morphologically rich. A single lemma can have hundreds of inflected variations.
This library uses:

* A character-level encoder-decoder architecture
* Trained using PyTorch on a curated Tamil lemma dataset
* Supports lemmatization for verbs and nouns

---

## 🛠️ Model Architecture

* Encoder: BiLSTM or Transformer (depending on version)
* Decoder: Attention-based sequence generator
* Loss: Cross entropy over Tamil character vocabulary

---

 

---

## 🔧 CLI Usage

```bash
tamil-lemmatizer "வந்தார்கள்"
```
 
---

## 📄 License

This project is released under the **MIT License**.

---

## 🤝 Contributing

Pull requests are welcome.
If contributing major changes, open an issue first to discuss what you want to change.

---

## ✉️ Contact

Maintainer: **Hemanth Kumar**
GitHub: [Hemanth Thunder](https://github.com/Hemanthkumar2112) 

---
