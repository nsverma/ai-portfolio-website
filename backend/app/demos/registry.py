"""Live-demo registry: maps project slugs to an input schema and a predict fn.

Every predict fn returns a uniform result shape the frontend can render:
    {
      "headline": str,            # the main result line
      "confidence": float | None, # 0-1 when the model outputs a probability
      "tone": "good" | "bad" | "neutral" | "info",
      "details": [{"label": str, "value": str}, ...],
    }
"""

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.demos import datasets

ARTIFACTS = Path(__file__).parent / "artifacts"


@lru_cache(maxsize=None)
def _load(name: str):
    path = ARTIFACTS / f"{name}.joblib"
    if not path.exists():
        raise FileNotFoundError(
            f"Demo artifact '{name}' missing — run `python -m app.demos.train` from backend/."
        )
    return joblib.load(path)


def _num(fields, name, label, mn, mx, step, default, help=None):
    fields.append(
        {"name": name, "label": label, "type": "number", "min": mn, "max": mx,
         "step": step, "default": default, "help": help}
    )


def _select(fields, name, label, options, default, help=None):
    fields.append(
        {"name": name, "label": label, "type": "select", "options": options,
         "default": default, "help": help}
    )


# ---------------------------------------------------------------- house price
def _house_fields():
    f = []
    _num(f, "area_sqft", "Area (sq ft)", 300, 5000, 50, 1500)
    _num(f, "bedrooms", "Bedrooms", 1, 6, 1, 3)
    _num(f, "bathrooms", "Bathrooms", 1, 4, 1, 2)
    _num(f, "age_years", "Property age (years)", 0, 50, 1, 10)
    _select(f, "location_tier", "Location", [
        {"value": 0, "label": "Average area"},
        {"value": 1, "label": "Good area"},
        {"value": 2, "label": "Prime area"},
    ], 1)
    _select(f, "garage", "Garage", [
        {"value": 0, "label": "No"}, {"value": 1, "label": "Yes"},
    ], 1)
    return f


def _house_predict(inputs):
    row = pd.DataFrame([{k: float(inputs[k]) for k in
                         ["area_sqft", "bedrooms", "bathrooms", "age_years", "location_tier", "garage"]}])
    price = float(_load("house_price").predict(row)[0])
    per_sqft = price / float(inputs["area_sqft"])
    return {
        "headline": f"Estimated price: ${price:,.0f}",
        "confidence": None,
        "tone": "info",
        "details": [
            {"label": "Price per sq ft", "value": f"${per_sqft:,.0f}"},
            {"label": "Model", "value": "Linear Regression"},
        ],
    }


# ------------------------------------------------------------- heart disease
def _heart_fields():
    f = []
    _num(f, "age", "Age", 20, 90, 1, 50)
    _select(f, "sex_male", "Sex", [
        {"value": 1, "label": "Male"}, {"value": 0, "label": "Female"},
    ], 1)
    _select(f, "chest_pain_level", "Chest pain", [
        {"value": 0, "label": "None"},
        {"value": 1, "label": "Mild (atypical)"},
        {"value": 2, "label": "Moderate (non-anginal)"},
        {"value": 3, "label": "Severe / typical angina"},
    ], 0)
    _num(f, "resting_bp", "Resting blood pressure (mmHg)", 90, 200, 1, 130)
    _num(f, "cholesterol", "Cholesterol (mg/dL)", 120, 570, 1, 240)
    _num(f, "max_heart_rate", "Max heart rate achieved", 70, 210, 1, 150)
    _select(f, "exercise_angina", "Chest pain during exercise", [
        {"value": 0, "label": "No"}, {"value": 1, "label": "Yes"},
    ], 0)
    _select(f, "fasting_blood_sugar_high", "Fasting blood sugar > 120 mg/dL", [
        {"value": 0, "label": "No"}, {"value": 1, "label": "Yes"},
    ], 0)
    return f


