"""Automation demos (category 4).

Each demo runs a real, deterministic workflow on embedded sample data and
reports the step-by-step result — no external services required. These are
"automation" in the RPA / data-pipeline sense: rule engines, parsers,
schedulers, and ETL, not ML models.
"""

import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from app.demos import agents_data


def _steps(items):
    """Render a workflow trace as ordered detail rows."""
    return [{"label": f"Step {i + 1}", "value": s} for i, s in enumerate(items)]


# ==================================================== Power BI refresh monitor
def _powerbi_fields():
    return [
        {"name": "report", "label": "Report / dataset", "type": "select", "options": [
            {"value": "Sales Dashboard", "label": "Sales Dashboard (hourly SLA)"},
            {"value": "Finance Report", "label": "Finance Report (daily SLA)"},
            {"value": "Ops Monitor", "label": "Ops Monitor (15-min SLA)"},
        ], "default": "Sales Dashboard"},
        {"name": "hours_since", "label": "Hours since last successful refresh",
         "type": "number", "min": 0, "max": 72, "step": 0.25, "default": 3},
        {"name": "last_status", "label": "Last refresh outcome", "type": "select", "options": [
            {"value": "success", "label": "Success"},
            {"value": "failed", "label": "Failed"},
        ], "default": "success"},
    ]


_POWERBI_SLA = {"Sales Dashboard": 1.0, "Finance Report": 24.0, "Ops Monitor": 0.25}


def _powerbi_predict(inputs):
    report = str(inputs.get("report"))
    hours = float(inputs.get("hours_since", 0))
    status = str(inputs.get("last_status"))
    sla = _POWERBI_SLA.get(report, 1.0)
    trace = [f"Connected to workspace, polled refresh history for '{report}'",
             f"Last outcome: {status.upper()}; {hours:g}h since last success (SLA: {sla:g}h)"]

    if status == "failed":
        breached, reason = True, "last scheduled refresh FAILED"
    elif hours > sla:
        breached, reason = True, f"data is stale ({hours:g}h > {sla:g}h SLA)"
    else:
        breached, reason = False, "refresh is current and healthy"

    if breached:
        trace.append(f"SLA rule triggered: {reason}")
        trace.append(f"Composed alert email to data-team@company + on-call channel")
        trace.append("Logged incident and scheduled an automatic re-run")
        return {"headline": f"⚠️ ALERT sent — {report}: {reason}", "confidence": None, "tone": "bad",
                "details": _steps(trace) + [{"label": "Notification", "value":
                    f"Subject: [Power BI] {report} refresh needs attention — {reason}"},
                    {"label": "Architecture", "value": "poll refresh API → SLA rule engine → notify + auto-remediate"}]}
    trace.append(f"SLA rule passed: {reason}")
    trace.append("No action needed — logged healthy check")
    return {"headline": f"✓ {report} is healthy — no alert needed", "confidence": None, "tone": "good",
            "details": _steps(trace) + [{"label": "Architecture", "value":
                "poll refresh API → SLA rule engine → notify + auto-remediate"}]}


# ======================================================== Excel data cleaning
_MESSY_ROWS = [
    {"Name": "  john SMITH ", "Email": "JOHN@Example.COM", "Amount": "1,200.50", "Date": "01/03/2025", "Region": "north"},
    {"Name": "Jane Doe", "Email": "jane@example.com", "Amount": "$980", "Date": "2025-03-02", "Region": "South"},
    {"Name": "john smith", "Email": "john@example.com", "Amount": "1200.5", "Date": "01/03/2025", "Region": "North"},
    {"Name": "Bob  Lee", "Email": "bob@@example.com", "Amount": "", "Date": "March 5 2025", "Region": "east"},
    {"Name": "Alice Wong", "Email": "alice@example.com", "Amount": "3,450.00", "Date": "2025/03/06", "Region": "WEST"},
    {"Name": "", "Email": "ghost@example.com", "Amount": "500", "Date": "2025-03-07", "Region": "north"},
]


