# utils/chart_utils.py

"""
matplotlib charts. 
"""
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple

def finalize_plot(fig: plt.Figure, save_path: Optional[str] = None, show: bool = True) -> None:
    """
    
    
    fig: The matplotlib Figure object.
    save_path:  saves the figure to this file path.
    show: If True, displays the plot; otherwise, closes the figure.
    """
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    if show:
        plt.show()
    else:
        plt.close(fig)

def plot_sales_bar_chart(
    data: Dict[str, float],
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    Creates a vertical bar chart of sales per Branch-Good combo.
    """
    if not data:
        print("No data to plot.")
        return

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(labels, values, color="#3498db")

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f'{height:.1f}',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha='center',
            fontsize=10
        )

    ax.set_title("Sales by Branch and Product", fontsize=16, fontweight="bold")
    ax.set_xlabel("Branch - Good", fontsize=12)
    ax.set_ylabel("Total Sold", fontsize=12)
    ax.tick_params(axis='x', labelrotation=30)
    ax.grid(axis='y', linestyle="--", alpha=0.7)
    fig.tight_layout()

    finalize_plot(fig, save_path=save_path, show=show)

def plot_sales_horizontal_chart(
    data: Dict[str, float],
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    Creates a horizontal bar chart of sales per Branch-Good combo.
    
    """
    if not data:
        print("No data to plot.")
        return

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.barh(labels, values, color="#2ecc71")

    for bar in bars:
        width = bar.get_width()
        ax.annotate(
            f'{width:.1f}',
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha='left',
            va='center',
            fontsize=10
        )

    ax.set_title("Horizontal View - Sales Performance", fontsize=16, weight="bold")
    ax.set_xlabel("Total Sold", fontsize=12)
    ax.set_ylabel("Branch - Good", fontsize=12)
    ax.grid(axis='x', linestyle="--", alpha=0.7)
    fig.tight_layout()

    finalize_plot(fig, save_path=save_path, show=show)

def plot_sales_pie_chart(
    data: Dict[str, float],
    figsize: Tuple[int, int] = (8, 8),
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    Creates a pie chart showing percentage sales distribution.
    
    """
    if not data:
        print("No data to plot.")
        return

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=figsize)
    ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        textprops={'fontsize': 10},
        colors=["#f39c12", "#e67e22", "#e74c3c", "#f06292", "#7dcea0", "#85c1e9"]
    )
    ax.set_title("Sales Distribution by Branch-Product", fontsize=14, weight="bold")
    plt.tight_layout()

    finalize_plot(fig, save_path=save_path, show=show)

def plot_sales_chart(
    data: Dict[str, float],
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    Creates a vertical bar chart for sales performance by Branch-Good combo.
    """
    if not data:
        print("No data to plot.")
        return

    labels = list(data.keys())
    values = list(data.values())

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    bars = ax.bar(labels, values, color="#3498db")

    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.5,
            f"{yval:.1f}",
            ha='center',
            fontsize=9
        )

    ax.set_title("Sales Performance by Branch", fontsize=14, fontweight='bold')
    ax.set_xlabel("Branch - Good", fontsize=12)
    ax.set_ylabel("Total Sold", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    finalize_plot(fig, save_path=save_path, show=show)

def plot_stacked_bar_chart(
    data: Dict[str, Dict[str, float]],
    title: str = "Stacked Bar Chart",
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    Creates a stacked bar chart. The input data should be a dictionary mapping each label to a dictionary of subcategory values.
    
    """
    if not data:
        print("No data to plot.")
        return

    labels = list(data.keys())
    subcategories = list(next(iter(data.values())).keys())
    bar_data = {sub: [data[label].get(sub, 0) for label in labels] for sub in subcategories}

    fig, ax = plt.subplots(figsize=figsize)
    bottom = [0] * len(labels)
    colors = plt.cm.Set3.colors

    for i, sub in enumerate(subcategories):
        values = bar_data[sub]
        ax.bar(labels, values, label=sub, bottom=bottom, color=colors[i % len(colors)])
        bottom = [sum(x) for x in zip(bottom, values)]

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel("Quantity", fontsize=12)
    ax.set_xlabel("Branch", fontsize=12)
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    finalize_plot(fig, save_path=save_path, show=show)

def plot_line_chart(
    data: Dict[str, List[float]],
    x_labels: List[str],
    title: str = "Line Chart",
    ylabel: str = "Quantity",
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    Creates a line chart for the given time series data.
    
    """
    if not data:
        print("No data to plot.")
        return

    plt.figure(figsize=figsize)
    styles = ["-o", "-s", "-^", "-*"]
    for i, (label, values) in enumerate(data.items()):
        plt.plot(x_labels, values, styles[i % len(styles)], label=label)

    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("Time", fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()

    finalize_plot(plt.gcf(), save_path=save_path, show=show)
