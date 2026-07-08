"""Synthetic-but-realistic datasets for the live demos.

Every generator is seeded so training is reproducible. Relationships between
features and targets are hand-designed to mirror the real-world effects each
project's write-up describes (e.g. month-to-month contracts raise churn risk).
"""

import numpy as np
import pandas as pd

SEED = 42


def house_prices(n: int = 3000) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    area = rng.uniform(500, 4000, n)
    bedrooms = rng.integers(1, 6, n)
    bathrooms = rng.integers(1, 4, n)
    age = rng.uniform(0, 40, n)
    location_tier = rng.integers(0, 3, n)  # 0 = Average, 1 = Good, 2 = Prime
    garage = rng.integers(0, 2, n)
    price = (
        25_000
        + area * 110
        + bedrooms * 8_000
        + bathrooms * 12_000
        - age * 1_200
        + location_tier * 60_000
        + garage * 15_000
        + rng.normal(0, 20_000, n)
    )
    return pd.DataFrame(
        {
            "area_sqft": area.round(0),
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "age_years": age.round(1),
            "location_tier": location_tier,
            "garage": garage,
            "price": price.clip(40_000),
        }
    )


def heart_disease(n: int = 4000) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    age = rng.uniform(29, 77, n)
    sex_male = rng.integers(0, 2, n)
    chest_pain = rng.integers(0, 4, n)  # 0 none → 3 severe/asymptomatic
    resting_bp = rng.normal(131, 17, n).clip(90, 200)
    cholesterol = rng.normal(246, 51, n).clip(120, 570)
    max_heart_rate = rng.normal(150, 22, n).clip(70, 210)
    exercise_angina = rng.integers(0, 2, n)
    fasting_blood_sugar = (rng.random(n) < 0.15).astype(int)
    z = (
        0.055 * (age - 54)
        + 0.65 * sex_male
        + 0.45 * chest_pain
        + 0.018 * (resting_bp - 130)
        + 0.004 * (cholesterol - 246)
        - 0.028 * (max_heart_rate - 150)
        + 0.95 * exercise_angina
        + 0.30 * fasting_blood_sugar
        - 0.6
    )
    y = rng.binomial(1, 1 / (1 + np.exp(-z)))
    return pd.DataFrame(
        {
            "age": age.round(0),
            "sex_male": sex_male,
            "chest_pain_level": chest_pain,
            "resting_bp": resting_bp.round(0),
            "cholesterol": cholesterol.round(0),
            "max_heart_rate": max_heart_rate.round(0),
            "exercise_angina": exercise_angina,
            "fasting_blood_sugar_high": fasting_blood_sugar,
            "disease": y,
        }
    )


def loan_approval(n: int = 4000) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    income = rng.uniform(20_000, 200_000, n)
    loan_amount = rng.uniform(5_000, 500_000, n)
    credit_score = rng.normal(680, 90, n).clip(300, 850)
    employment_years = rng.uniform(0, 30, n)
    existing_debt = income * rng.uniform(0, 0.8, n)
    education = rng.integers(0, 2, n)  # 1 = graduate
    payment_burden = (loan_amount / 60 + existing_debt / 12) / (income / 12)
    z = (
        0.014 * (credit_score - 650)
        - 3.2 * (payment_burden - 0.45)
        + 0.05 * employment_years
        + 0.25 * education
    )
    y = rng.binomial(1, 1 / (1 + np.exp(-z)))
    return pd.DataFrame(
        {
            "income": income.round(0),
            "loan_amount": loan_amount.round(0),
            "credit_score": credit_score.round(0),
            "employment_years": employment_years.round(1),
            "existing_debt": existing_debt.round(0),
            "education_graduate": education,
            "approved": y,
        }
    )


def churn(n: int = 4000) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    tenure = rng.integers(0, 73, n)
    contract = rng.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.25, 0.2])
    monthly_charges = rng.uniform(20, 120, n)
    internet = rng.choice(["DSL", "Fiber optic", "No internet"], n, p=[0.35, 0.45, 0.2])
    tech_support = rng.integers(0, 2, n)
    payment = rng.choice(
        ["Electronic check", "Mailed check", "Bank transfer", "Credit card"], n
    )
    z = (
        -0.045 * tenure
        + 1.2 * (contract == "Month-to-month")
        - 0.7 * (contract == "Two year")
        + 0.014 * (monthly_charges - 70)
        + 0.75 * (internet == "Fiber optic")
        - 0.65 * tech_support
        + 0.55 * (payment == "Electronic check")
        - 0.4
    )
    y = rng.binomial(1, 1 / (1 + np.exp(-z)))
    return pd.DataFrame(
        {
            "tenure_months": tenure,
            "contract": contract,
            "monthly_charges": monthly_charges.round(2),
            "internet_service": internet,
            "tech_support": tech_support,
            "payment_method": payment,
            "churned": y,
        }
    )


