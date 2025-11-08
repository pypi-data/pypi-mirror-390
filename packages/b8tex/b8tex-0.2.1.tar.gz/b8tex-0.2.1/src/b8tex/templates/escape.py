"""LaTeX character escaping utilities for the template system."""

from __future__ import annotations


class Raw(str):
    """Wrapper for raw LaTeX strings that should not be escaped.

    Example:
        Raw(r"\\textbf{bold text}")  # Will not be escaped
    """

    pass


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters in text.

    Escapes the following characters: \\ & % $ # _ { } ~ ^

    Args:
        text: Text to escape

    Returns:
        Escaped text safe for LaTeX

    Example:
        >>> escape_latex("50% of $100")
        '50\\% of \\$100'
    """
    if isinstance(text, Raw):
        return str(text)

    # Use single-pass character-by-character processing to avoid double-escaping
    escape_map = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
    }

    return ''.join(escape_map.get(c, c) for c in text)


def escape_latex_math(text: str) -> str:
    """Escape LaTeX characters for math mode.

    Math mode has different escaping rules - most characters like ^, _, {, }
    are actually math operators and should not be escaped.

    Args:
        text: Math expression text

    Returns:
        Text safe for LaTeX math mode
    """
    if isinstance(text, Raw):
        return str(text)

    # In math mode, only escape these
    replacements = [
        ("\\", r"\backslash"),
        ("%", r"\%"),
    ]

    result = text
    for char, escaped in replacements:
        result = result.replace(char, escaped)

    return result


def sanitize_label(label: str) -> str:
    """Sanitize a string for use as a LaTeX label.

    Converts spaces to hyphens, removes special characters.

    Args:
        label: Label text

    Returns:
        Sanitized label safe for \\label{}

    Example:
        >>> sanitize_label("My Section Title")
        'my-section-title'
    """
    # Convert to lowercase
    label = label.lower()

    # Replace spaces with hyphens
    label = label.replace(" ", "-")

    # Remove characters that aren't alphanumeric, hyphen, or colon
    # (colons are standard in LaTeX labels, e.g., "sec:intro")
    label = "".join(c for c in label if c.isalnum() or c in "-:")

    return label
