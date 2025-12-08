"""Prompt templates for AI content generation."""


def get_portfolio_prompt(portfolio_data: str) -> str:
    """
    Returns the prompt for portfolio results summary.
    
    Args:
        portfolio_data: Portfolio data
        
    Returns:
        Formatted prompt
    """
    return """## Prompt: Summarize the Client's Portfolio Results

### Objective:

You are a financial analyst creating a monthly investment report for a middle-market client.

Your task is to write a concise, client-facing summary (120–160 words) of the portfolio’s performance 
based strictly on the information provided.

### What to include:

- Overall portfolio return and comparison vs. benchmark (if provided)
- Performance of the main asset classes
- Key drivers of performance (positive/negative)
- Brief note on rebalancing or changes in allocation, if mentioned

### Style & Tone:

- Professional, confident, and objective
- Avoid overly technical language — prioritize clarity

### Important constraints (do NOT ignore)
- Do NOT invent numbers, events, or insights not included in the input
- Do NOT repeat the input verbatim; write a clean, narrative summary
- Use only the data provided below

---

### Input:

Below is the portfolio data and performance commentary:

{portfolio_results}""".format(portfolio_results=portfolio_data)


def get_risk_profile_prompt(risk_profile_data: str) -> str:
    """
    Returns the prompt for risk profile summary.
    
    Args:
        risk_profile_data: Risk profile data
        
    Returns:
        Formatted prompt
    """
    return """## Prompt: Summarize the Client's Risk Profile

### Objective:

Write a single, well-structured paragraph (80–120 words) summarizing the client’s investor profile 
based strictly on the information provided in the input.

### What to include:

In a single paragraph, summarize the following:

- Risk profile classification (e.g., conservative, moderate, aggressive)
- Investment horizon (short/medium/long term)
- Tolerance for volatility and losses
- Main investment objectives (e.g., income, accumulation, retirement)

### Style & Tone:

- Formal and private-banking-oriented
- Clear, concise, technical but client-friendly
- One paragraph only

### Important constraints
- Do NOT add information not present in the input
- Do NOT copy sentences verbatim; rephrase into a coherent summary
- Do NOT contradict or reinterpret the client’s stated profile

---

### Input:

Below is the full client profile:

{risk_profile}""".format(risk_profile=risk_profile_data)


def get_macro_outlook_prompt(macro_data: str) -> str:
    """
    Returns the prompt for macroeconomic outlook summary.
    
    Args:
        macro_data: Macroeconomic analysis data
        
    Returns:
        Formatted prompt
    """
    return """## Prompt: Summarize the Macroeconomic Outlook

### Objective:

You are preparing a macroeconomic commentary for a monthly investment report. 
Write a clear and concise paragraph (120–160 words) summarizing the outlook strictly from the input provided.

### What to include:

- Key macroeconomic trends (inflation, interest rates, growth)
- Market sentiment and investor positioning
- Relevant analyst signals or risks
- Points that matter for investment decisions

### Style & Tone:

- Formal, analytical, and investor-facing
- Jargon acceptable, but avoid unnecessary complexity
- One well-structured paragraph

### Important constraints
- Do NOT add projections, dates, numbers, or events that are not in the input
- Do NOT repeat long phrases from the input; summarize and synthesize
- Do NOT contradict the original commentary

---

### Input:

Below is the raw macroeconomic commentary for the month:

{macroeconomic_report}""".format(macroeconomic_report=macro_data)


def get_investment_letter_prompt(
    risk_profile_summary: str,
    macro_outlook_summary: str,
    portfolio_results_summary: str
) -> str:
    """
    Returns the prompt for investment letter generation.
    
    Args:
        risk_profile_summary: Risk profile summary
        macro_outlook_summary: Macroeconomic outlook summary
        portfolio_results_summary: Portfolio results summary
        
    Returns:
        Formatted prompt
    """
    return """## Prompt: Write the Monthly Investment Letter (in Portuguese)

### Objective:

Combine the three summaries below (risk profile, macro outlook, and portfolio performance) 
into a polished investment letter of up to 400–500 words, written entirely in Portuguese.

### What to include:

- Brief greeting and context (“Prezado... segue o relatório do mês...”)
- Portfolio results and allocation overview
- Connection to the macroeconomic scenario and its implications
- Recommendations aligned with the client’s risk profile
- Closing paragraph with professional sign-off

### Style & Tone:

- Formal, polished, and client-facing
- Flowing transitions between sections (“Nesse contexto...”, “Diante desse cenário...”)
- No repetition of the same idea across sections
- Voice of an experienced advisor: confident, clear, objective

### Important constraints
- Do NOT add data or insights not present in the three summaries
- Do NOT repeat the summaries verbatim; rephrase into a coherent narrative
- Do NOT contradict the inputs
- Keep the structure in paragraphs; do NOT use bullet points

---

### Inputs:

Below are the outputs from the previous steps:

#### 1. Client Risk Profile:

{risk_profile}

#### 2. Macroeconomic Outlook:

{macro_outlook}

#### 3. Portfolio Results:

{portfolio_results}""".format(
        risk_profile=risk_profile_summary,
        macro_outlook=macro_outlook_summary,
        portfolio_results=portfolio_results_summary
    )
