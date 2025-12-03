"""
Workflow de geração de carta de investimento mensal
Replica o workflow definido no enter_challenge.rivet-project usando a SDK da OpenAI
"""

from config import (
    PORTFOLIO_FILE,
    RISK_PROFILE_FILE,
    MACRO_ANALYSIS_FILE,
    OUTPUT_FILE,
)
from src import (
    read_file,
    write_file,
    summarize_portfolio_results,
    summarize_risk_profile,
    summarize_macroeconomic_outlook,
    generate_investment_letter,
)


def main():
    """Função principal que executa o workflow completo."""
    print("Iniciando workflow de geração de carta de investimento...")
    print("-" * 60)

    # Passo 1: Ler os arquivos de entrada
    print("\n[1/4] Lendo arquivos de entrada...")
    try:
        portfolio_data = read_file(PORTFOLIO_FILE)
        print(f"  ✓ Portfólio lido: {PORTFOLIO_FILE.name}")
        
        risk_profile_data = read_file(RISK_PROFILE_FILE)
        print(f"  ✓ Perfil de risco lido: {RISK_PROFILE_FILE.name}")
        
        macro_data = read_file(MACRO_ANALYSIS_FILE)
        print(f"  ✓ Análise macro lida: {MACRO_ANALYSIS_FILE.name}")
    except Exception as e:
        print(f"  ✗ Erro ao ler arquivos: {str(e)}")
        return

    # Passo 2: Gerar resumos
    print("\n[2/4] Gerando resumos com IA...")
    try:
        print("  → Gerando resumo do portfólio...")
        portfolio_summary = summarize_portfolio_results(portfolio_data)
        print("  ✓ Resumo do portfólio gerado")
        
        print("  → Gerando resumo do perfil de risco...")
        risk_profile_summary = summarize_risk_profile(risk_profile_data)
        print("  ✓ Resumo do perfil de risco gerado")
        
        print("  → Gerando resumo macroeconômico...")
        macro_outlook_summary = summarize_macroeconomic_outlook(macro_data)
        print("  ✓ Resumo macroeconômico gerado")
    except Exception as e:
        print(f"  ✗ Erro ao gerar resumos: {str(e)}")
        return

    # Passo 3: Gerar carta de investimento
    print("\n[3/4] Gerando carta de investimento...")
    try:
        investment_letter = generate_investment_letter(
            risk_profile_summary,
            macro_outlook_summary,
            portfolio_summary
        )
        print("  ✓ Carta de investimento gerada")
    except Exception as e:
        print(f"  ✗ Erro ao gerar carta: {str(e)}")
        return

    # Passo 4: Salvar resultado
    print("\n[4/4] Salvando resultado...")
    try:
        write_file(OUTPUT_FILE, investment_letter)
        print(f"  ✓ Carta salva em: {OUTPUT_FILE}")
    except Exception as e:
        print(f"  ✗ Erro ao salvar arquivo: {str(e)}")
        return

    print("\n" + "=" * 60)
    print("Workflow concluído com sucesso!")
    print("=" * 60)
    
    # Exibe um preview da carta
    print("\nPreview da carta gerada:")
    print("-" * 60)
    preview_length = 500
    if len(investment_letter) > preview_length:
        print(investment_letter[:preview_length] + "...")
    else:
        print(investment_letter)
    print("-" * 60)


if __name__ == "__main__":
    main()
