"""Corpora and datasets backing the AI-agent demos.

Everything is embedded so the demos work offline and reproducibly.
"""

import numpy as np
import pandas as pd

# ------------------------------------------------------------ research corpus
RESEARCH_ARTICLES = [
    {
        "title": "Transformers and the Attention Revolution",
        "topic": "transformers",
        "text": (
            "The transformer architecture replaced recurrence with self-attention, letting models "
            "process all tokens in parallel. Attention computes a weighted sum over every position, "
            "so long-range dependencies no longer decay with distance. Training cost grows "
            "quadratically with sequence length, which motivated sparse and linear attention variants. "
            "Pre-training on large corpora followed by fine-tuning became the dominant recipe. "
            "Scaling laws showed that model quality improves predictably with parameters, data, and compute."
        ),
    },
    {
        "title": "Why Convolutional Networks See So Well",
        "topic": "cnn",
        "text": (
            "Convolutional networks exploit two priors about images: locality and translation invariance. "
            "Early layers learn edge and texture detectors while deeper layers compose them into object parts. "
            "Pooling layers grant a degree of spatial invariance and reduce computation. "
            "Residual connections solved the vanishing gradient problem and enabled networks hundreds of layers deep. "
            "Data augmentation such as random crops and flips remains one of the cheapest accuracy boosts available."
        ),
    },
    {
        "title": "Gradient Descent and Its Modern Variants",
        "topic": "optimization",
        "text": (
            "Stochastic gradient descent estimates the gradient from mini-batches, trading noise for speed. "
            "Momentum accumulates a velocity vector that damps oscillation in ravines of the loss surface. "
            "Adam combines momentum with per-parameter learning rates derived from second-moment estimates. "
            "Learning-rate warmup and cosine decay schedules stabilize the early and late phases of training. "
            "Sharp minima tend to generalize worse than flat ones, which motivates techniques like weight averaging."
        ),
    },
    {
        "title": "The Overfitting Problem and Regularization",
        "topic": "regularization",
        "text": (
            "A model overfits when it memorizes training noise instead of learning the underlying signal. "
            "L2 regularization penalizes large weights and is equivalent to a Gaussian prior on parameters. "
            "Dropout randomly disables units during training, forcing redundant representations. "
            "Early stopping halts training when validation loss stops improving, acting as implicit regularization. "
            "The most reliable cure for overfitting is still more diverse training data."
        ),
    },
    {
        "title": "Retrieval-Augmented Generation Explained",
        "topic": "rag",
        "text": (
            "Retrieval-augmented generation grounds a language model in external documents fetched at query time. "
            "A retriever scores document chunks against the query, and the top passages are placed in the prompt. "
            "Grounding reduces hallucination because the model can quote sources instead of inventing facts. "
            "Chunk size is a key tuning knob: too small loses context, too large dilutes relevance. "
            "Citations back to source passages make RAG systems auditable in a way plain generation is not."
        ),
    },
    {
        "title": "Reinforcement Learning from Human Feedback",
        "topic": "rlhf",
        "text": (
            "RLHF aligns language models with human preferences in three stages. "
            "First, supervised fine-tuning teaches the base model to follow instructions. "
            "Second, humans rank pairs of model outputs and a reward model learns those preferences. "
            "Third, reinforcement learning optimizes the policy against the reward model with a KL penalty "
            "keeping it close to the supervised baseline. The KL constraint prevents reward hacking where "
            "the policy exploits flaws in the learned reward."
        ),
    },
    {
        "title": "Word Embeddings: From One-Hot to Semantic Space",
        "topic": "embeddings",
        "text": (
            "One-hot vectors treat every word as equally distant from every other, discarding meaning. "
            "Word2vec learns dense vectors by predicting words from their neighbors, so similar words cluster. "
            "The famous king minus man plus woman equals queen arithmetic shows embeddings capture relations. "
            "Contextual embeddings from transformers give each occurrence of a word its own vector. "
            "Embedding similarity search underpins modern semantic retrieval and recommendation systems."
        ),
    },
    {
        "title": "Evaluating Machine Learning Models Honestly",
        "topic": "evaluation",
        "text": (
            "Accuracy misleads on imbalanced data because predicting the majority class scores well. "
            "Precision measures how many flagged items were correct while recall measures how many true items were found. "
            "ROC-AUC summarizes ranking quality across all thresholds and is robust to class imbalance. "
            "Data leakage, where information from the test set influences training, inflates every metric. "
            "A held-out test set must be touched exactly once, after all tuning decisions are frozen."
        ),
    },
]

