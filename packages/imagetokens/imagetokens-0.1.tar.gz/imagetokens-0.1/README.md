# imagetokens 🖼️🔑

A lightweight Python package for **image tokenization** and **PyTorch dataset loading**.

## 🚀 Features
- Deterministic image token generation using SHA-256 hashing.
- Simple dataset loader for subfolder-structured image directories.
- Ready for machine learning pipelines with `torch.utils.data.DataLoader`.

## 📦 Installation
```bash
pip install imagetokens
```

---
# 🎯Usage
```Python
from imagetokens import TokenizedImageDataset
from torch.utils.data import DataLoader

dataset = TokenizedImageDataset("data/train")
loader = DataLoader(dataset, batch_size=8, shuffle=True)

for images, tokens, labels in loader:
    print(tokens[:3], labels[:3])
