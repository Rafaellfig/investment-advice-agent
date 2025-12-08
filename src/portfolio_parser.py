"""Module for processing and extracting information from portfolio files."""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


@dataclass
class Stock:
    """Represents a stock in the portfolio."""
    code: str
    position: float
    allocation_percentage: float
    return_rate: float
    last_price: Optional[float] = None
    average_price: Optional[float] = None
    quantity: Optional[int] = None
    investment_date: Optional[str] = None
    monthly_return: Optional[float] = None
    previous_month_price: Optional[float] = None


@dataclass
class InvestmentFund:
    """Represents an investment fund in the portfolio."""
    name: str
    position: float
    allocation_percentage: float
    return_rate: float
    invested_amount: Optional[float] = None
    net_value: Optional[float] = None
    investment_date: Optional[str] = None
    quota_date: Optional[str] = None


@dataclass
class FixedIncomeSecurity:
    """Represents a fixed income security in the portfolio."""
    name: str
    market_position: float
    allocation_percentage: float
    invested_amount: float
    market_rate: Optional[str] = None
    application_date: Optional[str] = None
    maturity_date: Optional[str] = None
    investment_date: Optional[str] = None


@dataclass
class InvestmentAdvisor:
    """Represents the investment advisor information."""
    name: str
    code: str
    position: str = "Assessor de Investimentos"
    company_name: str = "XP"


@dataclass
class PortfolioSummary:
    """Structured summary of the client's portfolio."""
    client_name: str
    total_assets: float
    total_invested: float
    available_balance: float
    stocks: List[Stock] = field(default_factory=list)
    funds: List[InvestmentFund] = field(default_factory=list)
    fixed_income_securities: List[FixedIncomeSecurity] = field(default_factory=list)
    stocks_percentage: float = 0.0
    funds_percentage: float = 0.0
    fixed_income_percentage: float = 0.0
    portfolio_monthly_return: Optional[float] = None
    advisor: Optional[InvestmentAdvisor] = None


def extract_monetary_value(text: str) -> Optional[float]:
    """Extracts monetary value from a string (format R$ X.XXX,XX or R$ X,XXX.XX)."""
    if not text:
        return None
    # Remove R$ and spaces
    clean_text = text.replace("R$", "").strip()
    # Remove all spaces
    clean_text = clean_text.replace(" ", "")
    
    # Detect format: if dot comes before comma, it's Brazilian format (R$ 1.234,56)
    # If comma comes before dot, it might be American format (R$ 1,234.56)
    if "." in clean_text and "," in clean_text:
        # Check which comes first
        dot_idx = clean_text.find(".")
        comma_idx = clean_text.find(",")
        if dot_idx < comma_idx:
            # Brazilian format: 1.234,56
            clean_text = clean_text.replace(".", "").replace(",", ".")
        else:
            # American format: 1,234.56
            clean_text = clean_text.replace(",", "")
    elif "," in clean_text:
        # Only comma, might be Brazilian decimal
        clean_text = clean_text.replace(",", ".")
    # If only dot, might be decimal or thousand - assume decimal if not 3 digits after
    
    try:
        return float(clean_text)
    except (ValueError, AttributeError):
        return None


def extract_percentage(text: str) -> Optional[float]:
    """Extracts percentage from a string (format X,XX% or X.XX%)."""
    if not text:
        return None
    clean_text = text.replace("%", "").strip()
    # Replace comma with dot
    clean_text = clean_text.replace(",", ".")
    try:
        return float(clean_text)
    except (ValueError, AttributeError):
        return None


def extract_return_rate(text: str) -> Optional[float]:
    """Extracts return rate from a string (may have negative sign)."""
    if not text:
        return None
    clean_text = text.replace("%", "").strip()
    # Replace comma with dot
    clean_text = clean_text.replace(",", ".")
    try:
        return float(clean_text)
    except (ValueError, AttributeError):
        return None