# ---------------------------------------------------------- company handbook
HANDBOOK_CHUNKS = [
    ("Working hours", "Standard working hours are 9:30 AM to 6:30 PM, Monday to Friday. Teams may adopt flexible timing as long as members overlap between 11 AM and 4 PM. Core meetings are scheduled inside the overlap window."),
    ("Remote work policy", "Employees may work remotely up to three days per week. Fully remote arrangements require written approval from the department head. Remote employees must be reachable on chat during working hours."),
    ("Leave policy", "Every employee receives 24 days of paid leave per calendar year, plus 8 public holidays. Unused leave up to 10 days carries over to the next year. Leave requests longer than five consecutive days need two weeks notice."),
    ("Sick leave", "Sick leave is separate from paid leave and allows 12 days per year. A medical certificate is required for absences longer than two consecutive days. Unused sick leave does not carry over."),
    ("Expense reimbursement", "Business expenses must be submitted within 30 days with receipts through the expense portal. Meals during business travel are reimbursed up to 2000 rupees per day. Software purchases above 5000 rupees need manager pre-approval."),
    ("Travel policy", "Domestic flights should be booked in economy class at least seven days in advance. Hotel bookings are capped at 6000 rupees per night in metro cities and 4000 rupees elsewhere. Airport taxis are reimbursable with receipts."),
    ("Probation and confirmation", "New employees serve a probation period of three months, extendable once by three months. A confirmation review happens in the final week of probation. Notice period during probation is 15 days."),
    ("Notice period", "Confirmed employees have a notice period of 60 days. The company may waive part of the notice at its discretion. Unused paid leave is encashed in the final settlement."),
    ("Health insurance", "The company provides group health insurance of 5 lakh rupees covering the employee, spouse, and up to two children. Parents can be added under a voluntary top-up plan paid by the employee. Claims are processed by the insurance partner within 15 working days."),
    ("Learning budget", "Every employee has an annual learning budget of 25000 rupees for courses, books, and conferences. Requests are approved by the reporting manager. Certifications directly relevant to the current role are fully covered outside this budget."),
    ("Performance reviews", "Performance reviews happen twice a year, in April and October. Ratings follow a five-point scale calibrated across teams. Promotion cases are considered during the April cycle."),
    ("Referral bonus", "Employees receive a referral bonus of 50000 rupees for successful engineering hires and 25000 rupees for other roles. The bonus is paid after the referred candidate completes three months. Referrals of former employees are not eligible."),
    ("Equipment policy", "Every employee receives a laptop and one external monitor. Laptops are refreshed every three years. Lost or damaged equipment must be reported to IT within 24 hours."),
    ("Security policy", "Two-factor authentication is mandatory on all company accounts. Customer data must never be copied to personal devices. Suspected phishing emails should be reported to the security team immediately."),
]

# ------------------------------------------------------- support ticket corpus
SUPPORT_TICKETS = {
    "refund": [
        "I want my money back for order 4521, the product is defective",
        "Please process a refund, the item arrived broken",
        "How do I get a refund for my last purchase",
        "The product does not match the description, I need a refund",
        "Refund my payment, I was charged twice for the same order",
        "I returned the item last week but have not received my money",
        "Cancel my order 8832 and refund the amount",
        "The shoes are the wrong size and I want my money returned",
        "I am not satisfied with the quality, please refund order 1290",
        "Requesting a full refund as the package never worked properly",
    ],
    "shipping": [
        "Where is my order 7745, it was supposed to arrive yesterday",
        "My package has been stuck in transit for a week",
        "Can you update the delivery address for my order",
        "Track my shipment please, order number 3321",
        "The courier says delivered but I never received the package",
        "When will my order ship, I placed it five days ago",
        "My tracking number is not working on your website",
        "Can I change the delivery date for order 6610",
        "Package shows out for delivery for three days now",
        "How long does express shipping take to Mumbai",
    ],
    "account": [
        "I cannot log into my account, it says wrong password",
        "How do I reset my password",
        "Please delete my account and all my data",
        "My account got locked after too many login attempts",
        "I want to change the email address on my account",
        "Someone else may have accessed my account, please help",
        "Update my phone number in the account settings",
        "I am not receiving the verification email to sign up",
        "How do I enable two factor authentication on my profile",
        "Merge my two accounts into one please",
    ],
    "billing": [
        "Why was I charged a subscription fee this month",
        "My invoice shows the wrong amount for order 2214",
        "I need a GST invoice for my company purchase",
        "The discount code was not applied to my bill",
        "Explain the extra charge of 199 on my statement",
        "Can I change my payment method for the subscription",
        "My card was declined but the amount was still deducted",
        "Send me a copy of the invoice for order 9902",
        "I was billed after cancelling my subscription",
        "The EMI option was not applied at checkout",
    ],
    "technical": [
        "The app crashes every time I open the cart",
        "Your website shows a 500 error on the checkout page",
        "I cannot upload my profile picture, it keeps failing",
        "The search feature returns no results for anything",
        "Video playback keeps buffering even on fast internet",
        "The mobile app will not install on my phone",
        "Dark mode setting resets every time I restart the app",
        "Payment page freezes after I enter card details",
        "The desktop notifications stopped working since the update",
        "Images are not loading anywhere on the site",
    ],
}

