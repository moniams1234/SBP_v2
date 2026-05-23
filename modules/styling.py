"""
Premium finance dashboard CSS for the IFRS 2 SBP Valuation App.
"""

PREMIUM_CSS = """
<style>
  /* ── Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
  }

  /* ── Background ── */
  .stApp { background: #F0F4F8; }
  .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1280px; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(175deg, #0B1F38 0%, #112D4E 50%, #1B4172 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
  }
  [data-testid="stSidebar"] * { color: #C9DDEF !important; }
  [data-testid="stSidebar"] .stSelectbox > div > div,
  [data-testid="stSidebar"] .stNumberInput > div > div,
  [data-testid="stSidebar"] .stTextInput > div > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 6px !important;
  }
  [data-testid="stSidebar"] .stRadio > div { gap: 6px; }
  [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }

  /* ── App title bar ── */
  .app-banner {
    background: linear-gradient(135deg, #0B1F38 0%, #1B4172 60%, #2563EB 100%);
    padding: 22px 30px;
    border-radius: 14px;
    margin-bottom: 22px;
    box-shadow: 0 4px 24px rgba(11,31,56,0.18);
  }
  .app-banner h1 {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.02em;
  }
  .app-banner p {
    color: #93C5FD;
    font-size: 13px;
    margin: 4px 0 0 0;
  }

  /* ── Section header ── */
  .section-hdr {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #FFFFFF;
    border-left: 4px solid #2563EB;
    border-radius: 0 8px 8px 0;
    padding: 10px 18px;
    margin: 22px 0 16px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    font-weight: 600;
    font-size: 14px;
    color: #0B1F38;
    letter-spacing: 0.01em;
  }

  /* ── KPI cards ── */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
  }
  .kpi-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    border-top: 3px solid #2563EB;
    position: relative;
    overflow: hidden;
  }
  .kpi-card::after {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 80px; height: 80px;
    background: rgba(37,99,235,0.05);
    border-radius: 50%;
  }
  .kpi-label {
    font-size: 11px;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
  }
  .kpi-value {
    font-size: 22px;
    font-weight: 700;
    color: #0F172A;
    font-family: 'DM Mono', monospace;
    line-height: 1.2;
  }
  .kpi-sub {
    font-size: 11px;
    color: #94A3B8;
    margin-top: 4px;
  }
  .kpi-card.green { border-top-color: #10B981; }
  .kpi-card.green .kpi-value { color: #065F46; }
  .kpi-card.amber { border-top-color: #F59E0B; }
  .kpi-card.amber .kpi-value { color: #78350F; }
  .kpi-card.red { border-top-color: #EF4444; }
  .kpi-card.red .kpi-value { color: #7F1D1D; }

  /* ── Journal table ── */
  .journal-wrap { overflow-x: auto; }
  .journal-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .journal-table thead th {
    background: #0B1F38;
    color: #FFFFFF;
    padding: 11px 16px;
    text-align: left;
    font-weight: 600;
    letter-spacing: 0.04em;
    font-size: 12px;
  }
  .journal-table tbody td {
    padding: 10px 16px;
    border-bottom: 1px solid #E2E8F0;
    vertical-align: top;
  }
  .journal-table tbody tr:nth-child(even) td { background: #F8FAFC; }
  .journal-table tbody tr:last-child td { border-bottom: none; }
  .j-debit  { color: #1D4ED8; font-weight: 700; font-family: 'DM Mono', monospace; text-align: right; }
  .j-credit { color: #065F46; font-weight: 700; font-family: 'DM Mono', monospace; text-align: right; }
  .j-zero   { color: #CBD5E1; font-family: 'DM Mono', monospace; text-align: right; }

  /* ── Formula box ── */
  .formula-box {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'DM Mono', monospace;
    font-size: 12.5px;
    color: #1E3A5F;
    white-space: pre-wrap;
    line-height: 1.7;
    margin: 10px 0 16px 0;
  }

  /* ── Disclaimer ── */
  .disclaimer-box {
    background: #FFFBEB;
    border: 1px solid #FCD34D;
    border-left: 5px solid #F59E0B;
    border-radius: 8px;
    padding: 14px 20px;
    font-size: 12.5px;
    color: #78350F;
    line-height: 1.6;
    margin: 16px 0;
  }

  /* ── Result panel ── */
  .result-panel {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 16px;
  }

  /* ── Info chip ── */
  .chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
  }
  .chip-blue  { background: #DBEAFE; color: #1D4ED8; }
  .chip-green { background: #D1FAE5; color: #065F46; }
  .chip-amber { background: #FEF3C7; color: #78350F; }

  /* ── Dataframe overrides ── */
  [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

  /* ── Tab styling ── */
  [data-baseweb="tab-list"] {
    gap: 6px;
    background: transparent;
    padding-bottom: 0;
  }
  [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
  }
  [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #2563EB !important;
  }

  /* ── Moneyness badge ── */
  .badge-itm  { background: #D1FAE5; color: #065F46; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; }
  .badge-atm  { background: #E0E7FF; color: #3730A3; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; }
  .badge-otm  { background: #FEE2E2; color: #7F1D1D; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; }

  footer { visibility: hidden; }
  #MainMenu { visibility: hidden; }
</style>
"""

def section(icon: str, title: str) -> str:
    return f'<div class="section-hdr"><span>{icon}</span><span>{title}</span></div>'


def kpi_card(label: str, value: str, sub: str = "", color: str = "") -> str:
    cls = f"kpi-card {color}".strip()
    return f"""<div class="{cls}">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  {f'<div class="kpi-sub">{sub}</div>' if sub else ''}
</div>"""


def journal_html(entries) -> str:
    rows = ""
    for e in entries:
        dr = f'<td class="j-debit">{e.debit:,.2f}</td>' if e.debit else '<td class="j-zero">—</td>'
        cr = f'<td class="j-credit">{e.credit:,.2f}</td>' if e.credit else '<td class="j-zero">—</td>'
        rows += f"""<tr>
          <td>{e.account}</td>
          {dr}
          {cr}
          <td style="font-size:11.5px; color:#64748B;">{e.explanation}</td>
        </tr>"""
    return f"""<div class="journal-wrap">
<table class="journal-table">
  <thead><tr>
    <th>Account</th>
    <th style="text-align:right">Debit</th>
    <th style="text-align:right">Credit</th>
    <th>Note / IFRS 2 Reference</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table></div>"""