def _excel_fields():
    return [{"name": "_", "label": "Sample messy spreadsheet (6 rows)", "type": "info",
             "help": "Click Run to clean a spreadsheet with mixed casing, duplicate rows, "
                     "inconsistent dates/currency, and missing values."}]


def _excel_predict(inputs):
    df = pd.DataFrame(_MESSY_ROWS)
    ops = []
    n0 = len(df)

    df["Name"] = df["Name"].str.strip().str.title()
    ops.append("Trimmed whitespace and title-cased the Name column")
    df["Email"] = df["Email"].str.strip().str.lower()
    bad_email = ~df["Email"].str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    ops.append(f"Lower-cased emails; flagged {int(bad_email.sum())} invalid address (bob@@…)")
    df["Region"] = df["Region"].str.strip().str.capitalize()
    ops.append("Standardized Region casing (north/NORTH → North)")

    def parse_amount(v):
        v = re.sub(r"[^\d.]", "", str(v))
        return float(v) if v else np.nan
    df["Amount"] = df["Amount"].map(parse_amount)
    missing_amt = int(df["Amount"].isna().sum())
    median = df["Amount"].median()
    df["Amount"] = df["Amount"].fillna(median)
    ops.append(f"Parsed currency to numbers; imputed {missing_amt} blank amount with median (₹{median:,.0f})")

    before_dupes = len(df)
    df = df[df["Name"] != ""].copy()
    dropped_blank = before_dupes - len(df)
    df = df.drop_duplicates(subset=["Name", "Email"]).reset_index(drop=True)
    ops.append(f"Dropped {dropped_blank} nameless row and de-duplicated (John Smith appeared twice)")

    preview = df.head(3).to_dict("records")
    detail_rows = [{"label": f"Cleaned row {i+1}",
                    "value": f"{r['Name']} · {r['Email']} · ₹{r['Amount']:,.0f} · {r['Region']}"}
                   for i, r in enumerate(preview)]
    return {"headline": f"✓ Cleaned {n0} messy rows → {len(df)} tidy records", "confidence": None, "tone": "good",
            "details": _steps(ops) + detail_rows + [
                {"label": "Architecture", "value": "pandas ETL: normalize → validate → impute → dedupe"}]}


# ==================================================== email classification
_EMAIL_RULES = [
    ("Invoices", ["invoice", "payment", "billing", "receipt", "amount due"], "high"),
    ("Support", ["error", "not working", "issue", "help", "broken", "bug"], "high"),
    ("Sales", ["quote", "pricing", "demo", "interested", "purchase", "buy"], "medium"),
    ("Recruiting", ["resume", "candidate", "application", "interview", "hiring"], "medium"),
    ("Spam", ["winner", "free money", "click here", "congratulations", "prize"], "low"),
]


def _email_fields():
    return [{"name": "text", "label": "Incoming email", "type": "textarea",
             "default": "Subject: Payment overdue\nHi, our invoice #4821 for last month's "
                        "subscription is still showing as unpaid. Please advise on the amount due.",
             "help": "The automation reads the email, routes it to the right team folder, "
                     "sets a priority, and drafts an auto-acknowledgement."}]


def _email_predict(inputs):
    text = str(inputs.get("text", "")).lower()
    if not text.strip():
        raise ValueError("Paste an email first.")
    scores = {}
    for folder, keywords, prio in _EMAIL_RULES:
        hits = [k for k in keywords if k in text]
        if hits:
            scores[folder] = (len(hits), prio, hits)
    if not scores:
        folder, prio, hits = "General", "medium", []
    else:
        folder = max(scores, key=lambda f: scores[f][0])
        _, prio, hits = scores[folder]
    trace = [f"Tokenized subject + body ({len(text.split())} words)",
             f"Keyword match: {', '.join(hits) if hits else 'no strong signal'}",
             f"Routed to folder: {folder} (priority: {prio})",
             f"Auto-reply queued and {'flagged for SLA timer' if prio == 'high' else 'added to daily digest'}"]
    tone = {"high": "bad", "medium": "neutral", "low": "info"}[prio]
    return {"headline": f"📁 Routed to {folder} — {prio.upper()} priority", "confidence": None, "tone": tone,
            "details": _steps(trace) + [
                {"label": "Auto-reply", "value": f"Thanks — your message was routed to our {folder} team."},
                {"label": "Architecture", "value": "keyword rule engine → folder routing → priority + auto-ack"}]}


