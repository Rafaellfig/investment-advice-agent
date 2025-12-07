"""Módulo para processar e extrair informações de arquivos de portfólio."""

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
class Acao:
    """Representa uma ação no portfólio."""
    codigo: str
    posicao: float
    percentual_alocacao: float
    rentabilidade: float
    ultimo_preco: Optional[float] = None
    preco_medio: Optional[float] = None
    quantidade: Optional[int] = None
    data_investimento: Optional[str] = None
    retorno_mensal: Optional[float] = None
    preco_mes_anterior: Optional[float] = None


@dataclass
class FundoInvestimento:
    """Representa um fundo de investimento no portfólio."""
    nome: str
    posicao: float
    percentual_alocacao: float
    rentabilidade: float
    valor_aplicado: Optional[float] = None
    valor_liquido: Optional[float] = None
    data_investimento: Optional[str] = None
    data_cota: Optional[str] = None


@dataclass
class TituloRendaFixa:
    """Representa um título de renda fixa no portfólio."""
    nome: str
    posicao_mercado: float
    percentual_alocacao: float
    valor_aplicado: float
    taxa_mercado: Optional[str] = None
    data_aplicacao: Optional[str] = None
    data_vencimento: Optional[str] = None
    data_investimento: Optional[str] = None


@dataclass
class PortfolioResumo:
    """Resumo estruturado do portfólio do cliente."""
    nome_cliente: str
    patrimonio_total: float
    total_investido: float
    saldo_disponivel: float
    acoes: List[Acao] = field(default_factory=list)
    fundos: List[FundoInvestimento] = field(default_factory=list)
    titulos_renda_fixa: List[TituloRendaFixa] = field(default_factory=list)
    percentual_acoes: float = 0.0
    percentual_fundos: float = 0.0
    percentual_renda_fixa: float = 0.0


def extrair_valor_monetario(texto: str) -> Optional[float]:
    """Extrai valor monetário de uma string (formato R$ X.XXX,XX ou R$ X,XXX.XX)."""
    if not texto:
        return None
    # Remove R$ e espaços
    texto_limpo = texto.replace("R$", "").strip()
    # Remove todos os espaços
    texto_limpo = texto_limpo.replace(" ", "")
    
    # Detecta formato: se tem ponto antes de vírgula, é formato brasileiro (R$ 1.234,56)
    # Se tem vírgula antes de ponto, pode ser formato americano (R$ 1,234.56)
    if "." in texto_limpo and "," in texto_limpo:
        # Verifica qual vem primeiro
        idx_ponto = texto_limpo.find(".")
        idx_virgula = texto_limpo.find(",")
        if idx_ponto < idx_virgula:
            # Formato brasileiro: 1.234,56
            texto_limpo = texto_limpo.replace(".", "").replace(",", ".")
        else:
            # Formato americano: 1,234.56
            texto_limpo = texto_limpo.replace(",", "")
    elif "," in texto_limpo:
        # Apenas vírgula, pode ser decimal brasileiro
        texto_limpo = texto_limpo.replace(",", ".")
    # Se só tem ponto, pode ser decimal ou milhar - assumimos decimal se não tiver 3 dígitos após
    
    try:
        return float(texto_limpo)
    except (ValueError, AttributeError):
        return None


def extrair_percentual(texto: str) -> Optional[float]:
    """Extrai percentual de uma string (formato X,XX% ou X.XX%)."""
    if not texto:
        return None
    texto_limpo = texto.replace("%", "").strip()
    # Substitui vírgula por ponto
    texto_limpo = texto_limpo.replace(",", ".")
    try:
        return float(texto_limpo)
    except (ValueError, AttributeError):
        return None


def extrair_rentabilidade(texto: str) -> Optional[float]:
    """Extrai rentabilidade de uma string (pode ter sinal negativo)."""
    if not texto:
        return None
    texto_limpo = texto.replace("%", "").strip()
    # Substitui vírgula por ponto
    texto_limpo = texto_limpo.replace(",", ".")
    try:
        return float(texto_limpo)
    except (ValueError, AttributeError):
        return None


