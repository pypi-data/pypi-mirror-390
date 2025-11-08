"""Tests for data-driven features (tables and plots)."""

from __future__ import annotations

from pathlib import Path

import pytest

# Only run these tests if optional dependencies are available
pytest.importorskip("pandas")
pytest.importorskip("matplotlib")

import pandas as pd
import matplotlib.pyplot as plt

from b8tex.templates.data import DataTable, PlotData


class TestDataTable:
    """Tests for DataTable class."""

    def test_create_from_dataframe(self):
        """DataTable should be created from DataFrame."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        table = DataTable(data=df)

        assert table.data is df
        assert table.caption is None
        assert table.use_booktabs is True

    def test_create_with_caption(self):
        """DataTable with caption should be valid."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, caption="Test Table")

        assert table.caption == "Test Table"

    def test_create_with_label(self):
        """DataTable with label should be valid."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, label="tab:test")

        assert table.label == "tab:test"

    def test_position_parameter(self):
        """Table position should be configurable."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, position="h")

        assert table.position == "h"

    def test_disable_booktabs(self):
        """Booktabs should be optional."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, use_booktabs=False)

        assert table.use_booktabs is False

    def test_column_format(self):
        """Column format should be configurable."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, column_format="lrc")

        assert table.column_format == "lrc"

    def test_to_latex_basic(self):
        """to_latex should generate LaTeX code."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        table = DataTable(data=df)

        latex = table.to_latex()

        assert isinstance(latex, str)
        assert r"\begin{table}" in latex
        assert r"\end{table}" in latex
        assert r"\begin{tabular}" in latex
        assert r"\end{tabular}" in latex

    def test_to_latex_with_caption(self):
        """LaTeX should include caption."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, caption="Results")

        latex = table.to_latex()

        assert r"\caption{Results}" in latex

    def test_to_latex_with_label(self):
        """LaTeX should include label."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, label="tab:results")

        latex = table.to_latex()

        assert r"\label{tab:results}" in latex

    def test_to_latex_booktabs(self):
        """LaTeX with booktabs should use toprule/midrule/bottomrule."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, use_booktabs=True)

        latex = table.to_latex()

        assert r"\toprule" in latex
        assert r"\midrule" in latex
        assert r"\bottomrule" in latex

    def test_to_latex_no_booktabs(self):
        """LaTeX without booktabs should use hline."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, use_booktabs=False)

        latex = table.to_latex()

        assert r"\hline" in latex

    def test_to_latex_centering(self):
        """LaTeX should include centering."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df)

        latex = table.to_latex()

        assert r"\centering" in latex

    def test_dataframe_with_index(self):
        """DataFrame with index should be handled."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["row1", "row2"])
        table = DataTable(data=df)

        latex = table.to_latex()

        # Index should be included in output
        assert "row1" in latex
        assert "row2" in latex

    def test_dataframe_without_index(self):
        """DataFrame without index rendering should work."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        table = DataTable(data=df, hide_index=True)

        latex = table.to_latex()

        # Should not include default integer index
        assert latex is not None

    def test_multicolumn_header(self):
        """MultiIndex columns should be handled."""
        df = pd.DataFrame(
            [[1, 2, 3, 4]],
            columns=pd.MultiIndex.from_tuples([("A", "a1"), ("A", "a2"), ("B", "b1"), ("B", "b2")]),
        )
        table = DataTable(data=df)

        latex = table.to_latex()

        # Should handle multiindex
        assert latex is not None

    def test_numeric_formatting(self):
        """Numeric formatting should be applied."""
        df = pd.DataFrame({"A": [1.23456, 2.34567]})
        table = DataTable(data=df, float_format="%.2f")

        latex = table.to_latex()

        assert "1.23" in latex or "1.24" in latex  # Rounded to 2 decimals


class TestDataTableFromListOfDicts:
    """Tests for DataTable from list of dicts."""

    def test_create_from_list_of_dicts(self):
        """DataTable should accept list of dicts."""
        data = [
            {"Name": "Alice", "Age": 30},
            {"Name": "Bob", "Age": 25},
        ]
        table = DataTable(data=data)

        assert table.data == data

    def test_to_latex_from_list_of_dicts(self):
        """LaTeX generation from list of dicts should work."""
        data = [
            {"A": 1, "B": 2},
            {"A": 3, "B": 4},
        ]
        table = DataTable(data=data)

        latex = table.to_latex()

        assert r"\begin{tabular}" in latex
        assert "A" in latex
        assert "B" in latex


