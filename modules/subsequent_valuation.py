"""
Subsequent period valuation helpers for IFRS 2.
Wraps accounting.py subsequent functions with richer output structures.
"""

from modules.black_scholes import bs_full
from modules.accounting import (
    subsequent_equity_settled,
    subsequent_cash_settled,
    subsequent_cash_settled_entries,
    equity_settled_entries,
    JournalEntry,
)
from typing import List


def run_equity_subsequent(
    grant_fv: float,
    instruments_granted: int,
    updated_forfeiture: float,
    cumulative_service: float,
    total_vesting: float,
    prior_cumulative_expense: float,
) -> dict:
    result = subsequent_equity_settled(
        grant_fv, instruments_granted, updated_forfeiture,
        cumulative_service, total_vesting, prior_cumulative_expense
    )
    result["entries"] = equity_settled_entries(max(result["current_period_expense"], 0))
    return result


def run_cash_subsequent(
    S0, K, r, q, sigma, T_remaining,
    outstanding_instruments, updated_forfeiture,
    cumulative_service, total_vesting,
    opening_liability, cash_paid,
) -> dict:
    bs = bs_full(S0, K, r, q, sigma, T_remaining)
    current_fv = bs["call"]
    calc = subsequent_cash_settled(
        current_fv, outstanding_instruments, updated_forfeiture,
        cumulative_service, total_vesting, opening_liability, cash_paid
    )
    calc["current_fv_per_option"] = current_fv
    calc["bs_results"] = bs
    calc["entries"] = subsequent_cash_settled_entries(
        calc["closing_liability"], opening_liability, cash_paid
    )
    return calc


def run_choice_subsequent(
    has_obligation: bool,
    opening_liability: float,
    cash_alt_fv: float,
    equity_alt_fv: float,
    updated_vested: float,
    service_pct: float,
    instruments_settled_cash: int,
    instruments_settled_equity: int,
    cash_paid: float,
    instruments_forfeited: int,
) -> dict:
    liability_component = cash_alt_fv * updated_vested * service_pct if has_obligation else 0
    equity_component = max((equity_alt_fv - cash_alt_fv) * updated_vested * service_pct, 0)
    total_expense = liability_component + equity_component
    remeasurement = liability_component - opening_liability

    entries: List[JournalEntry] = []
    if total_expense > 0:
        entries.append(JournalEntry("Employee Benefit Expense", total_expense, 0,
                                    "IFRS 2.34–43 – Compound instrument total expense"))
    if liability_component > 0:
        entries.append(JournalEntry("Share-Based Payment Liability", 0, liability_component,
                                    "Liability component remeasured"))
    if equity_component > 0:
        entries.append(JournalEntry("Share-Based Payment Reserve (Equity)", 0, equity_component,
                                    "Equity component – residual"))
    if cash_paid > 0:
        entries.append(JournalEntry("Share-Based Payment Liability", cash_paid, 0,
                                    "Settlement in cash"))
        entries.append(JournalEntry("Cash / Bank", 0, cash_paid,
                                    "Cash paid to employees"))

    return {
        "liability_component": liability_component,
        "equity_component": equity_component,
        "total_expense": total_expense,
        "remeasurement_gain_loss": remeasurement,
        "entries": entries,
    }
