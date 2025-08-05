"""
File utility functions for Word Document Server.
"""
import os
from typing import Tuple, Optional
import shutil


def check_file_writeable(filepath: str) -> Tuple[bool, str]:
    """
    Check if a file can be written to.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Tuple of (is_writeable, error_message)
    """
    # If file doesn't exist, check if directory is writeable
    if not os.path.exists(filepath):
        directory = os.path.dirname(filepath)
        # If no directory is specified (empty string), use current directory
        if directory == '':
            directory = '.'
        if not os.path.exists(directory):
            return False, f"Directory {directory} does not exist"
        if not os.access(directory, os.W_OK):
            return False, f"Directory {directory} is not writeable"
        return True, ""
    
    # If file exists, check if it's writeable
    if not os.access(filepath, os.W_OK):
        return False, f"File {filepath} is not writeable (permission denied)"
    
    # Try to open the file for writing to see if it's locked
    try:
        with open(filepath, 'a'):
            pass
        return True, ""
    except IOError as e:
        return False, f"File {filepath} is not writeable: {str(e)}"
    except Exception as e:
        return False, f"Unknown error checking file permissions: {str(e)}"


def create_document_copy(source_path: str, dest_path: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
    """
    Create a copy of a document.
    
    Args:
        source_path: Path to the source document
        dest_path: Optional path for the new document. If not provided, will use source_path + '_copy.docx'
        
    Returns:
        Tuple of (success, message, new_filepath)
    """
    if not os.path.exists(source_path):
        return False, f"Source document {source_path} does not exist", None
    
    if not dest_path:
        # Generate a new filename if not provided
        base, ext = os.path.splitext(source_path)
        dest_path = f"{base}_copy{ext}"
    
    try:
        # Simple file copy
        shutil.copy2(source_path, dest_path)
        return True, f"Document copied to {dest_path}", dest_path
    except Exception as e:
        return False, f"Failed to copy document: {str(e)}", None


def ensure_docx_extension(filename: str) -> str:
    """
    Ensure filename has .docx extension.
    
    Args:
        filename: The filename to check
        
    Returns:
        Filename with .docx extension
    """
    if not filename.endswith('.docx'):
        return filename + '.docx'
    return filename


def resolve_document_path(filename: str, save_path: Optional[str] = None) -> str:
    """
    解析文档完整路径
    
    Args:
        filename: 文件名
        save_path: 可选的保存路径
        
    Returns:
        完整的文件路径
    """
    filename = ensure_docx_extension(filename)
    
    if save_path:
        # 规范化路径
        save_path = os.path.abspath(save_path)
        # 确保目录存在
        os.makedirs(save_path, exist_ok=True)
        return os.path.join(save_path, filename)
    else:
        return filename


def validate_save_path(save_path: str) -> Tuple[bool, str]:
    """
    验证保存路径
    
    Args:
        save_path: 要验证的保存路径
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # 检查路径是否为绝对路径或相对路径
        abs_path = os.path.abspath(save_path)
        
        # 检查父目录是否存在或可创建
        if not os.path.exists(abs_path):
            os.makedirs(abs_path, exist_ok=True)
        
        # 检查写入权限
        if not os.access(abs_path, os.W_OK):
            return False, f"目录 {abs_path} 没有写入权限"
        
        return True, ""
    except Exception as e:
        return False, f"路径验证失败: {str(e)}"
