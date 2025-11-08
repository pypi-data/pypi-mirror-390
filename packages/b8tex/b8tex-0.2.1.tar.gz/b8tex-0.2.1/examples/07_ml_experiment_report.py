"""
Machine Learning Experiment Report Generator

Demonstrates B8TeX's capabilities for creating professional ML experiment reports
with multiple source files, data tables, and plots.

This example showcases:
- Multi-file project structure
- Data-driven table generation with tabularx
- Training curves with pgfplots
- Confusion matrices and metrics tables
- Professional scientific document formatting

Requirements:
    pip install b8tex numpy
"""

import shutil
import tempfile
from pathlib import Path

import numpy as np

from b8tex import TectonicCompiler, Document, Resource, OutputFormat


def generate_training_data() -> str:
    """Generate synthetic training metrics data."""
    np.random.seed(42)
    epochs = 50

    # Simulate training metrics with realistic curves
    train_loss = 2.5 * np.exp(-0.08 * np.arange(epochs)) + 0.1 + np.random.normal(0, 0.02, epochs)
    val_loss = 2.7 * np.exp(-0.07 * np.arange(epochs)) + 0.15 + np.random.normal(0, 0.03, epochs)
    train_acc = (1 - np.exp(-0.1 * np.arange(epochs))) * 0.95 + np.random.normal(0, 0.01, epochs)
    val_acc = (1 - np.exp(-0.09 * np.arange(epochs))) * 0.92 + np.random.normal(0, 0.015, epochs)

    # Format as CSV
    lines = ["epoch,train_loss,val_loss,train_acc,val_acc"]
    for i in range(epochs):
        lines.append(
            f"{i+1},{train_loss[i]:.4f},{val_loss[i]:.4f},"
            f"{train_acc[i]:.4f},{val_acc[i]:.4f}"
        )

    return "\n".join(lines)


def generate_confusion_matrix() -> str:
    """Generate confusion matrix data."""
    # 5-class classification results
    matrix = [
        [892, 15, 8, 5, 12],   # True class 0
        [18, 1045, 22, 8, 7],  # True class 1
        [12, 19, 978, 18, 5],  # True class 2
        [8, 11, 15, 1012, 24], # True class 3
        [14, 6, 9, 21, 950],   # True class 4
    ]

    return "\n".join([" & ".join(map(str, row)) + " \\\\" for row in matrix])


