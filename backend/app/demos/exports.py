"""CSV exports of the training data behind each live demo.

Each entry maps a project slug to (filename, builder) where the builder
returns a pandas DataFrame. Datasets are regenerated with the same seeds
used in training, so the download matches what the model actually saw.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from app.demos import agents_data, datasets, text_data

DATA_CACHE = Path(__file__).parent / "data_cache"


def _text_df(pos, neg, pos_label, neg_label, text_col="text", label_col="label"):
    return pd.DataFrame({
        text_col: list(pos) + list(neg),
        label_col: [pos_label] * len(pos) + [neg_label] * len(neg),
    })


def _sentiment_df(classes):
    texts, labels = text_data.sentiment_corpus(classes=classes)
    names = {2: ["negative", "positive"], 3: ["negative", "neutral", "positive"]}[classes]
    return pd.DataFrame({"review": texts, "sentiment": [names[l] for l in labels]})


def _topic_df():
    texts, labels = text_data.topic_corpus()
    return pd.DataFrame({"headline": texts,
                         "topic": [text_data.TOPIC_CLASSES[l] for l in labels]})


def _movies_df():
    rows = []
    for title, year, rating, genres in datasets.MOVIES:
        row = {"title": title, "year": year, "rating": rating}
        row.update({f"genre_{g.lower().replace('-', '_')}": flag
                    for g, flag in zip(datasets.GENRE_NAMES, genres)})
        rows.append(row)
    return pd.DataFrame(rows)


def _gene_df():
    X, labels = datasets.gene_expression()
    df = pd.DataFrame(X, columns=[f"gene_{i+1}" for i in range(X.shape[1])]).round(4)
    df.insert(0, "tissue", labels)
    return df


def _sensor_df():
    rng = np.random.default_rng(42)
    n = 6000
    rpm = rng.normal(1500, 150, n)
    return pd.DataFrame({
        "temperature_c": (60 + 0.01 * rpm + rng.normal(0, 2.5, n)).round(2),
        "vibration_mm_s": (0.002 * rpm + rng.normal(1.0, 0.25, n)).round(3),
        "pressure_bar": rng.normal(5.0, 0.35, n).round(3),
        "rpm": rpm.round(0),
        "current_a": (0.004 * rpm + rng.normal(2.0, 0.4, n)).round(3),
    })


def _digits_df():
    from sklearn.datasets import load_digits

    d = load_digits()
    df = pd.DataFrame(d.data.astype(int), columns=[f"pixel_{i}" for i in range(64)])
    df.insert(0, "digit", d.target)
    return df


def _pneumonia_df():
    from medmnist import PneumoniaMNIST

    ds = PneumoniaMNIST(split="train", download=False, root=str(DATA_CACHE))
    rng = np.random.default_rng(0)
    idx = rng.choice(len(ds.imgs), size=min(800, len(ds.imgs)), replace=False)
    flat = ds.imgs[idx].reshape(len(idx), -1)
    df = pd.DataFrame(flat, columns=[f"pixel_{i}" for i in range(flat.shape[1])])
    df.insert(0, "label", ["pneumonia" if l else "normal" for l in ds.labels[idx].squeeze()])
    return df


def _cifar_df():
    from torchvision import datasets as tvd

    ds = tvd.CIFAR10(DATA_CACHE, train=True, download=False)
    rng = np.random.default_rng(0)
    idx = rng.choice(len(ds.data), size=400, replace=False)
    flat = ds.data[idx].reshape(len(idx), -1)
    classes = ["airplane", "automobile", "bird", "cat", "deer",
               "dog", "frog", "horse", "ship", "truck"]
    df = pd.DataFrame(flat, columns=[f"px_{i}" for i in range(flat.shape[1])])
    df.insert(0, "label", [classes[ds.targets[i]] for i in idx])
    return df


def _research_df():
    return pd.DataFrame(agents_data.RESEARCH_ARTICLES)[["title", "topic", "text"]]


def _handbook_df():
    return pd.DataFrame(agents_data.HANDBOOK_CHUNKS, columns=["section", "content"])


def _support_df():
    rows = [(t, intent) for intent, ts in agents_data.SUPPORT_TICKETS.items() for t in ts]
    return pd.DataFrame(rows, columns=["ticket", "intent"])


def _roles_df():
    rows = []
    for key, role in agents_data.JOB_ROLES.items():
        rows.append({"role": role["label"], "slug": key,
                     "must_have_skills": "; ".join(role["must_have"]),
                     "nice_to_have_skills": "; ".join(role["nice_to_have"]),
                     "min_years_experience": role["min_years"]})
    return pd.DataFrame(rows)


DATASETS = {
    "house-price-prediction": ("house_prices.csv", datasets.house_prices),
    "heart-disease-prediction": ("heart_disease.csv", datasets.heart_disease),
    "loan-approval-prediction": ("loan_approval.csv", datasets.loan_approval),
    "customer-churn-prediction": ("customer_churn.csv", datasets.churn),
    "customer-segmentation-kmeans": ("customers.csv", datasets.customers),
    "credit-card-fraud-detection": ("transactions.csv", datasets.fraud),
    "email-spam-classification-svm": ("emails.csv", lambda: _text_df(
        datasets.SPAM_EMAILS, datasets.HAM_EMAILS, "spam", "ham", "email", "label")),
    "text-classification-naive-bayes": ("sms_messages.csv", lambda: _text_df(
        datasets.SPAM_SMS, datasets.HAM_SMS, "spam", "ham", "message", "label")),
    "movie-recommendation-knn": ("movies.csv", _movies_df),
    "gene-expression-pca": ("gene_expression.csv", _gene_df),
    "handwritten-digit-recognition-ann": ("digits_8x8.csv", _digits_df),
    "image-classification-cnn": ("cifar10_sample_400.csv", _cifar_df),
    "sentiment-analysis-rnn-lstm": ("sentiment_reviews_binary.csv", lambda: _sentiment_df(2)),
    "sentiment-analysis-lstm-gru": ("sentiment_reviews_3class.csv", lambda: _sentiment_df(3)),
    "text-classification-transformers": ("news_headlines.csv", _topic_df),
    "anomaly-detection-autoencoders": ("sensor_readings_healthy.csv", _sensor_df),
    "pneumonia-detection-transfer-learning": ("pneumonia_xrays_sample_800.csv", _pneumonia_df),
    "ai-research-assistant": ("research_corpus.csv", _research_df),
    "multi-agent-workflow": ("research_corpus.csv", _research_df),
    "document-qa-rag-agent": ("employee_handbook.csv", _handbook_df),
    "customer-support-agent": ("support_tickets.csv", _support_df),
    "resume-screening-ai-agent": ("job_role_requirements.csv", _roles_df),
    "data-analysis-agent": ("sales_orders_2025.csv", agents_data.sales_data),
}


def has_dataset(slug: str) -> bool:
    return slug in DATASETS


def build(slug: str) -> tuple[str, str]:
    """Returns (filename, csv_text). Raises KeyError for unknown slugs."""
    filename, builder = DATASETS[slug]
    return filename, builder().to_csv(index=False)
