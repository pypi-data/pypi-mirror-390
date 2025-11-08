"""Tests for LaTeX escaping utilities."""

from __future__ import annotations

import pytest

from b8tex.templates.escape import Raw, escape_latex


class TestRaw:
    """Tests for Raw wrapper class."""

    def test_raw_is_string_subclass(self):
        """Raw should be a string subclass."""
        raw = Raw(r"\textbf{bold}")
        assert isinstance(raw, str)
        assert str(raw) == r"\textbf{bold}"

    def test_raw_preserves_content(self):
        """Raw should preserve LaTeX commands."""
        content = r"\section{Title} \textit{italic} $x^2$"
        raw = Raw(content)
        assert str(raw) == content

    def test_raw_equality(self):
        """Raw should support equality comparison."""
        raw1 = Raw(r"\textbf{test}")
        raw2 = Raw(r"\textbf{test}")
        raw3 = Raw(r"\textit{test}")

        assert raw1 == raw2
        assert raw1 != raw3

    def test_raw_string_operations(self):
        """Raw should support string operations."""
        raw = Raw(r"\textbf{test}")

        assert len(raw) == 13  # \textbf{test} is 13 chars
        assert raw.startswith(r"\textbf")
        assert raw.endswith(r"}")
        assert r"test" in raw


class TestEscapeLatex:
    """Tests for escape_latex function."""

    def test_escape_backslash(self):
        """Backslash should be escaped to textbackslash."""
        assert escape_latex(r"C:\path\to\file") == r"C:\textbackslash{}path\textbackslash{}to\textbackslash{}file"

    def test_escape_ampersand(self):
        """Ampersand should be escaped."""
        assert escape_latex("Tom & Jerry") == r"Tom \& Jerry"

    def test_escape_percent(self):
        """Percent should be escaped."""
        assert escape_latex("50% success rate") == r"50\% success rate"

    def test_escape_dollar(self):
        """Dollar sign should be escaped."""
        assert escape_latex("Price: $100") == r"Price: \$100"

    def test_escape_hash(self):
        """Hash/pound sign should be escaped."""
        assert escape_latex("#hashtag") == r"\#hashtag"

    def test_escape_underscore(self):
        """Underscore should be escaped."""
        assert escape_latex("variable_name") == r"variable\_name"

    def test_escape_braces(self):
        """Curly braces should be escaped."""
        assert escape_latex("set {1, 2, 3}") == r"set \{1, 2, 3\}"

    def test_escape_tilde(self):
        """Tilde should be escaped to textasciitilde."""
        assert escape_latex("~username") == r"\textasciitilde{}username"

    def test_escape_caret(self):
        """Caret should be escaped."""
        assert escape_latex("x^2") == r"x\^{}2"

    def test_escape_all_special_chars(self):
        """All special characters should be escaped together."""
        text = r"\ & % $ # _ { } ~ ^"
        expected = r"\textbackslash{} \& \% \$ \# \_ \{ \} \textasciitilde{} \^{}"
        assert escape_latex(text) == expected

    def test_escape_mixed_text(self):
        """Mixed text with special characters should be escaped."""
        text = "Alice & Bob have $100 (50% each)"
        expected = r"Alice \& Bob have \$100 (50\% each)"
        assert escape_latex(text) == expected

    def test_escape_empty_string(self):
        """Empty string should remain empty."""
        assert escape_latex("") == ""

    def test_escape_no_special_chars(self):
        """Text without special characters should be unchanged."""
        text = "Hello World 123"
        assert escape_latex(text) == text

    def test_escape_unicode(self):
        """Unicode characters should pass through unchanged."""
        text = "Café résumé naïve"
        assert escape_latex(text) == text

    def test_raw_not_escaped(self):
        """Raw strings should not be escaped."""
        raw = Raw(r"\textbf{bold} & \textit{italic}")
        result = escape_latex(raw)
        assert result == r"\textbf{bold} & \textit{italic}"

    def test_raw_wrapper_preserves_content(self):
        """Raw wrapper should preserve LaTeX commands."""
        raw = Raw(r"\section{Introduction}")
        result = escape_latex(raw)
        assert result == r"\section{Introduction}"

    def test_escape_paths(self):
        """File paths should be properly escaped."""
        path = r"C:\Users\John_Doe\Documents\file#1.txt"
        result = escape_latex(path)
        assert r"\textbackslash{}" in result
        assert r"\_" in result
        assert r"\#" in result

    def test_escape_code_snippets(self):
        """Code snippets should be properly escaped."""
        code = "if (x > 0 && y < 100) { result = x_val + y_val; }"
        result = escape_latex(code)
        assert r"\&" in result  # &&
        assert r"\{" in result and r"\}" in result
        assert r"\_" in result  # x_val, y_val

    def test_escape_math_expression(self):
        """Math expressions in text should be escaped."""
        text = "The formula is x^2 + y^2 = r^2"
        result = escape_latex(text)
        assert r"\^{}" in result

    def test_escape_url(self):
        """URLs with special characters should be escaped."""
        url = "https://example.com/path?q=50%&sort=asc#section"
        result = escape_latex(url)
        assert r"\%" in result
        assert r"\&" in result
        assert r"\#" in result

    def test_escape_multiple_consecutive_special_chars(self):
        """Multiple consecutive special characters should all be escaped."""
        text = "$$$###%%%"
        result = escape_latex(text)
        assert result == r"\$\$\$\#\#\#\%\%\%"

    def test_raw_in_mixed_content(self):
        """Raw strings in mixed content should be handled correctly."""
        # This tests the expected use case where user manually concatenates
        raw_part = Raw(r"\textbf{Title}")
        escaped_part = escape_latex("User Input & Text")

        # Raw should not be escaped
        assert escape_latex(raw_part) == r"\textbf{Title}"
        # Regular text should be escaped
        assert escaped_part == r"User Input \& Text"

    def test_escape_newlines_preserved(self):
        """Newlines should be preserved."""
        text = "Line 1\nLine 2\nLine 3"
        result = escape_latex(text)
        assert "\n" in result
        assert result.count("\n") == 2

    def test_escape_tabs_preserved(self):
        """Tabs should be preserved."""
        text = "Column1\tColumn2\tColumn3"
        result = escape_latex(text)
        assert "\t" in result
        assert result.count("\t") == 2

    def test_escape_maintains_order(self):
        """Escaping should maintain character order."""
        text = "A & B $ C % D"
        result = escape_latex(text)
        # Check that A, B, C, D appear in order
        positions = [result.index(char) for char in "ABCD"]
        assert positions == sorted(positions)