def parse_portfolio(portfolio_text: str) -> PortfolioSummary:
    """
    Processes the portfolio text and extracts all structured information.
    
    Args:
        portfolio_text: Complete text from the portfolio file
        
    Returns:
        PortfolioSummary with all extracted information
    """
    lines = [line.strip() for line in portfolio_text.split('\n')]
    
    # Initialize summary
    summary = PortfolioSummary(
        client_name="",
        total_assets=0.0,
        total_invested=0.0,
        available_balance=0.0
    )
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Extract client name (first line)
        if not summary.client_name and line and "este é o seu patrimônio" in line.lower():
            # Extract name before comma
            parts = line.split(",")
            if parts:
                summary.client_name = parts[0].strip()
        
        # Extract advisor information
        if "código do assessor" in line.lower() and i + 1 < len(lines):
            advisor_code = lines[i + 1].strip() if i + 1 < len(lines) else ""
            advisor_name = ""
            
            # Look for "Nome do assessor" in the next few lines
            j = i + 2
            while j < len(lines) and j < i + 10:  # Search up to 10 lines ahead
                if "nome do assessor" in lines[j].lower():
                    if j + 1 < len(lines):
                        advisor_name = lines[j + 1].strip()
                    break
                j += 1
            
            # Create advisor object if we have at least the code
            if advisor_code:
                summary.advisor = InvestmentAdvisor(
                    name=advisor_name if advisor_name else "N/A",
                    code=advisor_code
                )
        
        # Collect all monetary values before "Ações" section
        # The order is: first value = total assets, second = total invested, last = available balance
        # Only process once when we first encounter "Total investido" or "Saldo Disponível"
        if line.lower() in ["total investido", "saldo disponível"] and summary.total_assets == 0.0:
            # Collect all R$ values between here and "Ações"
            j = i + 1
            monetary_values = []
            while j < len(lines) and lines[j] != "Ações":
                if lines[j].startswith("R$"):
                    value = extract_monetary_value(lines[j])
                    if value:
                        monetary_values.append(value)
                j += 1
            
            # Assign values based on order:
            # First value = total assets
            # Second value = total invested
            # Last value = available balance
            if len(monetary_values) >= 3:
                summary.total_assets = monetary_values[0]
                summary.total_invested = monetary_values[1]
                summary.available_balance = monetary_values[-1]
            elif len(monetary_values) == 2:
                # If only 2 values, assume first is total assets, second is total invested
                summary.total_assets = monetary_values[0]
                summary.total_invested = monetary_values[1]
                summary.available_balance = 0.0
            elif len(monetary_values) == 1:
                # If only 1 value, it's the total assets
                summary.total_assets = monetary_values[0]
                summary.total_invested = 0.0
                summary.available_balance = 0.0
        
        # Stocks section
        if line == "Ações" and i + 1 < len(lines):
            # Next line has total stocks percentage
            stocks_percentage = extract_percentage(lines[i+1])
            if stocks_percentage:
                summary.stocks_percentage = stocks_percentage
            
            # Skip headers and process stocks
            i += 2
            # Skip header lines until finding first stock
            while i < len(lines) and not re.match(r'^[A-Z]{4}\d$', lines[i]):
                i += 1
            
            # Process stocks until finding "Fundos de Investimentos"
            while i < len(lines) and lines[i] != "Fundos de Investimentos":
                current_line = lines[i]
                
                # Check if it's a stock code (format XXX3, XXX4, etc.)
                if re.match(r'^[A-Z]{4}\d$', current_line):
                    stock = Stock(code=current_line, position=0.0, allocation_percentage=0.0, return_rate=0.0)
                    
                    # Next lines have position, % allocation and return rate
                    # Skip empty lines
                    j = i + 1
                    while j < len(lines) and not lines[j]:
                        j += 1
                    if j < len(lines) and lines[j].startswith("R$"):
                        position = extract_monetary_value(lines[j])
                        if position:
                            stock.position = position
                    
                    j += 1
                    while j < len(lines) and not lines[j]:
                        j += 1
                    if j < len(lines) and "%" in lines[j]:
                        percentage = extract_percentage(lines[j])
                        if percentage:
                            stock.allocation_percentage = percentage
                    
                    j += 1
                    while j < len(lines) and not lines[j]:
                        j += 1
                    if j < len(lines) and ("%" in lines[j] or "-" in lines[j] or lines[j][0].isdigit()):
                        return_rate = extract_return_rate(lines[j])
                        if return_rate is not None:
                            stock.return_rate = return_rate
                    
                    summary.stocks.append(stock)
                    i = j + 1
                else:
                    i += 1
            continue
        
        # Investment Funds section
        if line == "Fundos de Investimentos" and i + 1 < len(lines):
            # Next line has total funds percentage
            funds_percentage = extract_percentage(lines[i+1])
            if funds_percentage:
                summary.funds_percentage = funds_percentage
            
            i += 2
            # Skip headers
            while i < len(lines) and (lines[i] in ["Posição", "% Alocação", "Rentabilidade", ""] or 
                                      lines[i].startswith("Posição") or lines[i].startswith("%")):
                i += 1
            
            # Process funds until finding "Renda Fixa"
            while i < len(lines) and "Renda Fixa" not in lines[i]:
                current_line = lines[i]
                
                # Check if there's a fund pattern: R$, %, % followed by fund name
                # This handles the case where data comes before the name
                if (i + 6 < len(lines) and
                    lines[i].startswith("R$") and
                    "%" in lines[i+2] and
                    "%" in lines[i+4] and
                    lines[i+6] and
                    len(lines[i+6]) > 10 and
                    ("FIC" in lines[i+6] or "FIM" in lines[i+6] or "FIA" in lines[i+6] or 
                     "Advisory" in lines[i+6] or "Hedge" in lines[i+6])):
                    
                    # Data comes before name
                    fund = InvestmentFund(
                        name=lines[i+6],
                        position=0.0,
                        allocation_percentage=0.0,
                        return_rate=0.0
                    )
                    
                    position = extract_monetary_value(lines[i])
                    if position:
                        fund.position = position
                    
                    percentage = extract_percentage(lines[i+2])
                    if percentage:
                        fund.allocation_percentage = percentage
                    
                    return_rate = extract_return_rate(lines[i+4])
                    if return_rate is not None:
                        fund.return_rate = return_rate
                    
                    summary.funds.append(fund)
                    i = i + 7
                    continue
                
                # Fund name is usually a long line that's not a stock code
                if (current_line and 
                    not re.match(r'^[A-Z]{4}\d$', current_line) and
                    not current_line.startswith("R$") and
                    "%" not in current_line and
                    "Posição" not in current_line and
                    "Alocação" not in current_line and
                    "Rentabilidade" not in current_line and
                    "Data" not in current_line and
                    "Valor" not in current_line and
                    len(current_line) > 10 and
                    ("FIC" in current_line or "FIM" in current_line or "FIA" in current_line or "Advisory" in current_line or "Hedge" in current_line)):
                    
                    fund = InvestmentFund(
                        name=current_line,
                        position=0.0,
                        allocation_percentage=0.0,
                        return_rate=0.0
                    )
                    
                    # Next lines have position, % allocation and return rate
                    j = i + 1
                    while j < len(lines) and not lines[j]:
                        j += 1
                    if j < len(lines) and lines[j].startswith("R$"):
                        position = extract_monetary_value(lines[j])
                        if position:
                            fund.position = position
                    
                    j += 1
                    while j < len(lines) and not lines[j]:
                        j += 1
                    if j < len(lines) and "%" in lines[j]:
                        percentage = extract_percentage(lines[j])
                        if percentage:
                            fund.allocation_percentage = percentage
                    
                    j += 1
                    while j < len(lines) and not lines[j]:
                        j += 1
                    if j < len(lines) and ("%" in lines[j] or "-" in lines[j] or (lines[j] and lines[j][0].isdigit())):
                        return_rate = extract_return_rate(lines[j])
                        if return_rate is not None:
                            fund.return_rate = return_rate
                    
                    summary.funds.append(fund)
                    i = j + 1
                else:
                    i += 1
            continue
        
        # Fixed Income section
        if line == "Renda Fixa" and i + 1 < len(lines):
            # Next line has total fixed income percentage
            fixed_income_percentage = extract_percentage(lines[i+1])
            if fixed_income_percentage:
                summary.fixed_income_percentage = fixed_income_percentage
            
            i += 2
            # Skip headers and empty lines
            while i < len(lines) and (lines[i] in ["Posição a mercado", "% Alocação", "Valor aplicado", ""] or
                                      lines[i].startswith("Posição") or lines[i].startswith("%") or
                                      lines[i].startswith("Valor") or not lines[i]):
                i += 1
            
            # Process fixed income securities
            while i < len(lines):
                current_line = lines[i].strip()  # Remove spaces and special characters
                
                # Remove control characters (form feed, etc.)
                current_line = re.sub(r'[\x00-\x1F\x7F]', '', current_line)
                
                # Security name usually contains "CDB", "LCI", "LCA", etc.
                if (current_line and 
                    ("CDB" in current_line.upper() or "LCI" in current_line.upper() or 
                     "LCA" in current_line.upper() or "DEB" in current_line.upper() or
                     "TESOURO" in current_line.upper() or "NTN" in current_line.upper() or
                     "BANCO" in current_line.upper() or "CONSIGNADO" in current_line.upper())):
                    
                    security = FixedIncomeSecurity(
                        name=current_line,
                        market_position=0.0,
                        allocation_percentage=0.0,
                        invested_amount=0.0
                    )
                    
                    # Look for market position, % allocation and invested amount
                    j = i + 1
                    r_values = []  # List to store R$ values found
                    percentages = []  # List to store percentages found
                    
                    while j < len(lines) and j < i + 20:
                        proc_line = lines[j]
                        
                        if not proc_line:
                            j += 1
                            continue
                        
                        # If finds "Conta:" or another section, stop
                        if proc_line.startswith("Conta:") or "Código do Assessor" in proc_line:
                            break
                        
                        if proc_line.startswith("R$"):
                            value = extract_monetary_value(proc_line)
                            if value:
                                r_values.append(value)
                        
                        if "%" in proc_line:
                            percentage = extract_percentage(proc_line)
                            if percentage:
                                percentages.append(percentage)
                        
                        j += 1
                    
                    # Associate values: first large R$ is market position, second is invested amount
                    if len(r_values) >= 1:
                        security.market_position = r_values[0]
                    if len(r_values) >= 2:
                        security.invested_amount = r_values[1]
                    elif len(r_values) == 1 and r_values[0] < 50000:  # If only one and it's small, might be invested amount
                        security.invested_amount = r_values[0]
                        security.market_position = r_values[0]  # Assume it's the same
                    
                    if len(percentages) >= 1:
                        security.allocation_percentage = percentages[0]
                    
                    summary.fixed_income_securities.append(security)
                    i = j
                else:
                    i += 1
            continue
        
        i += 1
    
    # Process additional stock information (last price, average price, quantity)
    # Search in stock details section
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for section with "Último preço (R$)"
        if "Último preço" in line and "Qtd. total" in (lines[i+2] if i+2 < len(lines) else ""):
            # Next lines have stock data
            j = i + 3
            stock_idx = 0
            while j < len(lines) and stock_idx < len(summary.stocks):
                # Look for date pattern (DD/MM/YYYY)
                if re.match(r'^\d{2}/\d{2}/\d{4}$', lines[j]):
                    if stock_idx < len(summary.stocks):
                        stock = summary.stocks[stock_idx]
                        
                        # Investment date
                        stock.investment_date = lines[j]
                        
                        # Average price (next non-empty line)
                        k = j + 1
                        while k < len(lines) and not lines[k]:
                            k += 1
                        if k < len(lines) and lines[k].startswith("R$"):
                            average_price = extract_monetary_value(lines[k])
                            if average_price:
                                stock.average_price = average_price
                        
                        # Last price (next non-empty line)
                        k += 1
                        while k < len(lines) and not lines[k]:
                            k += 1
                        if k < len(lines) and lines[k].startswith("R$"):
                            last_price = extract_monetary_value(lines[k])
                            if last_price:
                                stock.last_price = last_price
                        
                        # Quantity (next non-empty line)
                        k += 1
                        while k < len(lines) and not lines[k]:
                            k += 1
                        if k < len(lines):
                            try:
                                quantity = int(lines[k])
                                stock.quantity = quantity
                            except ValueError:
                                pass
                        
                        stock_idx += 1
                        j = k + 1
                    else:
                        j += 1
                else:
                    j += 1
            break
        i += 1
    
    # Process additional fund information (invested amount, net value, dates)
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for section with "Valor aplicado" and "Valor líquido"
        if "Valor aplicado" in line and "Valor líquido" in line:
            j = i + 1
            fund_idx = 0
            while j < len(lines) and fund_idx < len(summary.funds):
                # Look for date pattern (DD/MM/YYYY)
                if re.match(r'^\d{2}/\d{2}/\d{4}$', lines[j]):
                    if fund_idx < len(summary.funds):
                        fund = summary.funds[fund_idx]
                        
                        # Investment date
                        fund.investment_date = lines[j]
                        
                        # Invested amount (next non-empty line)
                        k = j + 1
                        while k < len(lines) and not lines[k]:
                            k += 1
                        if k < len(lines) and lines[k].startswith("R$"):
                            invested_amount = extract_monetary_value(lines[k])
                            if invested_amount:
                                fund.invested_amount = invested_amount
                        
                        # Net value (next non-empty line)
                        k += 1
                        while k < len(lines) and not lines[k]:
                            k += 1
                        if k < len(lines) and lines[k].startswith("R$"):
                            net_value = extract_monetary_value(lines[k])
                            if net_value:
                                fund.net_value = net_value
                        
                        # Quota date (next non-empty line)
                        k += 1
                        while k < len(lines) and not lines[k]:
                            k += 1
                        if k < len(lines):
                            quota_date = lines[k]
                            if re.match(r'^\d{2}/\d{2}/\d{4}$', quota_date):
                                fund.quota_date = quota_date
                        
                        fund_idx += 1
                        j = k + 1
                    else:
                        j += 1
                else:
                    j += 1
            break
        i += 1
    
    # Process additional fixed income information (rate, dates)
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for section with "Taxa a mercado" or "Data do investimento" followed by "Taxa a mercado"
        if "Taxa a mercado" in line:
            # Check if there's "Data aplicação" in next lines
            has_application_date = False
            for k in range(i+1, min(i+5, len(lines))):
                if "Data aplicação" in lines[k]:
                    has_application_date = True
                    break
            
            if has_application_date:
                # Look for "Data do investimento" header before
                j = i - 1
                while j >= 0 and "Data do investimento" not in lines[j]:
                    j -= 1
                
                if j >= 0:
                    # Skip headers and go to data
                    j = i + 1
                    while j < len(lines) and (not lines[j] or "Data" in lines[j] or "Taxa" in lines[j]):
                        j += 1
                    
                    security_idx = 0
                    while j < len(lines) and security_idx < len(summary.fixed_income_securities):
                        # Look for date pattern (DD/MM/YYYY)
                        if re.match(r'^\d{2}/\d{2}/\d{4}$', lines[j]):
                            if security_idx < len(summary.fixed_income_securities):
                                security = summary.fixed_income_securities[security_idx]
                                
                                # Investment date
                                security.investment_date = lines[j]
                                
                                # Market rate (next non-empty line)
                                k = j + 1
                                while k < len(lines) and not lines[k]:
                                    k += 1
                                if k < len(lines):
                                    security.market_rate = lines[k]
                                
                                # Application date (next non-empty line)
                                k += 1
                                while k < len(lines) and not lines[k]:
                                    k += 1
                                if k < len(lines) and re.match(r'^\d{2}/\d{2}/\d{4}$', lines[k]):
                                    security.application_date = lines[k]
                                
                                # Maturity date (next non-empty line)
                                k += 1
                                while k < len(lines) and not lines[k]:
                                    k += 1
                                if k < len(lines) and re.match(r'^\d{2}/\d{2}/\d{4}$', lines[k]):
                                    security.maturity_date = lines[k]
                                
                                security_idx += 1
                                j = k + 1
                            else:
                                j += 1
                        else:
                            j += 1
                break
        i += 1
    
    return summary


