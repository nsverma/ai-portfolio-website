"""Generate the evaluation / hyperparameter-tuning graph for every ML & DL demo.

Run from backend/ (after train, train_dl):
    ./venv/bin/python -m app.demos.train_evals

Writes dark-themed PNGs to artifacts/plots/{slug}.png plus captions.json.
"""

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import cross_val_predict, cross_val_score, train_test_split

from app.demos import datasets

ARTIFACTS = Path(__file__).parent / "artifacts"
PLOTS = ARTIFACTS / "plots"

BG = "#0d1226"
CYAN = "#22d3ee"
PURPLE = "#a78bfa"
BLUE = "#60a5fa"
ROSE = "#fb7185"
EMERALD = "#34d399"
GRID = "#2a3352"
TEXT = "#cbd5e1"

CAPTIONS = {}


def _load(name):
    return joblib.load(ARTIFACTS / f"{name}.joblib")


def _fig(title):
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=110)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_title(title, color="white", fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(colors=TEXT, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(color=GRID, linewidth=0.6, alpha=0.6)
    return fig, ax


def _style_ax(ax):
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)


def _finish(fig, ax, slug, caption, legend=True):
    _style_ax(ax)
    if legend and ax.get_legend_handles_labels()[0]:
        leg = ax.legend(facecolor=BG, edgecolor=GRID, labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOTS / f"{slug}.png", facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    CAPTIONS[slug] = caption
    print(f"  plotted {slug}")


# ------------------------------------------------------------------ classic ML
def plot_house():
    df = datasets.house_prices()
    X, y = df.drop(columns="price"), df["price"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    model = _load("house_price")
    pred = model.predict(X_te)
    r2 = model.score(X_te, y_te)
    fig, ax = _fig("Predicted vs actual sale price (held-out set)")
    ax.scatter(y_te / 1000, pred / 1000, s=10, alpha=0.45, color=CYAN, edgecolors="none")
    lims = [min(y_te.min(), pred.min()) / 1000, max(y_te.max(), pred.max()) / 1000]
    ax.plot(lims, lims, color=ROSE, linewidth=1.5, linestyle="--", label="perfect prediction")
    ax.set_xlabel("Actual price ($k)")
    ax.set_ylabel("Predicted price ($k)")
    ax.text(0.03, 0.92, f"R² = {r2:.3f}", transform=ax.transAxes, color=EMERALD, fontsize=11)
    _finish(fig, ax, "house-price-prediction",
            "Points hugging the diagonal mean accurate predictions. The linear model "
            f"explains {r2:.0%} of price variance on unseen homes.")


def plot_heart():
    from sklearn.metrics import roc_curve, roc_auc_score

    df = datasets.heart_disease()
    X, y = df.drop(columns="disease"), df["disease"]
    _, X_te, _, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    proba = _load("heart_disease").predict_proba(X_te)[:, 1]
    fpr, tpr, _ = roc_curve(y_te, proba)
    auc = roc_auc_score(y_te, proba)
    fig, ax = _fig("ROC curve — heart disease classifier")
    ax.plot(fpr, tpr, color=CYAN, linewidth=2, label=f"logistic regression (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], color=GRID, linestyle="--", linewidth=1.2, label="random guess (AUC = 0.5)")
    ax.fill_between(fpr, tpr, alpha=0.12, color=CYAN)
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    _finish(fig, ax, "heart-disease-prediction",
            f"The curve bows toward the top-left, giving ROC-AUC {auc:.2f} — the model ranks "
            "a random sick patient above a random healthy one that often.")


def plot_loan():
    from sklearn.metrics import roc_auc_score
    from sklearn.tree import DecisionTreeClassifier

    df = datasets.loan_approval()
    X, y = df.drop(columns="approved"), df["approved"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    depths = range(1, 13)
    train_auc, test_auc = [], []
    for d in depths:
        m = DecisionTreeClassifier(max_depth=d, min_samples_leaf=25, random_state=42).fit(X_tr, y_tr)
        train_auc.append(roc_auc_score(y_tr, m.predict_proba(X_tr)[:, 1]))
        test_auc.append(roc_auc_score(y_te, m.predict_proba(X_te)[:, 1]))
    fig, ax = _fig("Hyperparameter tuning — decision tree depth")
    ax.plot(depths, train_auc, "o-", color=PURPLE, linewidth=2, markersize=4, label="train AUC")
    ax.plot(depths, test_auc, "o-", color=CYAN, linewidth=2, markersize=4, label="validation AUC")
    best = int(np.argmax(test_auc)) + 1
    ax.axvline(best, color=EMERALD, linestyle="--", linewidth=1.2, label=f"chosen depth = {best}")
    ax.set_xlabel("max_depth")
    ax.set_ylabel("ROC-AUC")
    _finish(fig, ax, "loan-approval-prediction",
            "The classic overfitting picture: train AUC keeps climbing with depth while "
            f"validation AUC peaks at depth {best} and then decays as the tree memorizes noise.")


def plot_churn():
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder

    df = datasets.churn()
    X, y = df.drop(columns="churned"), df["churned"]
    cat = ["contract", "internet_service", "payment_method"]
    num = ["tenure_months", "monthly_charges", "tech_support"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    counts = [5, 10, 25, 50, 100, 200, 400]
    aucs = []
    for n in counts:
        pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), cat),
                                 ("num", "passthrough", num)])
        m = Pipeline([("pre", pre), ("clf", RandomForestClassifier(
            n_estimators=n, min_samples_leaf=10, random_state=42))]).fit(X_tr, y_tr)
        aucs.append(roc_auc_score(y_te, m.predict_proba(X_te)[:, 1]))
    fig, ax = _fig("Hyperparameter tuning — random forest size")
    ax.plot(counts, aucs, "o-", color=CYAN, linewidth=2, markersize=5)
    ax.axvline(200, color=EMERALD, linestyle="--", linewidth=1.2, label="chosen n_estimators = 200")
    ax.set_xscale("log")
    ax.set_xlabel("n_estimators (log scale)")
    ax.set_ylabel("Validation ROC-AUC")
    _finish(fig, ax, "customer-churn-prediction",
            "Validation AUC rises quickly up to ~50 trees, then flattens — after that, more "
            "trees only cost compute. 200 sits safely on the plateau.")


def plot_segmentation():
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    df = datasets.customers()
    art = _load("segmentation")
    Xs = art["scaler"].transform(df)
    ks = range(2, 10)
    inertia, silhouette = [], []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xs)
        inertia.append(km.inertia_)
        silhouette.append(silhouette_score(Xs, km.labels_))
    fig, ax = _fig("Choosing k — elbow method & silhouette score")
    ax.plot(ks, inertia, "o-", color=CYAN, linewidth=2, markersize=5, label="inertia (elbow)")
    ax.set_xlabel("number of clusters k")
    ax.set_ylabel("Inertia")
    ax2 = ax.twinx()
    ax2.plot(ks, silhouette, "o-", color=PURPLE, linewidth=2, markersize=5, label="silhouette")
    ax2.set_ylabel("Silhouette score", color=TEXT)
    ax2.tick_params(colors=TEXT, labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color(GRID)
    ax.axvline(4, color=EMERALD, linestyle="--", linewidth=1.2, label="chosen k = 4")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, facecolor=BG, edgecolor=GRID, labelcolor=TEXT, fontsize=9)
    _finish(fig, ax, "customer-segmentation-kmeans",
            "The inertia elbow and the silhouette peak agree: k = 4 clusters — matching the "
            "four customer personas the segmentation demo reports.", legend=False)


def plot_fraud():
    from sklearn.metrics import average_precision_score, precision_recall_curve

    df = datasets.fraud()
    X, y = df.drop(columns="fraud"), df["fraud"]
    _, X_te, _, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    proba = _load("fraud").predict_proba(X_te)[:, 1]
    prec, rec, _ = precision_recall_curve(y_te, proba)
    ap = average_precision_score(y_te, proba)
    fig, ax = _fig("Precision–recall curve — fraud detection (7% positives)")
    ax.plot(rec, prec, color=CYAN, linewidth=2, label=f"gradient boosting (AP = {ap:.3f})")
    ax.axhline(y_te.mean(), color=GRID, linestyle="--", linewidth=1.2,
               label=f"random guess (AP = {y_te.mean():.3f})")
    ax.fill_between(rec, prec, alpha=0.12, color=CYAN)
    ax.set_xlabel("Recall (share of fraud caught)")
    ax.set_ylabel("Precision (share of flags correct)")
    _finish(fig, ax, "credit-card-fraud-detection",
            "With only 7% fraud, accuracy would mislead — the PR curve shows the real trade-off. "
            f"Average precision {ap:.2f} vs {y_te.mean():.2f} for random guessing.")


def plot_spam_svm():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline
    from sklearn.svm import SVC

    texts = datasets.SPAM_EMAILS + datasets.HAM_EMAILS
    labels = [1] * len(datasets.SPAM_EMAILS) + [0] * len(datasets.HAM_EMAILS)
    Cs = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]
    means, stds = [], []
    for C in Cs:
        m = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
                      ("clf", SVC(kernel="linear", C=C))])
        scores = cross_val_score(m, texts, labels, cv=5)
        means.append(scores.mean())
        stds.append(scores.std())
    means, stds = np.array(means), np.array(stds)
    fig, ax = _fig("Hyperparameter tuning — SVM regularization C")
    ax.plot(Cs, means, "o-", color=CYAN, linewidth=2, markersize=5, label="5-fold CV accuracy")
    ax.fill_between(Cs, means - stds, means + stds, alpha=0.15, color=CYAN, label="± 1 std across folds")
    ax.set_xscale("log")
    best = Cs[int(np.argmax(means))]
    ax.axvline(best, color=EMERALD, linestyle="--", linewidth=1.2, label=f"best C = {best:g}")
    ax.set_xlabel("C (log scale)")
    ax.set_ylabel("CV accuracy")
    _finish(fig, ax, "email-spam-classification-svm",
            "Small C over-regularizes and underfits; accuracy climbs as C grows and plateaus — "
            "the margin/misclassification trade-off at the heart of SVMs.")


