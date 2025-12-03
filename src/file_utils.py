"""Utilitários para leitura e escrita de arquivos."""

from pathlib import Path


def read_file(file_path: Path) -> str:
    """
    Lê o conteúdo de um arquivo de texto.
    
    Args:
        file_path: Caminho do arquivo a ser lido
        
    Returns:
        Conteúdo do arquivo como string
        
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado
        Exception: Se ocorrer outro erro ao ler o arquivo
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo {file_path}: {str(e)}")


def write_file(file_path: Path, content: str) -> None:
    """
    Escreve conteúdo em um arquivo de texto.
    
    Args:
        file_path: Caminho do arquivo a ser escrito
        content: Conteúdo a ser escrito no arquivo
        
    Raises:
        Exception: Se ocorrer erro ao escrever o arquivo
    """
    try:
        # Garante que o diretório existe
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"Erro ao escrever arquivo {file_path}: {str(e)}")

