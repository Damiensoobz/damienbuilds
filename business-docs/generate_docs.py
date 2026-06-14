#!/usr/bin/env python3
"""
DamienBuilds — branded client-document generator.

Fill in the CONFIG block below with your real details ONCE, then run:

    py generate_docs.py          (Windows)
    python3 generate_docs.py     (otherwise)

It regenerates all the PDFs in ./pdf/. Anything still wrapped in
[ square brackets ] is auto-highlighted orange in the output so you can
see at a glance what's left to fill in (per-client details like names and
amounts are meant to stay as fill-in fields on the blank templates).

Requires: reportlab  ->  pip install reportlab
"""

import os
import re
import html
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

# ─────────────────────────────────────────────────────────────────────────
#  CONFIG — fill these in once. Leave the [ brackets ] on anything you don't
#  have yet; they'll render highlighted so you remember to come back to them.
# ─────────────────────────────────────────────────────────────────────────
CONFIG = {
    "legal_name": "[ FULL LEGAL NAME ]",
    "trading_as": "DamienBuilds",
    "location":   "Phoenix, Durban, South Africa",
    "address":    "[ REGISTERED / POSTAL ADDRESS ]",
    "email":      "damien@damienbuilds.dev",
    "phone":      "[ WHATSAPP / PHONE ]",
    "website":    "damienbuilds.dev",
    "vat_note":   "Not a registered VAT vendor — no VAT is charged on these fees.",
    "bank": {
        "account_name": "[ ACCOUNT NAME ]",
        "bank":         "[ BANK ]",
        "account_no":   "[ ACCOUNT NUMBER ]",
        "branch_code":  "[ BRANCH CODE ]",
        "account_type": "[ Cheque / Savings ]",
    },
    # Headline prices (keep in sync with the site's src/data/site.ts)
    "price_standard": "5,000",
    "price_founding": "2,500",
    "care_monthly":   "500",
}

# ── Brand palette ────────────────────────────────────────────────────────
NAVY   = HexColor("#0c1525")
ORANGE = HexColor("#E96530")
INK    = HexColor("#1f2733")
MUTED  = HexColor("#8a93a3")
LIGHT  = HexColor("#dfe3ea")
PANEL  = HexColor("#f4f6fa")

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Text helper: escape + auto-highlight [ placeholders ] ────────────────
def fmt(s):
    s = html.escape(str(s))
    return re.sub(r"(\[[^\]]*\])", r'<font color="#E96530"><b>\1</b></font>', s)

# ── Styles ───────────────────────────────────────────────────────────────
_ss = getSampleStyleSheet()
body   = ParagraphStyle("body",   parent=_ss["Normal"], fontName="Helvetica",
                        fontSize=9.5, leading=14, textColor=INK)
small  = ParagraphStyle("small",  parent=body, fontSize=8, leading=12, textColor=MUTED)
bodyb  = ParagraphStyle("bodyb",  parent=body, fontName="Helvetica-Bold")
title  = ParagraphStyle("title",  parent=body, fontName="Helvetica-Bold",
                        fontSize=21, leading=24, textColor=NAVY)
eyebrow= ParagraphStyle("eyebrow",parent=body, fontName="Helvetica-Bold",
                        fontSize=8, leading=10, textColor=ORANGE, spaceAfter=2)
h2     = ParagraphStyle("h2",     parent=body, fontName="Helvetica-Bold",
                        fontSize=11.5, leading=14, textColor=NAVY, spaceBefore=15)
cellL  = ParagraphStyle("cellL",  parent=body, fontSize=9, leading=13)
cellR  = ParagraphStyle("cellR",  parent=cellL, alignment=2)
cellH  = ParagraphStyle("cellH",  parent=body, fontName="Helvetica-Bold",
                        fontSize=8.5, leading=11, textColor=white)
klabel = ParagraphStyle("klabel", parent=small, fontName="Helvetica-Bold", textColor=MUTED)

def P(text, style=body):  return Paragraph(fmt(text), style)

def section(text):
    return [Paragraph(fmt(text), h2),
            HRFlowable(width=40, thickness=1.5, color=ORANGE, spaceBefore=3,
                       spaceAfter=8, hAlign="LEFT")]

def kv_table(rows, col0=42*mm):
    """Two-column key/value block (label | value)."""
    data = [[Paragraph(fmt(k), klabel), Paragraph(fmt(v), cellL)] for k, v in rows]
    t = Table(data, colWidths=[col0, None])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t

