"""Build the artifacts backing the AI-agent demos.

Run from backend/:
    ./venv/bin/python -m app.demos.train_agents
"""

import re
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline

from app.demos import agents_data

ARTIFACTS = Path(__file__).parent / "artifacts"
BACKEND_ROOT = Path(__file__).parents[2]
FRONTEND_SRC = BACKEND_ROOT.parent / "frontend" / "src"


def _save(name, obj):
    joblib.dump(obj, ARTIFACTS / f"{name}.joblib")
    print(f"saved {name}")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?]) +", text) if len(s.strip()) > 20]


def build_research_index():
    """Sentence-level TF-IDF index over the research corpus."""
    entries = []
    for art in agents_data.RESEARCH_ARTICLES:
        for sent in _sentences(art["text"]):
            entries.append({"title": art["title"], "topic": art["topic"], "sentence": sent})
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
    matrix = vec.fit_transform(e["sentence"] for e in entries)
    print(f"  research index: {len(entries)} sentences from {len(agents_data.RESEARCH_ARTICLES)} articles")
    _save("research_index", {"vectorizer": vec, "matrix": matrix, "entries": entries})


def build_handbook_index():
    """Chunk-level TF-IDF index over the employee handbook."""
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
    texts = [f"{title}. {body}" for title, body in agents_data.HANDBOOK_CHUNKS]
    matrix = vec.fit_transform(texts)
    print(f"  handbook index: {len(texts)} chunks")
    _save("handbook_index", {"vectorizer": vec, "matrix": matrix,
                             "chunks": agents_data.HANDBOOK_CHUNKS})


def build_codebase_index():
    """Index this very repository's source code for the code-RAG demo."""
    chunks = []
    patterns = [
        (BACKEND_ROOT / "app", "**/*.py"),
        (FRONTEND_SRC, "**/*.jsx"),
        (FRONTEND_SRC, "**/*.js"),
    ]
    for root, pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if "data_cache" in str(path) or "__pycache__" in str(path):
                continue
            lines = path.read_text(errors="ignore").splitlines()
            rel = str(path.relative_to(BACKEND_ROOT.parent))
            for start in range(0, len(lines), 30):
                block = lines[start:start + 40]
                text = "\n".join(block).strip()
                if len(text) > 80:
                    chunks.append({"file": rel, "start_line": start + 1,
                                   "end_line": min(start + 40, len(lines)), "text": text})
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                          token_pattern=r"[A-Za-z_][A-Za-z0-9_]+")
    matrix = vec.fit_transform(c["text"] for c in chunks)
    print(f"  codebase index: {len(chunks)} chunks")
    _save("codebase_index", {"vectorizer": vec, "matrix": matrix, "chunks": chunks})


def train_support_intent():
    texts, labels = [], []
    for intent, examples in agents_data.SUPPORT_TICKETS.items():
        texts += examples
        labels += [intent] * len(examples)
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    scores = cross_val_score(model, texts, labels, cv=5)
    model.fit(texts, labels)
    print(f"  support intent: 5-fold CV accuracy = {scores.mean():.3f}")
    _save("support_intent", model)


def build_sales_data():
    df = agents_data.sales_data()
    print(f"  sales data: {len(df)} orders, revenue total = {df.revenue.sum():,.0f}")
    _save("sales_data", df)


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    print("Building agent demo artifacts…")
    build_research_index()
    build_handbook_index()
    build_codebase_index()
    train_support_intent()
    build_sales_data()
    print("Done.")


if __name__ == "__main__":
    main()