def parse_portfolio(portfolio_text: str) -> PortfolioResumo:
    """
    Processa o texto do portfólio e extrai todas as informações estruturadas.
    
    Args:
        portfolio_text: Texto completo do arquivo de portfólio
        
    Returns:
        PortfolioResumo com todas as informações extraídas
    """
    linhas = [linha.strip() for linha in portfolio_text.split('\n')]
    
    # Inicializa o resumo
    resumo = PortfolioResumo(
        nome_cliente="",
        patrimonio_total=0.0,
        total_investido=0.0,
        saldo_disponivel=0.0
    )
    
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        
        # Extrai nome do cliente (primeira linha)
        if not resumo.nome_cliente and linha and "este é o seu patrimônio" in linha.lower():
            # Extrai nome antes da vírgula
            partes = linha.split(",")
            if partes:
                resumo.nome_cliente = partes[0].strip()
        
        # Total investido
        if linha.lower() == "total investido":
            # Procura o valor nas próximas linhas (pula linhas vazias)
            j = i + 1
            while j < len(linhas) and not linhas[j].startswith("R$"):
                j += 1
            if j < len(linhas):
                valor = extrair_valor_monetario(linhas[j])
                if valor:
                    resumo.total_investido = valor
        
        # Saldo disponível
        if linha.lower() == "saldo disponível":
            # Procura o valor nas próximas linhas (pula linhas vazias)
            # Pode haver um valor intermediário, então procura o último R$ antes de "Ações"
            j = i + 1
            ultimo_valor = None
            while j < len(linhas) and linhas[j] != "Ações":
                if linhas[j].startswith("R$"):
                    ultimo_valor = extrair_valor_monetario(linhas[j])
                j += 1
            if ultimo_valor:
                resumo.saldo_disponivel = ultimo_valor
        
        # Patrimônio total = Total investido + Saldo disponível
        resumo.patrimonio_total = resumo.total_investido + resumo.saldo_disponivel
        
        # Seção de Ações
        if linha == "Ações" and i + 1 < len(linhas):
            # Próxima linha tem o percentual total de ações
            percentual_acoes = extrair_percentual(linhas[i+1])
            if percentual_acoes:
                resumo.percentual_acoes = percentual_acoes
            
            # Pula cabeçalhos e processa ações
            i += 2
            # Pula linhas de cabeçalho até encontrar primeira ação
            while i < len(linhas) and not re.match(r'^[A-Z]{4}\d$', linhas[i]):
                i += 1
            
            # Processa ações até encontrar "Fundos de Investimentos"
            while i < len(linhas) and linhas[i] != "Fundos de Investimentos":
                linha_atual = linhas[i]
                
                # Verifica se é um código de ação (formato XXX3, XXX4, etc.)
                if re.match(r'^[A-Z]{4}\d$', linha_atual):
                    acao = Acao(codigo=linha_atual, posicao=0.0, percentual_alocacao=0.0, rentabilidade=0.0)
                    
                    # Próximas linhas têm posição, % alocação e rentabilidade
                    # Pula linhas vazias
                    j = i + 1
                    while j < len(linhas) and not linhas[j]:
                        j += 1
                    if j < len(linhas) and linhas[j].startswith("R$"):
                        posicao = extrair_valor_monetario(linhas[j])
                        if posicao:
                            acao.posicao = posicao
                    
                    j += 1
                    while j < len(linhas) and not linhas[j]:
                        j += 1
                    if j < len(linhas) and "%" in linhas[j]:
                        percentual = extrair_percentual(linhas[j])
                        if percentual:
                            acao.percentual_alocacao = percentual
                    
                    j += 1
                    while j < len(linhas) and not linhas[j]:
                        j += 1
                    if j < len(linhas) and ("%" in linhas[j] or "-" in linhas[j] or linhas[j][0].isdigit()):
                        rentabilidade = extrair_rentabilidade(linhas[j])
                        if rentabilidade is not None:
                            acao.rentabilidade = rentabilidade
                    
                    resumo.acoes.append(acao)
                    i = j + 1
                else:
                    i += 1
            continue
        
        # Seção de Fundos de Investimentos
        if linha == "Fundos de Investimentos" and i + 1 < len(linhas):
            # Próxima linha tem o percentual total de fundos
            percentual_fundos = extrair_percentual(linhas[i+1])
            if percentual_fundos:
                resumo.percentual_fundos = percentual_fundos
            
            i += 2
            # Pula cabeçalhos
            while i < len(linhas) and (linhas[i] in ["Posição", "% Alocação", "Rentabilidade", ""] or 
                                      linhas[i].startswith("Posição") or linhas[i].startswith("%")):
                i += 1
            
            # Processa fundos até encontrar "Renda Fixa"
            while i < len(linhas) and "Renda Fixa" not in linhas[i]:
                linha_atual = linhas[i]
                
                # Verifica se há um padrão de fundo: R$, %, % seguido de nome do fundo
                # Isso lida com o caso onde os dados vêm antes do nome
                if (i + 6 < len(linhas) and
                    linhas[i].startswith("R$") and
                    "%" in linhas[i+2] and
                    "%" in linhas[i+4] and
                    linhas[i+6] and
                    len(linhas[i+6]) > 10 and
                    ("FIC" in linhas[i+6] or "FIM" in linhas[i+6] or "FIA" in linhas[i+6] or 
                     "Advisory" in linhas[i+6] or "Hedge" in linhas[i+6])):
                    
                    # Dados vêm antes do nome
                    fundo = FundoInvestimento(
                        nome=linhas[i+6],
                        posicao=0.0,
                        percentual_alocacao=0.0,
                        rentabilidade=0.0
                    )
                    
                    posicao = extrair_valor_monetario(linhas[i])
                    if posicao:
                        fundo.posicao = posicao
                    
                    percentual = extrair_percentual(linhas[i+2])
                    if percentual:
                        fundo.percentual_alocacao = percentual
                    
                    rentabilidade = extrair_rentabilidade(linhas[i+4])
                    if rentabilidade is not None:
                        fundo.rentabilidade = rentabilidade
                    
                    resumo.fundos.append(fundo)
                    i = i + 7
                    continue
                
                # Nome do fundo geralmente é uma linha longa sem ser código de ação
                if (linha_atual and 
                    not re.match(r'^[A-Z]{4}\d$', linha_atual) and
                    not linha_atual.startswith("R$") and
                    "%" not in linha_atual and
                    "Posição" not in linha_atual and
                    "Alocação" not in linha_atual and
                    "Rentabilidade" not in linha_atual and
                    "Data" not in linha_atual and
                    "Valor" not in linha_atual and
                    len(linha_atual) > 10 and
                    ("FIC" in linha_atual or "FIM" in linha_atual or "FIA" in linha_atual or "Advisory" in linha_atual or "Hedge" in linha_atual)):
                    
                    fundo = FundoInvestimento(
                        nome=linha_atual,
                        posicao=0.0,
                        percentual_alocacao=0.0,
                        rentabilidade=0.0
                    )
                    
                    # Próximas linhas têm posição, % alocação e rentabilidade
                    j = i + 1
                    while j < len(linhas) and not linhas[j]:
                        j += 1
                    if j < len(linhas) and linhas[j].startswith("R$"):
                        posicao = extrair_valor_monetario(linhas[j])
                        if posicao:
                            fundo.posicao = posicao
                    
                    j += 1
                    while j < len(linhas) and not linhas[j]:
                        j += 1
                    if j < len(linhas) and "%" in linhas[j]:
                        percentual = extrair_percentual(linhas[j])
                        if percentual:
                            fundo.percentual_alocacao = percentual
                    
                    j += 1
                    while j < len(linhas) and not linhas[j]:
                        j += 1
                    if j < len(linhas) and ("%" in linhas[j] or "-" in linhas[j] or (linhas[j] and linhas[j][0].isdigit())):
                        rentabilidade = extrair_rentabilidade(linhas[j])
                        if rentabilidade is not None:
                            fundo.rentabilidade = rentabilidade
                    
                    resumo.fundos.append(fundo)
                    i = j + 1
                else:
                    i += 1
            continue
        
        # Seção de Renda Fixa
        if linha == "Renda Fixa" and i + 1 < len(linhas):
            # Próxima linha tem o percentual total de renda fixa
            percentual_rf = extrair_percentual(linhas[i+1])
            if percentual_rf:
                resumo.percentual_renda_fixa = percentual_rf
            
            i += 2
            # Pula cabeçalhos e linhas vazias
            while i < len(linhas) and (linhas[i] in ["Posição a mercado", "% Alocação", "Valor aplicado", ""] or
                                      linhas[i].startswith("Posição") or linhas[i].startswith("%") or
                                      linhas[i].startswith("Valor") or not linhas[i]):
                i += 1
            
            # Processa títulos de renda fixa
            while i < len(linhas):
                linha_atual = linhas[i].strip()  # Remove espaços e caracteres especiais
                
                # Remove caracteres de controle (form feed, etc.)
                linha_atual = re.sub(r'[\x00-\x1F\x7F]', '', linha_atual)
                
                # Nome do título geralmente contém "CDB", "LCI", "LCA", etc.
                if (linha_atual and 
                    ("CDB" in linha_atual.upper() or "LCI" in linha_atual.upper() or 
                     "LCA" in linha_atual.upper() or "DEB" in linha_atual.upper() or
                     "TESOURO" in linha_atual.upper() or "NTN" in linha_atual.upper() or
                     "BANCO" in linha_atual.upper() or "CONSIGNADO" in linha_atual.upper())):
                    
                    titulo = TituloRendaFixa(
                        nome=linha_atual,
                        posicao_mercado=0.0,
                        percentual_alocacao=0.0,
                        valor_aplicado=0.0
                    )
                    
                    # Procura posição a mercado, % alocação e valor aplicado
                    j = i + 1
                    valores_r = []  # Lista para armazenar valores R$ encontrados
                    percentuais = []  # Lista para armazenar percentuais encontrados
                    
                    while j < len(linhas) and j < i + 20:
                        linha_proc = linhas[j]
                        
                        if not linha_proc:
                            j += 1
                            continue
                        
                        # Se encontrar "Conta:" ou outra seção, para
                        if linha_proc.startswith("Conta:") or "Código do Assessor" in linha_proc:
                            break
                        
                        if linha_proc.startswith("R$"):
                            valor = extrair_valor_monetario(linha_proc)
                            if valor:
                                valores_r.append(valor)
                        
                        if "%" in linha_proc:
                            percentual = extrair_percentual(linha_proc)
                            if percentual:
                                percentuais.append(percentual)
                        
                        j += 1
                    
                    # Associa valores: primeiro R$ grande é posição a mercado, segundo é valor aplicado
                    if len(valores_r) >= 1:
                        titulo.posicao_mercado = valores_r[0]
                    if len(valores_r) >= 2:
                        titulo.valor_aplicado = valores_r[1]
                    elif len(valores_r) == 1 and valores_r[0] < 50000:  # Se só tem um e é pequeno, pode ser valor aplicado
                        titulo.valor_aplicado = valores_r[0]
                        titulo.posicao_mercado = valores_r[0]  # Assume que é o mesmo
                    
                    if len(percentuais) >= 1:
                        titulo.percentual_alocacao = percentuais[0]
                    
                    resumo.titulos_renda_fixa.append(titulo)
                    i = j
                else:
                    i += 1
            continue
        
        i += 1
    
    # Processa informações adicionais de ações (último preço, preço médio, quantidade)
    # Busca na seção de detalhes das ações
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        
        # Procura pela seção com "Último preço (R$)"
        if "Último preço" in linha and "Qtd. total" in (linhas[i+2] if i+2 < len(linhas) else ""):
            # Próximas linhas têm os dados das ações
            j = i + 3
            acao_idx = 0
            while j < len(linhas) and acao_idx < len(resumo.acoes):
                # Procura por padrão de data (DD/MM/YYYY)
                if re.match(r'^\d{2}/\d{2}/\d{4}$', linhas[j]):
                    if acao_idx < len(resumo.acoes):
                        acao = resumo.acoes[acao_idx]
                        
                        # Data do investimento
                        acao.data_investimento = linhas[j]
                        
                        # Preço médio (próxima linha não vazia)
                        k = j + 1
                        while k < len(linhas) and not linhas[k]:
                            k += 1
                        if k < len(linhas) and linhas[k].startswith("R$"):
                            preco_medio = extrair_valor_monetario(linhas[k])
                            if preco_medio:
                                acao.preco_medio = preco_medio
                        
                        # Último preço (próxima linha não vazia)
                        k += 1
                        while k < len(linhas) and not linhas[k]:
                            k += 1
                        if k < len(linhas) and linhas[k].startswith("R$"):
                            ultimo_preco = extrair_valor_monetario(linhas[k])
                            if ultimo_preco:
                                acao.ultimo_preco = ultimo_preco
                        
                        # Quantidade (próxima linha não vazia)
                        k += 1
                        while k < len(linhas) and not linhas[k]:
                            k += 1
                        if k < len(linhas):
                            try:
                                quantidade = int(linhas[k])
                                acao.quantidade = quantidade
                            except ValueError:
                                pass
                        
                        acao_idx += 1
                        j = k + 1
                    else:
                        j += 1
                else:
                    j += 1
            break
        i += 1
    
    # Processa informações adicionais de fundos (valor aplicado, valor líquido, datas)
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        
        # Procura pela seção com "Valor aplicado" e "Valor líquido"
        if "Valor aplicado" in linha and "Valor líquido" in linha:
            j = i + 1
            fundo_idx = 0
            while j < len(linhas) and fundo_idx < len(resumo.fundos):
                # Procura por padrão de data (DD/MM/YYYY)
                if re.match(r'^\d{2}/\d{2}/\d{4}$', linhas[j]):
                    if fundo_idx < len(resumo.fundos):
                        fundo = resumo.fundos[fundo_idx]
                        
                        # Data do investimento
                        fundo.data_investimento = linhas[j]
                        
                        # Valor aplicado (próxima linha não vazia)
                        k = j + 1
                        while k < len(linhas) and not linhas[k]:
                            k += 1
                        if k < len(linhas) and linhas[k].startswith("R$"):
                            valor_apl = extrair_valor_monetario(linhas[k])
                            if valor_apl:
                                fundo.valor_aplicado = valor_apl
                        
                        # Valor líquido (próxima linha não vazia)
                        k += 1
                        while k < len(linhas) and not linhas[k]:
                            k += 1
                        if k < len(linhas) and linhas[k].startswith("R$"):
                            valor_liq = extrair_valor_monetario(linhas[k])
                            if valor_liq:
                                fundo.valor_liquido = valor_liq
                        
                        # Data da cota (próxima linha não vazia)
                        k += 1
                        while k < len(linhas) and not linhas[k]:
                            k += 1
                        if k < len(linhas):
                            data_cota = linhas[k]
                            if re.match(r'^\d{2}/\d{2}/\d{4}$', data_cota):
                                fundo.data_cota = data_cota
                        
                        fundo_idx += 1
                        j = k + 1
                    else:
                        j += 1
                else:
                    j += 1
            break
        i += 1
    
    # Processa informações adicionais de renda fixa (taxa, datas)
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        
        # Procura pela seção com "Taxa a mercado" ou "Data do investimento" seguido de "Taxa a mercado"
        if "Taxa a mercado" in linha:
            # Verifica se há "Data aplicação" nas próximas linhas
            tem_data_aplicacao = False
            for k in range(i+1, min(i+5, len(linhas))):
                if "Data aplicação" in linhas[k]:
                    tem_data_aplicacao = True
                    break
            
            if tem_data_aplicacao:
                # Procura o cabeçalho "Data do investimento" antes
                j = i - 1
                while j >= 0 and "Data do investimento" not in linhas[j]:
                    j -= 1
                
                if j >= 0:
                    # Pula cabeçalhos e vai para os dados
                    j = i + 1
                    while j < len(linhas) and (not linhas[j] or "Data" in linhas[j] or "Taxa" in linhas[j]):
                        j += 1
                    
                    titulo_idx = 0
                    while j < len(linhas) and titulo_idx < len(resumo.titulos_renda_fixa):
                        # Procura por padrão de data (DD/MM/YYYY)
                        if re.match(r'^\d{2}/\d{2}/\d{4}$', linhas[j]):
                            if titulo_idx < len(resumo.titulos_renda_fixa):
                                titulo = resumo.titulos_renda_fixa[titulo_idx]
                                
                                # Data do investimento
                                titulo.data_investimento = linhas[j]
                                
                                # Taxa a mercado (próxima linha não vazia)
                                k = j + 1
                                while k < len(linhas) and not linhas[k]:
                                    k += 1
                                if k < len(linhas):
                                    titulo.taxa_mercado = linhas[k]
                                
                                # Data aplicação (próxima linha não vazia)
                                k += 1
                                while k < len(linhas) and not linhas[k]:
                                    k += 1
                                if k < len(linhas) and re.match(r'^\d{2}/\d{2}/\d{4}$', linhas[k]):
                                    titulo.data_aplicacao = linhas[k]
                                
                                # Data vencimento (próxima linha não vazia)
                                k += 1
                                while k < len(linhas) and not linhas[k]:
                                    k += 1
                                if k < len(linhas) and re.match(r'^\d{2}/\d{2}/\d{4}$', linhas[k]):
                                    titulo.data_vencimento = linhas[k]
                                
                                titulo_idx += 1
                                j = k + 1
                            else:
                                j += 1
                        else:
                            j += 1
                break
        i += 1
    
    return resumo