def line_items(rows, total_label="Total", total_val=None, note=None):
    """Description | Amount table with header + optional total row."""
    data = [[Paragraph("Description", cellH), Paragraph("Amount (R)", ParagraphStyle("h", parent=cellH, alignment=2))]]
    for desc, amt in rows:
        data.append([Paragraph(fmt(desc), cellL), Paragraph(fmt(amt), cellR)])
    t = Table(data, colWidths=[None, 32*mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, PANEL]),
    ]
    t.setStyle(TableStyle(style))
    out = [t]
    if total_val is not None:
        tot = Table([[Paragraph(total_label, ParagraphStyle("tl", parent=bodyb, alignment=2, textColor=NAVY)),
                      Paragraph(fmt(total_val), ParagraphStyle("tv", parent=bodyb, alignment=2, textColor=NAVY, fontSize=11))]],
                    colWidths=[None, 32*mm])
        tot.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 1.2, ORANGE),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ]))
        out.append(tot)
    if note:
        out += [Spacer(1, 4), P(note, small)]
    return out

def bullets(items, style=body):
    rows = []
    for it in items:
        rows.append([Paragraph('<font color="#E96530"><b>&#8250;</b></font>', style),
                     Paragraph(fmt(it), style)])
    t = Table(rows, colWidths=[10, None])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t

# ── Page furniture (subtle wordmark header + footer) ─────────────────────
def _decorations(canvas, doc):
    canvas.saveState()
    W, H = A4
    x = doc.leftMargin
    y = H - 30
    # wordmark: damien(light) builds(bold) .dev(orange)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica", 12)
    canvas.drawString(x, y, "damien")
    w1 = canvas.stringWidth("damien", "Helvetica", 12)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(x + w1, y, "builds")
    w2 = canvas.stringWidth("builds", "Helvetica-Bold", 12)
    canvas.setFillColor(ORANGE)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(x + w1 + w2 + 1.5, y + 4.5, ".dev")
    # thin orange bar under wordmark (echoes the favicon)
    canvas.setFillColor(ORANGE)
    canvas.rect(x, y - 4, w1 + w2, 1.4, fill=1, stroke=0)
    # right: document label
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(W - doc.rightMargin, y + 1, getattr(doc, "_label", ""))
    # footer
    fy = 30
    canvas.setStrokeColor(LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, fy, W - doc.rightMargin, fy)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(doc.leftMargin, fy - 11,
                      "DamienBuilds · Durban Web Design · " + CONFIG["email"])
    canvas.drawRightString(W - doc.rightMargin, fy - 11, "Page %d" % doc.page)
    canvas.restoreState()

def render(filename, label, story):
    path = os.path.join(OUT_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=28*mm, bottomMargin=20*mm,
                            title=label, author="DamienBuilds")
    doc._label = label
    doc.build(story, onFirstPage=_decorations, onLaterPages=_decorations)
    print("  wrote", os.path.relpath(path))

