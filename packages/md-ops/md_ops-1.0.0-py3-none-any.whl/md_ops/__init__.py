"""
md-ops: Convert Markdown <-> DOCX easily
A powerful Python library for converting between Markdown and DOCX formats.
"""

from .md_to_docx import md_to_docx
from .docx_to_md import docx_to_md

__version__ = "1.0.0"
__author__ = "Consult Anubhav"
__all__ = ["md_to_docx", "docx_to_md"]
