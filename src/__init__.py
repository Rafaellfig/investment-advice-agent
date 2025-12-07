"""Service and utility modules."""

from .file_utils import read_file, write_file
from .ai_service import (
    call_openai,
    summarize_portfolio_results,
    summarize_risk_profile,
    summarize_macroeconomic_outlook,
    generate_investment_letter,
)
from .portfolio_parser import (
    parse_portfolio,
    format_portfolio_summary,
    summarize_portfolio,
    calculate_monthly_stock_returns,
    calculate_monthly_stock_returns_list,
    PortfolioSummary,
    Stock,
    InvestmentFund,
    FixedIncomeSecurity,
)

__all__ = [
    "read_file",
    "write_file",
    "call_openai",
    "summarize_portfolio_results",
    "summarize_risk_profile",
    "summarize_macroeconomic_outlook",
    "generate_investment_letter",
    "parse_portfolio",
    "format_portfolio_summary",
    "summarize_portfolio",
    "calculate_monthly_stock_returns",
    "calculate_monthly_stock_returns_list",
    "PortfolioSummary",
    "Stock",
    "InvestmentFund",
    "FixedIncomeSecurity",
]
