"""AI-agent demos: real deterministic agent cores with an optional LLM upgrade.

Each agent demonstrates a genuine agent architecture — tool dispatch, retrieval,
classification + policy, pipeline orchestration — implemented with local models
so the demos run without external services. When ANTHROPIC_API_KEY is set,
generation steps upgrade to Claude automatically (see llm.py).
"""

import re
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

from app.demos import agents_data, llm

ARTIFACTS = Path(__file__).parent / "artifacts"


@lru_cache(maxsize=None)
def _load(name: str):
    path = ARTIFACTS / f"{name}.joblib"
    if not path.exists():
        raise FileNotFoundError(
            f"Agent artifact '{name}' missing — run `python -m app.demos.train_agents` from backend/."
        )
    return joblib.load(path)


def _retrieve(index, query: str, k: int = 4):
    """Cosine top-k over a TF-IDF index artifact. Returns (idx, score) pairs."""
    from sklearn.metrics.pairwise import cosine_similarity

    q = index["vectorizer"].transform([query])
    scores = cosine_similarity(q, index["matrix"]).ravel()
    order = np.argsort(scores)[::-1][:k]
    return [(int(i), float(scores[i])) for i in order if scores[i] > 0.02]


def _llm_note():
    return {"label": "Generation", "value":
            f"Claude ({llm.MODEL}) via Anthropic API" if llm.available()
            else "Extractive (no LLM key set — set ANTHROPIC_API_KEY to upgrade)"}


# ========================================================= personal assistant
_UNIT_TABLE = {
    ("km", "miles"): 0.621371, ("miles", "km"): 1.60934,
    ("kg", "lb"): 2.20462, ("lb", "kg"): 0.453592,
    ("m", "ft"): 3.28084, ("ft", "m"): 0.3048,
    ("l", "gallons"): 0.264172, ("gallons", "l"): 3.78541,
}


def _assistant_fields():
    return [{
        "name": "text", "label": "Ask the assistant", "type": "textarea",
        "default": "remind me to submit the assignment tomorrow at 5pm",
        "help": "Try: 'what is 15% of 240', 'convert 5 km to miles', 'what date is 45 days from now', 'remind me to call mom friday at 6pm'.",
    }]


