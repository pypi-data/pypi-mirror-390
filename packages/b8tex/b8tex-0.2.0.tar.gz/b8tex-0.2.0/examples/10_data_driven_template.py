#!/usr/bin/env python3
"""Example 10: Data-Driven Template Documents

This example demonstrates the most advanced features of B8TeX templates:
- Pandas DataFrames → LaTeX tables
- Matplotlib figures → embedded PDF plots
- Automatic formatting with booktabs
- Data-driven content generation
- Mixed content (data + text + equations)

Perfect for:
- Research reports with experimental data
- Technical documentation with plots
- Automated report generation pipelines
"""

from pathlib import Path

import b8tex
from b8tex.templates import DocumentBuilder

# Import optional dependencies
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    HAS_DATA_DEPS = True
except ImportError:
    HAS_DATA_DEPS = False
    print("Warning: pandas and matplotlib not installed. Install with:")
    print("  uv pip install 'b8tex[templates]'")

# Configure logging
b8tex.configure_logging(level=20)


def create_sample_data():
    """Generate sample experimental data."""
    # Training metrics over epochs
    epochs = list(range(1, 11))
    train_acc = [0.45, 0.62, 0.74, 0.81, 0.86, 0.89, 0.91, 0.93, 0.94, 0.95]
    val_acc = [0.42, 0.59, 0.70, 0.77, 0.81, 0.84, 0.86, 0.87, 0.88, 0.88]
    train_loss = [1.5, 1.1, 0.8, 0.6, 0.45, 0.35, 0.28, 0.22, 0.18, 0.15]

    # Model comparison
    models = ["ResNet-18", "ResNet-34", "ResNet-50", "EfficientNet-B0"]
    accuracy = [94.2, 95.8, 96.5, 96.9]
    params_m = [11.7, 21.8, 25.6, 5.3]  # millions of parameters
    inference_ms = [15, 22, 28, 18]  # milliseconds

    return {
        "epochs": epochs,
        "train_acc": train_acc,
        "val_acc": val_acc,
        "train_loss": train_loss,
        "models": models,
        "accuracy": accuracy,
        "params": params_m,
        "inference": inference_ms,
    }


def build_data_driven_report():
    """Build a complete report with tables and plots from data."""
    if not HAS_DATA_DEPS:
        print("\n✗ Skipping: pandas and matplotlib required")
        return None

    print("\n" + "=" * 70)
    print("Building Data-Driven Report")
    print("=" * 70)

    # Generate sample data
    data = create_sample_data()

    with DocumentBuilder(
        template="neurips",
        title="Experimental Results: Deep Learning Model Comparison",
        status="final",
        organization="ML Research Lab",
        doc_type="Technical Report",
    ) as builder:

        # Authors
        builder.add_author("Data Scientist", affiliation="Research Lab")

        # Abstract
        builder.set_abstract(
            """
            We compare several deep learning architectures on image classification
            tasks. Our experiments show that EfficientNet-B0 achieves the best
            trade-off between accuracy and efficiency. All results include
            training curves, model comparisons, and ablation studies.
            """
        )

        # Keywords
        builder.add_keyword("deep learning")
        builder.add_keyword("model comparison")
        builder.add_keyword("image classification")

        # Introduction
        with builder.section("Introduction"):
            builder.add_paragraph(
                """
                Selecting the right deep learning architecture is crucial for
                balancing accuracy, efficiency, and deployment constraints.
                This report presents comprehensive experimental results comparing
                four popular architectures.
                """
            )

        # Experimental Setup
        with builder.section("Experimental Setup"):
            with builder.subsection("Dataset"):
                builder.add_text(
                    """
                    We use the CIFAR-10 dataset with standard train/val split.
                    All models are trained for 100 epochs with the Adam optimizer.
                    """
                )

            with builder.subsection("Models Evaluated"):
                # Create DataFrame for model specifications
                model_df = pd.DataFrame(
                    {
                        "Model": data["models"],
                        "Parameters (M)": data["params"],
                        "Inference (ms)": data["inference"],
                    }
                )

                builder.add_text(
                    """
                    Table~\\ref{tab:models} summarizes the models evaluated in this study.
                    """
                )

                # Add table directly from DataFrame
                builder.add_table(
                    model_df,
                    caption="Model specifications and computational requirements.",
                    label="tab:models",
                )

        # Results Section with Plots
        with builder.section("Results"):
            with builder.subsection("Training Dynamics"):
                builder.add_paragraph(
                    """
                    Figure~\\ref{fig:training} shows the training and validation
                    accuracy curves across epochs for a representative model (ResNet-50).
                    """
                )

                # Create training plot
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

                # Accuracy plot
                ax1.plot(data["epochs"], data["train_acc"], "b-", label="Train", linewidth=2)
                ax1.plot(data["epochs"], data["val_acc"], "r--", label="Validation", linewidth=2)
                ax1.set_xlabel("Epoch")
                ax1.set_ylabel("Accuracy")
                ax1.set_title("Model Accuracy")
                ax1.legend()
                ax1.grid(True, alpha=0.3)

                # Loss plot
                ax2.plot(data["epochs"], data["train_loss"], "g-", linewidth=2)
                ax2.set_xlabel("Epoch")
                ax2.set_ylabel("Loss")
                ax2.set_title("Training Loss")
                ax2.grid(True, alpha=0.3)

                plt.tight_layout()

                # Add plot to document
                builder.add_plot(
                    fig,
                    caption="Training and validation metrics across epochs.",
                    label="fig:training",
                    width=r"0.9\textwidth",
                )

                plt.close(fig)

            with builder.subsection("Model Comparison"):
                builder.add_paragraph(
                    """
                    Table~\\ref{tab:comparison} presents the final test accuracy
                    for each model. EfficientNet-B0 achieves the best balance
                    between accuracy and parameter count.
                    """
                )

                # Create comparison DataFrame
                comparison_df = pd.DataFrame(
                    {
                        "Model": data["models"],
                        "Test Accuracy (%)": data["accuracy"],
                        "Parameters (M)": data["params"],
                        "Inference Time (ms)": data["inference"],
                    }
                )

                builder.add_table(
                    comparison_df,
                    caption="Comparison of model performance metrics.",
                    label="tab:comparison",
                    use_booktabs=True,  # Professional table style
                )

                # Add bar chart
                fig, ax = plt.subplots(figsize=(10, 5))
                x = np.arange(len(data["models"]))
                width = 0.35

                bars1 = ax.bar(
                    x - width / 2, data["accuracy"], width, label="Accuracy (%)", alpha=0.8
                )
                bars2 = ax.bar(
                    x + width / 2, data["inference"], width, label="Inference (ms)", alpha=0.8
                )

                ax.set_xlabel("Model")
                ax.set_title("Model Performance Comparison")
                ax.set_xticks(x)
                ax.set_xticklabels(data["models"], rotation=15, ha="right")
                ax.legend()
                ax.grid(True, axis="y", alpha=0.3)

                plt.tight_layout()

                builder.add_plot(
                    fig,
                    caption="Visual comparison of accuracy and inference time.",
                    label="fig:comparison",
                )

                plt.close(fig)

        # Discussion with template variables
        with builder.section("Discussion"):
            builder.set_variable("best_model", "EfficientNet-B0")
            builder.set_variable("best_accuracy", 96.9)
            builder.set_variable("param_count", 5.3)

            builder.add_paragraph(
                """
                Our experiments demonstrate that {{ best_model }} achieves
                {{ best_accuracy }}\\% accuracy with only {{ param_count }}M
                parameters, making it the most efficient choice for
                deployment scenarios with limited computational resources.
                """
            )

            with builder.subsection("Key Findings"):
                builder.add_text(
                    r"""
                    \begin{itemize}
                    \item Larger models (ResNet-50) provide marginal accuracy gains
                    \item EfficientNet's compound scaling is highly effective
                    \item Inference time scales roughly linearly with parameter count
                    \item All models achieve > 94\% accuracy on this task
                    \end{itemize}
                    """
                )

        # Conclusion
        with builder.section("Conclusion"):
            builder.add_paragraph(
                """
                This study provides comprehensive experimental evidence for model
                selection in image classification tasks. The data-driven approach,
                combining quantitative metrics with visual analysis, enables
                informed decision-making for production deployments.
                """
            )

        # Build document
        doc = builder.build()

    print(f"\n  Document structure:")
    print(f"    - Sections: {len(doc.sections)}")
    print(f"    - Authors: {len(doc.authors) if doc.authors else 0}")
    print(f"    - Keywords: {len(doc.keywords) if doc.keywords else 0}")

    # Compile to PDF
    result = b8tex.compile_template_document(
        doc,
        output_name="data_driven_report",
        validate=True,
    )

    print(f"\n✓ Compilation successful!")
    print(f"  Output: {result.pdf_path}")
    print(f"  Duration: {result.elapsed:.2f}s")
    print(f"  Size: {result.pdf_path.stat().st_size / 1024:.1f} KB")

    return result


