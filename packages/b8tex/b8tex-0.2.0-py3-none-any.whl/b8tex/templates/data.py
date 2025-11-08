"""Data-driven content generation for templates (tables, plots)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from b8tex.templates.escape import Raw, escape_latex


@dataclass
class DataTable:
    """Generate LaTeX table from data.

    Supports pandas DataFrames, lists of dicts, and lists of lists.
    Generates professional tables using booktabs package.

    Attributes:
        data: Table data (DataFrame, list of dicts, or list of lists)
        caption: Table caption
        label: Label for cross-references
        column_format: LaTeX column format string (e.g., "lccr")
        use_booktabs: Use booktabs package for professional tables
        header: Whether to include header row
        index: Whether to include index column (pandas only)
        float_format: Format string for floating point numbers
    """

    data: Any  # pandas.DataFrame | list[dict] | list[list]
    caption: str | None = None
    label: str | None = None
    column_format: str | None = None
    use_booktabs: bool = True
    header: bool = True
    index: bool = False
    float_format: str = ".2f"

    @classmethod
    def from_dataframe(
        cls,
        df: Any,  # pandas.DataFrame
        caption: str | None = None,
        label: str | None = None,
        **kwargs: Any,
    ) -> DataTable:
        """Create table from pandas DataFrame.

        Args:
            df: pandas DataFrame
            caption: Table caption
            label: Label for cross-references
            **kwargs: Additional DataTable arguments

        Returns:
            DataTable instance
        """
        return cls(data=df, caption=caption, label=label, **kwargs)

    @classmethod
    def from_list(
        cls,
        data: list[list[Any]] | list[dict[str, Any]],
        caption: str | None = None,
        label: str | None = None,
        **kwargs: Any,
    ) -> DataTable:
        """Create table from list of lists or list of dicts.

        Args:
            data: List of lists or list of dicts
            caption: Table caption
            label: Label for cross-references
            **kwargs: Additional DataTable arguments

        Returns:
            DataTable instance
        """
        return cls(data=data, caption=caption, label=label, **kwargs)

    def to_latex(self) -> str:
        """Convert to LaTeX table code.

        Returns:
            LaTeX table code as string
        """
        # Try pandas first
        try:
            import pandas as pd

            if isinstance(self.data, pd.DataFrame):
                return self._from_dataframe(self.data)
        except ImportError:
            pass

        # Handle list of dicts
        if isinstance(self.data, list) and self.data and isinstance(self.data[0], dict):
            return self._from_list_of_dicts(self.data)

        # Handle list of lists
        if isinstance(self.data, list):
            return self._from_list_of_lists(self.data)

        raise TypeError(
            f"Unsupported data type: {type(self.data)}. "
            "Expected pandas.DataFrame, list[dict], or list[list]."
        )

    def _from_dataframe(self, df: Any) -> str:
        """Generate LaTeX from pandas DataFrame."""
        import pandas as pd

        # Determine column format
        if self.column_format:
            col_fmt = self.column_format
        else:
            # Auto-detect: l for index, c for numbers, l for strings
            fmt_chars = []
            if self.index:
                fmt_chars.append("l")

            for dtype in df.dtypes:
                if pd.api.types.is_numeric_dtype(dtype):
                    fmt_chars.append("r")  # Right-align numbers
                else:
                    fmt_chars.append("l")  # Left-align text

            col_fmt = "".join(fmt_chars)

        # Build table
        lines = [r"\begin{table}[htbp]", r"\centering"]

        if self.caption:
            caption = escape_latex(self.caption)
            lines.append(f"\\caption{{{caption}}}")

        if self.label:
            from b8tex.templates.escape import sanitize_label
            safe_label = sanitize_label(self.label)
            lines.append(f"\\label{{{safe_label}}}")

        lines.append(f"\\begin{{tabular}}{{{col_fmt}}}")

        if self.use_booktabs:
            lines.append(r"\toprule")

        # Header row
        if self.header:
            headers = []
            if self.index:
                headers.append("")  # Empty for index column

            headers.extend(escape_latex(str(col)) for col in df.columns)
            lines.append(" & ".join(headers) + r" \\")

            if self.use_booktabs:
                lines.append(r"\midrule")
            else:
                lines.append(r"\hline")

        # Data rows
        for idx, row in df.iterrows():
            cells = []

            if self.index:
                cells.append(escape_latex(str(idx)))

            for value in row:
                if pd.isna(value):
                    cells.append("—")  # em dash for missing
                elif isinstance(value, (int, float)):
                    cells.append(f"{value:{self.float_format}}")
                else:
                    cells.append(escape_latex(str(value)))

            lines.append(" & ".join(cells) + r" \\")

        if self.use_booktabs:
            lines.append(r"\bottomrule")
        else:
            lines.append(r"\hline")

        lines.extend([r"\end{tabular}", r"\end{table}"])

        return "\n".join(lines)

    def _from_list_of_dicts(self, data: list[dict[str, Any]]) -> str:
        """Generate LaTeX from list of dictionaries."""
        if not data:
            return ""

        # Extract headers from first dict
        headers = list(data[0].keys())

        # Determine column format
        if self.column_format:
            col_fmt = self.column_format
        else:
            # Auto-detect based on first row values
            fmt_chars = []
            for key in headers:
                value = data[0][key]
                if isinstance(value, (int, float)):
                    fmt_chars.append("r")
                else:
                    fmt_chars.append("l")
            col_fmt = "".join(fmt_chars)

        # Build table
        lines = [r"\begin{table}[htbp]", r"\centering"]

        if self.caption:
            caption = escape_latex(self.caption)
            lines.append(f"\\caption{{{caption}}}")

        if self.label:
            from b8tex.templates.escape import sanitize_label
            safe_label = sanitize_label(self.label)
            lines.append(f"\\label{{{safe_label}}}")

        lines.append(f"\\begin{{tabular}}{{{col_fmt}}}")

        if self.use_booktabs:
            lines.append(r"\toprule")

        # Header row
        if self.header:
            header_cells = [escape_latex(str(h)) for h in headers]
            lines.append(" & ".join(header_cells) + r" \\")

            if self.use_booktabs:
                lines.append(r"\midrule")
            else:
                lines.append(r"\hline")

        # Data rows
        for row in data:
            cells = []
            for key in headers:
                value = row.get(key, "")
                if isinstance(value, (int, float)):
                    cells.append(f"{value:{self.float_format}}")
                else:
                    cells.append(escape_latex(str(value)))

            lines.append(" & ".join(cells) + r" \\")

        if self.use_booktabs:
            lines.append(r"\bottomrule")
        else:
            lines.append(r"\hline")

        lines.extend([r"\end{tabular}", r"\end{table}"])

        return "\n".join(lines)

    def _from_list_of_lists(self, data: list[list[Any]]) -> str:
        """Generate LaTeX from list of lists."""
        if not data:
            return ""

        # Determine column format
        if self.column_format:
            col_fmt = self.column_format
        else:
            # Auto-detect based on first data row (not header)
            data_row = data[1] if len(data) > 1 and self.header else data[0]
            fmt_chars = []
            for value in data_row:
                if isinstance(value, (int, float)):
                    fmt_chars.append("r")
                else:
                    fmt_chars.append("l")
            col_fmt = "".join(fmt_chars)

        # Build table
        lines = [r"\begin{table}[htbp]", r"\centering"]

        if self.caption:
            caption = escape_latex(self.caption)
            lines.append(f"\\caption{{{caption}}}")

        if self.label:
            from b8tex.templates.escape import sanitize_label
            safe_label = sanitize_label(self.label)
            lines.append(f"\\label{{{safe_label}}}")

        lines.append(f"\\begin{{tabular}}{{{col_fmt}}}")

        if self.use_booktabs:
            lines.append(r"\toprule")

        # Header row (if first row is header)
        start_idx = 0
        if self.header and data:
            header_cells = [escape_latex(str(cell)) for cell in data[0]]
            lines.append(" & ".join(header_cells) + r" \\")

            if self.use_booktabs:
                lines.append(r"\midrule")
            else:
                lines.append(r"\hline")

            start_idx = 1

        # Data rows
        for row in data[start_idx:]:
            cells = []
            for value in row:
                if isinstance(value, (int, float)):
                    cells.append(f"{value:{self.float_format}}")
                else:
                    cells.append(escape_latex(str(value)))

            lines.append(" & ".join(cells) + r" \\")

        if self.use_booktabs:
            lines.append(r"\bottomrule")
        else:
            lines.append(r"\hline")

        lines.extend([r"\end{tabular}", r"\end{table}"])

        return "\n".join(lines)


@dataclass
class PlotData:
    """Generate figure with embedded plot/image.

    Supports matplotlib figures and file paths to images.

    Attributes:
        source: matplotlib figure, Path to image, or InMemorySource
        caption: Figure caption
        label: Label for cross-references
        width: Figure width (LaTeX dimension, e.g., "0.8\\textwidth")
        placement: Figure placement specifier (e.g., "htbp")
    """

    source: Any  # matplotlib.figure.Figure | Path | InMemorySource
    caption: str | None = None
    label: str | None = None
    width: str = r"0.8\textwidth"
    placement: str = "htbp"

    @classmethod
    def from_matplotlib(
        cls,
        fig: Any,  # matplotlib.figure.Figure
        caption: str | None = None,
        label: str | None = None,
        **kwargs: Any,
    ) -> PlotData:
        """Create from matplotlib figure.

        Args:
            fig: matplotlib Figure object
            caption: Figure caption
            label: Label for cross-references
            **kwargs: Additional PlotData arguments

        Returns:
            PlotData instance
        """
        return cls(source=fig, caption=caption, label=label, **kwargs)

    @classmethod
    def from_path(
        cls,
        path: Path | str,
        caption: str | None = None,
        label: str | None = None,
        **kwargs: Any,
    ) -> PlotData:
        """Create from image file path.

        Args:
            path: Path to image file
            caption: Figure caption
            label: Label for cross-references
            **kwargs: Additional PlotData arguments

        Returns:
            PlotData instance
        """
        if isinstance(path, str):
            path = Path(path)
        return cls(source=path, caption=caption, label=label, **kwargs)

    def to_latex(self, save_path: Path | None = None) -> tuple[str, Path | None]:
        """Convert to LaTeX figure code.

        Args:
            save_path: Where to save matplotlib figure (if applicable)

        Returns:
            Tuple of (LaTeX code, saved file path if matplotlib figure)
        """
        # Handle matplotlib figure
        try:
            import matplotlib.figure

            if isinstance(self.source, matplotlib.figure.Figure):
                if save_path is None:
                    raise ValueError("save_path required for matplotlib figures")

                # Save figure
                self.source.savefig(save_path, bbox_inches="tight", dpi=300)
                image_path = save_path
            elif isinstance(self.source, Path):
                image_path = self.source
            else:
                raise TypeError(f"Unsupported source type: {type(self.source)}")
        except ImportError:
            # matplotlib not available
            if isinstance(self.source, Path):
                image_path = self.source
            else:
                raise TypeError(
                    "matplotlib not installed. Use Path for images or install matplotlib."
                )

        # Generate LaTeX
        lines = [f"\\begin{{figure}}[{self.placement}]", r"\centering"]

        # Image inclusion
        image_name = image_path.name
        lines.append(f"\\includegraphics[width={self.width}]{{{image_name}}}")

        if self.caption:
            caption = escape_latex(self.caption)
            lines.append(f"\\caption{{{caption}}}")

        if self.label:
            from b8tex.templates.escape import sanitize_label
            safe_label = sanitize_label(self.label)
            lines.append(f"\\label{{{safe_label}}}")

        lines.append(r"\end{figure}")

        latex_code = "\n".join(lines)
        return latex_code, image_path if isinstance(self.source, matplotlib.figure.Figure) else None
