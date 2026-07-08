"""PyTorch model definitions shared by training and inference.

Models are saved as (config, state_dict) pairs and rebuilt here, so artifacts
stay loadable across torch versions.
"""

import re

import torch
import torch.nn as nn

PAD, UNK = 0, 1
MAX_LEN = 24


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def build_vocab(texts: list[str]) -> dict[str, int]:
    vocab = {"<pad>": PAD, "<unk>": UNK}
    for t in texts:
        for w in tokenize(t):
            if w not in vocab:
                vocab[w] = len(vocab)
    return vocab


def encode(text: str, vocab: dict[str, int]) -> list[int]:
    ids = [vocab.get(w, UNK) for w in tokenize(text)][:MAX_LEN]
    return ids + [PAD] * (MAX_LEN - len(ids))


class TextRNN(nn.Module):
    """Vanilla RNN (or LSTM/GRU) sentence classifier."""

    def __init__(self, vocab_size, n_classes, cell="rnn", embed_dim=48, hidden=64):
        super().__init__()
        self.config = {"vocab_size": vocab_size, "n_classes": n_classes, "cell": cell,
                       "embed_dim": embed_dim, "hidden": hidden}
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=PAD)
        rnn_cls = {"rnn": nn.RNN, "lstm": nn.LSTM, "gru": nn.GRU}[cell]
        self.rnn = rnn_cls(embed_dim, hidden, batch_first=True)
        self.fc = nn.Linear(hidden, n_classes)

    def forward(self, x):
        emb = self.embed(x)
        out, _ = self.rnn(emb)
        # Mean over non-pad positions.
        mask = (x != PAD).unsqueeze(-1).float()
        pooled = (out * mask).sum(1) / mask.sum(1).clamp(min=1)
        return self.fc(pooled)


class TinyTransformer(nn.Module):
    """Small Transformer encoder classifier trained from scratch."""

    def __init__(self, vocab_size, n_classes, embed_dim=64, heads=4, layers=2):
        super().__init__()
        self.config = {"vocab_size": vocab_size, "n_classes": n_classes,
                       "embed_dim": embed_dim, "heads": heads, "layers": layers}
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=PAD)
        self.pos = nn.Parameter(torch.zeros(1, MAX_LEN, embed_dim))
        enc_layer = nn.TransformerEncoderLayer(
            embed_dim, heads, dim_feedforward=128, batch_first=True, dropout=0.1
        )
        self.encoder = nn.TransformerEncoder(enc_layer, layers)
        self.fc = nn.Linear(embed_dim, n_classes)

    def forward(self, x):
        pad_mask = x == PAD
        h = self.encoder(self.embed(x) + self.pos, src_key_padding_mask=pad_mask)
        mask = (~pad_mask).unsqueeze(-1).float()
        pooled = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
        return self.fc(pooled)


class SmallCNN(nn.Module):
    """CNN for 32x32 RGB images (CIFAR-10)."""

    def __init__(self, n_classes=10):
        super().__init__()
        self.config = {"n_classes": n_classes}
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(), nn.Linear(64 * 8 * 8, 256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, n_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


class GrayCNN(nn.Module):
    """CNN for 28x28 grayscale images (PneumoniaMNIST)."""

    def __init__(self, n_classes=2):
        super().__init__()
        self.config = {"n_classes": n_classes}
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(), nn.Linear(32 * 7 * 7, 64), nn.ReLU(), nn.Linear(64, n_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x))


MODEL_CLASSES = {
    "TextRNN": TextRNN,
    "TinyTransformer": TinyTransformer,
    "SmallCNN": SmallCNN,
    "GrayCNN": GrayCNN,
}


def save_model(model: nn.Module) -> dict:
    return {"class": type(model).__name__, "config": model.config,
            "state_dict": {k: v.cpu() for k, v in model.state_dict().items()}}


def load_model(payload: dict) -> nn.Module:
    model = MODEL_CLASSES[payload["class"]](**payload["config"])
    model.load_state_dict(payload["state_dict"])
    model.eval()
    return model