def formatar_resumo_portfolio(resumo: PortfolioResumo) -> str:
    """
    Formata o resumo do portfólio em uma string legível.
    
    Args:
        resumo: PortfolioResumo com as informações extraídas
        
    Returns:
        String formatada com o resumo
    """
    output = []
    output.append("=" * 80)
    output.append("RESUMO DO PORTFÓLIO")
    output.append("=" * 80)
    output.append("")
    
    # Informações básicas
    output.append(f"Nome do Cliente: {resumo.nome_cliente}")
    output.append(f"Patrimônio Total: R$ {resumo.patrimonio_total:,.2f}")
    output.append(f"Total Investido: R$ {resumo.total_investido:,.2f}")
    output.append(f"Saldo Disponível: R$ {resumo.saldo_disponivel:,.2f}")
    output.append("")
    
    # Ações
    output.append("-" * 80)
    output.append(f"AÇÕES - {resumo.percentual_acoes:.2f}% do portfólio")
    output.append("-" * 80)
    if resumo.acoes:
        for acao in resumo.acoes:
            output.append(f"\nCódigo: {acao.codigo}")
            output.append(f"  Posição: R$ {acao.posicao:,.2f}")
            output.append(f"  % Alocação: {acao.percentual_alocacao:.2f}%")
            output.append(f"  Rentabilidade: {acao.rentabilidade:.2f}%")
            if acao.retorno_mensal is not None:
                output.append(f"  Retorno Mensal: {acao.retorno_mensal:.2f}%")
            if acao.ultimo_preco:
                output.append(f"  Último Preço: R$ {acao.ultimo_preco:.2f}")
            if acao.preco_mes_anterior:
                output.append(f"  Preço Mês Anterior: R$ {acao.preco_mes_anterior:.2f}")
            if acao.preco_medio:
                output.append(f"  Preço Médio: R$ {acao.preco_medio:.2f}")
            if acao.quantidade:
                output.append(f"  Quantidade: {acao.quantidade}")
            if acao.data_investimento:
                output.append(f"  Data do Investimento: {acao.data_investimento}")
    else:
        output.append("Nenhuma ação encontrada.")
    output.append("")
    
    # Fundos
    output.append("-" * 80)
    output.append(f"FUNDOS DE INVESTIMENTO - {resumo.percentual_fundos:.2f}% do portfólio")
    output.append("-" * 80)
    if resumo.fundos:
        for fundo in resumo.fundos:
            output.append(f"\nNome: {fundo.nome}")
            output.append(f"  Posição: R$ {fundo.posicao:,.2f}")
            output.append(f"  % Alocação: {fundo.percentual_alocacao:.2f}%")
            output.append(f"  Rentabilidade: {fundo.rentabilidade:.2f}%")
            if fundo.valor_aplicado:
                output.append(f"  Valor Aplicado: R$ {fundo.valor_aplicado:,.2f}")
            if fundo.valor_liquido:
                output.append(f"  Valor Líquido: R$ {fundo.valor_liquido:,.2f}")
            if fundo.data_investimento:
                output.append(f"  Data do Investimento: {fundo.data_investimento}")
            if fundo.data_cota:
                output.append(f"  Data da Cota: {fundo.data_cota}")
    else:
        output.append("Nenhum fundo encontrado.")
    output.append("")
    
    # Renda Fixa
    output.append("-" * 80)
    output.append(f"RENDA FIXA - {resumo.percentual_renda_fixa:.2f}% do portfólio")
    output.append("-" * 80)
    if resumo.titulos_renda_fixa:
        for titulo in resumo.titulos_renda_fixa:
            output.append(f"\nNome: {titulo.nome}")
            output.append(f"  Posição a Mercado: R$ {titulo.posicao_mercado:,.2f}")
            output.append(f"  % Alocação: {titulo.percentual_alocacao:.2f}%")
            output.append(f"  Valor Aplicado: R$ {titulo.valor_aplicado:,.2f}")
            if titulo.taxa_mercado:
                output.append(f"  Taxa a Mercado: {titulo.taxa_mercado}")
            if titulo.data_aplicacao:
                output.append(f"  Data de Aplicação: {titulo.data_aplicacao}")
            if titulo.data_vencimento:
                output.append(f"  Data de Vencimento: {titulo.data_vencimento}")
            if titulo.data_investimento:
                output.append(f"  Data do Investimento: {titulo.data_investimento}")
    else:
        output.append("Nenhum título de renda fixa encontrado.")
    output.append("")
    
    output.append("=" * 80)
    
    return "\n".join(output)