def _heart_predict(inputs):
    cols = ["age", "sex_male", "chest_pain_level", "resting_bp", "cholesterol",
            "max_heart_rate", "exercise_angina", "fasting_blood_sugar_high"]
    row = pd.DataFrame([{k: float(inputs[k]) for k in cols}])
    p = float(_load("heart_disease").predict_proba(row)[0, 1])
    risk = "High" if p >= 0.6 else "Moderate" if p >= 0.3 else "Low"
    return {
        "headline": f"{risk} risk of heart disease ({p:.0%})",
        "confidence": p,
        "tone": "bad" if p >= 0.6 else "neutral" if p >= 0.3 else "good",
        "details": [
            {"label": "Model", "value": "Logistic Regression"},
            {"label": "Note", "value": "Educational demo — not medical advice."},
        ],
    }


# -------------------------------------------------------------- loan approval
def _loan_fields():
    f = []
    _num(f, "income", "Annual income ($)", 10000, 300000, 1000, 60000)
    _num(f, "loan_amount", "Loan amount ($)", 1000, 500000, 1000, 150000)
    _num(f, "credit_score", "Credit score", 300, 850, 5, 700)
    _num(f, "employment_years", "Years employed", 0, 40, 1, 5)
    _num(f, "existing_debt", "Existing annual debt payments ($)", 0, 150000, 500, 8000)
    _select(f, "education_graduate", "Education", [
        {"value": 1, "label": "Graduate"}, {"value": 0, "label": "Not graduate"},
    ], 1)
    return f


def _loan_predict(inputs):
    cols = ["income", "loan_amount", "credit_score", "employment_years",
            "existing_debt", "education_graduate"]
    row = pd.DataFrame([{k: float(inputs[k]) for k in cols}])
    model = _load("loan_approval")
    p = float(model.predict_proba(row)[0, 1])
    approved = p >= 0.5
    return {
        "headline": "Loan likely APPROVED" if approved else "Loan likely REJECTED",
        "confidence": p if approved else 1 - p,
        "tone": "good" if approved else "bad",
        "details": [
            {"label": "Approval probability", "value": f"{p:.0%}"},
            {"label": "Model", "value": "Decision Tree (depth 5)"},
        ],
    }


# ---------------------------------------------------------------------- churn
def _churn_fields():
    f = []
    _num(f, "tenure_months", "Tenure (months)", 0, 72, 1, 12)
    _select(f, "contract", "Contract", [
        {"value": "Month-to-month", "label": "Month-to-month"},
        {"value": "One year", "label": "One year"},
        {"value": "Two year", "label": "Two year"},
    ], "Month-to-month")
    _num(f, "monthly_charges", "Monthly charges ($)", 20, 120, 1, 70)
    _select(f, "internet_service", "Internet service", [
        {"value": "DSL", "label": "DSL"},
        {"value": "Fiber optic", "label": "Fiber optic"},
        {"value": "No internet", "label": "No internet"},
    ], "Fiber optic")
    _select(f, "tech_support", "Tech support subscribed", [
        {"value": 0, "label": "No"}, {"value": 1, "label": "Yes"},
    ], 0)
    _select(f, "payment_method", "Payment method", [
        {"value": "Electronic check", "label": "Electronic check"},
        {"value": "Mailed check", "label": "Mailed check"},
        {"value": "Bank transfer", "label": "Bank transfer"},
        {"value": "Credit card", "label": "Credit card"},
    ], "Electronic check")
    return f


def _churn_predict(inputs):
    row = pd.DataFrame([{
        "tenure_months": float(inputs["tenure_months"]),
        "contract": str(inputs["contract"]),
        "monthly_charges": float(inputs["monthly_charges"]),
        "internet_service": str(inputs["internet_service"]),
        "tech_support": float(inputs["tech_support"]),
        "payment_method": str(inputs["payment_method"]),
    }])
    p = float(_load("churn").predict_proba(row)[0, 1])
    risk = "high" if p >= 0.6 else "medium" if p >= 0.3 else "low"
    return {
        "headline": f"Churn risk: {risk.upper()} ({p:.0%})",
        "confidence": p,
        "tone": "bad" if risk == "high" else "neutral" if risk == "medium" else "good",
        "details": [
            {"label": "Model", "value": "Random Forest (200 trees)"},
            {"label": "Suggested action", "value": {
                "high": "Offer a contract upgrade discount now.",
                "medium": "Add to the nurture campaign.",
                "low": "No action needed.",
            }[risk]},
        ],
    }


