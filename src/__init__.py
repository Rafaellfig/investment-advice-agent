"""Service and utility modules."""

from .file_utils import read_file, write_file, create_letter
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
    calculate_portfolio_monthly_return_simple,
    plot_portfolio_donut_with_inner_ring,
    PortfolioSummary,
    Stock,
    InvestmentFund,
    FixedIncomeSecurity,
    InvestmentAdvisor,
)

__all__ = [
    "read_file",
    "write_file",
    "create_letter",
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
    "calculate_portfolio_monthly_return_simple",
    "plot_portfolio_donut_with_inner_ring",
    "create_letter",
    "PortfolioSummary",
    "Stock",
    "InvestmentFund",
    "FixedIncomeSecurity",
    "InvestmentAdvisor",
]