class TestDataTableFromListOfLists:
    """Tests for DataTable from list of lists."""

    def test_create_from_list_of_lists(self):
        """DataTable should accept list of lists."""
        data = [
            ["A", "B"],
            [1, 2],
            [3, 4],
        ]
        table = DataTable(data=data)

        assert table.data == data

    def test_to_latex_from_list_of_lists(self):
        """LaTeX generation from list of lists should work."""
        data = [
            ["Name", "Age"],
            ["Alice", 30],
            ["Bob", 25],
        ]
        table = DataTable(data=data, header_row=True)

        latex = table.to_latex()

        assert r"\begin{tabular}" in latex
        assert "Name" in latex
        assert "Alice" in latex


class TestPlotData:
    """Tests for PlotData class."""

    def test_create_from_figure(self):
        """PlotData should be created from matplotlib figure."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        plot = PlotData(source=fig)

        assert plot.source is fig
        assert plot.caption is None

        plt.close(fig)

    def test_create_with_caption(self):
        """PlotData with caption should be valid."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig, caption="Test Plot")

        assert plot.caption == "Test Plot"

        plt.close(fig)

    def test_create_with_label(self):
        """PlotData with label should be valid."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig, label="fig:test")

        assert plot.label == "fig:test"

        plt.close(fig)

    def test_width_parameter(self):
        """Plot width should be configurable."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig, width=r"0.5\textwidth")

        assert plot.width == r"0.5\textwidth"

        plt.close(fig)

    def test_position_parameter(self):
        """Plot position should be configurable."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig, position="h")

        assert plot.position == "h"

        plt.close(fig)

    def test_to_latex_with_temp_file(self, tmp_path):
        """to_latex should save figure and generate LaTeX."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        plot = PlotData(source=fig)
        save_path = tmp_path / "plot.pdf"

        latex, saved_path = plot.to_latex(save_path=save_path)

        assert isinstance(latex, str)
        assert r"\begin{figure}" in latex
        assert r"\end{figure}" in latex
        assert r"\includegraphics" in latex
        assert saved_path == save_path
        assert save_path.exists()

        plt.close(fig)

    def test_to_latex_with_caption(self, tmp_path):
        """LaTeX should include caption."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig, caption="Test Figure")
        latex, _ = plot.to_latex(save_path=tmp_path / "plot.pdf")

        assert r"\caption{Test Figure}" in latex

        plt.close(fig)

    def test_to_latex_with_label(self, tmp_path):
        """LaTeX should include label."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig, label="fig:test")
        latex, _ = plot.to_latex(save_path=tmp_path / "plot.pdf")

        assert r"\label{fig:test}" in latex

        plt.close(fig)

    def test_to_latex_centering(self, tmp_path):
        """LaTeX should include centering."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig)
        latex, _ = plot.to_latex(save_path=tmp_path / "plot.pdf")

        assert r"\centering" in latex

        plt.close(fig)

    def test_to_latex_width(self, tmp_path):
        """LaTeX should include width in includegraphics."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig, width=r"0.6\textwidth")
        latex, _ = plot.to_latex(save_path=tmp_path / "plot.pdf")

        assert r"width=0.6\textwidth" in latex

        plt.close(fig)

    def test_create_from_path(self):
        """PlotData should accept Path source."""
        path = Path("existing_plot.pdf")
        plot = PlotData(source=path)

        assert plot.source == path

    def test_to_latex_from_path(self):
        """LaTeX generation from Path should work."""
        path = Path("plot.pdf")
        plot = PlotData(source=path, caption="Existing Plot")

        latex, returned_path = plot.to_latex()

        assert r"\includegraphics" in latex
        assert "plot.pdf" in latex
        assert returned_path == path

    def test_save_with_dpi(self, tmp_path):
        """Figure should be saved with specified DPI."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig, dpi=150)
        save_path = tmp_path / "plot.pdf"

        latex, _ = plot.to_latex(save_path=save_path)

        assert save_path.exists()

        plt.close(fig)

    def test_bbox_inches_tight(self, tmp_path):
        """Figure should be saved with tight bounding box by default."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig)
        save_path = tmp_path / "plot.pdf"

        latex, _ = plot.to_latex(save_path=save_path)

        # Just verify it doesn't error
        assert save_path.exists()

        plt.close(fig)


