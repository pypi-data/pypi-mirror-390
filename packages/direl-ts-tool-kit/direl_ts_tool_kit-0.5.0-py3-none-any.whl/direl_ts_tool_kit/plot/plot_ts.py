import pandas as pd
from .plot_style import *
from scipy.stats import pearsonr


def plot_time_series(
    df_ts,
    variable,
    units="",
    color="BLUE_LINES",
    time_unit="Year",
    rot=90,
    auto_format_label=True,
):
    """
    Plots a time series with custom styling and dual-level grid visibility.

    This function automatically sets major and minor time-based locators
    on the x-axis based on the specified time unit, and formats the y-axis
    to use scientific notation.

    Parameters
    ----------
    df_ts : pd.DataFrame
        The DataFrame containing the time series data. Must have a DatetimeIndex.
    variable : str
        The name of the column to plot. The label is automatically formatted
        (e.g., 'total_sales' becomes 'Total Sales').
    units : str, optional
        Units to display next to the variable name on the y-axis (e.g., 'USD').
        Defaults to "".
    color : str, optional
        Key corresponding to the line color in the global 'paper_colors' dictionary.
        Defaults to "BLUE_LINES".
    time_unit : str, optional
        The time granularity of the data to define x-axis tick locators.
        Options include 'Year', 'Month', 'Weekday', 'Day' or 'Hour'. Defaults to "Year".
    rot : int, optional
        Rotation angle (in degrees) for the x-axis tick labels. Defaults to 90.
    auto_format_label : bool, optional
        Used internally for label formatting logic. Defaults to True.

    Returns
    -------
    matplotlib.figure.Figure
        The generated matplotlib figure object.

    Notes
    -----
    Major grid lines are displayed with a dashed line ('--'), and minor grid
    lines are displayed with a dotted line (':') for detailed temporal analysis.

        Available Colors
    ----------------
    The 'color' parameter accepts any key from the 'paper_colors' dictionary.

    Lines: 'BLUE_LINES', 'ORANGE_LINES', 'GREEN_LINES', 'RED_LINES',
           'GRAY_LINES', 'PURPLE_LINES', 'MAROON_LINES', 'GOLD_LINES'.

    Bars:  'BLUE_BARS', 'ORANGE_BARS', 'GREEN_BARS', 'RED_BARS',
           'GRAY_BARS', 'PURPLE_BARS', 'MAROON_BARS', 'GOLD_BARS'.
    """

    fig, ax = plt.subplots()
    ax.plot(df_ts.index, df_ts[variable], linewidth=3, color=paper_colors[color])

    if "-" in variable:
        variable = "-".join(
            [
                j.title() if i == 0 else j.lower()
                for i, j in enumerate(variable.split("-"))
            ]
        )
    elif "_" in variable:
        variable = " ".join(
            [
                j.title() if i == 0 else j.lower()
                for i, j in enumerate(variable.split("_"))
            ]
        )
    else:
        variable = (
            " ".join(
                [
                    j.title() if i == 0 else j.lower()
                    for i, j in enumerate(variable.split())
                ]
            )
            if auto_format_label
            else variable
        )

    ax.set(xlabel=f"{time_unit}", ylabel=f"{variable} {units}")
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

    if time_unit == "Year":
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_minor_locator(mdates.MonthLocator())

    if time_unit == "Month":
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator())

    if time_unit == "Weekday":
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator())

    if time_unit == "Day":
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_minor_locator(mdates.HourLocator())

    if time_unit == "Hour":
        ax.xaxis.set_major_locator(mdates.HourLocator())
        ax.xaxis.set_minor_locator(mdates.MinuteLocator())

    ax.tick_params(axis="x", rotation=rot)
    ax.grid(which="both")
    ax.grid(which="minor", alpha=0.6, linestyle=":")
    ax.grid(which="major", alpha=0.8, linestyle="--")

    return fig