def doc_head(eyebrow_text, title_text, meta_rows):
    """Eyebrow + big title on the left, a small meta box on the right."""
    left = [P(eyebrow_text, eyebrow), P(title_text, title)]
    meta = Table([[Paragraph(fmt(k), klabel), Paragraph(fmt(v), ParagraphStyle("m", parent=cellL, alignment=2))]
                  for k, v in meta_rows], colWidths=[20*mm, 32*mm])
    meta.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    head = Table([[left, meta]], colWidths=[None, 52*mm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return [head, Spacer(1, 6), HRFlowable(width="100%", thickness=0.6, color=LIGHT), Spacer(1, 12)]


# ═════════════════════════════════════════════════════════════════════════
#  1. QUOTE / PROPOSAL
# ═════════════════════════════════════════════════════════════════════════
def build_quote():
    s = doc_head("QUOTE", "Project Quote", [
        ("Quote no.", "[ Q-001 ]"),
        ("Date", "[ DD MMM 2026 ]"),
        ("Valid until", "[ +30 days ]"),
    ])
    s += [P("Prepared for", klabel), Spacer(1, 2),
          P("[ CLIENT NAME / BUSINESS ]", bodyb),
          P("[ CLIENT EMAIL · PHONE ]", small), Spacer(1, 12)]
    s += [P("Thanks for the chat! Here's everything in one place. This quote is a fixed "
            "price for the scope below — no surprise invoices. It's valid for 30 days.", body),
          Spacer(1, 10)]
    s += line_items(
        [("The Standard Build — complete 5-page website (domain & hosting setup included)",
          CONFIG["price_standard"]),
         ("[ Add-on, e.g. Business email setup (Google Workspace) ]", "[ 750 ]"),
         ("[ Add-on, e.g. Google Business Profile setup ]", "[ 750 ]"),
         ("Founding-client discount (if applicable)", "[ -2,500 ]")],
        total_label="Total (once-off)", total_val="[ TOTAL ]",
        note="Add or remove lines to match the agreed scope. " + CONFIG["vat_note"])
    s += [Spacer(1, 14)]
    s += section("What happens next")
    s += [bullets([
        "Reply to accept, and I'll send a deposit invoice for 50%.",
        "The other 50% is due on completion, before the site goes live.",
        "Two rounds of revisions are included. Timeline is usually 2–3 weeks once I have your content.",
    ])]
    s += [Spacer(1, 12)]
    s += section("A note on yearly running costs (paid to others, not me)")
    s += [bullets([
        "Domain (.co.za): ~R150–R300 / year, in your name.",
        "Hosting: often R0 / year at your size — if a paid plan is ever needed I'll tell you the exact figure first.",
    ], small)]
    render("01-quote.pdf", "Quote · DamienBuilds", s)


# ═════════════════════════════════════════════════════════════════════════
#  2 & 3. INVOICE (deposit + final)
# ═════════════════════════════════════════════════════════════════════════
def build_invoice(kind):
    is_dep = kind == "deposit"
    label = "Deposit Invoice" if is_dep else "Final Invoice"
    s = doc_head("INVOICE", label, [
        ("Invoice no.", "[ INV-001 ]" if is_dep else "[ INV-002 ]"),
        ("Date", "[ DD MMM 2026 ]"),
        ("Due", "[ +7 days ]"),
    ])
    frm = kv_table([
        ("From", CONFIG["legal_name"] + ", t/a " + CONFIG["trading_as"]),
        ("", CONFIG["location"]),
        ("", CONFIG["email"]),
    ])
    to = kv_table([
        ("Billed to", "[ CLIENT NAME / BUSINESS ]"),
        ("", "[ CLIENT ADDRESS ]"),
        ("", "[ CLIENT EMAIL ]"),
    ])
    cols = Table([[frm, to]], colWidths=[None, None])
    cols.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (0, 0), 0),
                              ("LEFTPADDING", (1, 0), (1, 0), 12)]))
    s += [cols, Spacer(1, 14)]

    if is_dep:
        rows = [("Website build — 50% deposit to begin work", "[ 2,500 ]")]
        total = "[ 2,500 ]"
        closing = ("This deposit confirms your booking and starts the work. The remaining "
                   "50% falls due on completion, before go-live and handover.")
    else:
        rows = [("Website build — final 50% on completion", "[ 2,500 ]"),
                ("[ Any approved extras / extra revision rounds ]", "[ 0 ]")]
        total = "[ 2,500 ]"
        closing = ("Final payment. Once this clears, ownership transfers to you and I hand "
                   "over every login, password, and renewal date.")
    s += line_items(rows, total_label="Amount due", total_val=total,
                    note=CONFIG["vat_note"])
    s += [Spacer(1, 16)]
    s += section("Payment")
    b = CONFIG["bank"]
    s += [kv_table([
        ("Account name", b["account_name"]),
        ("Bank", b["bank"]),
        ("Account no.", b["account_no"]),
        ("Branch code", b["branch_code"]),
        ("Account type", b["account_type"]),
        ("Reference", "[ CLIENT NAME ] / [ INV no. ]"),
    ])]
    s += [Spacer(1, 12), P(closing, small)]
    fname = "02-invoice-deposit.pdf" if is_dep else "03-invoice-final.pdf"
    render(fname, label + " · DamienBuilds", s)


