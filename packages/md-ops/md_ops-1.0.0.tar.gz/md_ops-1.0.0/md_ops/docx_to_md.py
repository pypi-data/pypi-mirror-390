"""
Convert DOCX to Markdown
"""

from docx import Document
import re


def docx_to_md(docx_path):
    """
    Convert a DOCX file to Markdown text.
    
    Args:
        docx_path (str): Path to the DOCX file
        
    Returns:
        str: The Markdown content
    """
    doc = Document(docx_path)
    markdown_lines = []
    
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        
        if not text:
            markdown_lines.append('')
            continue
            
        # Check if it's a heading
        if paragraph.style.name.startswith('Heading'):
            level = paragraph.style.name.split()[-1]
            if level.isdigit():
                markdown_lines.append('#' * int(level) + ' ' + text)
            else:
                markdown_lines.append(text)
        elif paragraph.style.name == 'List Bullet':
            markdown_lines.append('- ' + text)
        elif paragraph.style.name == 'Quote' or paragraph.style.name == 'Intense Quote':
            markdown_lines.append('> ' + text)
        else:
            # Process inline formatting
            formatted_text = text
            
            # Check for bold (simplified)
            for run in paragraph.runs:
                if run.bold:
                    formatted_text = formatted_text.replace(run.text, f'**{run.text}**')
                elif run.italic:
                    formatted_text = formatted_text.replace(run.text, f'*{run.text}*')
                    
            markdown_lines.append(formatted_text)
    
    return '\n'.join(markdown_lines)