def create_report_files(work_dir: Path) -> Document:
    """Create all files for the ML experiment report."""

    # Main document
    main_tex = r"""
\documentclass[11pt,a4paper]{article}

% Packages
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{xcolor}
\usepackage{pgfplots}
\usepackage{pgfplotstable}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{hyperref}

\pgfplotsset{compat=1.18}
\usepgfplotslibrary{groupplots}

% Custom colors
\definecolor{traincolor}{RGB}{31, 119, 180}
\definecolor{valcolor}{RGB}{255, 127, 14}
\definecolor{accentcolor}{RGB}{44, 160, 44}

% Metadata
\title{Image Classification Experiment Report\\
       \large ResNet-50 on CIFAR-10 Dataset}
\author{B8TeX ML Lab\\
        \texttt{experiments@b8tex.org}}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
This report presents the results of training a ResNet-50 model on the CIFAR-10 dataset.
We evaluate the model's performance across 50 epochs, analyzing training dynamics,
convergence behavior, and final classification accuracy. The model achieved 92.3\%
validation accuracy with minimal overfitting, demonstrating effective regularization.
\end{abstract}

\section{Introduction}

Deep convolutional neural networks have revolutionized image classification tasks.
This experiment evaluates the ResNet-50 architecture~\cite{he2016deep} on the
CIFAR-10 dataset~\cite{krizhevsky2009learning}, a standard benchmark consisting
of 60,000 32×32 color images across 10 classes.

\subsection{Research Questions}

\begin{enumerate}
    \item How does the model's training loss converge over 50 epochs?
    \item What is the gap between training and validation performance?
    \item Which classes are most frequently confused?
    \item How does data augmentation affect generalization?
\end{enumerate}

\section{Experimental Setup}

\subsection{Model Architecture}

We use the ResNet-50 architecture with the following specifications:

\begin{table}[h]
\centering
\caption{ResNet-50 Configuration}
\begin{tabularx}{0.8\textwidth}{lX}
\toprule
\textbf{Component} & \textbf{Configuration} \\
\midrule
Input Size & $32 \times 32 \times 3$ \\
Convolutional Blocks & 4 residual blocks with [3,4,6,3] layers \\
Channels & [64, 128, 256, 512] \\
Pooling & Global Average Pooling \\
Output Layer & 10-way softmax classifier \\
Total Parameters & 23.5M parameters \\
\bottomrule
\end{tabularx}
\label{tab:architecture}
\end{table}

\input{hyperparameters}

\subsection{Dataset}

The CIFAR-10 dataset consists of 50,000 training images and 10,000 test images
distributed across 10 classes: airplane, automobile, bird, cat, deer, dog, frog,
horse, ship, and truck. We apply standard data augmentation including random crops,
horizontal flips, and color jittering.

\section{Training Dynamics}

Figure~\ref{fig:training_curves} shows the evolution of loss and accuracy metrics
throughout training. The model converges smoothly with minimal oscillation,
indicating stable optimization.

\input{training_plots}

\subsection{Convergence Analysis}

The training loss decreases exponentially in the early epochs, reaching near-asymptotic
values by epoch 30. The validation loss follows a similar trajectory with a consistent
gap of approximately 0.05, suggesting well-controlled overfitting through dropout
(p=0.5) and weight decay ($\lambda=5 \times 10^{-4}$).

\section{Performance Evaluation}

\subsection{Final Metrics}

Table~\ref{tab:metrics} presents the comprehensive performance metrics on the test set.

\begin{table}[h]
\centering
\caption{Test Set Performance Metrics}
\begin{tabularx}{0.9\textwidth}{lcccc}
\toprule
\textbf{Metric} & \textbf{Train} & \textbf{Validation} & \textbf{Test} & \textbf{Target} \\
\midrule
Accuracy & 95.2\% & 92.3\% & 91.8\% & $\geq$ 90\% \\
Top-5 Accuracy & 99.8\% & 99.2\% & 99.1\% & $\geq$ 95\% \\
F1 Score (Macro) & 0.952 & 0.923 & 0.918 & $\geq$ 0.90 \\
Precision (Macro) & 0.954 & 0.925 & 0.920 & $\geq$ 0.90 \\
Recall (Macro) & 0.951 & 0.921 & 0.916 & $\geq$ 0.90 \\
\midrule
Inference Time & \multicolumn{3}{c}{12.3 ms/image (GPU)} & $\leq$ 20 ms \\
\bottomrule
\end{tabularx}
\label{tab:metrics}
\end{table}

\subsection{Per-Class Performance}

\input{class_metrics}

\subsection{Confusion Matrix Analysis}

Figure~\ref{fig:confusion_matrix} presents the confusion matrix for the test set,
revealing interesting error patterns.

\input{confusion_matrix}

Notable observations:
\begin{itemize}
    \item \textbf{Cat vs. Dog}: 42 cat images misclassified as dogs, and 38 dogs as cats
    \item \textbf{Automobile vs. Truck}: 28 confusions, likely due to similar shapes
    \item \textbf{Bird vs. Airplane}: 19 confusions, possibly due to sky backgrounds
\end{itemize}

\section{Ablation Studies}

We conducted ablation studies to understand the contribution of various components:

\begin{table}[h]
\centering
\caption{Ablation Study Results}
\begin{tabularx}{\textwidth}{Xcc}
\toprule
\textbf{Configuration} & \textbf{Val Acc} & \textbf{$\Delta$} \\
\midrule
Full model (baseline) & 92.3\% & --- \\
w/o data augmentation & 88.7\% & -3.6\% \\
w/o dropout & 90.1\% & -2.2\% \\
w/o weight decay & 89.4\% & -2.9\% \\
w/o batch normalization & 85.2\% & -7.1\% \\
ResNet-34 (fewer layers) & 90.8\% & -1.5\% \\
ResNet-101 (more layers) & 92.9\% & +0.6\% \\
\bottomrule
\end{tabularx}
\label{tab:ablation}
\end{table}

\section{Computational Resources}

The experiment utilized the following resources:

\begin{table}[h]
\centering
\caption{Resource Utilization}
\begin{tabularx}{0.8\textwidth}{lX}
\toprule
\textbf{Resource} & \textbf{Details} \\
\midrule
GPU & NVIDIA A100 (40GB) \\
Training Time & 3.2 hours (50 epochs) \\
Peak Memory & 18.4 GB \\
Batch Size & 128 images \\
Gradient Steps & 19,532 steps \\
Power Consumption & $\sim$850W average \\
\bottomrule
\end{tabularx}
\label{tab:resources}
\end{table}

\section{Conclusions}

This experiment successfully trained a ResNet-50 model achieving 91.8\% test accuracy
on CIFAR-10, exceeding our target of 90\%. Key findings include:

\begin{enumerate}
    \item Batch normalization provides the largest performance contribution (+7.1\%)
    \item Data augmentation significantly improves generalization (+3.6\%)
    \item The model shows minimal overfitting (2.9\% train-val gap)
    \item Cat/dog confusion remains the primary error mode
\end{enumerate}

\subsection{Future Work}

Potential improvements for future experiments:
\begin{itemize}
    \item Incorporate attention mechanisms for better feature discrimination
    \item Apply mixup or cutmix augmentation strategies
    \item Explore ensemble methods combining multiple architectures
    \item Implement class-balanced sampling for imbalanced scenarios
\end{itemize}

\begin{thebibliography}{99}

\bibitem{he2016deep}
He, K., Zhang, X., Ren, S., \& Sun, J. (2016).
Deep residual learning for image recognition.
In \textit{CVPR}, pp. 770--778.

\bibitem{krizhevsky2009learning}
Krizhevsky, A., \& Hinton, G. (2009).
Learning multiple layers of features from tiny images.
Technical report, University of Toronto.

\end{thebibliography}

\appendix

\section{Hyperparameter Search}

We performed a grid search over learning rates $\{10^{-4}, 10^{-3}, 10^{-2}\}$ and
batch sizes $\{64, 128, 256\}$. The optimal configuration (learning rate=$10^{-3}$,
batch size=128) was selected based on validation performance.

\section{Reproducibility}

Complete code and trained model weights are available at:
\texttt{https://github.com/b8tex-ml/cifar10-resnet50}

Random seed: 42 | Framework: PyTorch 2.0 | CUDA: 12.1

\end{document}
"""

    # Hyperparameters section
    hyperparams_tex = r"""
\subsection{Training Hyperparameters}

\begin{table}[h]
\centering
\caption{Hyperparameters Used for Training}
\begin{tabularx}{0.85\textwidth}{lX}
\toprule
\textbf{Hyperparameter} & \textbf{Value} \\
\midrule
Optimizer & Adam with AMSGrad \\
Learning Rate & $10^{-3}$ with cosine annealing \\
Batch Size & 128 \\
Weight Decay & $5 \times 10^{-4}$ \\
Dropout Rate & 0.5 \\
Label Smoothing & 0.1 \\
Gradient Clipping & max norm = 1.0 \\
Warmup Epochs & 5 \\
Total Epochs & 50 \\
\bottomrule
\end{tabularx}
\label{tab:hyperparams}
\end{table}
"""

    # Training plots section
    training_plots_tex = r"""
\begin{figure}[htbp]
\centering
\begin{tikzpicture}
\begin{groupplot}[
    group style={
        group size=2 by 1,
        horizontal sep=2cm,
    },
    width=0.48\textwidth,
    height=0.35\textwidth,
    xlabel={Epoch},
    grid=major,
    legend pos=north east,
    tick label style={font=\small},
    label style={font=\small},
    legend style={font=\footnotesize},
]

% Loss plot
\nextgroupplot[
    ylabel={Loss},
    ymin=0, ymax=3,
    title={Training and Validation Loss},
]
\addplot[traincolor, thick, mark=*, mark size=0.5pt]
    table[x=epoch, y=train_loss, col sep=comma] {training_data.csv};
\addplot[valcolor, thick, mark=square*, mark size=0.5pt]
    table[x=epoch, y=val_loss, col sep=comma] {training_data.csv};
\legend{Training, Validation}

% Accuracy plot
\nextgroupplot[
    ylabel={Accuracy},
    ymin=0, ymax=1,
    title={Training and Validation Accuracy},
]
\addplot[traincolor, thick, mark=*, mark size=0.5pt]
    table[x=epoch, y=train_acc, col sep=comma] {training_data.csv};
\addplot[valcolor, thick, mark=square*, mark size=0.5pt]
    table[x=epoch, y=val_acc, col sep=comma] {training_data.csv};
\legend{Training, Validation}

\end{groupplot}
\end{tikzpicture}
\caption{Evolution of loss and accuracy metrics during training. Both metrics show
smooth convergence with validation performance closely tracking training, indicating
effective regularization.}
\label{fig:training_curves}
\end{figure}
"""

    # Class-wise metrics
    class_metrics_tex = r"""
\begin{table}[h]
\centering
\caption{Per-Class Performance Metrics}
\begin{tabularx}{\textwidth}{Xcccc}
\toprule
\textbf{Class} & \textbf{Precision} & \textbf{Recall} & \textbf{F1-Score} & \textbf{Support} \\
\midrule
Airplane   & 0.935 & 0.925 & 0.930 & 1000 \\
Automobile & 0.968 & 0.972 & 0.970 & 1000 \\
Bird       & 0.885 & 0.892 & 0.888 & 1000 \\
Cat        & 0.812 & 0.798 & 0.805 & 1000 \\
Deer       & 0.918 & 0.905 & 0.911 & 1000 \\
Dog        & 0.874 & 0.883 & 0.878 & 1000 \\
Frog       & 0.942 & 0.958 & 0.950 & 1000 \\
Horse      & 0.951 & 0.946 & 0.948 & 1000 \\
Ship       & 0.968 & 0.975 & 0.971 & 1000 \\
Truck      & 0.947 & 0.945 & 0.946 & 1000 \\
\midrule
\textbf{Macro Avg} & \textbf{0.920} & \textbf{0.916} & \textbf{0.918} & \textbf{10000} \\
\textbf{Weighted Avg} & \textbf{0.920} & \textbf{0.918} & \textbf{0.918} & \textbf{10000} \\
\bottomrule
\end{tabularx}
\label{tab:class_metrics}
\end{table}

The cat class shows the lowest performance (F1=0.805), primarily due to confusion
with dogs. Automobile and ship classes achieve the highest scores ($>$0.97), likely
due to their distinctive shapes and colors.
"""

    # Confusion matrix visualization
    confusion_matrix_tex = r"""
\begin{figure}[htbp]
\centering
\begin{tikzpicture}
    \begin{axis}[
        colormap/viridis,
        colorbar,
        colorbar style={
            ylabel={Count},
        },
        width=0.7\textwidth,
        height=0.7\textwidth,
        xlabel={Predicted Class},
        ylabel={True Class},
        xtick={0,1,2,3,4,5,6,7,8,9},
        ytick={0,1,2,3,4,5,6,7,8,9},
        xticklabels={Air,Auto,Bird,Cat,Deer,Dog,Frog,Horse,Ship,Truck},
        yticklabels={Air,Auto,Bird,Cat,Deer,Dog,Frog,Horse,Ship,Truck},
        x tick label style={rotate=45, anchor=east, font=\small},
        y tick label style={font=\small},
        enlargelimits=false,
        axis on top,
    ]
    \addplot[
        matrix plot*,
        point meta=explicit,
        mesh/cols=10,
    ] table[meta=C] {
        x y C
        0 0 925
        1 0 8
        2 0 15
        3 0 12
        4 0 8
        5 0 18
        6 0 3
        7 0 5
        8 0 4
        9 0 2

        0 1 5
        1 1 972
        2 1 3
        3 1 2
        4 1 1
        5 1 4
        6 1 1
        7 1 2
        8 1 8
        9 1 2

        0 2 19
        1 2 2
        2 2 892
        3 2 28
        4 2 18
        5 2 22
        6 2 12
        7 2 4
        8 2 2
        9 2 1

        0 3 8
        1 3 3
        2 3 31
        3 3 798
        4 3 42
        5 3 38
        6 3 58
        7 3 18
        8 3 2
        9 3 2

        0 4 12
        1 4 1
        2 4 22
        3 4 35
        4 4 905
        5 4 8
        6 4 9
        7 4 6
        8 4 1
        9 4 1

        0 5 6
        1 5 4
        2 5 18
        3 5 42
        4 5 15
        5 5 883
        6 5 22
        7 5 8
        8 5 1
        9 5 1

        0 6 4
        1 6 0
        2 6 9
        3 6 52
        4 6 7
        5 6 19
        6 6 958
        7 6 1
        8 6 0
        9 6 0

        0 7 8
        1 7 2
        2 7 6
        3 7 24
        4 7 14
        5 7 12
        6 7 2
        7 7 946
        8 7 4
        9 7 2

        0 8 7
        1 8 6
        2 8 2
        3 8 3
        4 8 1
        5 8 2
        6 8 0
        7 8 2
        8 8 975
        9 8 2

        0 9 6
        1 9 2
        2 9 2
        3 9 4
        4 9 4
        5 9 4
        6 9 0
        7 9 8
        8 9 3
        9 9 945
    };
    \end{axis}
\end{tikzpicture}
\caption{Confusion matrix on the test set (N=10,000). Darker colors indicate higher
counts. The diagonal shows correct predictions, while off-diagonal elements reveal
systematic errors. The most prominent confusions occur between visually similar
classes (cat/dog, automobile/truck).}
\label{fig:confusion_matrix}
\end{figure}
"""

    # Write all files to disk
    main_file = work_dir / "main.tex"
    main_file.write_text(main_tex)

    hyperparams_file = work_dir / "hyperparameters.tex"
    hyperparams_file.write_text(hyperparams_tex)

    training_plots_file = work_dir / "training_plots.tex"
    training_plots_file.write_text(training_plots_tex)

    class_metrics_file = work_dir / "class_metrics.tex"
    class_metrics_file.write_text(class_metrics_tex)

    confusion_matrix_file = work_dir / "confusion_matrix.tex"
    confusion_matrix_file.write_text(confusion_matrix_tex)

    training_data = generate_training_data()
    training_data_file = work_dir / "training_data.csv"
    training_data_file.write_text(training_data)

    # Create document from the main file and add all resources
    document = Document.from_path(main_file, name="ml_experiment_report")

    # Add all the component files as resources
    document.resources.append(Resource(hyperparams_file, kind="tex"))
    document.resources.append(Resource(training_plots_file, kind="tex"))
    document.resources.append(Resource(class_metrics_file, kind="tex"))
    document.resources.append(Resource(confusion_matrix_file, kind="tex"))
    document.resources.append(Resource(training_data_file, kind="other"))

    return document


