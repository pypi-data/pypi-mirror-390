import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from typing import Optional, List
import canopy as cp
from canopy.visualization.plot_functions import get_color_palette, make_dark_mode, handle_figure_output, select_sites

def make_static_plot(field_a: cp.Field, field_b: cp.Field,
                     output_file: Optional[str] = None, layers: Optional[List[str] | str] = None,
                     field_a_label: Optional[str] = None, field_b_label: Optional[str] = None,
                     unit_a: Optional[str] = None, unit_b: Optional[str] = None,
                     sites: Optional[bool | List[tuple]] = False,
                     scatter_size: Optional[float] = 6, scatter_alpha: Optional[float] = 0.5,
                     title: Optional[str] = None, palette: Optional[str] = None,
                     custom_palette: Optional[str] = None, move_legend: Optional[bool] = False, 
                     dark_mode: Optional[bool] = False, transparent: Optional[bool] = False, 
                     x_fig: Optional[float] = 10, y_fig: Optional[float] = 10, 
                     return_fig: Optional[bool] = False, **kwargs) -> Optional[plt.Figure]:
    """
    This function generates a scatter plot with regression lines and r-scores from two input fields 
    (which can be reduced spatially, temporally or both).

    Parameters
    ----------
    field_a, field_b : cp.Field
        Input data Field to display.
    output_file : str, optional
        File path for saving the plot.
    layers : List[str] or str, optional
        Layers to plot from the input data.
    field_a_label, field_b_label : str, optional
        Labels for the data series, if not provided canopy will try to retrieve the name of the variable in the metadata.
    unit_a, unit_b : str, optional
        Units for the data series, if not provided canopy will try to retrieve the unit of the variable in the metadata.
    sites : bool or List[Tuple], optional
        Control site-level plotting instead of spatial reduction. Default is False. True = all sites,
        if provided with a list, only select the sites in the list.
    scatter_size : float, optional
        Marker size for scatter points. Default is 6.
    scatter_alpha : float, optional
        Transparency (alpha) for scatter points. Default is 0.1.
    title : str, optional
        Title of the plot.
    palette : str, optional
        Seaborn color palette to use for the line colors (https://seaborn.pydata.org/tutorial/color_palettes.html, 
        recommended palette are in https://colorbrewer2.org).
    custom_palette : str, optional
        Path of custom color palette .txt file to use. Names should match label names.
    move_legend : bool, optional
        Location of the legend ('in' or 'out'). Default is False.
    dark_mode : bool, optional
        Whether to apply dark mode styling to the plot.
    transparent : bool, optional
        If True, makes the background of the figure transparent.
    x_fig : float, optional
        Width of the figure in inches. Default is 10.
    y_fig : float, optional
        Height of the figure in inches. Default is 10.
    return_fig : bool, optional
        If True, returns the figure object that can be usuable by multiple_figs().
        Default is False.
    **kwargs
        Additional keyword arguments are passed directly to `seaborn.regplot`. This allows customization of
        plot features such as `lowess`, `robust`, `logx`, etc.
    """
    # Check for some initial conditions
    if layers and sites:
        raise ValueError("layers and sites argument cannot be used simultanuously. Only one layer for multiple sites.")

    # Force variables to be a list
    if isinstance(layers, str):
        layers = [layers]
    if not isinstance(sites, bool) and not isinstance(sites, list):
        sites = [sites]

    # Retrieve metadata
    field_a_label = field_a_label or field_a.metadata['name']
    field_b_label = field_b_label or field_b.metadata['name']
    unit_a = field_a.metadata['units'] if unit_a is None else unit_a
    unit_b = field_b.metadata['units'] if unit_b is None else unit_b
    layers = layers or field_a.layers

    df_a = cp.make_lines(field_a)
    df_b = cp.make_lines(field_b)

    if sites: # If sites, flatten data
        df_a = select_sites(df_a, sites)
        df_b = select_sites(df_b, sites)
        layers = df_a.columns

    # Set up the figure and axes
    fig, ax = plt.subplots(figsize=(x_fig, y_fig))

     # Get the palette
    colors, colors_dict = get_color_palette(len(layers), palette=palette, custom_palette=custom_palette)

    for i, layer in enumerate(tqdm(layers, desc="Plotting layers")):
        x = df_a[layer]
        y = df_b[layer]

        # Get 1D aligned vectors and compute Pearson R
        x1d, y1d = to_aligned_1d(x, y)
        if len(x1d) < 2 or x1d.nunique() <= 1 or y1d.nunique() <= 1:
            print(f"Skipping {layer}: insufficient valid data for correlation")
            continue
        r_value = float(np.corrcoef(x1d.values, y1d.values)[0, 1])

        sns.regplot(
            x=x1d, y=y1d,
            color=colors[i], label=f"{layer} (R={r_value:.2f})",
            scatter_kws={'s': scatter_size, 'alpha': scatter_alpha},
            ax=ax, **kwargs
        )
    
    # Set axis limits
    min_val = min(df_a[layers].min().min(), df_b[layers].min().min())
    max_val = max(df_a[layers].max().max(), df_b[layers].max().max())
    ax.set_xlim([min_val, max_val])
    ax.set_ylim([min_val, max_val])

    # Add 1:1 reference line (gray, dashed)
    ax.plot([min_val, max_val], [min_val, max_val], color='gray', linestyle='--', linewidth=1)

    # Make legend
    leg = ax.legend(loc='best')
    if move_legend is True:
            sns.move_legend(ax, "center left", bbox_to_anchor=(1, 0.85))
            leg = ax.get_legend()
    # Ensure legend markers are opaque (not affected by scatter_alpha)
    if leg is not None:
        for handle in leg.legend_handles:
            if hasattr(handle, 'set_alpha'):
                handle.set_alpha(1.0)

    # Set axis labels with units
    xlabel = f"{field_a_label} (in {unit_a})" if unit_a != "[no units]" else field_a_label
    ylabel = f"{field_b_label} (in {unit_b})" if unit_b != "[no units]" else field_b_label
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)   

    # Set plot title
    ax.set_title(title, fontsize=18) 

    # Apply dark mode if requested
    if dark_mode:
        fig, ax = make_dark_mode(fig, ax)

    return handle_figure_output(fig, output_file=output_file, return_fig=return_fig, transparent=transparent)

def to_aligned_1d(x_obj, y_obj):
    """Return pairwise-valid, aligned 1D Series for x and y (handles Series/DataFrame)."""
    xs = x_obj.stack(future_stack=True) if isinstance(x_obj, pd.DataFrame) else x_obj
    ys = y_obj.stack(future_stack=True) if isinstance(y_obj, pd.DataFrame) else y_obj
    xs, ys = xs.align(ys, join='inner')

    if isinstance(xs, pd.DataFrame):
        xs = xs.stack(future_stack=True)
    if isinstance(ys, pd.DataFrame):
        ys = ys.stack(future_stack=True)

    valid = xs.notna() & ys.notna()

    if isinstance(valid, pd.DataFrame):
        valid = valid.to_numpy().ravel()
        xs = pd.Series(xs.to_numpy().ravel())
        ys = pd.Series(ys.to_numpy().ravel())
        
    return xs[valid], ys[valid]
