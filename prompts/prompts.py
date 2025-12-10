"""Prompt templates for AI content generation."""


def get_portfolio_prompt(portfolio_data: str) -> str:
    return """
You are a financial analyst preparing a monthly performance summary for a mid-market client.

Write a concise, client-facing summary of 120–160 words describing the portfolio's performance 
strictly based on the input provided.

Include:
- Overall portfolio result and comparison with benchmark (if included in the input)
- Contribution of each asset class and key performance drivers
- Any rebalancing or allocation changes explicitly mentioned
- A brief explanation of the practical implications for the client

Style:
- Professional, clear, and objective
- Avoid jargon unless it appears in the input
- Do not repeat sentences or copy input text; synthesize into a clean narrative

Hard constraints:
- Do not add numbers, insights, or assumptions not present in the input
- Do not speculate
- Do not omit any essential performance elements present in the input

Input data:
{portfolio_results}
""".format(portfolio_results=portfolio_data)


def get_risk_profile_prompt(risk_profile_data: str) -> str:
    return """
Write a single structured paragraph of 80–120 words summarizing the client's investor risk profile 
strictly from the input provided.

Include:
- Risk classification (e.g., conservative, moderate, aggressive)
- Investment horizon
- Tolerance for volatility and drawdowns
- Primary investment objectives
- Practical implications for how the client should be positioned

Style:
- Private-banking tone: formal, concise, and polished
- One paragraph only
- Do not copy input sentences; paraphrase and synthesize

Hard constraints:
- Do not add or infer data not present in the input
- Do not contradict the stated profile
- Do not expand beyond the information provided

Input data:
{risk_profile}
""".format(risk_profile=risk_profile_data)


def get_macro_outlook_prompt(macro_data: str) -> str:
    return """
Write a concise macroeconomic outlook of 120–160 words strictly based on the input provided.

Include:
- Key macro trends mentioned (inflation, growth, interest rates, etc.)
- Market sentiment and positioning, if included
- Relevant risks noted by the source
- A brief explanation of why these points matter for investment decisions

Style:
- Analytical, clear, and professional
- Avoid unnecessary jargon or speculation
- Synthesize information rather than repeat it

Hard constraints:
- Do not introduce new projections, numbers, or events not found in the input
- Do not copy long phrases from the input
- Do not contradict or reinterpret the original commentary

Input data:
{macroeconomic_report}
""".format(macroeconomic_report=macro_data)


def get_investment_letter_prompt(
    risk_profile_summary: str,
    macro_outlook_summary: str,
    portfolio_results_summary: str
) -> str:
    return """
Write a polished, client-facing monthly investment letter in Portuguese. Keep it between 400 and 500 words strictly

The letter must combine the three inputs (risk profile, macroeconomic outlook, portfolio performance) 
into a cohesive narrative and include clear, actionable investment recommendations that are fully aligned 
with the information provided. The perspective of the letter is always the advisor speaking directly to the client.


IMPORTANT: A portfolio allocation chart (donut chart) will be inserted in the document showing the 
distribution across asset classes (stocks, funds, fixed income) and individual positions. When you 
discuss the portfolio allocation, naturally reference this chart. For example: "Como podemos observar 
no gráfico de distribuição do portfólio" or "Conforme ilustrado na visualização da alocação" or similar 
natural transitions. The chart will be placed near the paragraph where you discuss portfolio composition.

Required content:
- Brief context and introduction (DO NOT include greeting like "Prezado" or "Prezada" - this will be added automatically)
- Summary of the current portfolio allocation and recent performance (mention the chart naturally when discussing allocation)
- Connection between the macroeconomic environment and the portfolio's behavior
- Practical recommendations that are justified by the content of the summaries
- If the summaries mention available cash, risk capacity, or attractive opportunities, 
  explicitly address whether deploying cash now makes sense and into which asset classes — 
  but only if this is supported by the summaries
- Professional closing (DO NOT include sign-off like "Atenciosamente" or signature - this will be added automatically)

Integration requirements (EXTREMELY IMPORTANT):
- The letter must build a continuous and coherent narrative connecting:
  (1) the macroeconomic environment,
  (2) the portfolio’s recent behavior, and
  (3) the investment recommendation

Style:
- Formal, polished, advisor-like tone
- Smooth and natural transitions between topics
- When discussing portfolio allocation, naturally reference the chart that will appear in the document
- Provide recommendations that feel concrete and actionable (e.g., reinforcing exposure to 
  a defensive asset class, increasing allocation to instruments aligned with inflation protection, 
  maintaining a certain allocation considering the outlook)
- All recommendations must be directly derived from content already present in the summaries

Hard constraints:
- Do NOT include a greeting (e.g., "Prezado", "Prezada", "Caro", "Cara") - the greeting will be added automatically
- Do NOT include a sign-off or closing salutation (e.g., "Atenciosamente", "Cordialmente") - this will be added automatically
- Do NOT introduce new numbers, projections, or asset classes not mentioned in the summaries
- Do NOT invent macro trends, risk factors, or opportunities not supported by the summaries
- Do NOT copy the summaries verbatim; rewrite them into a fluid narrative in Portuguese
- All output must remain consistent with the client's risk profile
- When discussing portfolio composition/allocation, naturally reference the chart (e.g., "como mostra o gráfico", "conforme ilustrado", etc.)
- Use **text** format for bold text

Inputs to integrate:

Risk Profile Summary:
{risk_profile}

Macroeconomic Outlook Summary:
{macro_outlook}

Portfolio Results Summary:
{portfolio_results}
""".format(
        risk_profile=risk_profile_summary,
        macro_outlook=macro_outlook_summary,
        portfolio_results=portfolio_results_summary
    )
