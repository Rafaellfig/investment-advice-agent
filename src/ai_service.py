"""Services for integration with OpenAI API."""

import os
from openai import OpenAI
from dotenv import load_dotenv

from config.settings import MODEL, TEMPERATURE, MAX_TOKENS, OPENAI_API_KEY
from prompts.prompts import (
    get_portfolio_prompt,
    get_risk_profile_prompt,
    get_macro_outlook_prompt,
    get_investment_letter_prompt,
)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def call_openai(prompt: str) -> str:
    """
    Makes a call to the OpenAI API and returns the response.
    
    Args:
        prompt: Prompt text to be sent
        
    Returns:
        API response as string
        
    Raises:
        Exception: If an error occurs in the API call
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")


def summarize_portfolio_results(portfolio_data: str) -> str:
    """
    Generates summary of portfolio results.
    
    Args:
        portfolio_data: Client's portfolio data
        
    Returns:
        Summary of portfolio results
    """
    prompt = get_portfolio_prompt(portfolio_data)
    return call_openai(prompt)


def summarize_risk_profile(risk_profile_data: str) -> str:
    """
    Generates summary of client's risk profile.
    
    Args:
        risk_profile_data: Risk profile data
        
    Returns:
        Summary of risk profile
    """
    prompt = get_risk_profile_prompt(risk_profile_data)
    return call_openai(prompt)


def summarize_macroeconomic_outlook(macro_data: str) -> str:
    """
    Generates summary of macroeconomic outlook.
    
    Args:
        macro_data: Macroeconomic analysis data
        
    Returns:
        Summary of macroeconomic outlook
    """
    prompt = get_macro_outlook_prompt(macro_data)
    return call_openai(prompt)


def generate_investment_letter(
    risk_profile_summary: str,
    macro_outlook_summary: str,
    portfolio_results_summary: str
) -> str:
    """
    Generates the monthly investment letter in Portuguese.
    
    Args:
        risk_profile_summary: Risk profile summary
        macro_outlook_summary: Macroeconomic outlook summary
        portfolio_results_summary: Portfolio results summary
        
    Returns:
        Complete investment letter in Portuguese
    """
    prompt = get_investment_letter_prompt(
        risk_profile_summary,
        macro_outlook_summary,
        portfolio_results_summary
    )
    return call_openai(prompt)