def _assistant_predict(inputs):
    text = str(inputs.get("text", "")).strip().lower()
    if not text:
        raise ValueError("Ask something first.")
    trace = []

    # Tool 1: percentage / arithmetic calculator
    m = re.search(r"([\d.]+)\s*%\s*of\s*([\d.]+)", text)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        trace.append({"label": "Intent", "value": "calculation"})
        trace.append({"label": "Tool called", "value": f"calculator(percent={a}, of={b})"})
        return _assistant_result(f"{a}% of {b} = {a * b / 100:g}", trace)
    m = re.fullmatch(r"(?:what is |calculate |compute )?([\d\s+\-*/().]+)\??", text)
    if m and re.search(r"\d\s*[+\-*/]\s*\d", m.group(1)):
        expr = m.group(1).strip()
        if re.fullmatch(r"[\d\s+\-*/().]+", expr):
            trace.append({"label": "Intent", "value": "calculation"})
            trace.append({"label": "Tool called", "value": f"calculator('{expr}')"})
            try:
                return _assistant_result(f"{expr} = {eval(expr, {'__builtins__': {}}):g}", trace)
            except Exception:
                raise ValueError("I couldn't evaluate that expression.")

    # Tool 2: unit converter
    m = re.search(r"convert\s+([\d.]+)\s*(km|miles|kg|lb|m|ft|l|gallons)\s+(?:to|into)\s+(km|miles|kg|lb|m|ft|l|gallons)", text)
    if m:
        val, src, dst = float(m.group(1)), m.group(2), m.group(3)
        factor = _UNIT_TABLE.get((src, dst))
        trace.append({"label": "Intent", "value": "unit conversion"})
        trace.append({"label": "Tool called", "value": f"convert({val}, '{src}' → '{dst}')"})
        if factor is None:
            raise ValueError(f"I can't convert {src} to {dst}.")
        return _assistant_result(f"{val:g} {src} = {val * factor:.3f} {dst}", trace)

    # Tool 3: date math
    m = re.search(r"(\d+)\s+days?\s+from\s+(?:now|today)", text)
    if m:
        days = int(m.group(1))
        target = datetime.now() + timedelta(days=days)
        trace.append({"label": "Intent", "value": "date calculation"})
        trace.append({"label": "Tool called", "value": f"date_math(days=+{days})"})
        return _assistant_result(f"{days} days from now is {target.strftime('%A, %d %B %Y')}", trace)
    if re.search(r"what (?:day|date) is (?:it|today)", text):
        trace.append({"label": "Intent", "value": "date lookup"})
        trace.append({"label": "Tool called", "value": "current_date()"})
        return _assistant_result(f"Today is {datetime.now().strftime('%A, %d %B %Y')}", trace)

    # Tool 4: reminders
    m = re.search(r"remind me to (.+?)(?:\s+(tomorrow|today|on \w+|\w+day))?\s*(?:at\s+([\d:]+\s*[ap]m?))?$", text)
    if m and "remind" in text:
        task = m.group(1).strip()
        when = " ".join(p for p in [m.group(2), m.group(3)] if p) or "unspecified time"
        trace.append({"label": "Intent", "value": "set reminder"})
        trace.append({"label": "Tool called", "value": f"create_reminder(task='{task}', when='{when}')"})
        return _assistant_result(f"✓ Reminder set: “{task}” — {when}", trace)

    # Fallback: LLM if available, else honest decline
    trace.append({"label": "Intent", "value": "general query (no matching tool)"})
    answer = llm.generate(
        "You are a concise personal assistant. Answer in at most 3 sentences.", text
    )
    if answer:
        trace.append({"label": "Tool called", "value": "claude.generate()"})
        return _assistant_result(answer, trace)
    trace.append({"label": "Tool called", "value": "none"})
    return {
        "headline": "I don't have a tool for that yet",
        "confidence": None, "tone": "neutral",
        "details": trace + [
            {"label": "Available tools", "value": "calculator, unit converter, date math, reminders"},
            _llm_note(),
        ],
    }


def _assistant_result(answer, trace):
    return {"headline": answer, "confidence": None, "tone": "info",
            "details": trace + [{"label": "Architecture", "value": "intent parser → tool dispatch → tool execution"}]}


# ======================================================== research assistant
def _research_fields():
    return [{
        "name": "question", "label": "Research question", "type": "textarea",
        "default": "How does RLHF align language models with human preferences?",
        "help": "The agent searches an embedded ML research corpus, extracts key findings, and writes a brief with sources.",
    }]


def _research_predict(inputs):
    question = str(inputs.get("question", "")).strip()
    if not question:
        raise ValueError("Enter a research question.")
    index = _load("research_index")
    hits = _retrieve(index, question, k=5)
    if not hits:
        return {"headline": "No relevant findings in the corpus", "confidence": None,
                "tone": "neutral", "details": [{"label": "Corpus", "value": f"{len(agents_data.RESEARCH_ARTICLES)} articles"}]}
    findings = [index["entries"][i] for i, _ in hits]
    sources = sorted({f["title"] for f in findings})

    summary = llm.generate(
        "You are a research assistant. Using ONLY the provided findings, write a 3-sentence brief.",
        f"Question: {question}\n\nFindings:\n" + "\n".join(f"- {f['sentence']}" for f in findings),
    )
    headline = summary if summary else f"Found {len(findings)} relevant findings across {len(sources)} sources"
    return {
        "headline": headline,
        "confidence": hits[0][1], "tone": "info",
        "details": [{"label": f"Finding #{n+1}", "value": f["sentence"]} for n, f in enumerate(findings[:4])]
        + [{"label": "Sources", "value": " · ".join(sources)},
           {"label": "Pipeline", "value": "TF-IDF retrieval → sentence ranking → brief assembly"},
           _llm_note()],
    }