# Designed cluster centers: (annual income $k, spending score 0-100, age, visits/month)
SEGMENT_PERSONAS = [
    {
        "name": "Budget Browsers",
        "center": [32, 30, 45, 2],
        "description": "Lower income, low spending score, shop infrequently — respond to discounts and value bundles.",
    },
    {
        "name": "Loyal High-Spenders",
        "center": [95, 82, 42, 8],
        "description": "High income and high spending score with frequent visits — ideal for loyalty programs and premium lines.",
    },
    {
        "name": "Young Impulse Shoppers",
        "center": [45, 75, 26, 6],
        "description": "Younger customers who spend well above their income tier — engage via social channels and flash sales.",
    },
    {
        "name": "Wealthy but Cautious",
        "center": [110, 28, 55, 3],
        "description": "High income but low spending score — untapped potential; nurture with personalized outreach.",
    },
]


def customers(n_per_cluster: int = 250) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    spreads = [8, 10, 7, 12], [12, 8, 9, 2], [8, 9, 4, 2], [15, 9, 8, 1.5]
    for persona, spread in zip(SEGMENT_PERSONAS, spreads):
        block = rng.normal(persona["center"], spread, (n_per_cluster, 4))
        rows.append(block)
    data = np.vstack(rows)
    df = pd.DataFrame(data, columns=["annual_income_k", "spending_score", "age", "visits_per_month"])
    return df.clip(lower=[12, 1, 18, 0], upper=[200, 100, 80, 30], axis=1).round(1)


def fraud(n: int = 12000) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    amount = rng.lognormal(3.6, 1.1, n).clip(1, 5000)
    distance_from_home = rng.lognormal(2.2, 1.4, n).clip(0.1, 5000)
    ratio_to_median = rng.lognormal(0, 0.8, n).clip(0.05, 40)
    repeat_retailer = rng.binomial(1, 0.85, n)
    used_chip = rng.binomial(1, 0.65, n)
    used_pin = rng.binomial(1, 0.25, n)
    online_order = rng.binomial(1, 0.5, n)
    z = (
        2.0 * online_order
        - 1.6 * used_pin
        - 0.9 * used_chip
        - 1.1 * repeat_retailer
        + 0.9 * np.log(ratio_to_median)
        + 0.35 * np.log(distance_from_home)
        + 0.25 * np.log(amount / 40)
        - 3.4
    )
    y = rng.binomial(1, 1 / (1 + np.exp(-z)))
    return pd.DataFrame(
        {
            "amount": amount.round(2),
            "distance_from_home_km": distance_from_home.round(1),
            "ratio_to_median_purchase": ratio_to_median.round(2),
            "repeat_retailer": repeat_retailer,
            "used_chip": used_chip,
            "used_pin": used_pin,
            "online_order": online_order,
            "fraud": y,
        }
    )


SPAM_EMAILS = [
    "Congratulations! You have been selected to win a $1000 gift card. Click here to claim now",
    "URGENT: Your account will be suspended. Verify your password immediately at this link",
    "Get rich quick! Earn $5000 per week working from home, no experience needed",
    "You are a lucky winner of our international lottery. Send your bank details to collect",
    "Limited time offer!!! Buy cheap meds online without prescription, discreet shipping",
    "Hot singles in your area are waiting to meet you tonight, sign up free",
    "Final notice: unpaid invoice attached, download immediately to avoid legal action",
    "Your package could not be delivered. Pay a small customs fee here to release it",
    "Double your bitcoin in 24 hours, guaranteed returns, invest now before it is too late",
    "Claim your free iPhone 15 now, only 3 left in stock, act fast",
    "You have won a luxury cruise vacation. Reply with your credit card to reserve",
    "Exclusive deal just for you: 90% off designer watches, wholesale prices",
    "Your computer has a virus! Call this toll free number now for immediate support",
    "Make money fast with this one weird trick, banks hate it",
    "Pre-approved loan of $50,000 with no credit check, apply today",
    "Increase your followers instantly, buy 10k real followers for $9.99",
    "This is your last chance to claim unclaimed funds in your name",
    "Free trial of miracle weight loss pills, lose 10kg in one week",
    "Your subscription payment failed. Update card details at the secure link below",
    "Win big at our online casino, first deposit matched 500%",
]