# --------------------------------------------------------------- segmentation
def _segment_fields():
    f = []
    _num(f, "annual_income_k", "Annual income ($k)", 12, 200, 1, 60)
    _num(f, "spending_score", "Spending score (1–100)", 1, 100, 1, 50)
    _num(f, "age", "Age", 18, 80, 1, 35)
    _num(f, "visits_per_month", "Store visits per month", 0, 30, 1, 4)
    return f


def _segment_predict(inputs):
    art = _load("segmentation")
    row = pd.DataFrame([{k: float(inputs[k]) for k in
                         ["annual_income_k", "spending_score", "age", "visits_per_month"]}])
    cluster = int(art["kmeans"].predict(art["scaler"].transform(row))[0])
    persona = datasets.SEGMENT_PERSONAS[art["mapping"][cluster]]
    return {
        "headline": f"Segment: {persona['name']}",
        "confidence": None,
        "tone": "info",
        "details": [
            {"label": "Profile", "value": persona["description"]},
            {"label": "Model", "value": "K-Means (4 clusters)"},
        ],
    }


# ---------------------------------------------------------------------- fraud
def _fraud_fields():
    f = []
    _num(f, "amount", "Transaction amount ($)", 1, 5000, 1, 120)
    _num(f, "distance_from_home_km", "Distance from home (km)", 0, 5000, 1, 10)
    _num(f, "ratio_to_median_purchase", "Ratio to your median purchase", 0.05, 40, 0.05, 1.0,)
    _select(f, "repeat_retailer", "Retailer used before", [
        {"value": 1, "label": "Yes"}, {"value": 0, "label": "No"},
    ], 1)
    _select(f, "used_chip", "Chip used", [
        {"value": 1, "label": "Yes"}, {"value": 0, "label": "No"},
    ], 1)
    _select(f, "used_pin", "PIN entered", [
        {"value": 1, "label": "Yes"}, {"value": 0, "label": "No"},
    ], 0)
    _select(f, "online_order", "Online order", [
        {"value": 0, "label": "No"}, {"value": 1, "label": "Yes"},
    ], 0)
    return f


def _fraud_predict(inputs):
    cols = ["amount", "distance_from_home_km", "ratio_to_median_purchase",
            "repeat_retailer", "used_chip", "used_pin", "online_order"]
    row = pd.DataFrame([{k: float(inputs[k]) for k in cols}])
    p = float(_load("fraud").predict_proba(row)[0, 1])
    flag = p >= 0.5
    return {
        "headline": "⚠️ Transaction flagged as FRAUD" if flag else "Transaction looks legitimate",
        "confidence": p if flag else 1 - p,
        "tone": "bad" if flag else "good",
        "details": [
            {"label": "Fraud probability", "value": f"{p:.1%}"},
            {"label": "Model", "value": "Gradient Boosting"},
        ],
    }


# ------------------------------------------------------------------- spam SVM
def _spam_fields():
    return [{
        "name": "text", "label": "Email text", "type": "textarea",
        "default": "Congratulations! You won a free iPhone. Click here to claim your prize now!",
        "help": "Paste any email text and the SVM will classify it.",
    }]


def _spam_predict(inputs):
    text = str(inputs.get("text", "")).strip()
    if not text:
        raise ValueError("Please enter some email text.")
    p = float(_load("spam_svm").predict_proba([text])[0, 1])
    spam = p >= 0.5
    return {
        "headline": "SPAM 🚫" if spam else "Not spam ✅",
        "confidence": p if spam else 1 - p,
        "tone": "bad" if spam else "good",
        "details": [
            {"label": "Spam probability", "value": f"{p:.0%}"},
            {"label": "Model", "value": "Linear SVM + TF-IDF (calibrated)"},
        ],
    }