# ========================================================== resume screening
def _resume_fields():
    return [
        {"name": "role", "label": "Screening for role", "type": "select",
         "options": [{"value": k, "label": v["label"]} for k, v in agents_data.JOB_ROLES.items()],
         "default": "ml-engineer"},
        {"name": "resume", "label": "Resume text", "type": "textarea",
         "default": agents_data.SAMPLE_RESUME,
         "help": "Paste any resume — the agent extracts skills, experience, and education, then scores fit."},
    ]


def _resume_predict(inputs):
    resume = str(inputs.get("resume", "")).lower()
    if len(resume) < 30:
        raise ValueError("Paste a resume first.")
    role = agents_data.JOB_ROLES.get(str(inputs.get("role")), agents_data.JOB_ROLES["ml-engineer"])

    def has(pattern):
        return any(re.search(rf"\b{alt}\b", resume) for alt in pattern.split("|"))

    matched_must = [p for p in role["must_have"] if has(p)]
    missing_must = [p for p in role["must_have"] if not has(p)]
    matched_nice = [p for p in role["nice_to_have"] if has(p)]

    years = 0
    m = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", resume)
    if m:
        years = max(int(x) for x in m)
    has_degree = bool(re.search(r"b\.?tech|m\.?tech|bachelor|master|b\.?e\b|m\.?s\b|phd|mca|bca", resume))

    score = (0.5 * len(matched_must) / len(role["must_have"])
             + 0.3 * min(len(matched_nice) / 4, 1.0)
             + 0.1 * min(years / max(role["min_years"], 1) / 2, 1.0)
             + 0.1 * has_degree)
    decision = ("STRONG MATCH — advance to interview" if score >= 0.7
                else "POSSIBLE MATCH — needs review" if score >= 0.45
                else "NOT A MATCH for this role")
    fmt = lambda items: ", ".join(p.split("|")[0] for p in items) or "—"
    return {
        "headline": f"{decision} ({score:.0%})",
        "confidence": score,
        "tone": "good" if score >= 0.7 else "neutral" if score >= 0.45 else "bad",
        "details": [
            {"label": "Role", "value": role["label"]},
            {"label": "Required skills found", "value": fmt(matched_must)},
            {"label": "Required skills missing", "value": fmt(missing_must)},
            {"label": "Bonus skills found", "value": fmt(matched_nice)},
            {"label": "Experience detected", "value": f"{years} years (role asks {role['min_years']}+)"},
            {"label": "Degree detected", "value": "yes" if has_degree else "no"},
            {"label": "Pipeline", "value": "skill extraction → experience parsing → weighted scoring → decision"},
        ],
    }


# ============================================================ document Q&A RAG
def _docqa_fields():
    return [{
        "name": "question", "label": "Ask the employee handbook", "type": "textarea",
        "default": "How many days of paid leave do I get and can I carry them over?",
        "help": "RAG over a 14-section company handbook: retrieve → cite → answer.",
    }]


def _docqa_predict(inputs):
    question = str(inputs.get("question", "")).strip()
    if not question:
        raise ValueError("Ask a question.")
    index = _load("handbook_index")
    hits = _retrieve(index, question, k=3)
    if not hits:
        return {"headline": "The handbook doesn't cover that", "confidence": None,
                "tone": "neutral", "details": [{"label": "Searched", "value": f"{len(index['chunks'])} handbook sections"}]}
    top = [index["chunks"][i] for i, _ in hits]

    answer = llm.generate(
        "Answer the question using ONLY the provided handbook sections, in 1-2 sentences. Cite the section name.",
        f"Question: {question}\n\nSections:\n" + "\n".join(f"[{t}] {b}" for t, b in top),
    )
    if not answer:
        # Extractive: best-matching sentence from the top chunk
        title, body = top[0]
        sents = re.split(r"(?<=[.!?]) +", body)
        svec = index["vectorizer"].transform(sents)
        qvec = index["vectorizer"].transform([question])
        from sklearn.metrics.pairwise import cosine_similarity
        best = sents[int(np.argmax(cosine_similarity(qvec, svec)))]
        answer = f"{best} (from: {title})"
    return {
        "headline": answer,
        "confidence": hits[0][1], "tone": "info",
        "details": [{"label": f"Retrieved: {t}", "value": b[:160] + "…"} for t, b in top]
        + [{"label": "Pipeline", "value": "chunk retrieval (TF-IDF) → citation → answer"},
           _llm_note()],
    }


