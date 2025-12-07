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

You are a financial analyst creating a monthly investment report for a middle-market client. Below, you will receive detailed portfolio performance data, including asset allocation, returns (monthly, YTD, vs. benchmark), and any notable movements or rebalancing actions.

Your task is to write a concise, client-facing summary (1–2 paragraphs max) of the portfolio's performance, highlighting what matters most from an analytical and strategic point of view.

### What to include:

- Overall portfolio return

- Performance of key asset classes (e.g., equities, fixed income, alternatives)

### Style & Tone:

- Professional, confident, and objective

- Avoid overly technical language — prioritize clarity

### Example Output:

> The portfolio posted a 1.2% return in May, outperforming its benchmark by 0.4 percentage points. Equities were the primary driver of performance, with U.S. and European stocks benefiting from improved investor sentiment and solid earnings reports. On the other hand, Brazilian fixed income had a marginal negative contribution due to the flattening yield curve. No significant reallocations were made during the period, as we remain comfortable with the current positioning, particularly in global equities and inflation-linked bonds.

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

You are a financial analyst preparing a monthly investment report for a middle-market client. Your goal is to summarize the client's investor profile in a clear, concise, and professional paragraph.

The full profile includes answers to the risk tolerance questionnaire, age, income level, investment goals, liquidity needs, investment horizon, and previous investment experience.

### What to include:

In a single paragraph, summarize the following:

1. The client's risk profile (e.g., conservative, moderate, growth-oriented, aggressive)

2. Their investment horizon (short-, medium-, or long-term)

3. Their tolerance for volatility and potential losses

4. Their primary investment objectives (e.g., wealth accumulation, income generation, retirement planning)

### Style & Tone:

- Professional and formal (like a private banking advisor)

- Clear, technical, and investor-facing

- One paragraph only

### Example Output:

> The client has a moderate risk profile, with a long-term investment horizon and a balanced tolerance for short-term market volatility. The main objective is capital accumulation with an eye toward long-term financial independence and future retirement planning.

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

You are a financial analyst preparing a monthly investment report for a middle-market client. Your task is to analyze and summarize a set of macroeconomic insights — such as reports, articles, and analyst briefings — into a clear, concise paragraph in a professional tone.

This summary will later be integrated into a client-facing investment letter, so it should highlight only the most relevant points from the perspective of an investor.

### What to include:

Summarize in a single, well-structured paragraph:

- Key macroeconomic trends (e.g., inflation, interest rates, GDP, global risks)

- Market sentiment (positive, cautious, volatile, etc.)

- Relevant forecasts or analyst consensus

- Any significant updates that could impact investment decisions

### Style & Tone:

- Formal and analytical

- Jargon is acceptable, but avoid unnecessary complexity

- Keep it investor-facing: prioritize what matters for portfolio decisions

### Example Output:

> In May, global markets reflected a cautiously optimistic sentiment amid signals of moderating inflation in the U.S. and stable interest rates in Europe. Brazil's Central Bank continued its rate-cutting cycle, while China's slower-than-expected recovery raised concerns across emerging markets. Overall, the macroeconomic backdrop suggests a supportive environment for risk assets, though geopolitical tensions and U.S. election dynamics remain key watchpoints.

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

You are a financial analyst preparing a monthly investment letter to send to a middle-market client. You have already written three summaries:

1. **Client Risk Profile Summary**

2. **Macroeconomic Outlook Summary**

3. **Portfolio Results Summary**

Your task is now to integrate these three inputs into a single, well-structured investment letter, written in **Portuguese**, that will be sent directly to the client.

### What to include:

In up to two pages (approx. 500 words), write a polished investment letter that:

- Opens with a short greeting and context ("Prezado João, segue o relatório mensal...")

- Presents the **portfolio's performance**, allocation

- Highlights the **macroeconomic outlook** and how it impacts portfolio positioning going forward

- Make **recommendations** aligned with the client's risk profile

- Closes with a professional sign-off and availability for follow-ups

### Style & Tone:

- Formal, polished, and client-facing

- Avoid repetition across sections

- Use the voice of an experienced investment advisor: clear, confident, and tailored

- Use transitions to connect sections smoothly (e.g., "Nesse contexto macroeconômico...", "Diante desse cenário, nosso portfólio...", "Seguimos atentos...")

### Output format:

The output should be in well-formatted **Portuguese**. Use paragraphs (not bullet points), keep it concise but insightful, and avoid technical overload.

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