def demonstrate_table_features():
    """Show various table formatting options."""
    if not HAS_DATA_DEPS:
        return

    print("\n" + "=" * 70)
    print("Table Formatting Options")
    print("=" * 70)

    from b8tex.templates import DataTable

    # Create sample DataFrame
    df = pd.DataFrame(
        {
            "Method": ["Baseline", "Improved", "Advanced"],
            "Accuracy": [85.2, 92.7, 95.1],
            "F1-Score": [0.83, 0.91, 0.94],
        }
    )

    # Option 1: Booktabs style (professional)
    table1 = DataTable(
        data=df,
        caption="Results with booktabs style (default)",
        label="tab:booktabs",
        use_booktabs=True,
    )

    # Option 2: Classic LaTeX table
    table2 = DataTable(
        data=df,
        caption="Results with classic style",
        label="tab:classic",
        use_booktabs=False,
    )

    # Option 3: Custom formatting
    table3 = DataTable(
        data=df,
        caption="Results with custom formatting",
        label="tab:custom",
        use_booktabs=True,
        column_format="lcc",  # left-aligned first column, centered others
        position="h",  # "here" placement
    )

    print("\n✓ Created 3 table variations")
    print("  - Booktabs (professional)")
    print("  - Classic LaTeX")
    print("  - Custom column formatting")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("B8TeX Template Example - Data-Driven Documents")
    print("=" * 70)

    if not HAS_DATA_DEPS:
        print("\n✗ This example requires pandas and matplotlib")
        print("Install with: uv pip install 'b8tex[templates]'")
        return

    try:
        # Build complete data-driven report
        build_data_driven_report()

        # Show table options
        demonstrate_table_features()

        print("\n" + "=" * 70)
        print("Example completed successfully!")
        print("=" * 70)
        print("\nThis example demonstrated:")
        print("  ✓ Pandas DataFrame → LaTeX tables")
        print("  ✓ Matplotlib figures → embedded PDF plots")
        print("  ✓ Automatic table formatting (booktabs)")
        print("  ✓ Mixed content (data + text + equations)")
        print("  ✓ Template variables in data context")
        print("\nData-driven templates enable:")
        print("  - Automated report generation")
        print("  - Reproducible research documents")
        print("  - Real-time monitoring dashboards")
        print("  - Experiment tracking and comparison")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