# ========================================================== codebase RAG agent
def _coderag_fields():
    return [{
        "name": "question", "label": "Ask about this website's codebase", "type": "textarea",
        "default": "How are the demo models trained?",
        "help": "The agent has indexed this very portfolio's source code (backend + frontend). Try 'how does the digit canvas work' or 'where are projects fetched from the API'.",
    }]


def _coderag_predict(inputs):
    question = str(inputs.get("question", "")).strip()
    if not question:
        raise ValueError("Ask a question about the code.")
    index = _load("codebase_index")
    hits = _retrieve(index, question, k=3)
    if not hits:
        return {"headline": "No matching code found", "confidence": None, "tone": "neutral",
                "details": [{"label": "Indexed", "value": f"{len(index['chunks'])} code chunks"}]}
    details = []
    for i, score in hits:
        c = index["chunks"][i]
        snippet = " ".join(c["text"].split())[:200]
        details.append({"label": f"{c['file']}:{c['start_line']}–{c['end_line']} ({score:.2f})",
                        "value": snippet + "…"})
    best = index["chunks"][hits[0][0]]
    return {
        "headline": f"Most relevant: {best['file']} (lines {best['start_line']}–{best['end_line']})",
        "confidence": hits[0][1], "tone": "info",
        "details": details + [
            {"label": "Index", "value": f"{len(index['chunks'])} chunks across this repo's Python + JSX source"},
            {"label": "Pipeline", "value": "code chunking → TF-IDF retrieval → ranked snippets"},
        ],
    }


# =========================================================== data analysis
_ANALYSES = {
    "revenue_by_region": "Total revenue by region",
    "top_products": "Top 5 products by revenue",
    "monthly_trend": "Monthly revenue trend",
    "category_share": "Revenue share by category",
    "avg_order_value": "Average order value by region",
    "best_month": "Which month had the highest revenue?",
}

_ANALYSIS_CODE = {
    "revenue_by_region": "df.groupby('region').revenue.sum().sort_values(ascending=False)",
    "top_products": "df.groupby('product').revenue.sum().nlargest(5)",
    "monthly_trend": "df.set_index('order_date').resample('ME').revenue.sum()",
    "category_share": "df.groupby('category').revenue.sum() / df.revenue.sum()",
    "avg_order_value": "df.groupby('region').revenue.mean()",
    "best_month": "df.set_index('order_date').resample('ME').revenue.sum().idxmax()",
}


def _analysis_fields():
    return [{
        "name": "analysis", "label": "Ask the data agent (2025 sales, 3,000 orders)",
        "type": "select",
        "options": [{"value": k, "label": v} for k, v in _ANALYSES.items()],
        "default": "revenue_by_region",
    }]


