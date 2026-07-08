"""Train the deep-learning demo models and save the artifacts.

Run from backend/:
    ./venv/bin/python -m app.demos.train_dl
"""

import base64
import io
from pathlib import Path

import joblib
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from app.demos import text_data
from app.demos.torch_models import (
    SmallCNN, GrayCNN, TextRNN, TinyTransformer,
    build_vocab, encode, save_model,
)

ARTIFACTS = Path(__file__).parent / "artifacts"
DATA_CACHE = Path(__file__).parent / "data_cache"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

CIFAR_CLASSES = ["airplane", "automobile", "bird", "cat", "deer",
                 "dog", "frog", "horse", "ship", "truck"]


def _save(name, obj):
    joblib.dump(obj, ARTIFACTS / f"{name}.joblib")
    print(f"saved {name}")


def _png_b64(array_uint8, mode):
    from PIL import Image

    img = Image.fromarray(array_uint8, mode)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _train_torch(model, X, y, epochs, batch=128, lr=1e-3, X_val=None, y_val=None, name=""):
    torch.manual_seed(42)
    model = model.to(DEVICE)
    loader = DataLoader(TensorDataset(X, y), batch_size=batch, shuffle=True)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    history = {"loss": [], "val_acc": []}
    for ep in range(epochs):
        model.train()
        total = 0.0
        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
            total += loss.item() * len(xb)
        history["loss"].append(total / len(X))
        msg = f"  {name} epoch {ep + 1}/{epochs}: loss {total / len(X):.4f}"
        if X_val is not None:
            model.eval()
            with torch.no_grad():
                preds = []
                for i in range(0, len(X_val), 512):
                    preds.append(model(X_val[i:i + 512].to(DEVICE)).argmax(1).cpu())
                acc = (torch.cat(preds) == y_val).float().mean().item()
            history["val_acc"].append(acc)
            msg += f", val acc {acc:.3f}"
        print(msg)
    return model.cpu(), history


def _text_tensors(texts, labels, vocab):
    X = torch.tensor([encode(t, vocab) for t in texts], dtype=torch.long)
    y = torch.tensor(labels, dtype=torch.long)
    return X, y


def train_sentiment_rnn():
    texts, labels = text_data.sentiment_corpus(classes=2)
    vocab = build_vocab(texts)
    X, y = _text_tensors(texts, labels, vocab)
    n = int(len(X) * 0.9)
    idx = torch.randperm(len(X), generator=torch.Generator().manual_seed(0))
    model = TextRNN(len(vocab), 2, cell="rnn")
    model, history = _train_torch(model, X[idx[:n]], y[idx[:n]], epochs=8,
                                  X_val=X[idx[n:]], y_val=y[idx[n:]], name="sentiment RNN")
    _save("sentiment_rnn", {"model": save_model(model), "vocab": vocab,
                            "classes": ["negative", "positive"], "history": history})


def train_sentiment_lstm():
    texts, labels = text_data.sentiment_corpus(classes=3)
    vocab = build_vocab(texts)
    X, y = _text_tensors(texts, labels, vocab)
    n = int(len(X) * 0.9)
    idx = torch.randperm(len(X), generator=torch.Generator().manual_seed(0))
    model = TextRNN(len(vocab), 3, cell="lstm")
    model, history = _train_torch(model, X[idx[:n]], y[idx[:n]], epochs=8,
                                  X_val=X[idx[n:]], y_val=y[idx[n:]], name="sentiment LSTM")
    _save("sentiment_lstm", {"model": save_model(model), "vocab": vocab,
                             "classes": ["negative", "neutral", "positive"], "history": history})


def train_topic_transformer():
    texts, labels = text_data.topic_corpus()
    vocab = build_vocab(texts)
    X, y = _text_tensors(texts, labels, vocab)
    n = int(len(X) * 0.9)
    idx = torch.randperm(len(X), generator=torch.Generator().manual_seed(0))
    model = TinyTransformer(len(vocab), len(text_data.TOPIC_CLASSES))
    model, history = _train_torch(model, X[idx[:n]], y[idx[:n]], epochs=12, lr=5e-4,
                                  X_val=X[idx[n:]], y_val=y[idx[n:]], name="topic transformer")
    _save("topic_transformer", {"model": save_model(model), "vocab": vocab,
                                "classes": text_data.TOPIC_CLASSES, "history": history})