HAM_EMAILS = [
    "Hi team, attaching the minutes from today's standup. Let me know if I missed anything",
    "Can we move our 3pm meeting to tomorrow morning? Something came up",
    "The quarterly report is ready for review, feedback welcome by Friday",
    "Thanks for your help with the deployment yesterday, everything is running smoothly",
    "Reminder: the office will be closed on Monday for the public holiday",
    "Here is the updated project timeline after our discussion with the client",
    "Could you review my pull request when you get a chance? No rush",
    "Lunch on Thursday to celebrate the release? Vote for a place in the thread",
    "The training session on the new CRM starts at 10am in conference room B",
    "I've booked the flights for the conference, itinerary attached",
    "Please find attached the invoice for June as discussed in our contract",
    "Your interview is confirmed for Tuesday at 2pm, the panel details are below",
    "The database migration completed successfully last night, no downtime recorded",
    "Happy to introduce you to Sarah who leads our analytics team",
    "Following up on our call: next steps and owners are listed below",
    "The library books you reserved are ready for pickup at the front desk",
    "Your appointment with Dr. Mehta is scheduled for Friday at 9:30am",
    "Course registration for the fall semester opens next Monday",
    "Package delivered: your order #4832 was left at the front door",
    "Team offsite agenda draft attached, send topic suggestions by Wednesday",
]

SPAM_SMS = [
    "WINNER!! You won 2 lakh cash prize. SMS CLAIM to 56789 now",
    "FREE recharge worth Rs 500. Click bit.ly/freerchg to redeem before midnight",
    "Congratulations you are shortlisted for a govt job. Pay Rs 999 registration fee",
    "Your SIM will be blocked in 24hrs. Call 9876543210 to verify KYC immediately",
    "Get instant loan upto 5 lakh no documents. Apply now on this link",
    "Flat 90% off only today. Hurry limited stock. Shop at dealz4u.in",
    "You have been selected for a free health checkup worth 5000. Reply YES",
    "Earn 3000 daily from home. Join our whatsapp group now",
    "Ur electricity will be disconnected tonite. Pay bill immediately at this link",
    "Lucky draw winner! Your number won a Tata Safari. Call to claim",
    "Exclusive casino bonus 10000 free chips. Play and win real cash",
    "Your parcel is on hold. Pay Rs 25 customs duty here to release",
    "Last day! Unlimited data for 1 year at Rs 99 only. Recharge now",
    "Alert: suspicious login to your bank. Verify OTP at secure-bank-check.com",
    "Buy 1 get 3 free on all products. Mega sale ends tonight",
]

HAM_SMS = [
    "Hey, are we still meeting at the cafe at 6?",
    "Mom asked if you're coming home for dinner this weekend",
    "Your OTP for login is 482913. Do not share it with anyone",
    "The meeting got pushed to 4pm, see you in the conference room",
    "Can you send me the notes from yesterday's lecture?",
    "Train is running 20 mins late, will reach the station by 8",
    "Doctor confirmed the appointment for tomorrow 11am",
    "Congrats on the new job! We should celebrate this weekend",
    "Reminder: your car service is due on the 15th, call us to book a slot",
    "I'll pick up groceries on the way back, need anything else?",
    "Your Swiggy order has been delivered. Enjoy your meal",
    "Class is cancelled today, professor is unwell",
    "Movie starts at 9:15, let's meet at the mall by 8:45",
    "Your electricity bill of Rs 1240 is due on 28th June",
    "Happy birthday! Wishing you an amazing year ahead",
]

