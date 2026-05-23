"""
IFRS 2 accounting calculations:
- Expected vested instruments
- Total award fair value
- Annual / first-year expense
- Journal entries for equity-settled, cash-settled, employee choice
- Vesting schedule
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValuationInputs:
    grant_fv_per_option: float       # grant-date fair value per option
    instruments_granted: int          # total instruments granted
    forfeiture_rate: float            # expected forfeiture rate (0–1)
    vesting_period: float             # years
    months_in_first_year: int = 12   # proration
    expected_vesting_pct: Optional[float] = None  # override if not using forfeiture_rate


def expected_vested(inputs: ValuationInputs) -> float:
    if inputs.expected_vesting_pct is not None:
        return inputs.instruments_granted * inputs.expected_vesting_pct
    return inputs.instruments_granted * (1 - inputs.forfeiture_rate)


def total_award_fair_value(inputs: ValuationInputs) -> float:
    return inputs.grant_fv_per_option * expected_vested(inputs)


def annual_expense(inputs: ValuationInputs) -> float:
    tv = total_award_fair_value(inputs)
    return tv / inputs.vesting_period if inputs.vesting_period > 0 else 0.0


def first_year_expense(inputs: ValuationInputs) -> float:
    return annual_expense(inputs) * inputs.months_in_first_year / 12


def vesting_schedule(inputs: ValuationInputs) -> List[dict]:
    """Generate year-by-year expense schedule."""
    ann = annual_expense(inputs)
    months = inputs.months_in_first_year
    schedule = []
    cumulative = 0.0
    years = max(1, round(inputs.vesting_period))
    for y in range(1, years + 1):
        if y == 1:
            exp = ann * months / 12
        elif y == years and months < 12:
            # catch-up: remaining months carried into final year
            exp = ann * (1 + (12 - months) / 12)
        else:
            exp = ann
        cumulative += exp
        schedule.append({"Year": y, "Expense": exp, "Cumulative": cumulative})
    return schedule


# ── Journal entries ──────────────────────────────────────────────────────────

@dataclass
class JournalEntry:
    account: str
    debit: float
    credit: float
    explanation: str


def equity_settled_entries(expense: float) -> List[JournalEntry]:
    return [
        JournalEntry("Employee Benefit Expense", expense, 0,
                     "IFRS 2.7 – Equity-settled: fair value fixed at grant date"),
        JournalEntry("Share-Based Payment Reserve (Equity)", 0, expense,
                     "Equity reserve – not remeasured after grant date"),
    ]


def cash_settled_entries(expense: float) -> List[JournalEntry]:
    return [
        JournalEntry("Employee Benefit Expense", expense, 0,
                     "IFRS 2.30 – Cash-settled: expense based on current fair value"),
        JournalEntry("Share-Based Payment Liability", 0, expense,
                     "Liability remeasured at fair value each reporting date"),
    ]


def employee_choice_entries(expense: float, liability_component: float, equity_component: float) -> List[JournalEntry]:
    entries = [JournalEntry("Employee Benefit Expense", expense, 0,
                            "IFRS 2.34–43 – Compound instrument: total expense")]
    if liability_component > 0:
        entries.append(JournalEntry("Share-Based Payment Liability", 0, liability_component,
                                    "Liability component – cash alternative, remeasured each period"))
    if equity_component > 0:
        entries.append(JournalEntry("Share-Based Payment Reserve (Equity)", 0, equity_component,
                                    "Equity component – residual after cash alternative FV"))
    return entries


# ── Subsequent period ────────────────────────────────────────────────────────

def subsequent_equity_settled(
    grant_fv: float,
    instruments_granted: int,
    updated_forfeiture: float,
    cumulative_service: float,
    total_vesting: float,
    prior_cumulative_expense: float,
) -> dict:
    """Calculate catch-up adjustment for equity-settled awards."""
    updated_vested = instruments_granted * (1 - updated_forfeiture)
    updated_total_fv = grant_fv * updated_vested
    service_pct = min(cumulative_service / total_vesting, 1.0) if total_vesting > 0 else 0
    cumulative_required = updated_total_fv * service_pct
    current_period_expense = cumulative_required - prior_cumulative_expense
    return {
        "updated_vested": updated_vested,
        "updated_total_fv": updated_total_fv,
        "service_pct": service_pct,
        "cumulative_required": cumulative_required,
        "current_period_expense": current_period_expense,
        "equity_reserve_closing": cumulative_required,
    }


def subsequent_cash_settled(
    current_fv_per_option: float,
    outstanding_instruments: int,
    updated_forfeiture: float,
    cumulative_service: float,
    total_vesting: float,
    opening_liability: float,
    cash_paid: float,
) -> dict:
    """Calculate P&L and liability movement for cash-settled awards."""
    expected_vested = outstanding_instruments * (1 - updated_forfeiture)
    service_pct = min(cumulative_service / total_vesting, 1.0) if total_vesting > 0 else 0
    closing_liability = current_fv_per_option * expected_vested * service_pct
    pl_impact = closing_liability - opening_liability + cash_paid
    return {
        "expected_vested": expected_vested,
        "service_pct": service_pct,
        "closing_liability": closing_liability,
        "opening_liability": opening_liability,
        "cash_paid": cash_paid,
        "pl_impact": pl_impact,
    }


def subsequent_cash_settled_entries(closing_liability: float, opening_liability: float, cash_paid: float) -> List[JournalEntry]:
    entries = []
    net = closing_liability - opening_liability
    if net >= 0:
        entries.append(JournalEntry("Employee Benefit Expense", net, 0,
                                    "Increase in SBP liability – P&L charge"))
        entries.append(JournalEntry("Share-Based Payment Liability", 0, net,
                                    "Liability remeasured upward"))
    else:
        entries.append(JournalEntry("Share-Based Payment Liability", abs(net), 0,
                                    "Liability remeasured downward"))
        entries.append(JournalEntry("Employee Benefit Expense / Remeasurement Gain", 0, abs(net),
                                    "Decrease in SBP liability – P&L credit"))
    if cash_paid > 0:
        entries.append(JournalEntry("Share-Based Payment Liability", cash_paid, 0,
                                    "Settlement of liability"))
        entries.append(JournalEntry("Cash / Bank", 0, cash_paid,
                                    "Cash paid to employees on exercise"))
    return entries
