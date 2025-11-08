"""Module for making 2D Histogram plots."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import types
from atlasify import atlasify
from atlasify import monkeypatch_axis_labels
monkeypatch_axis_labels()

# Import own utility functions
import niceplot.utils as utils

# Create custom colormap
N = plt.cm.plasma.N
cmaplist_magma = [plt.cm.magma(i) for i in range(N)]

cmaplist = [plt.cm.plasma(i) for i in range(N)]
cmaplist[0] = mpl.colors.to_rgba('black')
cmaplist[-1] = cmaplist_magma[-1]

mycmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap', cmaplist, N)
mycmap.set_bad('gainsboro')

def draw2dhist(
    x: pd.core.series.Series,
    y: pd.core.series.Series,
    **kwargs
  ) -> str:
  """
  Function to draw a 2D histogram of x vs y. 
  
  Args:
    x (pd.core.series.Series): Pandas series for x-axis.
    y (pd.core.series.Series): Pandas series for y-axis.
  
  Keyword Args:
    nbins (int) = 50: Number of bins to plot.
    binrange (list) = [[min(x.values), max(x.values)], [min(y.values), max(y.values)]]: Range to use for plotting.
      Should have format: [[xmin, xmax], [ymin, ymax]].
    xlab (str) = utils.getnicestr(x.name): X-axis Label.
    ylab (str) = utils.getnicestr(y.name): Y-axis Label.
    z (pd.core.series.Series) = None: Pandas series for z-axis.
    zopt (str) = "counts": Option for z-axis. Supported are: "counts", "excl_frac" and "excl_max".
    suffix (str) = "": Suffix for pdf name.
    addinfo (str) = "": Additional information to add to plot.
    output_dir (str) = "plots": Output directory to save plots in.
    subdir (str) = "": Output subdirectory to save plots in.
    addnumbers (bool) = False: Add grey numbers in overlay.
    doballs (bool) = False: Plot balls with number of entries in bin for size.
  
  Returns:
    Location of saved plot.
  """
  
  # Read kwargs if provided:
  nbins = utils.popnonan(kwargs,'nbins', 50)
  binrange = utils.popnonan(kwargs,'binrange', [[min(x.values), max(x.values)], [min(y.values), max(y.values)]])
  xlab = utils.popnonan(kwargs,'xlab', utils.getnicestr(x.name))
  ylab = utils.popnonan(kwargs,'ylab', utils.getnicestr(y.name))
  z = utils.popnonan(kwargs,'z', None)
  zopt = utils.popnonan(kwargs,'zopt', "counts")
  suffix = utils.popnonan(kwargs,'suffix', "")
  addinfo = utils.popnonan(kwargs,'addinfo', "")
  output_dir = utils.popnonan(kwargs,'output_dir', "plots")
  subdir = utils.popnonan(kwargs,'subdir', "")
  addnumbers = utils.popnonan(kwargs,'addnumbers', False)
  doballs = utils.popnonan(kwargs,'doballs', False)
  
  fig, ax = plt.subplots(nrows=1, ncols=1)
  
  # TODO: fix log-log plot using this binning sheme:
  # nbins = [np.logspace(-4, 0, nbins), np.logspace(-4, 0, nbins)]
  
  # Make 2d hist (depending on zopt):
  if zopt == "counts":
    z_matrix, x_edges, y_edges, h = ax.hist2d(x, y, bins=nbins, range=binrange, cmin=1)
    clab = 'no. of models'
    figname = f'2dhist_{x.name}_vs_{y.name}_{suffix}.pdf'
    anncol = 'white'
    numdig = 0

  else:
    # Plot either exclusion fraction/max on z-axis. First, cast data into dataframe:
    df = pd.DataFrame( {
      'x': x,
      'y': y,
      'z': z
    } )
    
    # Next, we make a simple histogram to get the bin edges:
    counts, x_edges, y_edges = np.histogram2d(x, y, bins=nbins, range=binrange)
    
    # Bugfix for including 0. values:
    x_edges[0] = x_edges[0]-1e-9 if x_edges[0] == 0. else x_edges[0]
    y_edges[0] = y_edges[0]-1e-9 if y_edges[0] == 0. else y_edges[0]
        
    # Apply bins to df:
    # Bin the data for 'x' and 'y' columns
    bins_x = pd.cut(df['x'], bins=x_edges)
    bins_y = pd.cut(df['y'], bins=y_edges)

    if zopt == "excl_frac":
      z_excl = df.groupby([bins_x, bins_y], observed=False)['z'].apply(utils.frac_excl)
      clab = "Fraction of Excluded Models"
    elif zopt == "excl_max":
      z_excl = df.groupby([bins_x, bins_y], observed=False)['z'].apply(np.maximum.reduce)
      clab = "Maximum CLs value"
    else:
      raise ValueError(f"Value {zopt} for zopt is not supported!")

    # Reshape the data for plotting
    z_matrix = z_excl.unstack().values

    # Create a 2D color plot
    if not doballs:
      h = ax.pcolormesh(x_edges, y_edges, z_matrix.T, cmap=mycmap, vmin=0, vmax=1)
      figname = f'2dexcl_{zopt}_{z.name}_{x.name}_vs_{y.name}_{suffix}.pdf'
    else:
      # Calculate bin centers
      x_centers = (x_edges[:-1] + x_edges[1:]) / 2
      y_centers = (y_edges[:-1] + y_edges[1:]) / 2
      
      # grey background:
      h = ax.pcolormesh(x_edges, y_edges, z_matrix.T*np.nan, cmap=mycmap, vmin=0, vmax=1)
      # add balls:
      h = ax.scatter(x_centers.repeat(nbins), np.tile(y_centers, nbins), s=counts**2+3, c=z_matrix, cmap=mycmap, vmin=0, vmax=1)
      figname = f'2dexcl_balls_{zopt}_{z.name}_{x.name}_vs_{y.name}_{suffix}.pdf'
  
    addinfo += f", {z.name}"
    anncol = 'black'
    numdig = 2

  # Plot dashed grey line if mN1 on y axis:  
  if "m_chi_10" in y.name:
    xylinearr = np.linspace(min(ax.get_ylim()[0], ax.get_xlim()[0]), max(ax.get_ylim()[1], ax.get_xlim()[1]), 1000)
    ax.plot(xylinearr, xylinearr, linestyle='dashed', color='grey')

  # Overlay simplified model limits if they exist:
  simplified_limit = utils.get_simplified_limit(x.name, y.name, z)
  if simplified_limit is not None:
    ax.plot(simplified_limit[x.name], simplified_limit[y.name], linestyle='-', color='white', linewidth = 2.0)
    ax.plot(simplified_limit[x.name], simplified_limit[y.name], linestyle='--', color='black')

  if addnumbers:
    # Annotate numbers:  
    x_width = x_edges[1] - x_edges[0]
    y_width = y_edges[1] - y_edges[0]
    for i in range(len(x_edges) -1):
      for j in range(len(y_edges) -1):
        if f'{z_matrix[i, j]:.2f}' == 'nan': continue
        ax.annotate(f'{z_matrix[i, j]:.{numdig}f}', (x_edges[i] + x_width/2., y_edges[j] + y_width/2.), color=anncol, ha='center', va='center', fontsize=7)

  # Fix labels, offsets and layout:
  cbar = fig.colorbar(h, ax=ax)
  cbar.set_label(clab, fontsize=13)
  ax.set_xlabel(xlab, fontsize=13)
  ax.set_ylabel(ylab, fontsize=13)
  #TODO: fix log-log scale to work properly
  # ax.set_yscale('log')
  # ax.set_xscale('log')
  
  # Correct offset for potential exponential on x and y axes; fix layout:
  ax.xaxis._update_offset_text_position = types.MethodType(utils.bottom_offset, ax.xaxis)
  ax.yaxis._update_offset_text_position = types.MethodType(utils.top_offset, ax.yaxis)
  fig.tight_layout(rect=(0, 0, 1, 0.94)) # default: left=0, bottom=0, right=1, top=1
  
  # Add ATLAS label + info:
  atlasify("Internal", addinfo, outside=True) 
  
  # Save:
  return utils.savefile(fig, output_dir, subdir, figname)