SUPPORT_REPLIES = {
    "refund": "I've opened a refund request{order}. Refunds are processed to the original payment method within 5–7 business days once the return is confirmed.",
    "shipping": "I've checked the shipment status{order}. I'm escalating this to our logistics partner and you'll receive an updated tracking link within 24 hours.",
    "account": "I can help with your account. For security, I've sent a verification link to your registered email — follow it to complete this change.",
    "billing": "I've pulled up your billing history{order}. The charge details and a corrected invoice have been sent to your registered email.",
    "technical": "Thanks for reporting this. I've logged the issue with our engineering team{order}. Meanwhile, try clearing the app cache or using the latest version.",
}

# --------------------------------------------------------- resume screening
JOB_ROLES = {
    "ml-engineer": {
        "label": "Machine Learning Engineer",
        "must_have": ["python", "machine learning", "scikit-learn|sklearn", "sql"],
        "nice_to_have": ["pytorch|tensorflow", "deep learning", "docker", "aws|gcp|azure",
                          "fastapi|flask|django", "nlp|computer vision", "mlops|mlflow", "spark|hadoop"],
        "min_years": 2,
    },
    "frontend-developer": {
        "label": "Frontend Developer",
        "must_have": ["javascript|typescript", "react|vue|angular", "html", "css"],
        "nice_to_have": ["redux|zustand", "next.js|nextjs", "tailwind", "testing|jest|cypress",
                          "webpack|vite", "graphql", "accessibility|a11y", "figma"],
        "min_years": 2,
    },
    "data-analyst": {
        "label": "Data Analyst",
        "must_have": ["sql", "excel", "python|r", "data visualization|dashboards"],
        "nice_to_have": ["power bi|tableau|looker", "statistics", "pandas", "a/b testing",
                          "etl", "snowflake|bigquery|redshift", "storytelling", "stakeholder"],
        "min_years": 1,
    },
}

SAMPLE_RESUME = """Sudhanshu Verma
ML enthusiast with 3 years of experience building data products.

SKILLS: Python, scikit-learn, pandas, SQL, PyTorch, FastAPI, Docker, AWS
EXPERIENCE:
- Built a churn prediction model (Random Forest, ROC-AUC 0.84) deployed as a FastAPI service
- Developed NLP text classification pipelines with transformers
- Created Power BI dashboards for weekly business reporting
EDUCATION: M.Tech in Computer Science, BITS Pilani
"""


# --------------------------------------------------------------- sales data
def sales_data(n: int = 3000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    regions = ["North", "South", "East", "West"]
    products = {
        "Laptop": ("Electronics", 55000), "Smartphone": ("Electronics", 22000),
        "Headphones": ("Electronics", 2500), "Monitor": ("Electronics", 12000),
        "Desk Chair": ("Furniture", 8000), "Standing Desk": ("Furniture", 18000),
        "Bookshelf": ("Furniture", 5500), "Notebook Pack": ("Stationery", 300),
        "Pen Set": ("Stationery", 450), "Backpack": ("Accessories", 1800),
    }
    names = list(products)
    dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    rows = {
        "order_date": rng.choice(dates, n),
        "region": rng.choice(regions, n, p=[0.3, 0.28, 0.18, 0.24]),
        "product": rng.choice(names, n),
        "units": rng.integers(1, 6, n),
    }
    df = pd.DataFrame(rows)
    df["category"] = df["product"].map(lambda p: products[p][0])
    base = df["product"].map(lambda p: products[p][1])
    df["revenue"] = (base * df["units"] * rng.uniform(0.9, 1.1, n)).round(0)
    return df.sort_values("order_date").reset_index(drop=True)