def format_portfolio_summary(summary: PortfolioSummary) -> str:
    """
    Formats the portfolio summary into a readable string.
    
    Args:
        summary: PortfolioSummary with extracted information
        
    Returns:
        Formatted string with the summary
    """
    output = []
    output.append("=" * 80)
    output.append("PORTFOLIO SUMMARY")
    output.append("=" * 80)
    output.append("")
    
    # Basic information
    output.append(f"Client Name: {summary.client_name}")
    output.append(f"Total Assets: R$ {summary.total_assets:,.2f}")
    output.append(f"Total Invested: R$ {summary.total_invested:,.2f}")
    output.append(f"Available Balance: R$ {summary.available_balance:,.2f}")
    if summary.portfolio_monthly_return is not None:
        output.append(f"Portfolio Monthly Return: {summary.portfolio_monthly_return:.2f}%")
    if summary.advisor:
        output.append("")
        output.append("-" * 80)
        output.append("INVESTMENT ADVISOR")
        output.append("-" * 80)
        output.append(f"Name: {summary.advisor.name}")
        output.append(f"Code: {summary.advisor.code}")
        output.append(f"Position: {summary.advisor.position}")
        output.append(f"Company: {summary.advisor.company_name}")
    output.append("")
    
    # Stocks
    output.append("-" * 80)
    output.append(f"STOCKS - {summary.stocks_percentage:.2f}% of portfolio")
    output.append("-" * 80)
    if summary.stocks:
        for stock in summary.stocks:
            output.append(f"\nCode: {stock.code}")
            output.append(f"  Position: R$ {stock.position:,.2f}")
            output.append(f"  % Allocation: {stock.allocation_percentage:.2f}%")
            output.append(f"  Return Rate: {stock.return_rate:.2f}%")
            if stock.monthly_return is not None:
                output.append(f"  Monthly Return: {stock.monthly_return:.2f}%")
            if stock.last_price:
                output.append(f"  Last Price: R$ {stock.last_price:.2f}")
            if stock.previous_month_price:
                output.append(f"  Previous Month Price: R$ {stock.previous_month_price:.2f}")
            if stock.average_price:
                output.append(f"  Average Price: R$ {stock.average_price:.2f}")
            if stock.quantity:
                output.append(f"  Quantity: {stock.quantity}")
            if stock.investment_date:
                output.append(f"  Investment Date: {stock.investment_date}")
    else:
        output.append("No stocks found.")
    output.append("")
    
    # Funds
    output.append("-" * 80)
    output.append(f"INVESTMENT FUNDS - {summary.funds_percentage:.2f}% of portfolio")
    output.append("-" * 80)
    if summary.funds:
        for fund in summary.funds:
            output.append(f"\nName: {fund.name}")
            output.append(f"  Position: R$ {fund.position:,.2f}")
            output.append(f"  % Allocation: {fund.allocation_percentage:.2f}%")
            output.append(f"  Return Rate: {fund.return_rate:.2f}%")
            if fund.invested_amount:
                output.append(f"  Invested Amount: R$ {fund.invested_amount:,.2f}")
            if fund.net_value:
                output.append(f"  Net Value: R$ {fund.net_value:,.2f}")
            if fund.investment_date:
                output.append(f"  Investment Date: {fund.investment_date}")
            if fund.quota_date:
                output.append(f"  Quota Date: {fund.quota_date}")
    else:
        output.append("No funds found.")
    output.append("")
    
    # Fixed Income
    output.append("-" * 80)
    output.append(f"FIXED INCOME - {summary.fixed_income_percentage:.2f}% of portfolio")
    output.append("-" * 80)
    if summary.fixed_income_securities:
        for security in summary.fixed_income_securities:
            output.append(f"\nName: {security.name}")
            output.append(f"  Market Position: R$ {security.market_position:,.2f}")
            output.append(f"  % Allocation: {security.allocation_percentage:.2f}%")
            output.append(f"  Invested Amount: R$ {security.invested_amount:,.2f}")
            if security.market_rate:
                output.append(f"  Market Rate: {security.market_rate}")
            if security.application_date:
                output.append(f"  Application Date: {security.application_date}")
            if security.maturity_date:
                output.append(f"  Maturity Date: {security.maturity_date}")
            if security.investment_date:
                output.append(f"  Investment Date: {security.investment_date}")
    else:
        output.append("No fixed income securities found.")
    output.append("")
    
    output.append("=" * 80)
    
    return "\n".join(output)


