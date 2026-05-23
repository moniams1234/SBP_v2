"""
Premium finance dashboard CSS — matches SBP Valuation App v1 style.
IBM Plex Sans/Mono · Navy gradient sidebar · Dark readable input text.
"""

PREMIUM_CSS = """
<style>
  /* ── Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 14px;
  }

  /* ── Main background ── */
  .stApp { background: #F8FAFB !important; }
  .main .block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
    max-width: 1300px;
  }

  /* ══════════════════════════════════════════════
     SIDEBAR — navy gradient, white text on labels,
     dark text INSIDE input fields
  ══════════════════════════════════════════════ */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D2137 0%, #1A3A5C 60%, #2E6DA4 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
  }

  /* Labels, headings, captions in sidebar → light */
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3,
  [data-testid="stSidebar"] .stMarkdown,
  [data-testid="stSidebar"] .stCaption {
    color: #D4E8F8 !important;
  }

  /* Input BOXES background + dark text so it's readable */
  [data-testid="stSidebar"] input,
  [data-testid="stSidebar"] textarea,
  [data-testid="stSidebar"] [data-baseweb="select"] div,
  [data-testid="stSidebar"] [data-baseweb="input"] input,
  [data-testid="stSidebar"] [data-baseweb="base-input"] input {
    background: #FFFFFF !important;
    color: #0D2137 !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
  }

  /* Select dropdown value text */
  [data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
  [data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #0D2137 !important;
  }

  /* Selectbox container */
  [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
  }

  /* Number input container */
  [data-testid="stSidebar"] [data-baseweb="base-input"] {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
  }

  /* Date inputs */
  [data-testid="stSidebar"] [data-testid="stDateInput"] input {
    background: #FFFFFF !important;
    color: #0D2137 !important;
  }

  /* Radio buttons */
  [data-testid="stSidebar"] .stRadio label { color: #D4E8F8 !important; }

  /* Dividers */
  [data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
    margin: 10px 0 !important;
  }

  /* Info box in sidebar */
  [data-testid="stSidebar"] .stAlert {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
  }
  [data-testid="stSidebar"] .stAlert p { color: #FFFFFF !important; font-weight: 600 !important; }

  /* ══════════════════════════════════════════════
     MAIN AREA INPUTS — also always dark text
  ══════════════════════════════════════════════ */
  .main input,
  .main textarea,
  .main [data-baseweb="base-input"] input,
  .main [data-baseweb="select"] > div:first-child {
    color: #0D2137 !important;
    font-weight: 500 !important;
  }

  /* ── App banner ── */
  .app-banner {
    background: linear-gradient(135deg, #0D2137 0%, #1A3A5C 55%, #2E6DA4 100%);
    padding: 22px 30px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(13,33,55,0.20);
  }
  .app-banner h1 {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.02em;
    font-family: 'IBM Plex Sans', sans-serif;
  }
  .app-banner p {
    color: #90C4E8;
    font-size: 13px;
    margin: 5px 0 0 0;
  }

  /* ── Section header — same gradient as sidebar ── */
  .section-hdr {
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(90deg, #0D2137, #1A3A5C);
    color: #FFFFFF !important;
    border-radius: 8px;
    padding: 10px 18px;
    margin: 22px 0 14px 0;
    box-shadow: 0 2px 8px rgba(13,33,55,0.15);
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.02em;
  }
  .section-hdr span { color: #FFFFFF !important; }

  /* ── Subsequent period section — distinct amber accent ── */
  .section-hdr-subseq {
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(90deg, #78350F, #B45309);
    color: #FFFFFF !important;
    border-radius: 8px;
    padding: 10px 18px;
    margin: 28px 0 14px 0;
    box-shadow: 0 2px 8px rgba(120,53,15,0.20);
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.02em;
  }
  .section-hdr-subseq span { color: #FFFFFF !important; }

  /* ── KPI cards ── */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(195px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
  }
  .kpi-card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 16px 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-left: 4px solid #2E6DA4;
  }
  .kpi-label {
    font-size: 10.5px;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
  }
  .kpi-value {
    font-size: 21px;
    font-weight: 700;
    color: #0D2137;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.2;
  }
  .kpi-sub {
    font-size: 11px;
    color: #94A3B8;
    margin-top: 4px;
  }
  .kpi-card.green { border-left-color: #10B981; }
  .kpi-card.green .kpi-value { color: #065F46; }
  .kpi-card.amber { border-left-color: #F59E0B; }
  .kpi-card.amber .kpi-value { color: #78350F; }
  .kpi-card.red   { border-left-color: #EF4444; }
  .kpi-card.red   .kpi-value { color: #7F1D1D; }
  .kpi-card.blue  { border-left-color: #2563EB; }
  .kpi-card.blue  .kpi-value { color: #1E3A8A; }

  /* ── Journal table ── */
  .journal-wrap { overflow-x: auto; margin: 10px 0 16px 0; }
  .journal-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  }
  .journal-table thead th {
    background: #0D2137;
    color: #FFFFFF;
    padding: 11px 16px;
    text-align: left;
    font-weight: 600;
    letter-spacing: 0.04em;
    font-size: 12px;
  }
  .journal-table tbody td {
    padding: 9px 16px;
    border-bottom: 1px solid #E2E8F0;
    vertical-align: top;
    color: #0F172A;
  }
  .journal-table tbody tr:nth-child(even) td { background: #F3F8FD; }
  .journal-table tbody tr:last-child td { border-bottom: none; }
  .j-debit  { color: #1D4ED8 !important; font-weight: 700; font-family: 'IBM Plex Mono', monospace; text-align: right !important; }
  .j-credit { color: #065F46 !important; font-weight: 700; font-family: 'IBM Plex Mono', monospace; text-align: right !important; }
  .j-zero   { color: #CBD5E1 !important; font-family: 'IBM Plex Mono', monospace; text-align: right !important; }

  /* ── Formula / code box ── */
  .formula-box {
    background: #F0F7FF;
    border: 1px solid #BAD4F0;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
    color: #1E3A5F;
    white-space: pre-wrap;
    line-height: 1.75;
    margin: 8px 0 16px 0;
  }

  /* ── Disclaimer ── */
  .disclaimer-box {
    background: #FFFBEB;
    border: 1px solid #FCD34D;
    border-left: 5px solid #F59E0B;
    border-radius: 8px;
    padding: 12px 18px;
    font-size: 12.5px;
    color: #78350F;
    line-height: 1.6;
    margin: 14px 0;
  }

  /* ── Result panel ── */
  .result-panel {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 18px 22px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    margin-bottom: 14px;
  }
  .result-panel .kpi-label { font-size: 11px; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.06em; }

  /* ── Chips / badges ── */
  .chip { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.04em; }
  .chip-blue  { background: #DBEAFE; color: #1D4ED8; }
  .chip-green { background: #D1FAE5; color: #065F46; }
  .chip-amber { background: #FEF3C7; color: #78350F; }
  .badge-itm  { background: #D1FAE5; color: #065F46; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; }
  .badge-atm  { background: #E0E7FF; color: #3730A3; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; }
  .badge-otm  { background: #FEE2E2; color: #7F1D1D; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; }

  /* ── Tab bar ── */
  [data-baseweb="tab-list"] {
    gap: 4px;
    background: transparent !important;
  }
  [data-baseweb="tab"] {
    border-radius: 7px 7px 0 0 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    color: #334155 !important;
  }
  [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #1A3A5C !important;
    font-weight: 700 !important;
  }

  /* ── Subsequent period standalone container ── */
  .subseq-container {
    background: #FFFDF5;
    border: 2px solid #FDE68A;
    border-radius: 12px;
    padding: 22px 24px;
    margin: 20px 0;
  }

  /* ── Dataframes ── */
  [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

  footer { visibility: hidden; }
  #MainMenu { visibility: hidden; }
</style>
"""


