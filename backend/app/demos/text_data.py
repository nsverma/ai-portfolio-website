"""Template-generated text corpora for the sentiment and topic demos.

Small but combinatorially varied, with explicit negation patterns so the
recurrent models genuinely learn "not good" != "good".
"""

import random

POS_ADJ = ["amazing", "brilliant", "fantastic", "wonderful", "excellent", "gripping",
           "delightful", "superb", "outstanding", "heartwarming", "masterful", "stunning",
           "captivating", "powerful", "beautiful", "good", "great", "enjoyable", "fun"]
NEG_ADJ = ["terrible", "boring", "awful", "dreadful", "disappointing", "predictable",
           "bland", "painful", "forgettable", "horrible", "clumsy", "tedious",
           "unwatchable", "lifeless", "messy", "bad", "poor", "dull", "weak"]
SUBJECTS = ["the movie", "this film", "the plot", "the acting", "the soundtrack",
            "the story", "the direction", "the screenplay", "the pacing", "the cast",
            "the visuals", "the ending", "the dialogue", "the cinematography"]
NOUNS = ["movie", "film", "plot", "story", "acting", "soundtrack", "script",
         "cast", "ending", "dialogue", "performance"]
POS_VERB = ["loved", "enjoyed", "adored", "really liked"]
NEG_VERB = ["hated", "disliked", "regretted watching", "could not stand"]
INTENS = ["", "absolutely ", "truly ", "really ", "completely ", "utterly "]
NEUTRAL = ["{s} was okay", "{s} was average at best", "{s} was neither good nor bad",
           "{s} was fine i guess", "{s} was watchable but nothing special",
           "{s} was passable", "{s} had its moments but overall it was just okay",
           "{s} was neither impressive nor terrible", "{s} felt ordinary",
           "{s} was decent enough but easy to forget"]


def sentiment_corpus(n_per_class: int = 1200, classes: int = 2, seed: int = 7):
    """Returns (texts, labels). classes=2 → 0 neg / 1 pos; classes=3 → 0 neg / 1 neu / 2 pos."""
    rng = random.Random(seed)
    texts, labels = [], []

    def pos_label():
        return 2 if classes == 3 else 1

    for _ in range(n_per_class):
        s = rng.choice(SUBJECTS)
        i = rng.choice(INTENS)
        form = rng.randrange(7)
        tail = rng.choice(["", " at all"])
        n1, n2 = rng.sample(NOUNS, 2)
        # positive sample — negation of a negative adjective reads positive
        if form == 0:
            texts.append(f"{s} was {i}{rng.choice(POS_ADJ)}")
        elif form == 1:
            texts.append(f"i {rng.choice(POS_VERB)} {s}")
        elif form == 2:
            texts.append(f"{s} was not {rng.choice(NEG_ADJ)}{tail}, it was {rng.choice(POS_ADJ)}")
        elif form == 3:
            texts.append(f"{s} was not {rng.choice(NEG_ADJ)}{tail}")
        elif form == 4:
            texts.append(f"{s} was {rng.choice(POS_ADJ)} and {rng.choice(POS_ADJ)}")
        elif form == 5:
            texts.append(f"{i}{rng.choice(POS_ADJ)} {n1} and a {rng.choice(POS_ADJ)} {n2}")
        else:
            texts.append(f"what a {rng.choice(POS_ADJ)} {n1}")
        labels.append(pos_label())
        # negative sample — same forms, mirrored
        s = rng.choice(SUBJECTS)
        n1, n2 = rng.sample(NOUNS, 2)
        if form == 0:
            texts.append(f"{s} was {i}{rng.choice(NEG_ADJ)}")
        elif form == 1:
            texts.append(f"i {rng.choice(NEG_VERB)} {s}")
        elif form == 2:
            texts.append(f"{s} was not {rng.choice(POS_ADJ)}{tail}, it was {rng.choice(NEG_ADJ)}")
        elif form == 3:
            texts.append(f"{s} was not {rng.choice(POS_ADJ)}{tail}")
        elif form == 4:
            texts.append(f"{s} was {rng.choice(NEG_ADJ)} and {rng.choice(NEG_ADJ)}")
        elif form == 5:
            texts.append(f"{i}{rng.choice(NEG_ADJ)} {n1} and a {rng.choice(NEG_ADJ)} {n2}")
        else:
            texts.append(f"what a {rng.choice(NEG_ADJ)} {n1}")
        labels.append(0)
        if classes == 3:
            texts.append(rng.choice(NEUTRAL).format(s=rng.choice(SUBJECTS)))
            labels.append(1)
    return texts, labels


TEAMS = ["united", "city", "rovers", "athletic", "wanderers", "rangers"]
CITIES = ["madrid", "mumbai", "london", "tokyo", "chicago", "berlin"]
COMPANIES = ["tech giant", "startup", "chipmaker", "retailer", "carmaker", "bank"]
GADGETS = ["smartphone", "laptop", "chip", "headset", "smartwatch", "drone"]

TOPIC_TEMPLATES = {
    "sports": [
        "{team} beats {team2} in a thrilling final",
        "star striker scores hat trick against {team}",
        "{city} wins the championship after penalty shootout",
        "coach announces retirement after a losing season",
        "injury rules out captain for the world cup qualifier",
        "{team} signs record deal for young midfielder",
        "olympic sprinter breaks national record in {city}",
        "underdogs stun {team} with last minute goal",
        "tennis champion cruises into the semifinals",
        "{city} marathon draws record number of runners",
    ],
    "technology": [
        "new {gadget} promises faster ai performance",
        "{company} launches open source database tool",
        "researchers unveil breakthrough in quantum computing",
        "{company} releases urgent update to fix security flaw",
        "developers flock to new programming framework",
        "ai model writes code better than junior engineers, study finds",
        "{company} unveils foldable {gadget} at annual event",
        "cybersecurity experts warn of new phishing campaign",
        "open source community celebrates major kernel release",
        "cloud outage disrupts services for millions of users",
    ],
    "business": [
        "shares surge after strong quarterly earnings",
        "central bank raises interest rates to curb inflation",
        "{company} raises funding at billion dollar valuation",
        "merger talks between rival retailers collapse",
        "oil prices fall amid supply concerns",
        "{company} announces layoffs as demand slows",
        "housing market cools as mortgage rates climb",
        "regulators fine {company} over accounting practices",
        "exports jump on weaker currency, boosting gdp outlook",
        "small businesses struggle with rising input costs",
    ],
    "entertainment": [
        "actor wins best performance award at film festival",
        "new album tops the charts in its first week",
        "director announces sequel to blockbuster franchise",
        "streaming series renewed for a third season",
        "singer kicks off world tour with sold out show in {city}",
        "documentary about {city} street food wins critics prize",
        "band reunites for anniversary concert after a decade",
        "animated film breaks box office records worldwide",
        "celebrity couple announces engagement on social media",
        "reality show finale draws record television audience",
    ],
}

TOPIC_CLASSES = list(TOPIC_TEMPLATES.keys())


def topic_corpus(n_per_class: int = 300, seed: int = 11):
    rng = random.Random(seed)
    texts, labels = [], []
    for label, cls in enumerate(TOPIC_CLASSES):
        for _ in range(n_per_class):
            t = rng.choice(TOPIC_TEMPLATES[cls])
            team, team2 = rng.sample(TEAMS, 2)
            texts.append(t.format(team=team, team2=team2, city=rng.choice(CITIES),
                                  company=rng.choice(COMPANIES), gadget=rng.choice(GADGETS)))
            labels.append(label)
    return texts, labels
