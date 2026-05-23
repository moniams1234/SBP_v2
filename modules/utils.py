"""Utility formatting helpers for the IFRS 2 SBP Valuation App."""

def fc(val, decimals=2, prefix=""):
    """Format as currency / number."""
    if val is None:
        return "—"
    try:
        return f"{prefix}{float(val):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(val)


def fp(val, decimals=2):
    """Format as percentage."""
    if val is None:
        return "—"
    try:
        return f"{float(val) * 100:.{decimals}f}%"
    except (TypeError, ValueError):
        return str(val)


def fi(val):
    """Format as integer with thousands separator."""
    if val is None:
        return "—"
    try:
        return f"{int(val):,}"
    except (TypeError, ValueError):
        return str(val)


IFRS2_TOOLTIPS = {
    "S0":              "Current share price (spot price) at the grant date.",
    "K":               "Strike / exercise price – the price at which the holder can buy one share.",
    "r":               "Annual risk-free rate (e.g. government bond yield matching expected life).",
    "q":               "Expected annual dividend yield. Reduces call option value.",
    "sigma":           "Expected annualized share price volatility. Can be from historical data or implied.",
    "T":               "Expected life of the option in years (may be shorter than contractual life).",
    "vesting_period":  "Service period over which employees earn the right to exercise. IFRS 2 expense is spread over this period.",
    "forfeiture_rate": "Expected annual employee leavers. Reduces expected vested instruments. Updated each period.",
    "equity_settled":  "Awards settled by issuing shares. Fair value fixed at grant date – never remeasured (IFRS 2.7).",
    "cash_settled":    "Awards settled in cash. Liability remeasured at fair value each reporting date (IFRS 2.30).",
    "employee_choice": "Employee can choose cash or shares. Compound instrument: liability component (cash alt FV) + equity component (residual) (IFRS 2.34).",
    "months_prorate":  "If the award is granted mid-year, enter months active in year 1 to prorate the first-year expense.",
}

DISCLAIMER_HTML = """
<div class="disclaimer-box">
  ⚠️ <strong>Important Disclaimer:</strong> This tool is for educational and analytical purposes only.
  Final IFRS 2 classification and accounting treatment should be reviewed based on the legal terms
  of the share-based payment plan and confirmed with professional accounting advisors or auditors.
  This application does not constitute accounting, legal, or tax advice.
</div>
"""