def train_cifar_cnn():
    from torchvision import datasets

    train_ds = datasets.CIFAR10(DATA_CACHE, train=True, download=True)
    test_ds = datasets.CIFAR10(DATA_CACHE, train=False, download=True)
    mean = np.array([0.4914, 0.4822, 0.4465], dtype=np.float32)
    std = np.array([0.247, 0.243, 0.261], dtype=np.float32)

    def to_tensor(ds):
        raw = ds.data.astype(np.float32) / 255.0  # N,32,32,3
        X = torch.tensor(((raw - mean) / std).transpose(0, 3, 1, 2))
        return X, torch.tensor(ds.targets)

    X_tr, y_tr = to_tensor(train_ds)
    X_te, y_te = to_tensor(test_ds)
    model, history = _train_torch(SmallCNN(), X_tr, y_tr, epochs=6, batch=256,
                                  X_val=X_te, y_val=y_te, name="CIFAR CNN")

    # 24 sample test images for the picker (2-3 per class, true label hidden in value).
    rng = np.random.default_rng(3)
    sample_idx = []
    targets = np.array(test_ds.targets)
    for c in range(10):
        sample_idx += rng.choice(np.where(targets == c)[0], 2, replace=False).tolist()
    rng.shuffle(sample_idx)
    samples = []
    for i in map(int, sample_idx[:24]):
        samples.append({
            "image": _png_b64(test_ds.data[i], "RGB"),
            "pixels": test_ds.data[i].tolist(),
            "true_label": CIFAR_CLASSES[targets[i]],
        })
    _save("cifar_cnn", {"model": save_model(model), "classes": CIFAR_CLASSES,
                        "mean": mean.tolist(), "std": std.tolist(), "samples": samples,
                        "history": history})


def train_pneumonia_cnn():
    from medmnist import PneumoniaMNIST

    train_ds = PneumoniaMNIST(split="train", download=True, root=str(DATA_CACHE))
    test_ds = PneumoniaMNIST(split="test", download=True, root=str(DATA_CACHE))
    X_tr = torch.tensor(train_ds.imgs, dtype=torch.float32).unsqueeze(1) / 255.0
    y_tr = torch.tensor(train_ds.labels.squeeze(), dtype=torch.long)
    X_te = torch.tensor(test_ds.imgs, dtype=torch.float32).unsqueeze(1) / 255.0
    y_te = torch.tensor(test_ds.labels.squeeze(), dtype=torch.long)
    model, history = _train_torch(GrayCNN(), X_tr, y_tr, epochs=5, batch=128,
                                  X_val=X_te, y_val=y_te, name="pneumonia CNN")

    rng = np.random.default_rng(5)
    labels = test_ds.labels.squeeze()
    sample_idx = (rng.choice(np.where(labels == 0)[0], 8, replace=False).tolist()
                  + rng.choice(np.where(labels == 1)[0], 8, replace=False).tolist())
    rng.shuffle(sample_idx)
    samples = []
    for i in map(int, sample_idx):
        samples.append({
            "image": _png_b64(test_ds.imgs[i], "L"),
            "pixels": test_ds.imgs[i].tolist(),
            "true_label": "pneumonia" if labels[i] == 1 else "normal",
        })
    _save("pneumonia_cnn", {"model": save_model(model),
                            "classes": ["normal", "pneumonia"], "samples": samples,
                            "history": history})


def train_autoencoder():
    """Sensor-health autoencoder: trained on normal machine readings only."""
    from sklearn.neural_network import MLPRegressor
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(42)
    n = 6000
    rpm = rng.normal(1500, 150, n)
    vibration = 0.002 * rpm + rng.normal(1.0, 0.25, n)
    temperature = 60 + 0.01 * rpm + rng.normal(0, 2.5, n)
    pressure = rng.normal(5.0, 0.35, n)
    current = 0.004 * rpm + rng.normal(2.0, 0.4, n)
    X = np.column_stack([temperature, vibration, pressure, rpm, current])
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)
    ae = MLPRegressor(hidden_layer_sizes=(8, 3, 8), max_iter=800, random_state=42)
    ae.fit(Xs, Xs)
    errors = ((ae.predict(Xs) - Xs) ** 2).mean(axis=1)
    threshold = float(np.quantile(errors, 0.975))
    print(f"  autoencoder: reconstruction threshold {threshold:.4f}")
    _save("sensor_autoencoder", {"model": ae, "scaler": scaler, "threshold": threshold})


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    DATA_CACHE.mkdir(exist_ok=True)
    print(f"Training deep-learning demos on {DEVICE}…")
    train_sentiment_rnn()
    train_sentiment_lstm()
    train_topic_transformer()
    train_autoencoder()
    train_pneumonia_cnn()
    train_cifar_cnn()
    print("Done.")


if __name__ == "__main__":
    main()