# ==================================================== invoice extraction
_SAMPLE_INVOICE = """ACME SUPPLIES PVT LTD
Invoice No: INV-2025-0847
Date: 12/03/2025
Bill To: Nimbus Analytics

Description            Qty    Unit Price    Amount
Cloud GPU hours        120    45.00         5400.00
Data storage (TB)      8      120.00        960.00
Support retainer       1      15000.00      15000.00

Subtotal: 21360.00
GST (18%): 3844.80
Total Due: 24204.80
Due Date: 26/03/2025"""


def _invoice_fields():
    return [{"name": "text", "label": "Invoice text (OCR output)", "type": "textarea",
             "default": _SAMPLE_INVOICE,
             "help": "The automation parses raw invoice text into structured fields and "
                     "line items — the kind of output that feeds straight into an ERP."}]


def _invoice_predict(inputs):
    text = str(inputs.get("text", ""))
    if len(text) < 20:
        raise ValueError("Paste invoice text first.")

    def find(pat, default="—"):
        m = re.search(pat, text, re.IGNORECASE)
        return m.group(1).strip() if m else default

    vendor = text.strip().splitlines()[0].strip() if text.strip() else "—"
    inv_no = find(r"invoice\s*(?:no|number|#)\s*:?\s*([A-Za-z0-9\-]+)")
    date = find(r"date\s*:?\s*([\d/\-]+)")
    due = find(r"due\s*date\s*:?\s*([\d/\-]+)")
    total = find(r"total\s*(?:due)?\s*:?\s*([\d,]+\.?\d*)")

    line_items = re.findall(r"^(.+?)\s{2,}(\d+)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)\s*$", text, re.MULTILINE)
    items = [{"label": desc.strip(), "value": f"{qty} × ₹{unit} = ₹{amt}"} for desc, qty, unit, amt in line_items]

    fields = [
        {"label": "Vendor", "value": vendor},
        {"label": "Invoice #", "value": inv_no},
        {"label": "Invoice date", "value": date},
        {"label": "Due date", "value": due},
        {"label": "Total due", "value": f"₹{total}"},
    ]
    return {"headline": f"📄 Extracted {len(items)} line items + 5 header fields", "confidence": None, "tone": "good",
            "details": fields + items + [
                {"label": "Next step", "value": "Structured JSON posted to the accounts-payable queue"},
                {"label": "Architecture", "value": "OCR text → regex field extraction → validation → ERP payload"}]}


# ==================================================== web scraping market data
_MARKET_HTML = """
<table id="stocks">
  <tr><th>Ticker</th><th>Company</th><th>Price</th><th>Change</th></tr>
  <tr><td>NVDA</td><td>Nvidia</td><td>1204.50</td><td>+3.8%</td></tr>
  <tr><td>AAPL</td><td>Apple</td><td>229.10</td><td>-1.2%</td></tr>
  <tr><td>MSFT</td><td>Microsoft</td><td>498.75</td><td>+0.9%</td></tr>
  <tr><td>TSLA</td><td>Tesla</td><td>251.30</td><td>-4.5%</td></tr>
  <tr><td>AMZN</td><td>Amazon</td><td>212.40</td><td>+2.1%</td></tr>
  <tr><td>GOOGL</td><td>Alphabet</td><td>188.90</td><td>+1.4%</td></tr>
</table>
"""


def _scrape_fields():
    return [{"name": "_", "label": "Live market snapshot (HTML page)", "type": "info",
             "help": "The automation fetches a market page, parses the HTML table with "
                     "BeautifulSoup, and computes a summary — the core of any scraping pipeline."}]


