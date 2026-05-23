# Share-Based Payment Valuation App
### IFRS 2 · Black-Scholes · Equity-Settled · Cash-Settled · Employee Choice

A production-ready Streamlit application for IFRS 2 share-based payment valuation, expense calculation, and accounting entries generation.

---

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
sbp_v2/
├── app.py                        # Main Streamlit application (7 tabs)
├── requirements.txt
├── README.md
└── modules/
    ├── black_scholes.py          # Black-Scholes pricing + Greeks
    ├── volatility.py             # Historical volatility from CSV/XLSX
    ├── accounting.py             # IFRS 2 expense, vesting schedule, journal entries
    ├── subsequent_valuation.py   # Subsequent period remeasurement
    ├── export_excel.py           # 10-sheet professional Excel export
    ├── styling.py                # Premium CSS + HTML helpers
    └── utils.py                  # Formatters, tooltips, disclaimer
```

---

## Tabs

| # | Tab | Key Feature |
|---|-----|-------------|
| ① | Program Setup | Program type, instrument type, grant dates, employee count |
| ② | Black-Scholes | Full pricing with Greeks and moneyness indicator |
| ③ | Volatility | Manual or CSV/XLSX upload, Polish comma handling |
| ④ | Vesting & Forfeiture | Service conditions, performance conditions, guidance |
| ⑤ | First-Year Accounting | Expense proration, vesting schedule, journal entries |
| ⑥ | Subsequent Period | Equity catch-up, cash liability remeasurement, choice arrangement |
| ⑦ | Summary & Export | Executive KPI dashboard, summary table, Excel download |

---

## Black-Scholes Model

```
d₁ = [ ln(S₀/K) + (r - q + σ²/2)·T ] / (σ·√T)
d₂ = d₁ - σ·√T

Call: C = S₀·e^(-qT)·N(d₁) - K·e^(-rT)·N(d₂)
Put:  P = K·e^(-rT)·N(-d₂) - S₀·e^(-qT)·N(-d₁)
```

For IFRS 2, the **call option price** is used as the grant-date fair value per instrument.

---

## Volatility Calculation

Log returns: `r_t = ln(P_t / P_{t-1})`

Annualized volatility:
- Daily prices: `σ = std(r_t) × √252`
- Weekly prices: `σ = std(r_t) × √52`
- Monthly prices: `σ = std(r_t) × √12`

The app handles Polish decimal comma format automatically (e.g. "122,08" → 122.08).

---

## IFRS 2 Accounting Treatment

### Equity-Settled Awards (IFRS 2.7–15)

- Fair value is **fixed at grant date** using Black-Scholes.
- The entity **never remeasures** the grant-date fair value.
- The expense is spread over the **vesting period**.
- Non-market vesting conditions (e.g. service, EPS targets) are reflected by updating the **number of instruments expected to vest** at each reporting date.
- If the estimate changes, a catch-up adjustment is recognized in the current period.
- If awards ultimately do not vest due to non-market conditions, the cumulative expense is **reversed**.

**Why not remeasured?** Under IFRS 2, equity-settled awards are measured once at grant date because the entity's obligation is to issue shares, not cash. The fair value of the equity consideration is fixed at that point.

**Journal entry:**
```
Dr  Employee Benefit Expense            X
  Cr  Share-Based Payment Reserve       X
```

### Cash-Settled Awards (IFRS 2.30–33)

- The entity recognizes a **liability** equal to the fair value of the obligation.
- The liability is **remeasured at fair value at every reporting date** until final settlement.
- Changes in fair value (both from share price and option Greeks) are recognized in **P&L** in the period they occur.

**Why remeasured?** Because the entity's obligation is to pay cash based on the share price. The amount is variable and must reflect current market conditions.

**Current period P&L:**
```
P&L impact = Closing liability - Opening liability + Cash paid
```

**Journal entries:**
```
If liability increases:
Dr  Employee Benefit Expense            X
  Cr  Share-Based Payment Liability     X

On settlement:
Dr  Share-Based Payment Liability       X
  Cr  Cash / Bank                       X
```

### Employee Choice Arrangements (IFRS 2.34–43)

When an employee can choose between cash or equity settlement, the entity has granted a **compound instrument**:

1. **Liability component** = fair value of the cash alternative
2. **Equity component** = fair value of equity settlement − fair value of cash alternative

The liability component is **remeasured each period**. The equity component is **fixed at grant date** (unless modification accounting applies).

---

## Employee Turnover and Expected Vested Instruments

For non-market conditions:

```
Expected vested = Total granted × (1 − forfeiture rate)
```

This estimate is updated at each reporting date. The cumulative IFRS 2 expense is recalculated based on the updated estimate. The difference from the prior cumulative is recognized as a catch-up (positive or negative) in the current period.

---

## Subsequent Period Expense (Equity-Settled)

```
Updated expected vested instruments = Granted × (1 − updated forfeiture rate)
Updated total fair value             = Grant-date FV × Updated vested
Cumulative expense required          = Updated total FV × (Elapsed service / Total vesting)
Current period expense               = Cumulative required − Prior cumulative expense
```

This "catch-up" approach ensures that the total recognized expense always equals the expected ultimate cost, spread over the remaining vesting period.

---

## Excel Export – 10 Sheets

1. Executive Summary
2. Inputs
3. Historical Prices
4. Log Returns
5. Volatility Calculation
6. Black-Scholes Valuation
7. Vesting Assumptions
8. First-Year Accounting
9. Accounting Entries
10. Subsequent Period

---

## Disclaimer

This tool is for educational and analytical purposes only. Final IFRS 2 classification and accounting treatment should be reviewed based on the legal terms of the share-based payment plan and confirmed with professional accounting advisors or auditors. This application does not constitute accounting, legal, or tax advice.