# ═════════════════════════════════════════════════════════════════════════
#  4. HANDOVER PACK
# ═════════════════════════════════════════════════════════════════════════
def build_handover():
    s = doc_head("HANDOVER PACK", "Your Site, Your Keys", [
        ("Client", "[ CLIENT NAME ]"),
        ("Site", "[ yourdomain.co.za ]"),
        ("Date", "[ DD MMM 2026 ]"),
    ])
    s += [P("Everything you need to fully own and run your website is below. You own all of "
            "it outright — no lock-in, no leash. Keep this document somewhere safe (and maybe "
            "not in your inbox forever).", body), Spacer(1, 12)]

    s += section("Domain")
    s += [kv_table([("Domain", "[ yourdomain.co.za ]"), ("Registrar", "[ e.g. Domains.co.za ]"),
                    ("Login URL", "[ registrar login ]"), ("Username", "[ ___ ]"),
                    ("Password", "[ ___ ]"), ("Renews", "[ DD MMM ]  ·  ~R[ 150–300 ] / year")])]
    s += section("Hosting")
    s += [kv_table([("Provider", "[ e.g. Vercel ]"), ("Login URL", "[ host login ]"),
                    ("Username", "[ ___ ]"), ("Password", "[ ___ ]"),
                    ("Plan / cost", "[ Free tier  ·  R0 / year ]")])]
    s += section("Business email")
    s += [kv_table([("Provider", "[ Google Workspace / N/A ]"), ("Address(es)", "[ you@yourdomain.co.za ]"),
                    ("Login URL", "[ mail login ]"), ("Password", "[ ___ ]"),
                    ("Renews", "[ DD MMM ]  ·  R[ ___ ] / month")])]
    s += section("Website admin / other accounts")
    s += [kv_table([("Admin / CMS", "[ login + password, if any ]"),
                    ("Analytics", "[ Google Analytics access, if set up ]"),
                    ("Google Business Profile", "[ access, if set up ]"),
                    ("Other", "[ anything else ]")])]

    s += [Spacer(1, 6)]
    s += section("What renews, and when")
    s += [P("The short version, so nothing expires quietly at 2am:", small), Spacer(1, 4)]
    s += line_items([("Domain renewal — [ DD MMM ]", "[ 150–300 ] /yr"),
                     ("Hosting — [ DD MMM ]", "[ 0 ] /yr"),
                     ("Email — [ DD MMM ]", "[ ___ ] /mo")])
    s += [Spacer(1, 12)]
    s += section("Need a hand later?")
    s += [P("You can do changes yourself, hire anyone you like, or come back to me — "
            "email " + CONFIG["email"] + ". Prefer to never think about it? Ask about the "
            "optional Care Plan and I'll keep the renewals and small changes handled.", body)]
    render("04-handover.pdf", "Handover · DamienBuilds", s)


# ═════════════════════════════════════════════════════════════════════════
#  5. CARE PLAN TERMS
# ═════════════════════════════════════════════════════════════════════════
def build_careplan():
    s = doc_head("CARE PLAN", "Care Plan — Terms", [
        ("Price", "R" + CONFIG["care_monthly"] + " / month"),
        ("Term", "Month-to-month"),
    ])
    s += [P("Most of my clients don't need ongoing help — that's the point of how I hand "
            "things over. But if you'd rather never think about your website again, the Care "
            "Plan has you covered. Here's exactly what it is and isn't.", body), Spacer(1, 10)]
    s += section("What you get every month")
    s += [bullets([
        "Your hosting and domain renewals managed — nothing lapses or expires.",
        "Up to 2 small content changes a month (new prices, updated hours, a swapped photo).",
        "Uptime monitoring — if your site goes down, I usually know before you do.",
        "A short monthly summary of your traffic, in plain English.",
        "Priority WhatsApp support — you skip the queue.",
    ])]
    s += section("What counts as a “small change”")
    s += [P("A small change is a quick edit to existing content — roughly 30 minutes or less, "
            "with no new pages, sections, or features. Bigger work (new pages, redesigns, new "
            "functionality) is quoted separately, and Care Plan clients get a friendly rate.", body)]
    s += section("The fine print")
    s += [bullets([
        "R" + CONFIG["care_monthly"] + " per month, billed [ monthly / annually ] by EFT.",
        "Month-to-month. Cancel anytime with [ 30 ] days' notice — no penalty.",
        "Every account (domain, hosting, email) stays registered in your name. This is a "
        "convenience, never a lock-in.",
        "Unused monthly changes don't roll over.",
        "If you cancel, your site keeps running exactly as it is — you just take the wheel again.",
    ])]
    s += [Spacer(1, 10), P(CONFIG["vat_note"], small)]
    render("05-care-plan.pdf", "Care Plan · DamienBuilds", s)


if __name__ == "__main__":
    print("Generating DamienBuilds documents ->", OUT_DIR)
    build_quote()
    build_invoice("deposit")
    build_invoice("final")
    build_handover()
    build_careplan()
    print("Done.")