MOVIES = [
    # title, year, rating, genres: action comedy drama scifi romance thriller animation crime
    ("The Dark Knight", 2008, 9.0, [1, 0, 1, 0, 0, 1, 0, 1]),
    ("Inception", 2010, 8.8, [1, 0, 0, 1, 0, 1, 0, 0]),
    ("Interstellar", 2014, 8.7, [0, 0, 1, 1, 0, 0, 0, 0]),
    ("The Matrix", 1999, 8.7, [1, 0, 0, 1, 0, 1, 0, 0]),
    ("Blade Runner 2049", 2017, 8.0, [0, 0, 1, 1, 0, 1, 0, 0]),
    ("Mad Max: Fury Road", 2015, 8.1, [1, 0, 0, 1, 0, 1, 0, 0]),
    ("The Shawshank Redemption", 1994, 9.3, [0, 0, 1, 0, 0, 0, 0, 1]),
    ("The Godfather", 1972, 9.2, [0, 0, 1, 0, 0, 0, 0, 1]),
    ("Pulp Fiction", 1994, 8.9, [0, 1, 1, 0, 0, 1, 0, 1]),
    ("Goodfellas", 1990, 8.7, [0, 0, 1, 0, 0, 0, 0, 1]),
    ("The Departed", 2006, 8.5, [0, 0, 1, 0, 0, 1, 0, 1]),
    ("Se7en", 1995, 8.6, [0, 0, 1, 0, 0, 1, 0, 1]),
    ("Forrest Gump", 1994, 8.8, [0, 1, 1, 0, 1, 0, 0, 0]),
    ("The Notebook", 2004, 7.8, [0, 0, 1, 0, 1, 0, 0, 0]),
    ("La La Land", 2016, 8.0, [0, 1, 1, 0, 1, 0, 0, 0]),
    ("Titanic", 1997, 7.9, [0, 0, 1, 0, 1, 0, 0, 0]),
    ("Pride and Prejudice", 2005, 7.8, [0, 0, 1, 0, 1, 0, 0, 0]),
    ("Crazy Rich Asians", 2018, 6.9, [0, 1, 1, 0, 1, 0, 0, 0]),
    ("Superbad", 2007, 7.6, [0, 1, 0, 0, 0, 0, 0, 0]),
    ("The Hangover", 2009, 7.7, [0, 1, 0, 0, 0, 0, 0, 1]),
    ("21 Jump Street", 2012, 7.2, [1, 1, 0, 0, 0, 0, 0, 1]),
    ("Deadpool", 2016, 8.0, [1, 1, 0, 1, 0, 0, 0, 0]),
    ("Guardians of the Galaxy", 2014, 8.0, [1, 1, 0, 1, 0, 0, 0, 0]),
    ("The Avengers", 2012, 8.0, [1, 0, 0, 1, 0, 0, 0, 0]),
    ("Spider-Man: Into the Spider-Verse", 2018, 8.4, [1, 1, 0, 1, 0, 0, 1, 0]),
    ("Toy Story", 1995, 8.3, [0, 1, 0, 0, 0, 0, 1, 0]),
    ("Finding Nemo", 2003, 8.2, [0, 1, 1, 0, 0, 0, 1, 0]),
    ("Up", 2009, 8.3, [0, 1, 1, 0, 0, 0, 1, 0]),
    ("Spirited Away", 2001, 8.6, [0, 0, 1, 0, 0, 0, 1, 0]),
    ("Your Name", 2016, 8.4, [0, 0, 1, 1, 1, 0, 1, 0]),
    ("Gone Girl", 2014, 8.1, [0, 0, 1, 0, 0, 1, 0, 1]),
    ("Shutter Island", 2010, 8.2, [0, 0, 1, 0, 0, 1, 0, 1]),
    ("Prisoners", 2013, 8.1, [0, 0, 1, 0, 0, 1, 0, 1]),
    ("Parasite", 2019, 8.5, [0, 1, 1, 0, 0, 1, 0, 1]),
    ("Whiplash", 2014, 8.5, [0, 0, 1, 0, 0, 0, 0, 0]),
    ("The Social Network", 2010, 7.8, [0, 0, 1, 0, 0, 0, 0, 0]),
    ("12 Angry Men", 1957, 9.0, [0, 0, 1, 0, 0, 0, 0, 1]),
    ("Arrival", 2016, 7.9, [0, 0, 1, 1, 0, 1, 0, 0]),
    ("Ex Machina", 2014, 7.7, [0, 0, 1, 1, 0, 1, 0, 0]),
    ("Her", 2013, 8.0, [0, 0, 1, 1, 1, 0, 0, 0]),
]

GENRE_NAMES = ["Action", "Comedy", "Drama", "Sci-Fi", "Romance", "Thriller", "Animation", "Crime"]


def gene_expression(n_per_group: int = 80, n_genes: int = 50):
    """Three tissue groups, each over-expressing a distinct block of genes."""
    rng = np.random.default_rng(SEED)
    groups = []
    labels = []
    for g in range(3):
        base = rng.normal(0, 1, (n_per_group, n_genes))
        signature = slice(g * 12, g * 12 + 12)
        base[:, signature] += rng.normal(3.0, 0.5, (n_per_group, 12))
        groups.append(base)
        labels += [f"Tissue {chr(65 + g)}"] * n_per_group
    return np.vstack(groups), np.array(labels)