# ------------------------------------------------------------------ movie KNN
def _movie_fields():
    options = [{"value": i, "label": f"{t} ({y})"} for i, (t, y, _, _) in enumerate(datasets.MOVIES)]
    return [{
        "name": "movie", "label": "Pick a movie you like", "type": "select",
        "options": options, "default": 1,
    }]


def _movie_predict(inputs):
    idx = int(inputs["movie"])
    art = _load("movie_knn")
    _, indices = art["nn"].kneighbors(art["features"][idx : idx + 1])
    title, year, _, genres = datasets.MOVIES[idx]
    details = []
    for rank, j in enumerate([j for j in indices[0] if j != idx][:5], start=1):
        t, y, r, g = datasets.MOVIES[j]
        genre_str = ", ".join(n for n, flag in zip(datasets.GENRE_NAMES, g) if flag)
        details.append({"label": f"#{rank}  {t} ({y})", "value": f"⭐ {r} · {genre_str}"})
    return {
        "headline": f"Because you liked {title}",
        "confidence": None,
        "tone": "info",
        "details": details,
    }


# --------------------------------------------------------------------- SMS NB
def _sms_fields():
    return [{
        "name": "text", "label": "SMS message", "type": "textarea",
        "default": "WINNER!! You won a cash prize of 2 lakh. SMS CLAIM to 56789 now",
        "help": "Naive Bayes with word counts — try a normal message too.",
    }]


def _sms_predict(inputs):
    text = str(inputs.get("text", "")).strip()
    if not text:
        raise ValueError("Please enter a message.")
    p = float(_load("sms_nb").predict_proba([text])[0, 1])
    spam = p >= 0.5
    return {
        "headline": "SPAM 🚫" if spam else "Legitimate message ✅",
        "confidence": p if spam else 1 - p,
        "tone": "bad" if spam else "good",
        "details": [
            {"label": "Spam probability", "value": f"{p:.0%}"},
            {"label": "Model", "value": "Multinomial Naive Bayes + bag-of-words"},
        ],
    }


# ------------------------------------------------------------------- gene PCA
def _pca_fields():
    return [{
        "name": "n_components", "label": "Number of principal components", "type": "number",
        "min": 1, "max": 20, "step": 1, "default": 2,
        "help": "The dataset has 50 genes. How much variance do the top components capture?",
    }]


def _pca_predict(inputs):
    n = max(1, min(20, int(inputs["n_components"])))
    art = _load("gene_pca")
    evr = art["explained_variance_ratio"]
    cum = float(np.cumsum(evr)[n - 1])
    need_90 = int(np.searchsorted(np.cumsum(evr), 0.9) + 1)
    details = [
        {"label": f"PC{i + 1}", "value": f"{evr[i]:.1%} of variance"} for i in range(min(n, 5))
    ]
    details.append({"label": "Components for 90% variance", "value": str(need_90)})
    details.append({"label": "Dataset", "value": f"{art['n_genes']} genes, 3 tissue types"})
    return {
        "headline": f"Top {n} component{'s' if n > 1 else ''} explain {cum:.1%} of variance",
        "confidence": cum,
        "tone": "info",
        "details": details,
    }


# ----------------------------------------------------------------- digits ANN
def _digits_fields():
    return [{
        "name": "pixels", "label": "Draw a digit (0–9)", "type": "digit_canvas",
        "help": "Draw with your mouse or finger, then classify.",
    }]


def _digits_predict(inputs):
    pixels = inputs.get("pixels")
    if not isinstance(pixels, list) or len(pixels) != 64:
        raise ValueError("Expected 64 pixel values (8×8 grid).")
    arr = np.clip(np.array(pixels, dtype=float), 0, 16).reshape(1, -1) / 16.0
    if arr.sum() == 0:
        raise ValueError("The canvas is empty — draw a digit first.")
    model = _load("digits_ann")
    proba = model.predict_proba(arr)[0]
    top = np.argsort(proba)[::-1][:3]
    return {
        "headline": f"That looks like a {top[0]}",
        "confidence": float(proba[top[0]]),
        "tone": "info",
        "details": [
            {"label": f"Guess #{i + 1}: digit {d}", "value": f"{proba[d]:.0%}"}
            for i, d in enumerate(top)
        ] + [{"label": "Model", "value": "MLP neural network (64 hidden units), trained on sklearn digits"}],
    }


