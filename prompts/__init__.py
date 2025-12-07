"""Prompt templates for OpenAI API."""

from .prompts import (
    get_portfolio_prompt,
    get_risk_profile_prompt,
    get_macro_outlook_prompt,
    get_investment_letter_prompt,
)

__all__ = [
    "get_portfolio_prompt",
    "get_risk_profile_prompt",
    "get_macro_outlook_prompt",
    "get_investment_letter_prompt",
]