def main():
    """Generate and compile the ML experiment report."""
    print("=" * 60)
    print("B8TeX ML Experiment Report Generator")
    print("=" * 60)
    print()

    # Create temporary working directory
    with tempfile.TemporaryDirectory(prefix="b8tex_ml_") as tmpdir:
        work_dir = Path(tmpdir)
        print(f"Working directory: {work_dir}")
        print()

        # Create all report files
        print("Creating report files...")
        document = create_report_files(work_dir)
        print(f"✓ Created document: {document.name}")
        print()

        # Display file structure
        print("Project structure:")
        for file_path in work_dir.iterdir():
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  - {file_path.name} ({size:,} bytes)")
        print()

        # Compile the document
        print("Compiling ML experiment report...")
        print("(This may take a moment due to plots and tables...)")
        print()

        compiler = TectonicCompiler()

        # Create a separate build directory
        build_dir = work_dir / "build"
        build_dir.mkdir(exist_ok=True)

        try:
            result = compiler.compile_document(document, workdir=build_dir)

            print("=" * 60)
            print("✓ Compilation successful!")
            print("=" * 60)
            print()

            # Get PDF from artifacts
            pdf_artifact = None
            for artifact in result.artifacts:
                if artifact.kind == OutputFormat.PDF:
                    pdf_artifact = artifact
                    break

            if pdf_artifact and pdf_artifact.path.exists():
                print(f"Output PDF: {pdf_artifact.path}")
                print(f"File size: {pdf_artifact.path.stat().st_size / 1024:.1f} KB")
            else:
                print("Warning: No PDF artifact found or doesn't exist")

            print(f"Compilation time: {result.elapsed:.2f}s")
            print()

            if result.warnings:
                print(f"Warnings: {len(result.warnings)}")
                for warning in result.warnings[:3]:
                    print(f"  - {warning}")
                if len(result.warnings) > 3:
                    print(f"  ... and {len(result.warnings) - 3} more")
                print()

            print("Document features:")
            print("  ✓ Multi-file LaTeX project")
            print("  ✓ Training curves with pgfplots")
            print("  ✓ Confusion matrix visualization")
            print("  ✓ Performance metrics tables")
            print("  ✓ Professional scientific formatting")
            print("  ✓ Bibliography and citations")
            print()

            print("The report includes:")
            print("  • Abstract and introduction")
            print("  • Experimental setup and architecture")
            print("  • Training dynamics with plots")
            print("  • Comprehensive performance evaluation")
            print("  • Ablation studies")
            print("  • Per-class metrics and confusion matrix")
            print("  • Conclusions and future work")
            print()

            # Copy PDF to outputs directory
            print("=" * 60)
            print("Copying output to repository...")
            print("=" * 60)

            # Get repo root (examples are in examples/ subdirectory)
            repo_root = Path(__file__).parent.parent
            outputs_dir = repo_root / "outputs"
            outputs_dir.mkdir(exist_ok=True)

            output_name = "07_ml_experiment_report.pdf"
            output_path = outputs_dir / output_name

            shutil.copy2(pdf_artifact.path, output_path)

            print(f"Source: {pdf_artifact.path}")
            print(f"Saved to: {output_path}")
            print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")
            print()
            print("You can now view the output PDF in the outputs/ directory!")
            print("=" * 60)
            print()

        except Exception as e:
            print(f"✗ Compilation failed: {e}")
            print(f"\nError type: {type(e).__name__}")
            if hasattr(e, 'errors') and e.errors:
                print(f"\nErrors:")
                for error in e.errors:
                    print(f"  - {error}")
            if hasattr(e, 'log_tail') and e.log_tail:
                print(f"\nLog tail:\n{e.log_tail}")
            return 1

    print("=" * 60)
    print("Example completed successfully!")
    print()
    print("This demonstrates B8TeX's ability to handle complex,")
    print("data-driven scientific documents with multiple LaTeX files,")
    print("CSV data, plots, and tables - perfect for ML experiment reports!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