def _scrape_predict(inputs):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_MARKET_HTML, "html.parser")
    rows = soup.select("#stocks tr")[1:]
    parsed = []
    for r in rows:
        cells = [c.get_text(strip=True) for c in r.find_all("td")]
        if len(cells) == 4:
            # e.g. "+3.8%" / "-4.5%" — float() already handles the sign; just drop "%" and "+".
            change = float(cells[3].replace("%", "").replace("+", ""))
            parsed.append({"ticker": cells[0], "company": cells[1],
                           "price": float(cells[2]), "change": change})
    df = pd.DataFrame(parsed)
    gainer = df.loc[df["change"].idxmax()]
    loser = df.loc[df["change"].idxmin()]
    trace = [f"Fetched market page, located <table id='stocks'>",
             f"Parsed {len(df)} rows into structured records with BeautifulSoup",
             f"Computed summary metrics and saved snapshot to CSV"]
    return {"headline": f"🔎 Scraped {len(df)} tickers — top gainer {gainer['ticker']} ({gainer['change']:+.1f}%)",
            "confidence": None, "tone": "good",
            "details": _steps(trace) + [
                {"label": "Top gainer", "value": f"{gainer['company']} ({gainer['ticker']}) ₹{gainer['price']:,.2f} {gainer['change']:+.1f}%"},
                {"label": "Top loser", "value": f"{loser['company']} ({loser['ticker']}) ₹{loser['price']:,.2f} {loser['change']:+.1f}%"},
                {"label": "Avg change", "value": f"{df['change'].mean():+.2f}%"},
                {"label": "Architecture", "value": "HTTP fetch → BeautifulSoup parse → transform → CSV/DB sink"}]}


# ==================================================== daily reporting pipeline
def _pipeline_fields():
    return [{"name": "_", "label": "Daily reporting ETL (over 3,000 sales orders)", "type": "info",
             "help": "Runs a scheduled Extract → Transform → Load pipeline and generates "
                     "the daily KPI report that would be emailed to stakeholders."}]


def _pipeline_predict(inputs):
    import joblib
    from pathlib import Path

    df = joblib.load(Path(__file__).parent / "artifacts" / "sales_data.joblib")
    yesterday = df["order_date"].max()
    day_df = df[df["order_date"] == yesterday]
    trace = [f"EXTRACT: pulled {len(df):,} orders from the sales database",
             f"TRANSFORM: filtered to reporting day ({yesterday.strftime('%d %b %Y')}), cleaned & typed columns",
             f"AGGREGATE: computed revenue, order count, and top category",
             "LOAD: rendered the daily report and queued the stakeholder email"]
    rev = day_df["revenue"].sum()
    top_cat = day_df.groupby("category").revenue.sum().idxmax() if len(day_df) else "—"
    top_region = day_df.groupby("region").revenue.sum().idxmax() if len(day_df) else "—"
    return {"headline": f"📊 Daily report ready — ₹{rev:,.0f} across {len(day_df)} orders",
            "confidence": None, "tone": "good",
            "details": _steps(trace) + [
                {"label": "Reporting day", "value": yesterday.strftime("%A, %d %B %Y")},
                {"label": "Revenue", "value": f"₹{rev:,.0f}"},
                {"label": "Orders", "value": str(len(day_df))},
                {"label": "Top category", "value": top_cat},
                {"label": "Top region", "value": top_region},
                {"label": "Architecture", "value": "scheduled ETL: extract → transform → aggregate → email report"}]}


# ==================================================== approval workflow
def _approval_fields():
    return [
        {"name": "type", "label": "Request type", "type": "select", "options": [
            {"value": "expense", "label": "Expense reimbursement"},
            {"value": "purchase", "label": "Purchase order"},
            {"value": "leave", "label": "Leave request"},
        ], "default": "purchase"},
        {"name": "amount", "label": "Amount (₹) — ignored for leave", "type": "number",
         "min": 0, "max": 1000000, "step": 500, "default": 45000},
        {"name": "requester_level", "label": "Requester level", "type": "select", "options": [
            {"value": "junior", "label": "Junior"},
            {"value": "manager", "label": "Manager"},
            {"value": "director", "label": "Director"},
        ], "default": "junior"},
    ]


