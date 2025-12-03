"""Módulos de serviços e utilitários."""

from .file_utils import read_file, write_file
from .ai_service import (
    call_openai,
    summarize_portfolio_results,
    summarize_risk_profile,
    summarize_macroeconomic_outlook,
    generate_investment_letter,
)

__all__ = [
    "read_file",
    "write_file",
    "call_openai",
    "summarize_portfolio_results",
    "summarize_risk_profile",
    "summarize_macroeconomic_outlook",
    "generate_investment_letter",
]

