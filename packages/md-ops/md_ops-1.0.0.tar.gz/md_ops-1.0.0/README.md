# md-ops

🔄 **Convert Markdown ↔️ DOCX easily**

A powerful Python library for converting between Markdown and DOCX formats with ease.

## 📦 Installation

```bash
pip install md-ops
```

## 🚀 Quick Start

### Convert Markdown to DOCX

```python
from md_ops import md_to_docx

markdown = """
# Hello World

This is **bold** and this is *italic*.

- Item 1
- Item 2
"""

md_to_docx(markdown, "output.docx")
```

### Convert DOCX to Markdown

```python
from md_ops import docx_to_md

markdown = docx_to_md("input.docx")
print(markdown)
```

## 📖 API Reference

### `md_to_docx(markdown_text, output_path='output.docx')`

Converts Markdown text to a DOCX file.

**Parameters:**

- `markdown_text` (str): The Markdown content to convert
- `output_path` (str, optional): Output file path (default: 'output.docx')

**Returns:** `str` - Path to the created DOCX file

**Example:**

```python
md_to_docx("# My Document", "my-file.docx")
```

### `docx_to_md(docx_path)`

Converts a DOCX file to Markdown text.

**Parameters:**

- `docx_path` (str): Path to the DOCX file

**Returns:** `str` - The Markdown content

**Example:**

```python
markdown = docx_to_md("document.docx")
```

## ✨ Supported Features

### Markdown → DOCX

- ✅ Headings (H1-H6)
- ✅ **Bold** and _Italic_ text
- ✅ `Inline code`
- ✅ Code blocks
- ✅ Links
- ✅ Lists (ordered & unordered)
- ✅ Blockquotes
- ✅ Horizontal rules

### DOCX → Markdown

- ✅ Headings
- ✅ Text formatting (bold, italic)
- ✅ Lists
- ✅ Blockquotes

## 🧪 Testing

Run the included test file:

```bash
python test.py
```

## 📄 License

Proprietary © Consult Anubhav - All Rights Reserved

## 👨‍💻 Author

**Consult Anubhav**

---

Made with ❤️ for developers who need easy document conversion