# ===================================================== deep-learning demos
def _torch_predict_text(artifact_name, text):
    import torch

    from app.demos.torch_models import encode, load_model

    art = _load(artifact_name)
    model = load_model(art["model"])
    x = torch.tensor([encode(text, art["vocab"])], dtype=torch.long)
    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1)[0]
    return art["classes"], probs.tolist()


def _sentiment_rnn_fields():
    return [{
        "name": "text", "label": "Movie review", "type": "textarea",
        "default": "the acting was absolutely wonderful and the story was gripping",
        "help": "A vanilla RNN reads your words in order — try adding a 'not'.",
    }]


def _sentiment_rnn_predict(inputs):
    text = str(inputs.get("text", "")).strip()
    if not text:
        raise ValueError("Please enter a review.")
    classes, probs = _torch_predict_text("sentiment_rnn", text)
    top = int(np.argmax(probs))
    positive = classes[top] == "positive"
    return {
        "headline": f"Sentiment: {classes[top].upper()} ({probs[top]:.0%})",
        "confidence": probs[top],
        "tone": "good" if positive else "bad",
        "details": [
            {"label": "Positive", "value": f"{probs[classes.index('positive')]:.0%}"},
            {"label": "Negative", "value": f"{probs[classes.index('negative')]:.0%}"},
            {"label": "Model", "value": "Vanilla RNN (PyTorch), word embeddings, trained from scratch"},
        ],
    }


def _sentiment_lstm_fields():
    return [{
        "name": "text", "label": "Product / movie review", "type": "textarea",
        "default": "the plot was okay, nothing special but watchable",
        "help": "An LSTM with a 3-way head: negative / neutral / positive.",
    }]


def _sentiment_lstm_predict(inputs):
    text = str(inputs.get("text", "")).strip()
    if not text:
        raise ValueError("Please enter a review.")
    classes, probs = _torch_predict_text("sentiment_lstm", text)
    top = int(np.argmax(probs))
    tone = {"positive": "good", "negative": "bad", "neutral": "neutral"}[classes[top]]
    return {
        "headline": f"Sentiment: {classes[top].upper()} ({probs[top]:.0%})",
        "confidence": probs[top],
        "tone": tone,
        "details": [
            {"label": c.capitalize(), "value": f"{p:.0%}"} for c, p in zip(classes, probs)
        ] + [{"label": "Model", "value": "LSTM (PyTorch), trained from scratch"}],
    }


def _topic_fields():
    return [{
        "name": "text", "label": "News headline", "type": "textarea",
        "default": "startup raises funding at billion dollar valuation",
        "help": "A small Transformer encoder classifies the headline into 4 topics.",
    }]


def _topic_predict(inputs):
    text = str(inputs.get("text", "")).strip()
    if not text:
        raise ValueError("Please enter a headline.")
    classes, probs = _torch_predict_text("topic_transformer", text)
    order = np.argsort(probs)[::-1]
    top = int(order[0])
    return {
        "headline": f"Topic: {classes[top].upper()} ({probs[top]:.0%})",
        "confidence": probs[top],
        "tone": "info",
        "details": [
            {"label": classes[i].capitalize(), "value": f"{probs[i]:.0%}"} for i in order
        ] + [{"label": "Model", "value": "Transformer encoder (2 layers, 4 heads), trained from scratch in PyTorch"}],
    }


def _autoencoder_fields():
    f = []
    _num(f, "temperature", "Temperature (°C)", 40, 120, 0.5, 75)
    _num(f, "vibration", "Vibration (mm/s)", 0, 15, 0.1, 4.0)
    _num(f, "pressure", "Pressure (bar)", 2, 8, 0.1, 5.0)
    _num(f, "rpm", "Motor speed (RPM)", 500, 3000, 10, 1500)
    _num(f, "current", "Motor current (A)", 0, 20, 0.1, 8.0)
    return f