def plot_movie_knn():
    art = _load("movie_knn")
    X = art["features"]
    from sklearn.metrics.pairwise import cosine_similarity

    sim = cosine_similarity(X)
    np.fill_diagonal(sim, -1)
    ks = range(1, 11)
    avg_sim = [np.mean(np.sort(sim, axis=1)[:, -k:]) for k in ks]
    fig, ax = _fig("Choosing k — how similar are the k nearest movies?")
    ax.plot(ks, avg_sim, "o-", color=CYAN, linewidth=2, markersize=5, label="mean cosine similarity of top-k")
    ax.axvline(5, color=EMERALD, linestyle="--", linewidth=1.2, label="chosen k = 5")
    ax.set_xlabel("k (recommendations shown)")
    ax.set_ylabel("Avg similarity to query movie")
    _finish(fig, ax, "movie-recommendation-knn",
            "Recommendation quality decays as k grows — each extra neighbor is less similar to "
            "the query movie. k = 5 keeps recommendations tight without being trivial.")


def plot_sms_nb():
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics import confusion_matrix
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline

    texts = datasets.SPAM_SMS + datasets.HAM_SMS
    labels = np.array([1] * len(datasets.SPAM_SMS) + [0] * len(datasets.HAM_SMS))
    model = Pipeline([("count", CountVectorizer(ngram_range=(1, 2))), ("clf", MultinomialNB())])
    pred = cross_val_predict(model, texts, labels, cv=5)
    cm = confusion_matrix(labels, pred)
    fig, ax = _fig("Cross-validated confusion matrix — Naive Bayes")
    im = ax.imshow(cm, cmap="Purples")
    classes = ["ham", "spam"]
    ax.set_xticks([0, 1], [f"predicted {c}" for c in classes])
    ax.set_yticks([0, 1], [f"actual {c}" for c in classes])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=18,
                    color="white" if cm[i, j] > cm.max() / 2 else PURPLE, fontweight="bold")
    ax.grid(False)
    acc = (cm[0, 0] + cm[1, 1]) / cm.sum()
    _finish(fig, ax, "text-classification-naive-bayes",
            f"Out-of-fold predictions: {acc:.0%} accuracy. The off-diagonal cells are the "
            "mistakes — false alarms (top right) vs missed spam (bottom left).", legend=False)


