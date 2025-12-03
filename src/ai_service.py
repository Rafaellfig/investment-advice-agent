"""Serviços de integração com a API da OpenAI."""

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

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa o cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


def call_openai(prompt: str) -> str:
    """
    Faz uma chamada à API da OpenAI e retorna a resposta.
    
    Args:
        prompt: Texto do prompt a ser enviado
        
    Returns:
        Resposta da API como string
        
    Raises:
        Exception: Se ocorrer erro na chamada à API
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
        raise Exception(f"Erro ao chamar API da OpenAI: {str(e)}")


def summarize_portfolio_results(portfolio_data: str) -> str:
    """
    Gera resumo dos resultados do portfólio.
    
    Args:
        portfolio_data: Dados do portfólio do cliente
        
    Returns:
        Resumo dos resultados do portfólio
    """
    prompt = get_portfolio_prompt(portfolio_data)
    return call_openai(prompt)


def summarize_risk_profile(risk_profile_data: str) -> str:
    """
    Gera resumo do perfil de risco do cliente.
    
    Args:
        risk_profile_data: Dados do perfil de risco
        
    Returns:
        Resumo do perfil de risco
    """
    prompt = get_risk_profile_prompt(risk_profile_data)
    return call_openai(prompt)


def summarize_macroeconomic_outlook(macro_data: str) -> str:
    """
    Gera resumo da perspectiva macroeconômica.
    
    Args:
        macro_data: Dados da análise macroeconômica
        
    Returns:
        Resumo da perspectiva macroeconômica
    """
    prompt = get_macro_outlook_prompt(macro_data)
    return call_openai(prompt)


def generate_investment_letter(
    risk_profile_summary: str,
    macro_outlook_summary: str,
    portfolio_results_summary: str
) -> str:
    """
    Gera a carta de investimento mensal em português.
    
    Args:
        risk_profile_summary: Resumo do perfil de risco
        macro_outlook_summary: Resumo da perspectiva macroeconômica
        portfolio_results_summary: Resumo dos resultados do portfólio
        
    Returns:
        Carta de investimento completa em português
    """
    prompt = get_investment_letter_prompt(
        risk_profile_summary,
        macro_outlook_summary,
        portfolio_results_summary
    )
    return call_openai(prompt)

