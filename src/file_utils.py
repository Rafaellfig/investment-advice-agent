"""Utilities for reading and writing files."""

from pathlib import Path


def read_file(file_path: Path) -> str:
    """
    Reads the content of a text file.
    
    Args:
        file_path: Path of the file to be read
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If the file is not found
        Exception: If another error occurs while reading the file
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")


def write_file(file_path: Path, content: str) -> None:
    """
    Writes content to a text file.
    
    Args:
        file_path: Path of the file to be written
        content: Content to be written to the file
        
    Raises:
        Exception: If an error occurs while writing the file
    """
    try:
        # Ensure the directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"Error writing file {file_path}: {str(e)}")
