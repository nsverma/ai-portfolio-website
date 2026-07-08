"""Train every live-demo model and save the artifacts.

Run from backend/:
    ./venv/bin/python -m app.demos.train
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import NearestNeighbors
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from app.demos import datasets

ARTIFACTS = Path(__file__).parent / "artifacts"


def _save(name: str, obj) -> None:
    joblib.dump(obj, ARTIFACTS / f"{name}.joblib")
    print(f"saved {name}")


def _clf_report(name, model, X_test, y_test):
    proba = model.predict_proba(X_test)[:, 1]
    print(f"  {name}: test ROC-AUC = {roc_auc_score(y_test, proba):.3f}")


def train_house_price():
    df = datasets.house_prices()
    X, y = df.drop(columns="price"), df["price"]
    model = LinearRegression().fit(X, y)
    print(f"  house price: R^2 = {model.score(X, y):.3f}")
    _save("house_price", model)


def train_heart_disease():
    df = datasets.heart_disease()
    X, y = df.drop(columns="disease"), df["disease"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = Pipeline([("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))])
    model.fit(X_tr, y_tr)
    _clf_report("heart disease", model, X_te, y_te)
    _save("heart_disease", model)


def train_loan_approval():
    df = datasets.loan_approval()
    X, y = df.drop(columns="approved"), df["approved"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = DecisionTreeClassifier(max_depth=5, min_samples_leaf=25, random_state=42)
    model.fit(X_tr, y_tr)
    _clf_report("loan approval", model, X_te, y_te)
    _save("loan_approval", model)


def train_churn():
    df = datasets.churn()
    X, y = df.drop(columns="churned"), df["churned"]
    cat = ["contract", "internet_service", "payment_method"]
    num = ["tenure_months", "monthly_charges", "tech_support"]
    pre = ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore"), cat), ("num", "passthrough", num)]
    )
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = Pipeline(
        [
            ("pre", pre),
            ("clf", RandomForestClassifier(n_estimators=200, min_samples_leaf=10, random_state=42)),
        ]
    )
    model.fit(X_tr, y_tr)
    _clf_report("churn", model, X_te, y_te)
    _save("churn", model)


def train_segmentation():
    df = datasets.customers()
    scaler = StandardScaler().fit(df)
    km = KMeans(n_clusters=4, n_init=10, random_state=42).fit(scaler.transform(df))
    # Optimal one-to-one assignment of learned clusters to designed personas.
    from scipy.optimize import linear_sum_assignment

    centers = scaler.inverse_transform(km.cluster_centers_)
    persona_centers = np.array([p["center"] for p in datasets.SEGMENT_PERSONAS])
    cost = np.linalg.norm(centers[:, None, :] - persona_centers[None, :, :], axis=2)
    rows, cols = linear_sum_assignment(cost)
    mapping = {int(r): int(c) for r, c in zip(rows, cols)}
    print(f"  segmentation: cluster→persona mapping {mapping}")
    _save("segmentation", {"scaler": scaler, "kmeans": km, "mapping": mapping})


def train_fraud():
    df = datasets.fraud()
    X, y = df.drop(columns="fraud"), df["fraud"]
    print(f"  fraud: positive rate = {y.mean():.3f}")
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_tr, y_tr)
    _clf_report("fraud", model, X_te, y_te)
    _save("fraud", model)


def train_spam_svm():
    texts = datasets.SPAM_EMAILS + datasets.HAM_EMAILS
    labels = [1] * len(datasets.SPAM_EMAILS) + [0] * len(datasets.HAM_EMAILS)
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
            ("clf", CalibratedClassifierCV(LinearSVC(), cv=5)),
        ]
    )
    model.fit(texts, labels)
    print(f"  spam SVM: train acc = {model.score(texts, labels):.3f}")
    _save("spam_svm", model)


def train_sms_nb():
    texts = datasets.SPAM_SMS + datasets.HAM_SMS
    labels = [1] * len(datasets.SPAM_SMS) + [0] * len(datasets.HAM_SMS)
    model = Pipeline(
        [("count", CountVectorizer(ngram_range=(1, 2))), ("clf", MultinomialNB())]
    )
    model.fit(texts, labels)
    print(f"  SMS naive bayes: train acc = {model.score(texts, labels):.3f}")
    _save("sms_nb", model)


def train_movie_knn():
    feats = []
    for _, year, rating, genres in datasets.MOVIES:
        feats.append(genres + [(year - 1990) / 30, (rating - 7) / 2])
    X = np.array(feats, dtype=float)
    nn = NearestNeighbors(n_neighbors=6, metric="cosine").fit(X)
    _save("movie_knn", {"nn": nn, "features": X})


def train_pca():
    X, labels = datasets.gene_expression()
    pca = PCA(n_components=20, random_state=42).fit(X)
    coords = pca.transform(X)[:, :2]
    # Store a small per-group summary for the scatter description.
    summary = {}
    for lab in np.unique(labels):
        pts = coords[labels == lab]
        summary[str(lab)] = {
            "mean_pc1": float(pts[:, 0].mean()),
            "mean_pc2": float(pts[:, 1].mean()),
            "n": int(len(pts)),
        }
    _save(
        "gene_pca",
        {
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
            "n_genes": X.shape[1],
            "group_summary": summary,
        },
    )


def train_digits():
    from sklearn.datasets import load_digits

    digits = load_digits()
    X, y = digits.data / 16.0, digits.target
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = MLPClassifier(hidden_layer_sizes=(64,), max_iter=400, random_state=42)
    model.fit(X_tr, y_tr)
    print(f"  digits ANN: test acc = {model.score(X_te, y_te):.3f}")
    _save("digits_ann", model)


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    print("Training demo models…")
    train_house_price()
    train_heart_disease()
    train_loan_approval()
    train_churn()
    train_segmentation()
    train_fraud()
    train_spam_svm()
    train_sms_nb()
    train_movie_knn()
    train_pca()
    train_digits()
    print("Done.")


if __name__ == "__main__":
    main()