def sumarizar_portfolio(arquivo_ou_texto: Union[str, Path]) -> PortfolioResumo:
    """
    Função principal para processar um arquivo de portfólio e retornar resumo estruturado.
    
    Args:
        arquivo_ou_texto: Caminho do arquivo (Path ou str) ou texto do portfólio
        
    Returns:
        PortfolioResumo com todas as informações extraídas
        
    Example:
        >>> from src import sumarizar_portfolio
        >>> resumo = sumarizar_portfolio("Input/XP - Albert_s portfolio.txt")
        >>> print(resumo.nome_cliente)
        >>> print(resumo.patrimonio_total)
    """
    # Se for um Path ou string que parece um caminho de arquivo, lê o arquivo
    if isinstance(arquivo_ou_texto, Path) or (isinstance(arquivo_ou_texto, str) and 
                                               (Path(arquivo_ou_texto).exists() or 
                                                arquivo_ou_texto.endswith('.txt'))):
        try:
            caminho = Path(arquivo_ou_texto)
            with open(caminho, 'r', encoding='utf-8') as f:
                texto = f.read()
        except FileNotFoundError:
            # Se não encontrar o arquivo, assume que é texto
            texto = str(arquivo_ou_texto)
    else:
        # Assume que é texto
        texto = str(arquivo_ou_texto)
    
    return parse_portfolio(texto)


