"""
Black-Scholes option pricing model for IFRS 2 share-based payment valuation.

Formulas:
  d1 = [ln(S0/K) + (r - q + σ²/2)·T] / (σ·√T)
  d2 = d1 - σ·√T
  Call: C = S0·e^(-qT)·N(d1) - K·e^(-rT)·N(d2)
  Put:  P = K·e^(-rT)·N(-d2) - S0·e^(-qT)·N(-d1)
"""

import numpy as np
from scipy.stats import norm


def validate_inputs(S0, K, r, q, sigma, T):
    """Raise ValueError if inputs are invalid."""
    if S0 <= 0:
        raise ValueError("Share price S0 must be positive.")
    if K <= 0:
        raise ValueError("Strike price K must be positive.")
    if sigma <= 0:
        raise ValueError("Volatility σ must be positive.")
    if T <= 0:
        raise ValueError("Expected life T must be positive.")


def compute_d1_d2(S0: float, K: float, r: float, q: float, sigma: float, T: float):
    """Return (d1, d2) for the Black-Scholes model."""
    validate_inputs(S0, K, r, q, sigma, T)
    d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def bs_call(S0, K, r, q, sigma, T):
    """Black-Scholes call option price."""
    d1, d2 = compute_d1_d2(S0, K, r, q, sigma, T)
    return S0 * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def bs_put(S0, K, r, q, sigma, T):
    """Black-Scholes put option price."""
    d1, d2 = compute_d1_d2(S0, K, r, q, sigma, T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S0 * np.exp(-q * T) * norm.cdf(-d1)


def bs_full(S0, K, r, q, sigma, T):
    """Return full Black-Scholes results dict."""
    d1, d2 = compute_d1_d2(S0, K, r, q, sigma, T)
    call = bs_call(S0, K, r, q, sigma, T)
    put = bs_put(S0, K, r, q, sigma, T)

    # Greeks
    delta_call = np.exp(-q * T) * norm.cdf(d1)
    delta_put = -np.exp(-q * T) * norm.cdf(-d1)
    gamma = np.exp(-q * T) * norm.pdf(d1) / (S0 * sigma * np.sqrt(T))
    vega = S0 * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T) / 100
    theta_call = (
        -S0 * np.exp(-q * T) * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
        - r * K * np.exp(-r * T) * norm.cdf(d2)
        + q * S0 * np.exp(-q * T) * norm.cdf(d1)
    ) / 365

    return {
        "d1": d1, "d2": d2,
        "Nd1": norm.cdf(d1), "Nd2": norm.cdf(d2),
        "N_neg_d1": norm.cdf(-d1), "N_neg_d2": norm.cdf(-d2),
        "call": call, "put": put,
        "delta_call": delta_call, "delta_put": delta_put,
        "gamma": gamma, "vega": vega, "theta_call": theta_call,
    }