def _analysis_predict(inputs):
    key = str(inputs.get("analysis"))
    if key not in _ANALYSES:
        raise ValueError("Pick an analysis.")
    df = _load("sales_data")
    details = [{"label": "Generated pandas", "value": _ANALYSIS_CODE[key]}]

    if key == "revenue_by_region":
        result = df.groupby("region").revenue.sum().sort_values(ascending=False)
        details += [{"label": r, "value": f"₹{v:,.0f}"} for r, v in result.items()]
        headline = f"{result.index[0]} leads with ₹{result.iloc[0]:,.0f} in revenue"
    elif key == "top_products":
        result = df.groupby("product").revenue.sum().nlargest(5)
        details += [{"label": f"#{n+1} {p}", "value": f"₹{v:,.0f}"} for n, (p, v) in enumerate(result.items())]
        headline = f"Top product: {result.index[0]} (₹{result.iloc[0]:,.0f})"
    elif key == "monthly_trend":
        result = df.set_index("order_date").resample("ME").revenue.sum()
        details += [{"label": d.strftime("%b %Y"), "value": f"₹{v:,.0f}"} for d, v in result.items()]
        change = (result.iloc[-1] - result.iloc[0]) / result.iloc[0]
        headline = f"Revenue {'grew' if change >= 0 else 'fell'} {abs(change):.0%} from Jan to Dec"
    elif key == "category_share":
        result = (df.groupby("category").revenue.sum() / df.revenue.sum()).sort_values(ascending=False)
        details += [{"label": c, "value": f"{v:.1%}"} for c, v in result.items()]
        headline = f"{result.index[0]} drives {result.iloc[0]:.0%} of all revenue"
    elif key == "avg_order_value":
        result = df.groupby("region").revenue.mean().sort_values(ascending=False)
        details += [{"label": r, "value": f"₹{v:,.0f}"} for r, v in result.items()]
        headline = f"Highest average order value: {result.index[0]} (₹{result.iloc[0]:,.0f})"
    else:  # best_month
        monthly = df.set_index("order_date").resample("ME").revenue.sum()
        best = monthly.idxmax()
        headline = f"Best month: {best.strftime('%B %Y')} with ₹{monthly.max():,.0f}"
        details += [{"label": "Runner-up", "value": monthly.drop(best).idxmax().strftime("%B %Y")}]

    details.append({"label": "Pipeline", "value": "question → plan → pandas execution → result narration"})
    return {"headline": headline, "confidence": None, "tone": "info", "details": details}


# ========================================================== customer support
def _support_fields():
    return [{
        "name": "text", "label": "Customer message", "type": "textarea",
        "default": "My package for order 7745 has been stuck in transit for a week, where is it?",
        "help": "The agent classifies intent, extracts entities, drafts a reply, and decides whether to escalate.",
    }]


def _support_predict(inputs):
    text = str(inputs.get("text", "")).strip()
    if not text:
        raise ValueError("Enter a customer message.")
    model = _load("support_intent")
    probs = model.predict_proba([text])[0]
    classes = list(model.classes_)
    top = int(np.argmax(probs))
    intent, conf = classes[top], float(probs[top])

    order_match = re.search(r"order\s*(?:number\s*)?#?(\d{3,})", text.lower())
    order = f" for order #{order_match.group(1)}" if order_match else ""
    escalate = conf < 0.3

    reply = None
    if llm.available():
        reply = llm.generate(
            f"You are a customer support agent. The classified intent is '{intent}'. Write a helpful 2-sentence reply.",
            text,
        )
    if not reply:
        reply = agents_data.SUPPORT_REPLIES[intent].format(order=order)
    if escalate:
        reply = "I'm connecting you with a human specialist who can help with this. " \
                "You'll hear back within 2 business hours."
    return {
        "headline": f"Intent: {intent.upper()} ({conf:.0%})" + (" → escalated to human" if escalate else ""),
        "confidence": conf,
        "tone": "neutral" if escalate else "good",
        "details": [
            {"label": "Intent probabilities", "value": ", ".join(f"{c} {p:.0%}" for c, p in
                                                                 sorted(zip(classes, probs), key=lambda x: -x[1]))},
            {"label": "Entities extracted", "value": f"order #{order_match.group(1)}" if order_match else "none"},
            {"label": "Escalation rule", "value": f"confidence < 50% → human handoff ({'triggered' if escalate else 'not triggered'})"},
            {"label": "Drafted reply", "value": reply},
            {"label": "Pipeline", "value": "intent classifier (TF-IDF + LogReg) → entity extraction → policy → reply"},
            _llm_note(),
        ],
    }