def _autoencoder_predict(inputs):
    art = _load("sensor_autoencoder")
    row = np.array([[float(inputs[k]) for k in
                     ["temperature", "vibration", "pressure", "rpm", "current"]]])
    xs = art["scaler"].transform(row)
    error = float(((art["model"].predict(xs) - xs) ** 2).mean())
    ratio = error / art["threshold"]
    anomaly = ratio > 1.0
    return {
        "headline": "⚠️ ANOMALY detected — machine needs inspection" if anomaly
        else "Readings look normal",
        "confidence": min(ratio / 2, 1.0) if anomaly else None,
        "tone": "bad" if anomaly else "good",
        "details": [
            {"label": "Reconstruction error", "value": f"{error:.4f}"},
            {"label": "Anomaly threshold", "value": f"{art['threshold']:.4f}"},
            {"label": "Error vs threshold", "value": f"{ratio:.1f}×"},
            {"label": "Model", "value": "Autoencoder (8→3→8 bottleneck) trained on healthy readings only"},
        ],
    }


def _image_choice_fields(artifact_name, label):
    art = _load(artifact_name)
    options = [
        {"value": i, "label": f"Sample {i + 1}", "image": s["image"]}
        for i, s in enumerate(art["samples"])
    ]
    return [{"name": "sample", "label": label, "type": "image_choice",
             "options": options, "default": 0}]


def _image_predict(artifact_name, inputs, normalize=None):
    import torch

    from app.demos.torch_models import load_model

    art = _load(artifact_name)
    idx = int(inputs["sample"])
    if not 0 <= idx < len(art["samples"]):
        raise ValueError("Pick one of the sample images.")
    sample = art["samples"][idx]
    pixels = np.array(sample["pixels"], dtype=np.float32)
    if normalize == "cifar":
        x = (pixels / 255.0 - np.array(art["mean"], dtype=np.float32)) / np.array(art["std"], dtype=np.float32)
        x = torch.tensor(x.transpose(2, 0, 1)).unsqueeze(0)
    else:  # grayscale 28x28
        x = torch.tensor(pixels / 255.0).unsqueeze(0).unsqueeze(0)
    model = load_model(art["model"])
    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1)[0].tolist()
    return art["classes"], probs, sample["true_label"]


def _cifar_fields():
    return _image_choice_fields("cifar_cnn", "Pick a test image (the model has never seen these)")


def _cifar_predict(inputs):
    classes, probs, true_label = _image_predict("cifar_cnn", inputs, normalize="cifar")
    order = np.argsort(probs)[::-1][:3]
    predicted = classes[int(order[0])]
    correct = predicted == true_label
    return {
        "headline": f"CNN says: {predicted} ({probs[int(order[0])]:.0%})",
        "confidence": probs[int(order[0])],
        "tone": "good" if correct else "bad",
        "details": [
            {"label": "Actual label", "value": f"{true_label} — {'correct ✅' if correct else 'wrong ❌'}"},
        ] + [
            {"label": f"Guess #{r + 1}: {classes[int(i)]}", "value": f"{probs[int(i)]:.0%}"}
            for r, i in enumerate(order)
        ] + [{"label": "Model", "value": "4-layer CNN trained on CIFAR-10 (50,000 images)"}],
    }


def _pneumonia_fields():
    return _image_choice_fields("pneumonia_cnn", "Pick a chest X-ray from the test set")


def _pneumonia_predict(inputs):
    classes, probs, true_label = _image_predict("pneumonia_cnn", inputs)
    top = int(np.argmax(probs))
    predicted = classes[top]
    correct = predicted == true_label
    return {
        "headline": f"Diagnosis: {predicted.upper()} ({probs[top]:.0%})",
        "confidence": probs[top],
        "tone": "good" if correct else "bad",
        "details": [
            {"label": "Actual label", "value": f"{true_label} — {'correct ✅' if correct else 'wrong ❌'}"},
            {"label": "Pneumonia probability", "value": f"{probs[classes.index('pneumonia')]:.0%}"},
            {"label": "Dataset", "value": "PneumoniaMNIST — real chest X-rays (5,856 images)"},
            {"label": "Note", "value": "Educational demo — not medical advice."},
        ],
    }