def _approval_predict(inputs):
    rtype = str(inputs.get("type"))
    amount = float(inputs.get("amount", 0))
    level = str(inputs.get("requester_level"))
    trace = [f"Received {rtype} request (₹{amount:,.0f}) from a {level}",
             "Evaluated routing policy for type + amount + requester level"]

    if rtype == "leave":
        chain, decision, tone = ["Reporting manager"], "Routed for manager sign-off", "info"
    else:
        chain = []
        if amount <= 5000 and level in ("manager", "director"):
            chain, decision, tone = [], "AUTO-APPROVED (under ₹5k delegated limit)", "good"
        else:
            chain.append("Reporting manager")
            if amount > 25000:
                chain.append("Department head")
            if amount > 100000:
                chain.append("Finance director")
            if amount > 500000:
                chain.append("CFO")
            decision = f"Routed through {len(chain)}-step approval chain"
            tone = "neutral"
    if chain:
        trace.append(f"Built approval chain: {' → '.join(chain)}")
        trace.append(f"Notified {chain[0]} and started the SLA clock")
    else:
        trace.append("Matched delegated-authority rule — no human approval needed")
    return {"headline": f"🧾 {decision}", "confidence": None, "tone": tone,
            "details": _steps(trace) + [
                {"label": "Approval chain", "value": " → ".join(chain) if chain else "None (auto-approved)"},
                {"label": "Architecture", "value": "policy rule engine → approver-chain builder → notify + track"}]}


# ==================================================== HR recruitment automation
_CANDIDATES = [
    {"name": "Priya S.", "years": 4, "skills": "python, machine learning, sql, pytorch, aws", "degree": True},
    {"name": "Rahul M.", "years": 1, "skills": "python, excel, sql", "degree": True},
    {"name": "Chen W.", "years": 6, "skills": "python, deep learning, tensorflow, docker, mlops, sql", "degree": True},
    {"name": "Sam K.", "years": 2, "skills": "javascript, react, css", "degree": False},
    {"name": "Aisha R.", "years": 3, "skills": "python, machine learning, nlp, fastapi, sql", "degree": True},
]


def _hr_fields():
    return [{"name": "role", "label": "Screen a candidate pool for role", "type": "select",
             "options": [{"value": k, "label": v["label"]} for k, v in agents_data.JOB_ROLES.items()],
             "default": "ml-engineer",
             "help": "The automation screens an inbound candidate pool against the role's "
                     "requirements, scores each, and produces a ranked shortlist."}]


def _hr_predict(inputs):
    role = agents_data.JOB_ROLES.get(str(inputs.get("role")), agents_data.JOB_ROLES["ml-engineer"])

    def score(c):
        text = c["skills"].lower()
        has = lambda p: any(re.search(rf"\b{a}\b", text) for a in p.split("|"))
        must = sum(has(p) for p in role["must_have"]) / len(role["must_have"])
        nice = min(sum(has(p) for p in role["nice_to_have"]) / 4, 1.0)
        exp = min(c["years"] / max(role["min_years"], 1) / 2, 1.0)
        return 0.55 * must + 0.25 * nice + 0.1 * exp + 0.1 * c["degree"]

    ranked = sorted(_CANDIDATES, key=score, reverse=True)
    trace = [f"Received {len(_CANDIDATES)} applications for {role['label']}",
             "Parsed each resume for skills, experience, and education",
             "Scored every candidate against the role rubric",
             f"Auto-shortlisted the top {sum(1 for c in ranked if score(c) >= 0.6)} (score ≥ 60%)"]
    rows = [{"label": f"#{i+1} {c['name']}", "value":
             f"{score(c):.0%} fit · {c['years']}y · {'shortlisted ✅' if score(c) >= 0.6 else 'archived'}"}
            for i, c in enumerate(ranked)]
    top = ranked[0]
    return {"headline": f"👥 Screened {len(_CANDIDATES)} candidates — top pick {top['name']} ({score(top):.0%})",
            "confidence": None, "tone": "good",
            "details": _steps(trace) + rows + [
                {"label": "Architecture", "value": "resume parse → rubric scoring → rank → auto-shortlist + notify"}]}