def plot_pca():
    art = _load("gene_pca")
    evr = np.array(art["explained_variance_ratio"])
    cum = np.cumsum(evr)
    n = len(evr)
    fig, ax = _fig("Scree plot — variance explained per principal component")
    ax.bar(range(1, n + 1), evr, color=CYAN, alpha=0.8, label="per component")
    ax.plot(range(1, n + 1), cum, "o-", color=PURPLE, linewidth=2, markersize=4, label="cumulative")
    need = int(np.searchsorted(cum, 0.9) + 1)
    ax.axhline(0.9, color=EMERALD, linestyle="--", linewidth=1.2, label=f"90% at {need} components")
    ax.set_xlabel("Principal component")
    ax.set_ylabel("Explained variance ratio")
    _finish(fig, ax, "gene-expression-pca",
            f"The first few components dominate: {need} of 50 gene dimensions capture 90% of "
            "the variance — the compression PCA is prized for.")


def plot_digits():
    from sklearn.datasets import load_digits
    from sklearn.neural_network import MLPClassifier

    digits = load_digits()
    X, y = digits.data / 16.0, digits.target
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    sizes = [4, 8, 16, 32, 64, 128]
    train_acc, test_acc = [], []
    for h in sizes:
        m = MLPClassifier(hidden_layer_sizes=(h,), max_iter=400, random_state=42).fit(X_tr, y_tr)
        train_acc.append(m.score(X_tr, y_tr))
        test_acc.append(m.score(X_te, y_te))
    fig, ax = _fig("Hyperparameter tuning — hidden layer width (MLP)")
    ax.plot(sizes, train_acc, "o-", color=PURPLE, linewidth=2, markersize=5, label="train accuracy")
    ax.plot(sizes, test_acc, "o-", color=CYAN, linewidth=2, markersize=5, label="validation accuracy")
    ax.axvline(64, color=EMERALD, linestyle="--", linewidth=1.2, label="chosen width = 64")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Hidden units (log₂ scale)")
    ax.set_ylabel("Accuracy")
    _finish(fig, ax, "handwritten-digit-recognition-ann",
            "Capacity sweep: 4 hidden units underfit badly; validation accuracy saturates "
            "around 64 units — bigger buys nothing but parameters.")