DEMOS = {
    "house-price-prediction": {
        "title": "Try it: estimate a house price",
        "cta": "Estimate price",
        "fields": _house_fields, "predict": _house_predict,
    },
    "heart-disease-prediction": {
        "title": "Try it: assess heart disease risk",
        "cta": "Assess risk",
        "fields": _heart_fields, "predict": _heart_predict,
    },
    "loan-approval-prediction": {
        "title": "Try it: will this loan be approved?",
        "cta": "Check approval",
        "fields": _loan_fields, "predict": _loan_predict,
    },
    "customer-churn-prediction": {
        "title": "Try it: will this customer churn?",
        "cta": "Predict churn",
        "fields": _churn_fields, "predict": _churn_predict,
    },
    "customer-segmentation-kmeans": {
        "title": "Try it: which segment is this customer?",
        "cta": "Find segment",
        "fields": _segment_fields, "predict": _segment_predict,
    },
    "credit-card-fraud-detection": {
        "title": "Try it: is this transaction fraudulent?",
        "cta": "Check transaction",
        "fields": _fraud_fields, "predict": _fraud_predict,
    },
    "email-spam-classification-svm": {
        "title": "Try it: classify an email",
        "cta": "Classify",
        "fields": _spam_fields, "predict": _spam_predict,
    },
    "movie-recommendation-knn": {
        "title": "Try it: get movie recommendations",
        "cta": "Recommend",
        "fields": _movie_fields, "predict": _movie_predict,
    },
    "text-classification-naive-bayes": {
        "title": "Try it: classify an SMS",
        "cta": "Classify",
        "fields": _sms_fields, "predict": _sms_predict,
    },
    "gene-expression-pca": {
        "title": "Try it: how many components do you need?",
        "cta": "Compute",
        "fields": _pca_fields, "predict": _pca_predict,
    },
    "handwritten-digit-recognition-ann": {
        "title": "Try it: draw a digit and let the network guess",
        "cta": "Classify digit",
        "fields": _digits_fields, "predict": _digits_predict,
    },
    "image-classification-cnn": {
        "title": "Try it: classify a CIFAR-10 test image",
        "cta": "Classify image",
        "fields": _cifar_fields, "predict": _cifar_predict,
    },
    "sentiment-analysis-rnn-lstm": {
        "title": "Try it: RNN sentiment analysis",
        "cta": "Analyze sentiment",
        "fields": _sentiment_rnn_fields, "predict": _sentiment_rnn_predict,
    },
    "sentiment-analysis-lstm-gru": {
        "title": "Try it: LSTM sentiment (negative / neutral / positive)",
        "cta": "Analyze sentiment",
        "fields": _sentiment_lstm_fields, "predict": _sentiment_lstm_predict,
    },
    "text-classification-transformers": {
        "title": "Try it: classify a headline with a Transformer",
        "cta": "Classify topic",
        "fields": _topic_fields, "predict": _topic_predict,
    },
    "anomaly-detection-autoencoders": {
        "title": "Try it: is this machine healthy?",
        "cta": "Check readings",
        "fields": _autoencoder_fields, "predict": _autoencoder_predict,
    },
    "pneumonia-detection-transfer-learning": {
        "title": "Try it: diagnose a chest X-ray",
        "cta": "Diagnose",
        "fields": _pneumonia_fields, "predict": _pneumonia_predict,
    },
}


def get_schema(slug: str) -> dict | None:
    demo = DEMOS.get(slug)
    if not demo:
        return None
    try:
        fields = demo["fields"]()
    except FileNotFoundError:
        # Artifact not trained yet — hide the demo instead of breaking the page.
        return None
    return {"slug": slug, "title": demo["title"], "cta": demo["cta"], "fields": fields}


def run_predict(slug: str, inputs: dict) -> dict:
    demo = DEMOS.get(slug)
    if not demo:
        raise KeyError(slug)
    return demo["predict"](inputs)