def summarize_portfolio(file_or_text: Union[str, Path]) -> PortfolioSummary:
    """
    Main function to process a portfolio file and return structured summary.
    
    Args:
        file_or_text: File path (Path or str) or portfolio text
        
    Returns:
        PortfolioSummary with all extracted information
        
    Example:
        >>> from src import summarize_portfolio
        >>> summary = summarize_portfolio("Input/XP - Albert_s portfolio.txt")
        >>> print(summary.client_name)
        >>> print(summary.total_assets)
    """
    # If it's a Path or string that looks like a file path, read the file
    if isinstance(file_or_text, Path) or (isinstance(file_or_text, str) and 
                                               (Path(file_or_text).exists() or 
                                                file_or_text.endswith('.txt'))):
        try:
            path = Path(file_or_text)
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            # If file not found, assume it's text
            text = str(file_or_text)
    else:
        # Assume it's text
        text = str(file_or_text)
    
    summary = parse_portfolio(text)
    
    # Calculate portfolio monthly return if stocks have monthly_return calculated
    if summary.stocks:
        # Check if at least one stock has monthly_return calculated
        has_monthly_returns = any(stock.monthly_return is not None for stock in summary.stocks)
        if has_monthly_returns:
            summary.portfolio_monthly_return = calculate_portfolio_monthly_return_simple(summary.stocks)
    
    return summary