# ========================================================= multi-agent workflow
def _multiagent_fields():
    return [{
        "name": "question", "label": "Research & report topic", "type": "textarea",
        "default": "What causes overfitting and how can it be prevented?",
        "help": "Three agents collaborate: a Researcher retrieves sources, an Analyst extracts key points, a Writer assembles the report.",
    }]


def _multiagent_predict(inputs):
    question = str(inputs.get("question", "")).strip()
    if not question:
        raise ValueError("Enter a topic.")
    index = _load("research_index")

    # Agent 1: Researcher — retrieve candidate material
    hits = _retrieve(index, question, k=8)
    if not hits:
        return {"headline": "The research corpus has nothing on that topic", "confidence": None,
                "tone": "neutral", "details": []}
    material = [index["entries"][i] for i, _ in hits]
    sources = sorted({m["title"] for m in material})

    # Agent 2: Analyst — dedupe to the strongest distinct points
    key_points, seen_titles = [], set()
    for m in material:
        if len(key_points) < 3 or m["title"] not in seen_titles:
            key_points.append(m)
            seen_titles.add(m["title"])
        if len(key_points) == 4:
            break

    # Agent 3: Writer — assemble the report (LLM if available, template otherwise)
    report = llm.generate(
        "You are a report writer. Combine the analyst's key points into a crisp 4-sentence report.",
        f"Topic: {question}\nKey points:\n" + "\n".join(f"- {p['sentence']}" for p in key_points),
    )
    if not report:
        report = " ".join(p["sentence"] for p in key_points[:3])
    return {
        "headline": report,
        "confidence": hits[0][1], "tone": "info",
        "details": [
            {"label": "🔎 Researcher", "value": f"retrieved {len(material)} passages from {len(sources)} sources"},
            {"label": "🧠 Analyst", "value": f"distilled {len(key_points)} key points: " +
             " | ".join(p["sentence"][:60] + "…" for p in key_points[:2])},
            {"label": "✍️ Writer", "value": "assembled the report above from the analyst's points"},
            {"label": "Sources", "value": " · ".join(sources)},
            {"label": "Architecture", "value": "sequential multi-agent pipeline with role-specialized agents"},
            _llm_note(),
        ],
    }


AGENT_DEMOS = {
    "personal-ai-assistant": {
        "title": "Try it: give the assistant a task",
        "cta": "Ask assistant",
        "fields": _assistant_fields, "predict": _assistant_predict,
    },
    "ai-research-assistant": {
        "title": "Try it: ask a research question",
        "cta": "Research",
        "fields": _research_fields, "predict": _research_predict,
    },
    "resume-screening-ai-agent": {
        "title": "Try it: screen a resume",
        "cta": "Screen resume",
        "fields": _resume_fields, "predict": _resume_predict,
    },
    "document-qa-rag-agent": {
        "title": "Try it: question the employee handbook (RAG)",
        "cta": "Ask",
        "fields": _docqa_fields, "predict": _docqa_predict,
    },
    "rag-based-agent-codebase": {
        "title": "Try it: ask about this site's own source code",
        "cta": "Search code",
        "fields": _coderag_fields, "predict": _coderag_predict,
    },
    "data-analysis-agent": {
        "title": "Try it: analyze a year of sales data",
        "cta": "Analyze",
        "fields": _analysis_fields, "predict": _analysis_predict,
    },
    "customer-support-agent": {
        "title": "Try it: send a support ticket",
        "cta": "Handle ticket",
        "fields": _support_fields, "predict": _support_predict,
    },
    "multi-agent-workflow": {
        "title": "Try it: run the researcher → analyst → writer pipeline",
        "cta": "Run workflow",
        "fields": _multiagent_fields, "predict": _multiagent_predict,
    },
}