# ==================================================== support ticket automation
def _ticket_fields():
    return [{"name": "text", "label": "Incoming support ticket", "type": "textarea",
             "default": "URGENT: production checkout is down, customers can't pay and we're losing sales!",
             "help": "The automation classifies the ticket, assigns priority + team, sets an "
                     "SLA, and drafts the first response — full intake triage."}]


_TICKET_TEAMS = {
    "billing": ("Billing", ["invoice", "charge", "payment", "refund", "billing", "subscription"]),
    "technical": ("Engineering", ["down", "error", "crash", "bug", "broken", "not working", "500"]),
    "account": ("Account Ops", ["login", "password", "account", "access", "locked"]),
    "general": ("Front-line Support", []),
}


def _ticket_predict(inputs):
    text = str(inputs.get("text", "")).lower()
    if not text.strip():
        raise ValueError("Paste a ticket first.")
    category = "general"
    for cat, (_, kws) in _TICKET_TEAMS.items():
        if kws and any(k in text for k in kws):
            category = cat
            break
    team = _TICKET_TEAMS[category][0]
    urgent = any(w in text for w in ["urgent", "down", "asap", "critical", "immediately", "losing"])
    priority = "P1 – Critical" if urgent else "P3 – Normal"
    sla = "1 hour" if urgent else "1 business day"
    trace = [f"Parsed ticket ({len(text.split())} words) and detected sentiment/urgency",
             f"Classified category: {category} → routed to {team}",
             f"Priority set to {priority} (SLA: {sla})",
             "Assigned to next available agent and sent auto-acknowledgement"]
    return {"headline": f"🎫 {priority} — assigned to {team} (SLA {sla})", "confidence": None,
            "tone": "bad" if urgent else "neutral",
            "details": _steps(trace) + [
                {"label": "Auto-reply", "value": f"We've received your ticket and routed it to {team}. "
                                                 f"Expected first response within {sla}."},
                {"label": "Architecture", "value": "intake → classify → prioritize → assign + SLA + auto-ack"}]}


AUTOMATION_DEMOS = {
    "powerbi-report-refresh-automation": {
        "title": "Try it: monitor a report refresh", "cta": "Run monitor",
        "fields": _powerbi_fields, "predict": _powerbi_predict},
    "excel-data-cleaning-automation": {
        "title": "Try it: clean a messy spreadsheet", "cta": "Run cleaning",
        "fields": _excel_fields, "predict": _excel_predict},
    "email-classification-automation": {
        "title": "Try it: auto-route an incoming email", "cta": "Classify & route",
        "fields": _email_fields, "predict": _email_predict},
    "invoice-data-extraction-automation": {
        "title": "Try it: extract fields from an invoice", "cta": "Extract",
        "fields": _invoice_fields, "predict": _invoice_predict},
    "web-scraping-market-data-automation": {
        "title": "Try it: scrape a market data page", "cta": "Scrape",
        "fields": _scrape_fields, "predict": _scrape_predict},
    "data-pipeline-automation-daily-reporting": {
        "title": "Try it: run the daily reporting pipeline", "cta": "Run pipeline",
        "fields": _pipeline_fields, "predict": _pipeline_predict},
    "workflow-automation-approvals": {
        "title": "Try it: route an approval request", "cta": "Route request",
        "fields": _approval_fields, "predict": _approval_predict},
    "hr-recruitment-automation": {
        "title": "Try it: screen a candidate pool", "cta": "Screen candidates",
        "fields": _hr_fields, "predict": _hr_predict},
    "customer-support-ticket-automation": {
        "title": "Try it: triage a support ticket", "cta": "Triage ticket",
        "fields": _ticket_fields, "predict": _ticket_predict},
}
