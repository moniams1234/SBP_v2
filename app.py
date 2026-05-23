"""
Share-Based Payment Valuation App
IFRS 2 | Black-Scholes | Equity-settled | Cash-settled | Employee Choice
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

from modules.black_scholes import bs_full, bs_call, bs_put
from modules.volatility import compute_volatility, load_uploaded_file, clean_series
from modules.accounting import (
    ValuationInputs, expected_vested as calc_ev, total_award_fair_value,
    annual_expense as calc_ann, first_year_expense as calc_fy,
    vesting_schedule as calc_vs,
    equity_settled_entries, cash_settled_entries, employee_choice_entries,
)
from modules.subsequent_valuation import (
    run_equity_subsequent, run_cash_subsequent, run_choice_subsequent
)
from modules.export_excel import build_excel
from modules.styling import PREMIUM_CSS, section, section_subseq, kpi_card, kpi_row, journal_html
from modules.utils import fc, fp, fi, IFRS2_TOOLTIPS, DISCLAIMER_HTML

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SBP Valuation | IFRS 2",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ─── Banner ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-banner">
  <h1>📈 Share-Based Payment Valuation App</h1>
  <p>IFRS 2 · Black-Scholes · Equity-Settled · Cash-Settled · Employee Choice Arrangements</p>
</div>
""", unsafe_allow_html=True)
st.markdown(DISCLAIMER_HTML, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Program Configuration")
    st.markdown("---")

    program_type = st.selectbox(
        "Program Type",
        ["Equity-settled", "Cash-settled", "Employee choice (cash or equity)"],
        help=f"{IFRS2_TOOLTIPS['equity_settled']}\n\n{IFRS2_TOOLTIPS['cash_settled']}\n\n{IFRS2_TOOLTIPS['employee_choice']}"
    )
    instrument_type = st.selectbox(
        "Instrument Type",
        ["Stock option", "Warrant", "RSU / Performance share"]
    )

    st.markdown("---")
    st.markdown("### 📅 Key Dates")
    grant_date    = st.date_input("Grant Date",     value=date(2024, 1, 1))
    reporting_date= st.date_input("Reporting Date", value=date.today())
    program_start = st.date_input("Program Start",  value=date(2024, 1, 1))

    st.markdown("---")
    st.markdown("### 👥 Grant Details")
    n_employees   = st.number_input("Number of Employees",      min_value=1,   value=50,    step=1)
    opts_per_emp  = st.number_input("Options per Employee",     min_value=1,   value=5000,  step=100)
    n_total       = n_employees * opts_per_emp
    st.info(f"**Total Granted: {n_total:,}**")

    st.markdown("---")
    st.markdown("### ⏳ Program Terms")
    vesting_period= st.number_input("Vesting Period (years)",       min_value=0.5, value=3.0, step=0.5, help=IFRS2_TOOLTIPS["vesting_period"])
    total_period  = st.number_input("Total Program Period (years)", min_value=0.5, value=5.0, step=0.5)
    months_yr1    = st.number_input("Months Active – Year 1",       min_value=1,   max_value=12, value=12, step=1, help=IFRS2_TOOLTIPS["months_prorate"])

    st.markdown("---")
    st.markdown("### 📉 Forfeiture")
    forfeiture_rate = st.number_input("Expected Forfeiture Rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5, help=IFRS2_TOOLTIPS["forfeiture_rate"]) / 100
    exp_vest_pct_input = st.number_input("Expected Vesting % (override)", min_value=0.0, max_value=100.0,
                                          value=round((1 - forfeiture_rate) * 100, 2), step=0.5) / 100

    st.markdown("---")
    st.caption("IFRS 2 SBP Valuation App · Educational Use Only")


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED STATE
# ═══════════════════════════════════════════════════════════════════════════════
ev_instruments = n_total * exp_vest_pct_input

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_labels = [
    "① Program Setup",
    "② Black-Scholes",
    "③ Volatility",
    "④ Vesting & Forfeiture",
    "⑤ First-Year Accounting",
    "⑥ Subsequent Period",
    "⑦ Summary & Export",
]
t1, t2, t3, t4, t5, t6, t7 = st.tabs(tab_labels)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – PROGRAM SETUP
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    st.markdown(section("①", "Program Setup"), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="result-panel">
          <div class="kpi-label">Program Type</div>
          <div style="font-size:18px; font-weight:700; color:#0B1F38; margin-top:4px">{program_type}</div>
          <div style="margin-top:8px"><span class="chip chip-blue">{instrument_type}</span></div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="result-panel">
          <div class="kpi-label">Grant Date</div>
          <div style="font-size:18px; font-weight:700; color:#0B1F38; margin-top:4px">{grant_date.strftime('%d %b %Y')}</div>
          <div class="kpi-sub">Reporting: {reporting_date.strftime('%d %b %Y')}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="result-panel">
          <div class="kpi-label">Vesting Period</div>
          <div style="font-size:18px; font-weight:700; color:#0B1F38; margin-top:4px">{vesting_period:.1f} years</div>
          <div class="kpi-sub">Total program: {total_period:.1f} years</div>
        </div>""", unsafe_allow_html=True)

    # Instrument summary table
    st.markdown(section("📊", "Grant Summary"), unsafe_allow_html=True)
    summ_df = pd.DataFrame({
        "Parameter": ["Total Instruments Granted", "Number of Employees",
                      "Instruments per Employee", "Expected Forfeiture Rate",
                      "Expected Vesting %", "Expected Vested Instruments"],
        "Value": [fi(n_total), fi(n_employees), fi(opts_per_emp),
                  fp(forfeiture_rate), fp(exp_vest_pct_input), fi(ev_instruments)],
    })
    st.dataframe(summ_df, use_container_width=True, hide_index=True)

    # IFRS 2 classification info
    st.markdown(section("📘", "IFRS 2 Classification"), unsafe_allow_html=True)
    if program_type == "Equity-settled":
        st.info("""**Equity-settled share-based payments (IFRS 2.7–15):**
Fair value is measured at **grant date** and is **never remeasured**.
The expense is spread over the vesting period based on the number of instruments expected to vest.
Non-market vesting conditions affect the number of awards, not the fair value per award.""")
    elif program_type == "Cash-settled":
        st.info("""**Cash-settled share-based payments (IFRS 2.30–33):**
A **liability** is recognized and **remeasured at fair value** at each reporting date until settlement.
Changes in fair value after grant date are recognized in profit or loss in the period they occur.""")
    else:
        st.info("""**Employee choice arrangements (IFRS 2.34–43):**
The entity has granted a **compound instrument** containing both a liability component
(fair value of cash alternative) and an equity component (residual).
The liability is remeasured each period; the equity component is fixed at grant date.""")

    # Employee choice extra fields
    if program_type == "Employee choice (cash or equity)":
        st.markdown(section("💼", "Employee Choice – Settlement Details"), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            has_obligation = st.radio("Entity has present obligation to settle in cash?", ["Yes", "No"])
            liability_val = st.number_input("Existing Liability Value", min_value=0.0, value=0.0, step=1000.0)
        with c2:
            cash_alt_fv   = st.number_input("Cash Alternative FV per Option", min_value=0.0, value=0.0, step=0.01)
            equity_alt_fv = st.number_input("Equity Alternative FV per Option", min_value=0.0, value=0.0, step=0.01)
        st.session_state["choice_params"] = dict(
            has_obligation=has_obligation == "Yes",
            liability_val=liability_val,
            cash_alt_fv=cash_alt_fv,
            equity_alt_fv=equity_alt_fv,
        )
    else:
        st.session_state["choice_params"] = {}


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – BLACK-SCHOLES VALUATION
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    st.markdown(section("②", "Black-Scholes Option Valuation"), unsafe_allow_html=True)

    st.markdown("""<div class="formula-box">Call: C = S₀·e^(-qT)·N(d₁) - K·e^(-rT)·N(d₂)
Put:  P = K·e^(-rT)·N(-d₂) - S₀·e^(-qT)·N(-d₁)

  d₁ = [ ln(S₀/K) + (r - q + σ²/2)·T ] / (σ·√T)
  d₂ = d₁ - σ·√T</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        S0 = st.number_input("Share Price S₀", min_value=0.01, value=100.0, step=0.01, help=IFRS2_TOOLTIPS["S0"])
        K  = st.number_input("Strike Price K", min_value=0.01, value=100.0, step=0.01, help=IFRS2_TOOLTIPS["K"])
        r  = st.number_input("Risk-free Rate r (%)", min_value=0.0, max_value=30.0, value=4.0, step=0.05, help=IFRS2_TOOLTIPS["r"]) / 100
        q  = st.number_input("Dividend Yield q (%)",  min_value=0.0, max_value=20.0, value=0.0, step=0.05, help=IFRS2_TOOLTIPS["q"]) / 100
    with col2:
        T  = st.number_input("Expected Life T (years)", min_value=0.1, max_value=20.0, value=float(total_period), step=0.1, help=IFRS2_TOOLTIPS["T"])
        option_type = st.selectbox("Option Type for IFRS 2", ["Call (standard)", "Put (informational)", "Show both"])

        # Moneyness
        if K > 0 and S0 > 0:
            m = S0 / K
            if abs(m - 1) < 0.03:
                badge = f'<span class="badge-atm">At-the-money ({m:.3f}×)</span>'
            elif m > 1:
                badge = f'<span class="badge-itm">In-the-money ({m:.3f}×)</span>'
            else:
                badge = f'<span class="badge-otm">Out-of-the-money ({m:.3f}×)</span>'
            st.markdown(f"**Moneyness:** {badge}", unsafe_allow_html=True)

    # Volatility from session or placeholder
    sigma_val = st.session_state.get("sigma", None)
    if sigma_val is None:
        sigma_ph = st.number_input(
            "Volatility σ (%) — configure in ③ Volatility tab",
            min_value=0.1, max_value=300.0, value=30.0, step=0.1,
            help=IFRS2_TOOLTIPS["sigma"]
        )
        sigma_val = sigma_ph / 100
        st.info("💡 Configure historical volatility in the **③ Volatility** tab. Using manual value here.")
    else:
        st.success(f"✅ Using σ = **{sigma_val * 100:.2f}%** from Volatility tab")

    # Store for other tabs
    st.session_state["S0"] = S0
    st.session_state["K"]  = K
    st.session_state["r"]  = r
    st.session_state["q"]  = q
    st.session_state["T"]  = T
    st.session_state["sigma_bs"] = sigma_val

    # Compute
    bs_res = None
    try:
        bs_res = bs_full(S0, K, r, q, sigma_val, T)
        st.session_state["bs_results"] = bs_res
        st.session_state["grant_fv"] = bs_res["call"]

        st.markdown(section("📊", "Valuation Results"), unsafe_allow_html=True)

        # KPI row
        kpi_html = '<div class="kpi-grid">'
        kpi_html += kpi_card("d₁", f"{bs_res['d1']:.4f}", "N(d₁) = " + f"{bs_res['Nd1']:.4f}")
        kpi_html += kpi_card("d₂", f"{bs_res['d2']:.4f}", "N(d₂) = " + f"{bs_res['Nd2']:.4f}")
        kpi_html += kpi_card("Call Option", fc(bs_res["call"]), "Grant-date fair value", "green")
        kpi_html += kpi_card("Put Option", fc(bs_res["put"]), "Informational only", "amber")
        kpi_html += '</div>'
        st.markdown(kpi_html, unsafe_allow_html=True)

        # Greeks
        with st.expander("📐 Option Greeks"):
            g_df = pd.DataFrame({
                "Greek": ["Delta (Call)", "Delta (Put)", "Gamma", "Vega (per 1%σ)", "Theta (Call/day)"],
                "Value": [
                    fc(bs_res["delta_call"], 4), fc(bs_res["delta_put"], 4),
                    fc(bs_res["gamma"], 6), fc(bs_res["vega"], 4), fc(bs_res["theta_call"], 4),
                ],
                "Interpretation": [
                    "Share price sensitivity", "Share price sensitivity (put)",
                    "Rate of change of delta", "Value change per 1% vol rise",
                    "Value lost per calendar day",
                ]
            })
            st.dataframe(g_df, use_container_width=True, hide_index=True)

        # Full table
        st.markdown("##### Detailed Black-Scholes Output")
        full_df = pd.DataFrame({
            "Parameter": ["d₁", "d₂", "N(d₁)", "N(d₂)", "N(-d₁)", "N(-d₂)",
                          "Call Price", "Put Price"],
            "Value": [
                fc(bs_res["d1"], 6), fc(bs_res["d2"], 6),
                fc(bs_res["Nd1"], 6), fc(bs_res["Nd2"], 6),
                fc(bs_res["N_neg_d1"], 6), fc(bs_res["N_neg_d2"], 6),
                fc(bs_res["call"]), fc(bs_res["put"]),
            ]
        })
        st.dataframe(full_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Black-Scholes error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – VOLATILITY
# ══════════════════════════════════════════════════════════════════════════════
with t3:
    st.markdown(section("③", "Volatility Calculation"), unsafe_allow_html=True)

    vol_method = st.radio("Volatility Method", ["Manual input", "Upload historical prices"], horizontal=True)

    sigma_final = None
    log_ret_series = None
    prices_df_store = None
    vol_info_store = None

    if vol_method == "Manual input":
        sigma_manual = st.number_input("Annual Volatility σ (%)", min_value=0.1, max_value=300.0, value=30.0, step=0.1, help=IFRS2_TOOLTIPS["sigma"])
        sigma_final = sigma_manual / 100
        st.success(f"✅ σ set to **{sigma_manual:.2f}%** per annum")
        st.session_state["sigma"] = sigma_final

    else:
        uploaded = st.file_uploader("Upload CSV or XLSX with historical share prices", type=["csv", "xlsx", "xls"])
        if uploaded:
            try:
                df_prices = load_uploaded_file(uploaded)
                prices_df_store = df_prices
                st.session_state["prices_df"] = df_prices

                st.markdown("**Preview (first 10 rows):**")
                st.dataframe(df_prices.head(10), use_container_width=True)

                c1, c2 = st.columns(2)
                with c1:
                    col_method = st.radio("Select price column by:", ["Column name", "Column number"], horizontal=True)
                    if col_method == "Column name":
                        price_col = st.selectbox("Price column", df_prices.columns.tolist())
                    else:
                        col_num = st.number_input("Column number (1-based)", min_value=1, max_value=len(df_prices.columns), value=1, step=1)
                        price_col = df_prices.columns[col_num - 1]
                        st.info(f"Selected: **{price_col}**")
                with c2:
                    freq = st.selectbox("Price frequency", ["daily", "weekly", "monthly"])

                if st.button("🔢 Calculate Volatility", type="primary"):
                    try:
                        result = compute_volatility(df_prices[price_col], freq)
                        sigma_final = result["ann_vol"]
                        log_ret_series = result["log_returns"]
                        vol_info_store = {**result, "frequency": freq}
                        st.session_state["sigma"] = sigma_final
                        st.session_state["log_returns"] = log_ret_series
                        st.session_state["vol_info"] = vol_info_store

                        # KPIs
                        kh = '<div class="kpi-grid">'
                        kh += kpi_card("Std Dev (log returns)", fc(result["std"], 6), "Sample std dev")
                        freq_map = {"daily": 252, "weekly": 52, "monthly": 12}
                        kh += kpi_card("Annualization Factor", fc(result["factor"], 4), f"√{freq_map[freq]}")
                        kh += kpi_card("Annual Volatility σ", fp(sigma_final), "Used in Black-Scholes", "green")
                        kh += '</div>'
                        st.markdown(kh, unsafe_allow_html=True)

                        st.markdown("**Log Returns (first 20):**")
                        st.dataframe(log_ret_series.head(20).to_frame("Log Return"), use_container_width=True)
                        st.bar_chart(log_ret_series.rename("Log Return"), height=220)

                    except Exception as e:
                        st.error(f"Volatility error: {e}")

            except Exception as e:
                st.error(f"File load error: {e}")

        if "sigma" in st.session_state:
            sv = st.session_state["sigma"]
            use_calc = st.checkbox(f"Use calculated σ = {sv*100:.2f}% in Black-Scholes", value=True)
            if use_calc:
                sigma_final = sv
            else:
                ov = st.number_input("Override σ (%)", min_value=0.1, value=float(sv * 100), step=0.1)
                sigma_final = ov / 100
                st.session_state["sigma"] = sigma_final
        elif sigma_final is None:
            fallback = st.number_input("Fallback σ (%)", min_value=0.1, value=30.0, step=0.1)
            sigma_final = fallback / 100
            st.session_state["sigma"] = sigma_final

    # Retrieve cached
    if "log_returns" in st.session_state and log_ret_series is None:
        log_ret_series = st.session_state["log_returns"]
    if "prices_df" in st.session_state and prices_df_store is None:
        prices_df_store = st.session_state["prices_df"]
    if "vol_info" in st.session_state and vol_info_store is None:
        vol_info_store = st.session_state["vol_info"]

    st.markdown("""<div class="formula-box">Log return:   r_t = ln(P_t / P_{t-1})
Annual σ:     std(r_t) × √factor

  Daily:   factor = √252  ≈ 15.87
  Weekly:  factor = √52   ≈ 7.21
  Monthly: factor = √12   ≈ 3.46</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – VESTING & FORFEITURE
# ══════════════════════════════════════════════════════════════════════════════
with t4:
    st.markdown(section("④", "Vesting & Forfeiture Assumptions"), unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        t4_employees   = st.number_input("Employees at Grant Date", min_value=1, value=int(n_employees), step=1)
        t4_turnover    = st.number_input("Annual Turnover (%)", min_value=0.0, max_value=100.0, value=float(forfeiture_rate * 100), step=0.5) / 100
        t4_forfeiture  = st.number_input("Expected Forfeiture Rate (%)", min_value=0.0, max_value=100.0, value=float(forfeiture_rate * 100), step=0.5) / 100
        t4_leaving     = st.number_input("Expected Employees Leaving before Vesting", min_value=0, value=max(0, int(n_employees * t4_forfeiture)), step=1)
        service_ok     = st.radio("Service condition fulfilled?", ["Yes", "No", "Uncertain"], horizontal=True)
        perf_ok        = st.radio("Non-market performance condition fulfilled?", ["Yes", "No", "Uncertain"], horizontal=True)
        t4_vest_pct    = st.number_input("Expected % of Instruments Vesting", min_value=0.0, max_value=100.0, value=float(exp_vest_pct_input * 100), step=0.5) / 100

    with c2:
        t4_vested_n = n_total * t4_vest_pct
        st.markdown(f"""<div class="formula-box">Instruments granted:        {n_total:,}
Expected forfeiture rate:   {t4_forfeiture * 100:.2f}%
Expected vesting rate:      {t4_vest_pct * 100:.2f}%
Expected vested instruments:{t4_vested_n:,.0f}

Expected employees leaving: {t4_leaving:,}
of {t4_employees:,} employees</div>""", unsafe_allow_html=True)

        if service_ok == "No" or perf_ok == "No":
            st.warning("⚠️ If a non-market vesting condition will not be met, the cumulative IFRS 2 expense must be reversed.")
        elif service_ok == "Uncertain" or perf_ok == "Uncertain":
            st.info("ℹ️ Update the expected vesting % as the best estimate evolves over the vesting period.")

    # Vesting type guidance
    st.markdown(section("📘", "IFRS 2 Vesting Treatment"), unsafe_allow_html=True)
    if program_type == "Equity-settled":
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""**Equity-settled – key rules:**
- ✅ Fair value **fixed at grant date**
- ✅ Do **not** remeasure grant-date fair value
- ✅ Update **number of expected vested instruments** each period
- ✅ Cumulative expense = FV × updated vested instruments × service elapsed
- ✅ Catch-up in current period if estimate changes""")
        with col_b:
            grant_fv_t4 = st.session_state.get("grant_fv", 0.0)
            ev_t4 = n_total * t4_vest_pct
            total_fv_t4 = grant_fv_t4 * ev_t4
            ann_exp_t4 = total_fv_t4 / vesting_period if vesting_period > 0 else 0
            st.markdown(f"""**Estimated expense at current forfeiture:**
- Fair value/option: **{fc(grant_fv_t4)}**
- Expected vested: **{fi(ev_t4)}**
- Total fair value: **{fc(total_fv_t4)}**
- Annual expense: **{fc(ann_exp_t4)}**""")

    elif program_type == "Cash-settled":
        st.markdown("""**Cash-settled – key rules:**
- 💰 Liability remeasured at **current fair value** each reporting date
- 💰 Fair value changes recognized in **P&L** immediately
- 💰 Forfeiture reduces the liability
- 💰 Closing liability = FV × expected vested × service proportion""")
        s0_now = st.number_input("Current Share Price (reporting date)", min_value=0.01, value=st.session_state.get("S0", 100.0), step=0.01)
        st.session_state["S0_remeasure"] = s0_now
    else:
        st.markdown("""**Employee choice – compound instrument:**
- Liability component remeasured each period
- Equity component fixed at grant date
- If employee chooses equity: transfer liability to equity on settlement""")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 – FIRST-YEAR ACCOUNTING
# ══════════════════════════════════════════════════════════════════════════════
with t5:
    st.markdown(section("⑤", "First-Year IFRS 2 Accounting"), unsafe_allow_html=True)

    grant_fv_t5 = st.session_state.get("grant_fv", 0.0)
    if grant_fv_t5 == 0.0:
        grant_fv_t5 = st.number_input("Grant-Date Fair Value per Option (override)", min_value=0.0, value=0.0, step=0.01)

    c1, c2 = st.columns(2)
    with c1:
        t5_grant_fv = st.number_input("Grant-Date FV per Option", min_value=0.0, value=float(round(grant_fv_t5, 4)), step=0.0001, format="%.4f")
        t5_months   = st.number_input("Months Active in First Year", min_value=1, max_value=12, value=int(months_yr1), step=1)
        t5_vest_pct = st.number_input("Expected Vesting %", min_value=0.0, max_value=100.0, value=float(exp_vest_pct_input * 100), step=0.5) / 100

    with c2:
        t5_ev = n_total * t5_vest_pct
        t5_total_fv = t5_grant_fv * t5_ev
        t5_annual = t5_total_fv / vesting_period if vesting_period > 0 else 0
        t5_first_yr = t5_annual * t5_months / 12

        st.markdown(f"""<div class="formula-box">Total award fair value = {fc(t5_grant_fv)} × {fi(t5_ev)} = {fc(t5_total_fv)}
Annual expense       = {fc(t5_total_fv)} / {vesting_period:.1f} = {fc(t5_annual)}
First-year expense   = {fc(t5_annual)} × {t5_months}/12 = {fc(t5_first_yr)}</div>""", unsafe_allow_html=True)

    # KPI cards
    kh5 = '<div class="kpi-grid">'
    kh5 += kpi_card("Fair Value / Option", fc(t5_grant_fv), "Grant date", "green")
    kh5 += kpi_card("Expected Vested", fi(t5_ev), f"{t5_vest_pct*100:.1f}% of {fi(n_total)}")
    kh5 += kpi_card("Total Award FV", fc(t5_total_fv), "Grant-date measurement")
    kh5 += kpi_card("Annual Expense", fc(t5_annual), f"/ {vesting_period:.1f} years", "blue" if True else "")
    kh5 += kpi_card("First-Year Expense", fc(t5_first_yr), f"{t5_months}/12 months", "green")
    kh5 += '</div>'
    st.markdown(kh5, unsafe_allow_html=True)

    # Vesting schedule
    st.markdown(section("📅", "Vesting Schedule"), unsafe_allow_html=True)
    inp5 = ValuationInputs(
        grant_fv_per_option=t5_grant_fv,
        instruments_granted=n_total,
        forfeiture_rate=0.0,
        vesting_period=vesting_period,
        months_in_first_year=t5_months,
        expected_vesting_pct=t5_vest_pct,
    )
    sched5 = calc_vs(inp5)
    sched_df5 = pd.DataFrame(sched5)
    sched_df5["Expense_fmt"]     = sched_df5["Expense"].apply(fc)
    sched_df5["Cumulative_fmt"]  = sched_df5["Cumulative"].apply(fc)
    st.dataframe(sched_df5[["Year", "Expense_fmt", "Cumulative_fmt"]].rename(
        columns={"Expense_fmt": "Period Expense", "Cumulative_fmt": "Cumulative Expense"}),
        use_container_width=True, hide_index=True)
    st.bar_chart(sched_df5.set_index("Year")["Expense"], height=220)

    # Journal entries
    st.markdown(section("📒", "First-Year Journal Entry"), unsafe_allow_html=True)
    if program_type == "Equity-settled":
        entries5 = equity_settled_entries(t5_first_yr)
    elif program_type == "Cash-settled":
        entries5 = cash_settled_entries(t5_first_yr)
    else:
        cp = st.session_state.get("choice_params", {})
        liab_c = min(cp.get("cash_alt_fv", 0) * t5_ev, t5_first_yr)
        eq_c = max(t5_first_yr - liab_c, 0)
        entries5 = employee_choice_entries(t5_first_yr, liab_c, eq_c)

    st.markdown(journal_html(entries5), unsafe_allow_html=True)
    st.session_state["entries5"] = entries5
    st.session_state["first_year_data"] = {
        "grant_fv": t5_grant_fv, "expected_vested": t5_ev,
        "total_fv": t5_total_fv, "annual_expense": t5_annual,
        "first_year_expense": t5_first_yr, "months": t5_months,
    }
    st.session_state["sched5"] = sched5


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 – SUBSEQUENT PERIOD VALUATION
# ══════════════════════════════════════════════════════════════════════════════
with t6:
    # ── Top banner for this tab ──────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#78350F,#B45309,#D97706);
         padding:18px 24px; border-radius:10px; margin-bottom:18px;
         box-shadow:0 3px 12px rgba(120,53,15,0.25);">
      <div style="color:#FFF;font-size:20px;font-weight:700;font-family:'IBM Plex Sans',sans-serif;">
        ⑥ &nbsp; Subsequent Period Valuation
      </div>
      <div style="color:#FDE68A;font-size:12.5px;margin-top:4px;">
        Remeasurement · Catch-up adjustments · Liability movement · IFRS 2 subsequent accounting
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-box" style="background:#FFF7ED;border-color:#FB923C;border-left-color:#EA580C;color:#7C2D12;">
      📌 <strong>Subsequent Period Logic:</strong> Equity-settled awards use a catch-up method
      (no remeasurement of fair value — only update the expected number of vested instruments).
      Cash-settled awards require a full Black-Scholes remeasurement at the reporting date.
      Employee choice arrangements remeasure the liability component only.
    </div>
    """, unsafe_allow_html=True)

    subseq_type = st.selectbox(
        "Settlement Type for This Subsequent Period Calculation",
        ["Equity-settled", "Cash-settled", "Employee choice (cash or equity)"],
        index=["Equity-settled", "Cash-settled", "Employee choice (cash or equity)"].index(
            program_type if program_type in ["Equity-settled", "Cash-settled", "Employee choice (cash or equity)"] else "Equity-settled"
        )
    )

    subseq_result = None

    # ── EQUITY-SETTLED ───────────────────────────────────────────────────────
    if subseq_type == "Equity-settled":
        st.markdown(section_subseq("📌", "Equity-Settled — Subsequent Period Inputs"), unsafe_allow_html=True)
        st.markdown('<div class="subseq-container">', unsafe_allow_html=True)
        st.info("✅ **Equity-settled rule:** Fair value is fixed at grant date and **never remeasured**. Only the expected number of vested instruments is updated each period.")
        c1, c2 = st.columns(2)
        with c1:
            s6e_grant_fv    = st.number_input("Grant-Date Fair Value per Option", min_value=0.0,
                                               value=float(round(st.session_state.get("grant_fv", 25.0), 4)), step=0.0001, format="%.4f")
            s6e_granted     = st.number_input("Original Instruments Granted", min_value=1, value=int(n_total), step=1)
            s6e_new_forf    = st.number_input("Updated Forfeiture Rate (%)", min_value=0.0, max_value=100.0, value=float(forfeiture_rate * 100), step=0.5) / 100
            s6e_vesting     = st.number_input("Total Vesting Period (years)", min_value=0.1, value=float(vesting_period), step=0.1)
        with c2:
            s6e_service     = st.number_input("Cumulative Service Completed (years)", min_value=0.0, value=1.0, step=0.25)
            s6e_prior_exp   = st.number_input("Cumulative Expense in Prior Periods", min_value=0.0, value=0.0, step=1000.0)
            s6e_forfeited   = st.number_input("Instruments Forfeited This Period", min_value=0, value=0, step=10)
            s6e_vested_date = st.number_input("Instruments Vested to Date", min_value=0, value=0, step=10)
        st.markdown('</div>', unsafe_allow_html=True)

        subseq_result = run_equity_subsequent(
            s6e_grant_fv, s6e_granted, s6e_new_forf,
            s6e_service, s6e_vesting, s6e_prior_exp
        )

        st.markdown(section_subseq("📊", "Equity-Settled — Subsequent Period Results"), unsafe_allow_html=True)
        khe = '<div class="kpi-grid">'
        khe += kpi_card("Updated Expected Vested", fi(subseq_result["updated_vested"]), f"{(1-s6e_new_forf)*100:.1f}% of {fi(s6e_granted)}")
        khe += kpi_card("Updated Total FV", fc(subseq_result["updated_total_fv"]), "Grant FV × Updated Vested")
        khe += kpi_card("Service Proportion", fp(subseq_result["service_pct"]), f"{s6e_service:.2f} / {s6e_vesting:.2f} yrs")
        khe += kpi_card("Cumulative Expense Required", fc(subseq_result["cumulative_required"]), "Updated FV × Service %")
        khe += kpi_card("Current Period Expense", fc(subseq_result["current_period_expense"]),
                         "Catch-up / reversal", "green" if subseq_result["current_period_expense"] >= 0 else "red")
        khe += kpi_card("Equity Reserve Closing", fc(subseq_result["equity_reserve_closing"]), "= Cumulative Required")
        khe += '</div>'
        st.markdown(khe, unsafe_allow_html=True)

        st.markdown(f"""<div class="formula-box">Updated vested instruments:  {fi(subseq_result['updated_vested'])}  ({s6e_granted:,} × {(1-s6e_new_forf)*100:.1f}%)
Updated total award FV:      {fc(subseq_result['updated_total_fv'])}
Service proportion:          {subseq_result['service_pct']*100:.2f}%  ({s6e_service:.2f} / {s6e_vesting:.2f} yrs)
Cumulative expense required: {fc(subseq_result['cumulative_required'])}
Prior cumulative expense:    {fc(s6e_prior_exp)}
Current period expense:      {fc(subseq_result['current_period_expense'])}  (catch-up adjustment)</div>""", unsafe_allow_html=True)

        st.markdown(section_subseq("📒", "Journal Entry — Current Period"), unsafe_allow_html=True)
        st.markdown(journal_html(subseq_result["entries"]), unsafe_allow_html=True)

    # ── CASH-SETTLED ─────────────────────────────────────────────────────────
    elif subseq_type == "Cash-settled":
        st.markdown(section_subseq("💰", "Cash-Settled — Subsequent Period Inputs"), unsafe_allow_html=True)
        st.markdown('<div class="subseq-container">', unsafe_allow_html=True)
        st.info("💰 **Cash-settled rule:** Liability is **remeasured at current fair value** at every reporting date. Full Black-Scholes recalculation required.")
        c1, c2 = st.columns(2)
        with c1:
            s6c_S0       = st.number_input("Current Share Price S₀", min_value=0.01,
                                            value=float(st.session_state.get("S0", 100.0)), step=0.01)
            s6c_K        = st.number_input("Strike Price K", min_value=0.01,
                                            value=float(st.session_state.get("K", 100.0)), step=0.01)
            s6c_r        = st.number_input("Risk-free Rate (%)", min_value=0.0, max_value=30.0,
                                            value=float(st.session_state.get("r", 0.04) * 100), step=0.05) / 100
            s6c_q        = st.number_input("Dividend Yield (%)", min_value=0.0, max_value=20.0,
                                            value=float(st.session_state.get("q", 0.0) * 100), step=0.05) / 100
            s6c_sigma    = st.number_input("Volatility σ (%)", min_value=0.1, max_value=300.0,
                                            value=float(st.session_state.get("sigma", st.session_state.get("sigma_bs", 0.30)) * 100), step=0.1) / 100
        with c2:
            s6c_T        = st.number_input("Remaining Expected Life (years)", min_value=0.1, max_value=20.0, value=max(0.5, float(total_period - 1.0)), step=0.1)
            s6c_outstand = st.number_input("Instruments Outstanding", min_value=0, value=int(n_total), step=10)
            s6c_forf     = st.number_input("Updated Forfeiture Rate (%)", min_value=0.0, max_value=100.0, value=float(forfeiture_rate * 100), step=0.5) / 100
            s6c_service  = st.number_input("Cumulative Service (years)", min_value=0.0, value=1.0, step=0.25)
            s6c_vesting  = st.number_input("Total Vesting Period (years)", min_value=0.1, value=float(vesting_period), step=0.1)
            s6c_open_lib = st.number_input("Opening Liability (prior period)", min_value=0.0, value=0.0, step=1000.0)
            s6c_cash     = st.number_input("Cash Paid / Settled This Period", min_value=0.0, value=0.0, step=1000.0)
        st.markdown('</div>', unsafe_allow_html=True)

        try:
            subseq_result = run_cash_subsequent(
                s6c_S0, s6c_K, s6c_r, s6c_q, s6c_sigma, s6c_T,
                s6c_outstand, s6c_forf, s6c_service, s6c_vesting,
                s6c_open_lib, s6c_cash
            )

            st.markdown(section_subseq("📊", "Cash-Settled — Subsequent Period Results"), unsafe_allow_html=True)
            pl_sign = "green" if subseq_result["pl_impact"] >= 0 else "red"
            khc = '<div class="kpi-grid">'
            khc += kpi_card("Current FV / Option", fc(subseq_result["current_fv_per_option"]), "Black-Scholes at reporting date", "blue")
            khc += kpi_card("Expected Vested", fi(subseq_result["expected_vested"]), "After forfeiture")
            khc += kpi_card("Service Proportion", fp(subseq_result["service_pct"]), f"{s6c_service:.2f} / {s6c_vesting:.2f} yrs")
            khc += kpi_card("Closing Liability", fc(subseq_result["closing_liability"]), "Remeasured", "amber")
            khc += kpi_card("Opening Liability", fc(s6c_open_lib), "Prior period")
            khc += kpi_card("P&L Charge / (Credit)", fc(subseq_result["pl_impact"]), "Current period impact", pl_sign)
            khc += '</div>'
            st.markdown(khc, unsafe_allow_html=True)

            st.markdown(f"""<div class="formula-box">Current FV per option (BS):  {fc(subseq_result['current_fv_per_option'])}
Expected vested:             {fi(subseq_result['expected_vested'])}
Service proportion:          {subseq_result['service_pct']*100:.2f}%
Closing liability:           FV × Vested × Service = {fc(subseq_result['closing_liability'])}
Opening liability:           {fc(s6c_open_lib)}
Cash paid this period:       {fc(s6c_cash)}
P&L impact:                  Closing - Opening + Cash = {fc(subseq_result['pl_impact'])}</div>""", unsafe_allow_html=True)

            st.markdown(section_subseq("📒", "Journal Entries — Current Period"), unsafe_allow_html=True)
            st.markdown(journal_html(subseq_result["entries"]), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Cash-settled remeasurement error: {e}")

    # ── EMPLOYEE CHOICE ──────────────────────────────────────────────────────
    else:
        st.markdown(section_subseq("🔄", "Employee Choice — Subsequent Period Inputs"), unsafe_allow_html=True)
        st.markdown('<div class="subseq-container">', unsafe_allow_html=True)
        st.warning("⚠️ Employee choice arrangements require detailed analysis of the contractual terms. Classification must be confirmed with auditors.")
        c1, c2 = st.columns(2)
        with c1:
            s6ch_obligation = st.radio("Entity has present obligation to settle in cash?", ["Yes", "No"], horizontal=True)
            s6ch_open_lib   = st.number_input("Opening Liability", min_value=0.0, value=0.0, step=1000.0)
            s6ch_cash_alt   = st.number_input("Updated Cash Alternative FV per Option", min_value=0.0, value=0.0, step=0.01)
            s6ch_equity_alt = st.number_input("Updated Equity Alternative FV per Option", min_value=0.0, value=0.0, step=0.01)
        with c2:
            s6ch_updated_vested = st.number_input("Updated Expected Vested Instruments", min_value=0, value=int(n_total * exp_vest_pct_input), step=10)
            s6ch_service     = st.number_input("Service Proportion (0–1)", min_value=0.0, max_value=1.0, value=min(1.0, 1.0/vesting_period), step=0.01)
            s6ch_cash_settled= st.number_input("Instruments Settled in Cash", min_value=0, value=0, step=10)
            s6ch_eq_settled  = st.number_input("Instruments Settled in Equity", min_value=0, value=0, step=10)
            s6ch_cash_paid   = st.number_input("Cash Paid This Period", min_value=0.0, value=0.0, step=1000.0)
            s6ch_forfeited   = st.number_input("Instruments Forfeited / Cancelled", min_value=0, value=0, step=10)
        st.markdown('</div>', unsafe_allow_html=True)

        subseq_result = run_choice_subsequent(
            has_obligation=(s6ch_obligation == "Yes"),
            opening_liability=s6ch_open_lib,
            cash_alt_fv=s6ch_cash_alt,
            equity_alt_fv=s6ch_equity_alt,
            updated_vested=float(s6ch_updated_vested),
            service_pct=s6ch_service,
            instruments_settled_cash=s6ch_cash_settled,
            instruments_settled_equity=s6ch_eq_settled,
            cash_paid=s6ch_cash_paid,
            instruments_forfeited=s6ch_forfeited,
        )

        st.markdown(section_subseq("📊", "Employee Choice — Subsequent Results"), unsafe_allow_html=True)
        kho = '<div class="kpi-grid">'
        kho += kpi_card("Liability Component", fc(subseq_result["liability_component"]), "Cash alternative FV × vested × service", "amber")
        kho += kpi_card("Equity Component", fc(subseq_result["equity_component"]), "Residual (equity alt – cash alt)", "green")
        kho += kpi_card("Total Period Expense", fc(subseq_result["total_expense"]), "Liability + Equity components")
        kho += kpi_card("Remeasurement Gain/(Loss)", fc(subseq_result["remeasurement_gain_loss"]),
                         "Liability vs opening", "green" if subseq_result["remeasurement_gain_loss"] <= 0 else "red")
        kho += '</div>'
        st.markdown(kho, unsafe_allow_html=True)
        st.markdown(section_subseq("📒", "Journal Entries — Current Period"), unsafe_allow_html=True)
        st.markdown(journal_html(subseq_result["entries"]), unsafe_allow_html=True)

    st.session_state["subseq_result"] = subseq_result


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 – SUMMARY & EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with t7:
    st.markdown(section("⑦", "Executive Summary & Export"), unsafe_allow_html=True)

    # ── KPI dashboard ────────────────────────────────────────────────────────
    bs_r     = st.session_state.get("bs_results", {})
    fy_data  = st.session_state.get("first_year_data", {})
    sub_r    = st.session_state.get("subseq_result", {})

    grant_fv_sum    = bs_r.get("call", 0.0)
    ev_sum          = n_total * exp_vest_pct_input
    total_fv_sum    = grant_fv_sum * ev_sum
    annual_exp_sum  = total_fv_sum / vesting_period if vesting_period > 0 else 0
    fy_exp_sum      = annual_exp_sum * months_yr1 / 12
    closing_lib_sum = sub_r.get("closing_liability", sub_r.get("liability_component", 0.0)) if sub_r else 0.0
    eq_reserve_sum  = sub_r.get("equity_reserve_closing", sub_r.get("equity_component", 0.0)) if sub_r else total_fv_sum * (months_yr1 / 12 / vesting_period)
    curr_exp_sum    = sub_r.get("current_period_expense", sub_r.get("pl_impact", sub_r.get("total_expense", 0.0))) if sub_r else 0.0

    kh7 = '<div class="kpi-grid">'
    kh7 += kpi_card("Program Type", program_type.split()[0], instrument_type)
    kh7 += kpi_card("Fair Value / Option", fc(grant_fv_sum), "Black-Scholes call", "green")
    kh7 += kpi_card("Expected Vested", fi(ev_sum), f"{exp_vest_pct_input*100:.1f}% of {fi(n_total)}")
    kh7 += kpi_card("Total Award FV", fc(total_fv_sum), "Grant-date measurement", "blue" if True else "")
    kh7 += kpi_card("First-Year Expense", fc(fy_exp_sum), f"{months_yr1}/12 months", "green")
    kh7 += kpi_card("Current Period Expense", fc(curr_exp_sum), "From subsequent tab", "amber")
    kh7 += kpi_card("Closing Liability", fc(closing_lib_sum), "Cash-settled / choice", "red" if closing_lib_sum > 0 else "")
    kh7 += kpi_card("Equity Reserve", fc(eq_reserve_sum), "Equity-settled / choice")
    kh7 += '</div>'
    st.markdown(kh7, unsafe_allow_html=True)

    # ── IFRS 2 Conclusion ────────────────────────────────────────────────────
    st.markdown(section("📋", "Key IFRS 2 Conclusion"), unsafe_allow_html=True)
    if program_type == "Equity-settled":
        conclusion = f"""✅ **Equity-Settled Award**
- Grant-date fair value of **{fc(grant_fv_sum)}** per option is fixed and not remeasured.
- Expected vested instruments: **{fi(ev_sum)}** ({exp_vest_pct_input*100:.1f}% of {fi(n_total)} granted).
- Total IFRS 2 cost to be recognized over **{vesting_period:.1f} years**: **{fc(total_fv_sum)}**.
- Year 1 expense ({months_yr1}/12 months): **{fc(fy_exp_sum)}**.
- Credit: Share-based payment reserve (equity). No liability recognized."""
    elif program_type == "Cash-settled":
        conclusion = f"""💰 **Cash-Settled Award**
- A liability is recognized and **remeasured at each reporting date**.
- Year 1 expense: **{fc(fy_exp_sum)}**. Opening liability: **{fc(0.0)}**.
- Subsequent period closing liability: **{fc(closing_lib_sum)}**.
- P&L impact (subsequent period): **{fc(curr_exp_sum)}**.
- Fair value used from Black-Scholes: **{fc(grant_fv_sum)}** per option at grant date."""
    else:
        conclusion = f"""🔄 **Employee Choice – Compound Instrument**
- The arrangement contains both a liability component (cash alternative) and an equity component.
- Total IFRS 2 cost: **{fc(total_fv_sum)}** over **{vesting_period:.1f} years**.
- Year 1 expense: **{fc(fy_exp_sum)}**.
- Liability component is remeasured each period; equity component is fixed at grant date.
- ⚠️ Classification requires review of the specific legal terms of the arrangement."""

    st.info(conclusion)

    # ── Summary table ────────────────────────────────────────────────────────
    st.markdown(section("📊", "Full Assumptions & Results Summary"), unsafe_allow_html=True)
    summ_rows = [
        ("PROGRAM INPUTS", "", ""),
        ("Program Type", program_type, ""),
        ("Instrument Type", instrument_type, ""),
        ("Grant Date", str(grant_date), ""),
        ("Reporting Date", str(reporting_date), ""),
        ("Number of Employees", fi(n_employees), ""),
        ("Instruments per Employee", fi(opts_per_emp), ""),
        ("Total Instruments Granted", fi(n_total), ""),
        ("Expected Forfeiture Rate", fp(forfeiture_rate), ""),
        ("Expected Vesting %", fp(exp_vest_pct_input), ""),
        ("Expected Vested Instruments", fi(ev_sum), "Granted × vesting %"),
        ("Vesting Period", f"{vesting_period:.1f} years", ""),
        ("BLACK-SCHOLES INPUTS", "", ""),
        ("Share Price S₀", fc(st.session_state.get("S0", 0)), "At grant date"),
        ("Strike Price K", fc(st.session_state.get("K", 0)), ""),
        ("Risk-free Rate r", fp(st.session_state.get("r", 0)), ""),
        ("Dividend Yield q", fp(st.session_state.get("q", 0)), ""),
        ("Volatility σ", fp(st.session_state.get("sigma", st.session_state.get("sigma_bs", 0))), "Annualized"),
        ("Expected Life T", f"{st.session_state.get('T', 0):.1f} years", ""),
        ("VALUATION RESULTS", "", ""),
        ("Fair Value per Option (Call)", fc(grant_fv_sum), "Black-Scholes"),
        ("Fair Value per Option (Put)", fc(bs_r.get("put", 0)), "Informational"),
        ("Total Award Fair Value", fc(total_fv_sum), "FV × Expected Vested"),
        ("Annual IFRS 2 Expense", fc(annual_exp_sum), "Total FV / Vesting Period"),
        ("First-Year Expense", fc(fy_exp_sum), f"{months_yr1}/12 months"),
        ("SUBSEQUENT PERIOD", "", ""),
        ("Current Period Expense / P&L", fc(curr_exp_sum), ""),
        ("Closing Liability", fc(closing_lib_sum), "Cash-settled / choice only"),
        ("Equity Reserve Closing", fc(eq_reserve_sum), ""),
    ]
    summ_df7 = pd.DataFrame(summ_rows, columns=["Category / Item", "Value", "Notes"])
    st.dataframe(summ_df7, use_container_width=True, hide_index=True)

    # ── First-year accounting recap ──────────────────────────────────────────
    st.markdown(section("📒", "First-Year Journal Entry"), unsafe_allow_html=True)
    entries7 = st.session_state.get("entries5", equity_settled_entries(fy_exp_sum))
    st.markdown(journal_html(entries7), unsafe_allow_html=True)

    # ── EXPORT ───────────────────────────────────────────────────────────────
    st.markdown(section("📥", "Export to Excel"), unsafe_allow_html=True)
    st.markdown("""The Excel workbook includes 10 sheets:
**Executive Summary · Inputs · Historical Prices · Log Returns · Volatility Calculation ·
Black-Scholes Valuation · Vesting Assumptions · First-Year Accounting · Accounting Entries · Subsequent Period**""")

    if st.button("📊 Generate Excel Report", type="primary"):
        with st.spinner("Building professional Excel report..."):
            try:
                inputs_dict = {
                    "program_type": program_type,
                    "instrument_type": instrument_type,
                    "grant_date": grant_date,
                    "reporting_date": reporting_date,
                    "vesting_period": vesting_period,
                    "total_period": total_period,
                    "n_employees": n_employees,
                    "options_per_employee": opts_per_emp,
                    "n_total": n_total,
                    "forfeiture_rate": forfeiture_rate,
                    "expected_vesting_pct": exp_vest_pct_input,
                    "months_in_first_year": months_yr1,
                    "S0": st.session_state.get("S0", 0),
                    "K":  st.session_state.get("K", 0),
                    "r":  st.session_state.get("r", 0),
                    "q":  st.session_state.get("q", 0),
                    "T":  st.session_state.get("T", 0),
                }
                sigma_exp = st.session_state.get("sigma", st.session_state.get("sigma_bs", None))
                lr_exp = st.session_state.get("log_returns", None)
                pd_exp = st.session_state.get("prices_df", None)
                vi_exp = st.session_state.get("vol_info", None)
                sched_exp = st.session_state.get("sched5", [])
                sub_exp = st.session_state.get("subseq_result", None)

                summary_kpis = {
                    "Program Type": program_type,
                    "Instrument Type": instrument_type,
                    "Fair Value per Option": fc(grant_fv_sum),
                    "Expected Vested Instruments": fi(ev_sum),
                    "Total Award Fair Value": fc(total_fv_sum),
                    "First-Year IFRS 2 Expense": fc(fy_exp_sum),
                    "Current Period Expense": fc(curr_exp_sum),
                    "Closing Liability": fc(closing_lib_sum),
                    "Equity Reserve": fc(eq_reserve_sum),
                    "Volatility σ": fp(sigma_exp) if sigma_exp else "—",
                }

                excel_bytes = build_excel(
                    inputs=inputs_dict,
                    bs_results=bs_r if bs_r else None,
                    sigma=sigma_exp,
                    first_year=fy_data if fy_data else None,
                    vesting_sched=sched_exp,
                    accounting_entries=entries7,
                    subsequent_result=sub_exp,
                    log_returns_series=lr_exp,
                    prices_df=pd_exp,
                    vol_info=vi_exp,
                    summary_kpis=summary_kpis,
                )
                st.download_button(
                    label="⬇️ Download Excel Workbook",
                    data=excel_bytes,
                    file_name=f"IFRS2_SBP_Valuation_{date.today().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                st.success("✅ Excel report ready!")
            except Exception as e:
                st.error(f"Export error: {e}")
                import traceback
                st.code(traceback.format_exc())

    st.markdown(DISCLAIMER_HTML, unsafe_allow_html=True)