def section(icon: str, title: str) -> str:
    return f'<div class="section-hdr"><span>{icon}</span><span>{title}</span></div>'


def section_subseq(icon: str, title: str) -> str:
    """Amber-toned header for Subsequent Period sections."""
    return f'<div class="section-hdr-subseq"><span>{icon}</span><span>{title}</span></div>'


def kpi_card(label: str, value: str, sub: str = "", color: str = "") -> str:
    cls = f"kpi-card {color}".strip()
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ''
    return f'<div class="{cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{sub_html}</div>'


def kpi_row(*cards: str) -> str:
    return f'<div class="kpi-grid">{"".join(cards)}</div>'


def journal_html(entries) -> str:
    rows = ""
    for e in entries:
        dr = f'<td class="j-debit">{e.debit:,.2f}</td>' if e.debit else '<td class="j-zero">—</td>'
        cr = f'<td class="j-credit">{e.credit:,.2f}</td>' if e.credit else '<td class="j-zero">—</td>'
        rows += (
            f'<tr><td style="color:#0F172A">{e.account}</td>'
            f'{dr}{cr}'
            f'<td style="font-size:11.5px;color:#64748B;">{e.explanation}</td></tr>'
        )
    return (
        '<div class="journal-wrap">'
        '<table class="journal-table">'
        '<thead><tr>'
        '<th>Account</th>'
        '<th style="text-align:right">Debit</th>'
        '<th style="text-align:right">Credit</th>'
        '<th>Note / IFRS 2 Reference</th>'
        '</tr></thead>'
        f'<tbody>{rows}</tbody>'
        '</table></div>'
    )
