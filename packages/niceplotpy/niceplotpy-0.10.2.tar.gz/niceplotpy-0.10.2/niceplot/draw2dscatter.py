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

def draw2dscatter(
    x: pd.core.series.Series,
    y: pd.core.series.Series,
    z: pd.core.series.Series,
    **kwargs
  ) -> str:
  """
  Function to draw a 2D histogram of x vs y. 
  
  Args:
    x (pd.core.series.Series): Pandas series for x-axis.
    y (pd.core.series.Series): Pandas series for y-axis.
    z (pd.core.series.Series): Pandas series for z-axis.
  
  Keyword Args:
    range (list) = None: Range to use for plotting. Should have format: [[xmin, xmax], [ymin, ymax]].
    xlab (str) = utils.getnicestr(x.name): X-axis Label.
    ylab (str) = utils.getnicestr(y.name): Y-axis Label.
    suffix (str) = "": Suffix for pdf name.
    addinfo (str) = "": Additional information to add to plot.
    output_dir (str) = "plots": Output directory to save plots in.
    subdir (str) = "": Output subdirectory to save plots in.
  
  Returns:
    Location of saved plot.
  """
  
  # Read kwargs if provided:
  range = utils.popnonan(kwargs,'range', None)
  xlab = utils.popnonan(kwargs,'xlab', utils.getnicestr(x.name))
  ylab = utils.popnonan(kwargs,'ylab', utils.getnicestr(y.name))
  suffix = utils.popnonan(kwargs,'suffix', "")
  addinfo = utils.popnonan(kwargs,'addinfo', "")
  output_dir = utils.popnonan(kwargs,'output_dir', "plots")
  subdir = utils.popnonan(kwargs,'subdir', "")

  fig, ax = plt.subplots(nrows=1, ncols=1)
  
  ax.grid(True, zorder=0)
  # ax.set_axisbelow(True)
  try: 
    z.name
    h = ax.scatter(x, y, s=(plt.rcParams['lines.markersize']/2.) ** 2, c=z, cmap=mycmap, zorder=1)
  except:
    h = ax.scatter(x, y, s=(plt.rcParams['lines.markersize']/2.) ** 2, zorder=1)
  # h = ax.scatter(x, y, s=(plt.rcParams['lines.markersize']/2.) ** 2, c=z, zorder=1)
  
  # Change plot ranges if appliccable:
  if range is not None:
    ax.set_xlim(range[0][0], range[1][1])
    ax.set_ylim(range[1][0], range[1][1])
  
  # Plot dashed grey line if mN1 on y axis:  
  if "m_chi_10" in y.name:
    xylinearr = np.linspace(min(ax.get_ylim()[0], ax.get_xlim()[0]), max(ax.get_ylim()[1], ax.get_xlim()[1]), 1000)
    ax.plot(xylinearr, xylinearr, linestyle='dashed', color='grey')

  # Overlay simplified model limits if they exist:
  simplified_limit = utils.get_simplified_limit(x.name, y.name, z)
  if simplified_limit is not None:
    ax.plot(simplified_limit[x.name], simplified_limit[y.name], linestyle='-', color='white', linewidth = 2.0)
    ax.plot(simplified_limit[x.name], simplified_limit[y.name], linestyle='--', color='black')

  # Fix labels, offsets and layout:
  try:
    z.name
    cbar = fig.colorbar(h, ax=ax)
    cbar.set_label(z.name, fontsize=13)
  except: pass
  ax.set_xlabel(xlab, fontsize=13)
  ax.set_ylabel(ylab, fontsize=13)
  
  # Correct offset for potential exponential on x and y axes; fix layout:
  ax.xaxis._update_offset_text_position = types.MethodType(utils.bottom_offset, ax.xaxis)
  ax.yaxis._update_offset_text_position = types.MethodType(utils.top_offset, ax.yaxis)
  fig.tight_layout(rect=(0, 0, 1, 0.94)) # default: left=0, bottom=0, right=1, top=1
  
  # Add ATLAS label + info:
  atlasify("Internal", addinfo, outside=True) 
  
  # Save:
  try:
    figname = f'2dscatter_{x.name}_vs_{y.name}_{z.name}_{suffix}.pdf'
  except:
    figname = f'2dscatter_{x.name}_vs_{y.name}_{suffix}.pdf'
  return utils.savefile(fig, output_dir, subdir, figname)