def calcular_retorno_mensal_acoes(
    portfolio_resumo: PortfolioResumo,
    usar_ultimo_preco_portfolio: bool = False
) -> PortfolioResumo:
    """
    Calcula o retorno mensal total de cada ação no portfólio usando yfinance.
    
    O retorno é calculado usando preços ajustados (auto_adjust=True):
    - Usa auto_adjust=True para obter preços já ajustados para dividendos e desdobramentos
    - A coluna "Close" com auto_adjust=True contém os preços ajustados
    - Compara o último preço disponível com o preço de 1 mês atrás
    - O retorno total já inclui todos os ajustes (dividendos, desdobramentos, etc.)
    
    Args:
        portfolio_resumo: PortfolioResumo com as ações do cliente
        usar_ultimo_preco_portfolio: Se True, atualiza o último preço do portfólio com o Adj Close.
                                     Se False, mantém o preço original do portfólio.
                                     O cálculo do retorno sempre usa Adj Close do yfinance.
        
    Returns:
        PortfolioResumo com os campos retorno_mensal e preco_mes_anterior preenchidos
        
    Example:
        >>> from src import sumarizar_portfolio, calcular_retorno_mensal_acoes
        >>> resumo = sumarizar_portfolio("Input/XP - Albert_s portfolio.txt")
        >>> resumo = calcular_retorno_mensal_acoes(resumo)
        >>> for acao in resumo.acoes:
        ...     print(f"{acao.codigo}: {acao.retorno_mensal:.2f}%")
    """
    if not YFINANCE_AVAILABLE:
        raise ImportError(
            "yfinance não está instalado. Instale com: pip install yfinance"
        )
    
    for acao in portfolio_resumo.acoes:
        try:
            # Para ações brasileiras, adiciona sufixo .SA
            codigo_yfinance = f"{acao.codigo}.SA"
            
            # Busca dados históricos com auto_adjust=True para obter preços ajustados
            # auto_adjust=True retorna preços já ajustados para dividendos e desdobramentos na coluna "Close"
            ticker = yf.Ticker(codigo_yfinance)
            hist = ticker.history(period="3mo", auto_adjust=True)
            
            if hist.empty:
                print(f"Aviso: Não foi possível obter dados para {acao.codigo}")
                continue
            
            # Verifica se temos a coluna Close (que contém os preços ajustados quando auto_adjust=True)
            if 'Close' not in hist.columns:
                print(f"Aviso: Dados de preços não disponíveis para {acao.codigo}")
                continue
            
            # Pega o último preço disponível (Close com auto_adjust=True já considera dividendos e desdobramentos)
            data_atual = hist.index[-1]
            ultimo_preco_adj = hist['Close'].iloc[-1]
            
            # Atualiza o último preço do portfólio se solicitado
            if usar_ultimo_preco_portfolio:
                acao.ultimo_preco = ultimo_preco_adj
            
            # Calcula a data de 1 mês atrás (aproximadamente 30 dias)
            # Procura na janela de 25 a 35 dias atrás para ter flexibilidade com dias não úteis
            data_inicio = data_atual - timedelta(days=35)
            data_fim = data_atual - timedelta(days=25)
            
            # Filtra dados nessa janela
            dados_mes_anterior = hist[(hist.index >= data_inicio) & (hist.index <= data_fim)]
            
            if dados_mes_anterior.empty:
                # Se não encontrar dados na janela, tenta pegar o mais antigo disponível
                # que seja pelo menos 20 dias atrás
                dados_antigos = hist[hist.index <= (data_atual - timedelta(days=20))]
                if not dados_antigos.empty:
                    preco_mes_anterior_adj = dados_antigos['Close'].iloc[-1]
                    data_mes_anterior = dados_antigos.index[-1]
                else:
                    print(f"Aviso: Não foi possível encontrar preço de 1 mês atrás para {acao.codigo}")
                    continue
            else:
                # Pega o preço mais próximo da data desejada (último da janela)
                preco_mes_anterior_adj = dados_mes_anterior['Close'].iloc[-1]
                data_mes_anterior = dados_mes_anterior.index[-1]
            
            # Calcula o retorno mensal total usando preços ajustados
            # Com auto_adjust=True, a coluna Close já considera dividendos, desdobramentos, etc.
            # Retorno = (Preço Atual - Preço Mês Anterior) / Preço Mês Anterior * 100
            retorno_mensal = ((ultimo_preco_adj - preco_mes_anterior_adj) / preco_mes_anterior_adj) * 100
            
            # Atualiza os campos da ação
            acao.retorno_mensal = retorno_mensal
            acao.preco_mes_anterior = preco_mes_anterior_adj
            
            # Se não tinha último preço, atualiza com o do yfinance
            if not acao.ultimo_preco:
                acao.ultimo_preco = ultimo_preco_adj
                
        except Exception as e:
            print(f"Erro ao calcular retorno mensal para {acao.codigo}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    return portfolio_resumo


def calcular_retorno_mensal_acoes_lista(
    acoes: List[Acao],
    usar_ultimo_preco_portfolio: bool = False
) -> List[Acao]:
    """
    Calcula o retorno mensal total de uma lista de ações usando yfinance.
    
    O retorno é calculado usando preços ajustados (auto_adjust=True):
    - Usa auto_adjust=True para obter preços já ajustados para dividendos e desdobramentos
    - A coluna "Close" com auto_adjust=True contém os preços ajustados
    - Compara o último preço disponível com o preço de 1 mês atrás
    
    Args:
        acoes: Lista de objetos Acao
        usar_ultimo_preco_portfolio: Se True, atualiza o último preço do portfólio com o preço ajustado.
                                     Se False, mantém o preço original do portfólio.
                                     O cálculo do retorno sempre usa preços ajustados do yfinance.
        
    Returns:
        Lista de ações com os campos retorno_mensal e preco_mes_anterior preenchidos
    """
    if not YFINANCE_AVAILABLE:
        raise ImportError(
            "yfinance não está instalado. Instale com: pip install yfinance"
        )
    
    for acao in acoes:
        try:
            # Para ações brasileiras, adiciona sufixo .SA
            codigo_yfinance = f"{acao.codigo}.SA"
            
            # Busca dados históricos com auto_adjust=True para obter preços ajustados
            # auto_adjust=True retorna preços já ajustados para dividendos e desdobramentos na coluna "Close"
            ticker = yf.Ticker(codigo_yfinance)
            hist = ticker.history(period="3mo", auto_adjust=True)
            
            if hist.empty:
                print(f"Aviso: Não foi possível obter dados para {acao.codigo}")
                continue
            
            # Verifica se temos a coluna Close (que contém os preços ajustados quando auto_adjust=True)
            if 'Close' not in hist.columns:
                print(f"Aviso: Dados de preços não disponíveis para {acao.codigo}")
                continue
            
            # Pega o último preço disponível (Close com auto_adjust=True já considera dividendos e desdobramentos)
            data_atual = hist.index[-1]
            ultimo_preco_adj = hist['Close'].iloc[-1]
            
            # Atualiza o último preço do portfólio se solicitado
            if usar_ultimo_preco_portfolio:
                acao.ultimo_preco = ultimo_preco_adj
            
            # Calcula a data de 1 mês atrás (aproximadamente 30 dias)
            # Procura na janela de 25 a 35 dias atrás para ter flexibilidade com dias não úteis
            data_inicio = data_atual - timedelta(days=35)
            data_fim = data_atual - timedelta(days=25)
            
            # Filtra dados nessa janela
            dados_mes_anterior = hist[(hist.index >= data_inicio) & (hist.index <= data_fim)]
            
            if dados_mes_anterior.empty:
                # Se não encontrar dados na janela, tenta pegar o mais antigo disponível
                # que seja pelo menos 20 dias atrás
                dados_antigos = hist[hist.index <= (data_atual - timedelta(days=20))]
                if not dados_antigos.empty:
                    preco_mes_anterior_adj = dados_antigos['Close'].iloc[-1]
                    data_mes_anterior = dados_antigos.index[-1]
                else:
                    print(f"Aviso: Não foi possível encontrar preço de 1 mês atrás para {acao.codigo}")
                    continue
            else:
                preco_mes_anterior_adj = dados_mes_anterior['Close'].iloc[-1]
                data_mes_anterior = dados_mes_anterior.index[-1]
            
            # Calcula o retorno mensal total usando preços ajustados
            # Com auto_adjust=True, a coluna Close já considera dividendos, desdobramentos, etc.
            retorno_mensal = ((ultimo_preco_adj - preco_mes_anterior_adj) / preco_mes_anterior_adj) * 100
            
            # Atualiza os campos da ação
            acao.retorno_mensal = retorno_mensal
            acao.preco_mes_anterior = preco_mes_anterior_adj
            
            # Se não tinha último preço, atualiza com o do yfinance
            if not acao.ultimo_preco:
                acao.ultimo_preco = ultimo_preco_adj
                
        except Exception as e:
            print(f"Erro ao calcular retorno mensal para {acao.codigo}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    return acoes