def plot_autoencoder():
    art = _load("sensor_autoencoder")
    rng = np.random.default_rng(7)
    n = 4000
    rpm = rng.normal(1500, 150, n)
    healthy = np.column_stack([
        60 + 0.01 * rpm + rng.normal(0, 2.5, n),
        0.002 * rpm + rng.normal(1.0, 0.25, n),
        rng.normal(5.0, 0.35, n),
        rpm,
        0.004 * rpm + rng.normal(2.0, 0.4, n),
    ])
    Xs = art["scaler"].transform(healthy)
    errors = ((art["model"].predict(Xs) - Xs) ** 2).mean(axis=1)
    fig, ax = _fig("Reconstruction error distribution — healthy readings")
    ax.hist(errors, bins=60, color=CYAN, alpha=0.8, label="healthy sensor readings")
    ax.axvline(art["threshold"], color=ROSE, linewidth=2, linestyle="--",
               label=f"anomaly threshold (97.5th pct = {art['threshold']:.3f})")
    ax.set_xlabel("Reconstruction error (MSE, scaled space)")
    ax.set_ylabel("Count")
    ax.set_yscale("log")
    _finish(fig, ax, "anomaly-detection-autoencoders",
            "The autoencoder reconstructs healthy readings with tiny error; anything to the "
            "right of the dashed threshold is flagged as an anomaly.")


# -------------------------------------------------------- DL training curves
def _plot_history(slug, artifact, title, caption):
    art = _load(artifact)
    hist = art.get("history")
    if not hist or not hist.get("loss"):
        print(f"  ! no history in {artifact}, skipping {slug}")
        return
    epochs = range(1, len(hist["loss"]) + 1)
    fig, ax = _fig(title)
    ax.plot(epochs, hist["loss"], "o-", color=PURPLE, linewidth=2, markersize=5, label="training loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Training loss", color=TEXT)
    if hist.get("val_acc"):
        ax2 = ax.twinx()
        ax2.plot(epochs, hist["val_acc"], "o-", color=CYAN, linewidth=2, markersize=5,
                 label="validation accuracy")
        ax2.set_ylabel("Validation accuracy", color=TEXT)
        ax2.tick_params(colors=TEXT, labelsize=9)
        for spine in ax2.spines.values():
            spine.set_color(GRID)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, facecolor=BG, edgecolor=GRID, labelcolor=TEXT,
                  fontsize=9, loc="center right")
    _finish(fig, ax, slug, caption, legend=False)


def main():
    PLOTS.mkdir(exist_ok=True)
    print("Generating evaluation plots…")
    plot_house()
    plot_heart()
    plot_loan()
    plot_churn()
    plot_segmentation()
    plot_fraud()
    plot_spam_svm()
    plot_movie_knn()
    plot_sms_nb()
    plot_pca()
    plot_digits()
    plot_autoencoder()
    _plot_history("sentiment-analysis-rnn-lstm", "sentiment_rnn",
                  "Training curve — vanilla RNN sentiment classifier",
                  "Loss falls and validation accuracy climbs across 8 epochs — the RNN "
                  "gradually learns word order and negation patterns.")
    _plot_history("sentiment-analysis-lstm-gru", "sentiment_lstm",
                  "Training curve — LSTM sentiment classifier (3-class)",
                  "The LSTM converges faster and higher than the vanilla RNN on the same task — "
                  "its gates handle long-range dependencies like negation better.")
    _plot_history("text-classification-transformers", "topic_transformer",
                  "Training curve — Transformer topic classifier",
                  "The Transformer reaches near-perfect validation accuracy within a few "
                  "epochs — self-attention quickly locks onto topic-defining words.")
    _plot_history("image-classification-cnn", "cifar_cnn",
                  "Training curve — CNN on CIFAR-10 (50,000 images)",
                  "Six epochs of real training on CIFAR-10: loss drops steadily while held-out "
                  "accuracy climbs to ~75% — honest numbers for a small CNN without augmentation.")
    _plot_history("pneumonia-detection-transfer-learning", "pneumonia_cnn",
                  "Training curve — CNN on PneumoniaMNIST chest X-rays",
                  "Real medical imaging data: training loss decreases while validation accuracy "
                  "reaches ~87% on held-out X-rays.")
    with open(PLOTS / "captions.json", "w") as f:
        json.dump(CAPTIONS, f, indent=2)
    print(f"Done — {len(CAPTIONS)} plots + captions.json")


if __name__ == "__main__":
    main()