def save_figure(
    fig,
    file_name,
    variable_name="",
    path="./",
):
    """
    Saves a Matplotlib figure in three common high-quality formats (PNG, PDF, SVG).

    The function creates a consistent file name structure:
    {path}/{file_name}_{variable_name}.{extension}.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The Matplotlib figure object to be saved.
    file_name : str
        The primary name for the file (e.g., 'timeseries_report').
    variable_name : str, optional
        An optional secondary name, often the name of the plotted variable,
        to be appended to the file name. Defaults to "".
    path : str, optional
        The directory path where the figure files will be saved.
        Defaults to the current directory ('./').

    Returns
    -------
    None
    """

    if variable_name:
        base_name = f"{path}/{file_name}_{variable_name}"
    else:
        base_name = f"{path}/{file_name}"

    fig.savefig(f"{base_name}.png")
    fig.savefig(f"{base_name}.pdf")
    fig.savefig(f"{base_name}.svg")


def heat_map(X, y, colors="Blues"):
    """
    Generates a correlation heatmap plot for a set of features and a target variable.

    This function concatenates the feature DataFrame (X) and the target Series (y)
    to compute and visualize the full pairwise correlation matrix using Seaborn.

    Parameters
    ----------
    X : pd.DataFrame
        The DataFrame containing the feature variables.
    y : pd.Series or pd.DataFrame
        The target variable (must be concatenable with X).
    colors : str or matplotlib.colors.Colormap, optional
        The colormap to use for the heatmap, passed to the 'cmap' argument
        in seaborn.heatmap. Defaults to "Blues".

        Note: For standard correlation matrices (which include negative values),
        a diverging colormap (e.g., "coolwarm", "vlag") is usually recommended.

    Returns
    -------
    matplotlib.figure.Figure
        The generated Matplotlib figure object containing the heatmap.

    Notes
    -----
    The heatmap displays the Pearson correlation coefficient rounded to two
    decimal places and includes annotations for improved readability.
    """
    fig, ax = plt.subplots()
    Z = pd.concat([X, y], axis=1)

    ax = sns.heatmap(
        Z.corr(),
        cmap=colors,
        annot=True,
        linewidths=0.5,
        fmt=".2f",
        annot_kws={"size": 10},
    )

    return fig


def corrfunc(x, y, ax=None, **kws):
    """Plot the correlation coefficient in the top left hand corner of a plot."""
    r, _ = pearsonr(x, y)
    ax = ax or plt.gca()
    ax.annotate(f"R = {r:.2f}", xy=(0.1, 0.9), fontsize=25, xycoords=ax.transAxes)


def pair_plot(X, y):
    """
    Generates a cornered pair plot (scatterplot matrix) to visualize relationships
    between features and the target variable.

    The function combines the feature DataFrame (X) and the target Series (y)
    and uses seaborn.pairplot to create a matrix of scatter plots and histograms.
    It focuses on the lower triangular part (corner=True) and includes a
    regression line for trend visualization.

    Parameters
    ----------
    X : pd.DataFrame
        The DataFrame containing the feature variables.
    y : pd.Series or pd.DataFrame
        The target variable (must be concatenable with X).

    Returns
    -------
    matplotlib.figure.Figure
        The generated Matplotlib Figure object containing the cornered pair plot.

    Notes
    -----
    1. **Dependency:** This function requires a previously defined custom function
       `corrfunc` to be available in the local namespace, as it is used via
       `svm.map_lower()`. This custom function is typically used to display
       correlation coefficients (e.g., Pearson's r) in the lower panel.
    2. **Aesthetics:** Uses a regression line (`kind="reg"`) with custom color
       (RED_LINES) to highlight linear relationships.
    3. **Output:** The returned Figure object can be manipulated further
       or saved using methods like `fig.savefig()`.
    """
    Z = pd.concat([X, y], axis=1)
    svm = sns.pairplot(
        Z,
        corner=True,
        kind="reg",
        plot_kws={"line_kws": {"color": paper_colors["RED_LINES"]}},
    )
    svm.map_lower(corrfunc)

    fig = svm.fig

    return fig
