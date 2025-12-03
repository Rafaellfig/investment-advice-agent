# Workflow de Geração de Carta de Investimento

Este projeto replica o workflow definido no `enter_challenge.rivet-project` usando Python e a SDK da OpenAI.

## 📁 Estrutura do Projeto

```
PS_ENTER/
├── main.py                 # Script principal (orquestração)
├── config/                 # Configurações
│   ├── __init__.py
│   └── settings.py         # Configurações e constantes
├── src/                    # Módulos de serviços
│   ├── __init__.py
│   ├── file_utils.py       # Utilitários de leitura/escrita
│   └── ai_service.py       # Serviços de integração com OpenAI
├── prompts/                # Templates de prompts
│   ├── __init__.py
│   └── prompts.py          # Templates de prompts para IA
├── Input/                  # Arquivos de entrada
│   ├── XP - Albert_s portfolio.txt
│   ├── XP - Albert_s risk profile.txt
│   └── XP - Macro analysis.txt
├── Output/                 # Arquivos de saída
│   └── output_letter.txt
├── requirements.txt        # Dependências Python
├── .env                   # Variáveis de ambiente (não versionado)
└── .gitignore             # Arquivos ignorados pelo Git
```

## 🚀 Como Usar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```
OPENAI_API_KEY=sua_chave_api_aqui
```

**Como obter a chave da API:**
1. Acesse: https://platform.openai.com/api-keys
2. Faça login (ou crie uma conta)
3. Clique em "Create new secret key"
4. Copie a chave (formato: `sk-proj-...`)

### 3. Executar o workflow

```bash
python main.py
```

## 📋 Workflow

O workflow executa as seguintes etapas:

1. **Leitura de arquivos de entrada:**
   - Portfólio do cliente
   - Perfil de risco
   - Análise macroeconômica

2. **Geração de resumos com IA:**
   - Resumo dos resultados do portfólio
   - Resumo do perfil de risco
   - Resumo da perspectiva macroeconômica

3. **Geração da carta de investimento:**
   - Combina os três resumos em uma carta profissional em português

4. **Salvamento do resultado:**
   - Salva a carta em `Output/output_letter.txt`

## 🏗️ Arquitetura

### `main.py`
Script principal que orquestra o workflow completo. Mantém apenas a lógica de fluxo.

### `config/settings.py`
Centraliza todas as configurações:
- Configurações da API OpenAI (modelo, temperatura, tokens)
- Caminhos de arquivos e diretórios
- Variáveis de ambiente

### `src/file_utils.py`
Utilitários para manipulação de arquivos:
- `read_file()`: Lê arquivos de texto
- `write_file()`: Escreve conteúdo em arquivos

### `src/ai_service.py`
Serviços de integração com a OpenAI:
- `call_openai()`: Chamada genérica à API
- `summarize_portfolio_results()`: Resumo do portfólio
- `summarize_risk_profile()`: Resumo do perfil de risco
- `summarize_macroeconomic_outlook()`: Resumo macroeconômico
- `generate_investment_letter()`: Geração da carta final

### `prompts/prompts.py`
Templates de prompts organizados em funções:
- `get_portfolio_prompt()`: Prompt para resumo do portfólio
- `get_risk_profile_prompt()`: Prompt para perfil de risco
- `get_macro_outlook_prompt()`: Prompt para análise macro
- `get_investment_letter_prompt()`: Prompt para carta final

## ⚙️ Configurações

As configurações podem ser alteradas em `config/settings.py`:

- **Modelo:** `gpt-4o-mini`
- **Temperature:** `0.5`
- **Max Tokens:** `1024`

## 📝 Requisitos

- Python 3.7 ou superior
- Chave de API da OpenAI
- Arquivos de entrada na pasta `Input/`

## 🔒 Segurança

- O arquivo `.env` está no `.gitignore` (não será versionado)
- Nunca compartilhe sua chave da API publicamente
- Se a chave for exposta, revogue-a imediatamente no site da OpenAI

## 📚 Benefícios da Nova Estrutura

✅ **Separação de responsabilidades:** Cada módulo tem uma função específica  
✅ **Manutenibilidade:** Código mais fácil de entender e modificar  
✅ **Reutilização:** Funções podem ser reutilizadas em outros projetos  
✅ **Testabilidade:** Módulos isolados são mais fáceis de testar  
✅ **Escalabilidade:** Fácil adicionar novos recursos sem poluir o código principal  

## 🐛 Troubleshooting

### Erro: "API key not found"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Confirme que a chave está correta e completa
- Certifique-se de que não há espaços extras no arquivo

### Erro: "Arquivo não encontrado"
- Verifique se os arquivos de entrada existem na pasta `Input/`
- Confirme os nomes dos arquivos (case-sensitive)

### Erro: "Module not found"
- Certifique-se de que todas as dependências estão instaladas: `pip install -r requirements.txt`
- Verifique se está executando o script da raiz do projeto