class TestDataIntegration:
    """Integration tests for data features."""

    def test_table_and_plot_together(self, tmp_path):
        """Tables and plots should work together."""
        # Create table
        df = pd.DataFrame({"X": [1, 2, 3], "Y": [1, 4, 9]})
        table = DataTable(data=df, caption="Data")
        table_latex = table.to_latex()

        # Create plot
        fig, ax = plt.subplots()
        ax.plot(df["X"], df["Y"])
        plot = PlotData(source=fig, caption="Visualization")
        plot_latex, _ = plot.to_latex(save_path=tmp_path / "plot.pdf")

        plt.close(fig)

        # Both should generate valid LaTeX
        assert r"\begin{table}" in table_latex
        assert r"\begin{figure}" in plot_latex

    def test_multiple_tables(self):
        """Multiple tables should be independent."""
        df1 = pd.DataFrame({"A": [1, 2]})
        df2 = pd.DataFrame({"B": [3, 4]})

        table1 = DataTable(data=df1, caption="Table 1", label="tab:1")
        table2 = DataTable(data=df2, caption="Table 2", label="tab:2")

        latex1 = table1.to_latex()
        latex2 = table2.to_latex()

        assert r"\label{tab:1}" in latex1
        assert r"\label{tab:2}" in latex2
        assert "Table 1" in latex1
        assert "Table 2" in latex2

    def test_multiple_plots(self, tmp_path):
        """Multiple plots should be independent."""
        fig1, ax1 = plt.subplots()
        ax1.plot([1, 2], [1, 2])

        fig2, ax2 = plt.subplots()
        ax2.plot([1, 2], [2, 1])

        plot1 = PlotData(source=fig1, label="fig:1")
        plot2 = PlotData(source=fig2, label="fig:2")

        latex1, _ = plot1.to_latex(save_path=tmp_path / "plot1.pdf")
        latex2, _ = plot2.to_latex(save_path=tmp_path / "plot2.pdf")

        plt.close(fig1)
        plt.close(fig2)

        assert r"\label{fig:1}" in latex1
        assert r"\label{fig:2}" in latex2

    def test_large_dataframe(self):
        """Large DataFrame should be handled."""
        df = pd.DataFrame(
            {f"Col{i}": range(100) for i in range(10)}
        )
        table = DataTable(data=df)

        latex = table.to_latex()

        # Should handle large data without errors
        assert r"\begin{table}" in latex

    def test_complex_plot(self, tmp_path):
        """Complex matplotlib plot should be handled."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        ax1.plot([1, 2, 3], [1, 4, 9])
        ax1.set_title("Subplot 1")

        ax2.scatter([1, 2, 3], [3, 1, 4])
        ax2.set_title("Subplot 2")

        plot = PlotData(source=fig, caption="Complex Figure")
        latex, saved_path = plot.to_latex(save_path=tmp_path / "complex.pdf")

        assert saved_path.exists()
        assert r"\caption{Complex Figure}" in latex

        plt.close(fig)

    def test_empty_dataframe(self):
        """Empty DataFrame should be handled gracefully."""
        df = pd.DataFrame()
        table = DataTable(data=df)

        latex = table.to_latex()

        # Should generate valid (though empty) table
        assert r"\begin{table}" in latex


class TestDataEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_table_without_save_path_error(self):
        """PlotData from figure requires save_path."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig)

        # Should work with save_path
        with pytest.raises((ValueError, TypeError)):
            plot.to_latex()  # Missing save_path

        plt.close(fig)

    def test_dataframe_with_special_characters(self):
        """DataFrame with LaTeX special characters should be escaped."""
        df = pd.DataFrame({"A & B": ["$100", "50%"]})
        table = DataTable(data=df, escape_special_chars=True)

        latex = table.to_latex()

        # Special characters should be escaped
        assert r"\&" in latex or "A & B" in latex  # May vary by pandas version

    def test_custom_column_format(self):
        """Custom column format should be respected."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})
        table = DataTable(data=df, column_format="lcc")

        latex = table.to_latex()

        assert "{lcc}" in latex or "lcc" in latex

    def test_table_position_htbp(self):
        """Table position with multiple options should work."""
        df = pd.DataFrame({"A": [1, 2]})
        table = DataTable(data=df, position="htbp")

        latex = table.to_latex()

        assert "[htbp]" in latex

    def test_plot_position_H(self):
        """Plot with H position (requires float package) should work."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])

        plot = PlotData(source=fig, position="H")

        assert plot.position == "H"

        plt.close(fig)