def calculate_monthly_stock_returns(
    portfolio_summary: PortfolioSummary,
    use_portfolio_last_price: bool = False
) -> PortfolioSummary:
    """
    Calculates the total monthly return of each stock in the portfolio using yfinance.
    
    The return is calculated using adjusted prices (auto_adjust=True):
    - Uses auto_adjust=True to get prices already adjusted for dividends and splits
    - The "Close" column with auto_adjust=True contains adjusted prices
    - Compares the last available price with the price from 1 month ago
    - The total return already includes all adjustments (dividends, splits, etc.)
    
    Args:
        portfolio_summary: PortfolioSummary with client's stocks
        use_portfolio_last_price: If True, updates the portfolio's last price with adjusted price.
                                     If False, keeps the original portfolio price.
                                     The return calculation always uses adjusted prices from yfinance.
        
    Returns:
        PortfolioSummary with monthly_return and previous_month_price fields filled
        
    Example:
        >>> from src import summarize_portfolio, calculate_monthly_stock_returns
        >>> summary = summarize_portfolio("Input/XP - Albert_s portfolio.txt")
        >>> summary = calculate_monthly_stock_returns(summary)
        >>> for stock in summary.stocks:
        ...     print(f"{stock.code}: {stock.monthly_return:.2f}%")
    """
    if not YFINANCE_AVAILABLE:
        raise ImportError(
            "yfinance is not installed. Install with: pip install yfinance"
        )
    
    for stock in portfolio_summary.stocks:
        try:
            # For Brazilian stocks, add .SA suffix
            yfinance_code = f"{stock.code}.SA"

            if yfinance_code.startswith("MRFG3"):
                yfinance_code = "MBRF3.SA"
            elif yfinance_code.startswith("ARZZ3"):
                yfinance_code = "AZZA3.SA" 
            
            
            # Fetch historical data with auto_adjust=True to get adjusted prices
            # auto_adjust=True returns prices already adjusted for dividends and splits in the "Close" column
            ticker = yf.Ticker(yfinance_code)
            hist = ticker.history(period="3mo", auto_adjust=True)
            
            if hist.empty:
                print(f"Warning: Could not get data for {stock.code}")
                continue
            
            # Check if we have the Close column (which contains adjusted prices when auto_adjust=True)
            if 'Close' not in hist.columns:
                print(f"Warning: Price data not available for {stock.code}")
                continue
            
            # Get last available price (Close with auto_adjust=True already considers dividends and splits)
            current_date = hist.index[-1]
            last_price_adj = hist['Close'].iloc[-1]
            
            # Update portfolio's last price if requested
            if use_portfolio_last_price:
                stock.last_price = last_price_adj
            
            # Calculate date from 1 month ago (approximately 30 days)
            # Search in window of 25 to 35 days ago for flexibility with non-trading days
            start_date = current_date - timedelta(days=35)
            end_date = current_date - timedelta(days=25)
            
            # Filter data in this window
            previous_month_data = hist[(hist.index >= start_date) & (hist.index <= end_date)]
            
            if previous_month_data.empty:
                # If no data in window, try to get the oldest available
                # that is at least 20 days ago
                old_data = hist[hist.index <= (current_date - timedelta(days=20))]
                if not old_data.empty:
                    previous_month_price_adj = old_data['Close'].iloc[-1]
                else:
                    print(f"Warning: Could not find price from 1 month ago for {stock.code}")
                    continue
            else:
                # Get price closest to desired date (last in window)
                previous_month_price_adj = previous_month_data['Close'].iloc[-1]
            
            # Calculate total monthly return using adjusted prices
            # With auto_adjust=True, the Close column already considers dividends, splits, etc.
            # Return = (Current Price - Previous Month Price) / Previous Month Price * 100
            monthly_return = ((last_price_adj - previous_month_price_adj) / previous_month_price_adj) * 100
            
            # Update stock fields
            stock.monthly_return = monthly_return
            stock.previous_month_price = previous_month_price_adj
            
            # If didn't have last price, update with yfinance one
            if not stock.last_price:
                stock.last_price = last_price_adj
                
        except Exception as e:
            print(f"Error calculating monthly return for {stock.code}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    return portfolio_summary


def calculate_monthly_stock_returns_list(
    stocks: List[Stock],
    use_portfolio_last_price: bool = False
) -> List[Stock]:
    """
    Calculates the total monthly return of a list of stocks using yfinance.
    
    The return is calculated using adjusted prices (auto_adjust=True):
    - Uses auto_adjust=True to get prices already adjusted for dividends and splits
    - The "Close" column with auto_adjust=True contains adjusted prices
    - Compares the last available price with the price from 1 month ago
    
    Args:
        stocks: List of Stock objects
        use_portfolio_last_price: If True, updates the portfolio's last price with adjusted price.
                                     If False, keeps the original portfolio price.
                                     The return calculation always uses adjusted prices from yfinance.
        
    Returns:
        List of stocks with monthly_return and previous_month_price fields filled
    """
    if not YFINANCE_AVAILABLE:
        raise ImportError(
            "yfinance is not installed. Install with: pip install yfinance"
        )
    
    for stock in stocks:
        try:
            # For Brazilian stocks, add .SA suffix
            yfinance_code = f"{stock.code}.SA"

            if yfinance_code.startswith("MRFG3"):
                yfinance_code = "MBRF3.SA"
            elif yfinance_code.startswith("ARZZ3"):
                yfinance_code = "AZZA3.SA" 
            
            # Fetch historical data with auto_adjust=True to get adjusted prices
            # auto_adjust=True returns prices already adjusted for dividends and splits in the "Close" column
            ticker = yf.Ticker(yfinance_code)
            hist = ticker.history(period="3mo", auto_adjust=True)
            
            if hist.empty:
                print(f"Warning: Could not get data for {stock.code}")
                continue
            
            # Check if we have the Close column (which contains adjusted prices when auto_adjust=True)
            if 'Close' not in hist.columns:
                print(f"Warning: Price data not available for {stock.code}")
                continue
            
            # Get last available price (Close with auto_adjust=True already considers dividends and splits)
            current_date = hist.index[-1]
            last_price_adj = hist['Close'].iloc[-1]
            
            # Update portfolio's last price if requested
            if use_portfolio_last_price:
                stock.last_price = last_price_adj
            
            # Calculate date from 1 month ago (approximately 30 days)
            # Search in window of 25 to 35 days ago for flexibility with non-trading days
            start_date = current_date - timedelta(days=35)
            end_date = current_date - timedelta(days=25)
            
            # Filter data in this window
            previous_month_data = hist[(hist.index >= start_date) & (hist.index <= end_date)]
            
            if previous_month_data.empty:
                # If no data in window, try to get the oldest available
                # that is at least 20 days ago
                old_data = hist[hist.index <= (current_date - timedelta(days=20))]
                if not old_data.empty:
                    previous_month_price_adj = old_data['Close'].iloc[-1]
                else:
                    print(f"Warning: Could not find price from 1 month ago for {stock.code}")
                    continue
            else:
                previous_month_price_adj = previous_month_data['Close'].iloc[-1]
            
            # Calculate total monthly return using adjusted prices
            # With auto_adjust=True, the Close column already considers dividends, splits, etc.
            monthly_return = ((last_price_adj - previous_month_price_adj) / previous_month_price_adj) * 100
            
            # Update stock fields
            stock.monthly_return = monthly_return
            stock.previous_month_price = previous_month_price_adj
            
            # If didn't have last price, update with yfinance one
            if not stock.last_price:
                stock.last_price = last_price_adj
                
        except Exception as e:
            print(f"Error calculating monthly return for {stock.code}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    return stocks


def calculate_portfolio_monthly_return_simple(
    stocks: List[Stock]
) -> float:
    """
    Simplified version that returns just the weighted monthly return percentage.
    
    Args:
        stocks: List of Stock objects with filled monthly_return and last_price fields
    
    Returns:
        Weighted monthly return percentage for the portfolio
    """
    if not stocks:
        return 0.0
    
    total_position_value = 0.0
    weighted_return_sum = 0.0
    
    # First pass: calculate total portfolio value
    for stock in stocks:
        if stock.quantity > 0 and stock.last_price > 0:
            position_value = stock.quantity * stock.last_price
            total_position_value += position_value
    
    if total_position_value <= 0:
        return 0.0
    
    # Second pass: calculate weighted returns
    for stock in stocks:
        if stock.quantity > 0 and stock.last_price > 0 and stock.monthly_return is not None:
            position_value = stock.quantity * stock.last_price
            weight = position_value / total_position_value
            weighted_return_sum += stock.monthly_return * weight
    
    return weighted_return_sum