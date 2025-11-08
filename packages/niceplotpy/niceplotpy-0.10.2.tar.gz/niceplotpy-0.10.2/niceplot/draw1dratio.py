"""Module for making plot with two 1D Histograms and their ratio."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import types
import pandas as pd
from atlasify import atlasify
from atlasify import monkeypatch_axis_labels
monkeypatch_axis_labels()

# Import own utility functions
import niceplot.utils as utils

def draw1dratio(
    dfdict: dict[pd.DataFrame],
    x: str,
    denominator: str,
    numerator: str,
    denomlab: str,
    numlab: str,
    **kwargs
  ) -> str:
  """
  Function to draw two 1d histograms and their ratio, both including statistical uncertainties.
  
  Args:
    dfdict (dict[pd.DataFrame]): DataFrame dictionary containing DataFrames to plot.
    x (str): Name of the DataFrame column to use as x-axis.
    denominator (str): Denominator configuration for ratio.
    numerator (str): Numerator configuration for ratio.
    denomlab (str): Legend label for denominator.
    numlab (str): Legend label for Numerator.
  
  Keyword Args:
    weights (str) = "": DataFrame column to take the weights from.
    nbins (int) = 50: Number of bins to plot.
    range (list) = None: Range to use for plotting. Should have format: [xmin, xmax].
      If None, will automatically generate range to include all data.
    xlab (str) = utils.getnicestr(x): X-axis Label.
    ylab (str) = "events": Y-axis Label.
    suffix (str) = "": Suffix for pdf name.
    addinfo (str) = "": Additional information to add to plot.
    logy (bool) = False: Boolean for making log plot.
    output_dir (str) = "plots": Output directory to save plots in.
    subdir (str) = "": Output subdirectory to save plots in.
  
  Returns:
    Location of saved plot.
  """
  
  # Read kwargs if provided:
  weights = utils.popnonan(kwargs,'weights', None)
  nbins = utils.popnonan(kwargs,'nbins', 50)
  range = utils.popnonan(kwargs,'range', None)
  xlab = utils.popnonan(kwargs,'xlab', utils.getnicestr(x))
  ylab = utils.popnonan(kwargs,'ylab', "events")
  suffix = utils.popnonan(kwargs,'suffix', "")
  addinfo = utils.popnonan(kwargs,'addinfo', "")
  logy = utils.popnonan(kwargs,'logy', False)
  output_dir = utils.popnonan(kwargs,'output_dir', "plots")
  subdir = utils.popnonan(kwargs,'subdir', "")
  
  fig, (ax_top, ax_bottom) = plt.subplots(nrows=2, ncols=1, height_ratios=[1.5,1])
  
  # Get denominator and numerator:
  x_denom = dfdict[denominator][x]
  x_num = dfdict[numerator][x]
  
  # Get weights for denominator and numerator:
  weights_denom = dfdict[denominator][weights] if weights is not None else np.ones(x_denom.shape)
  weights_num = dfdict[numerator][weights] if weights is not None else np.ones(x_num.shape)
  
  # If range is not provided, take min/max of the two histograms:
  if range is None:
    minval = min(min(dfdict[denominator][x].values), min(dfdict[numerator][x].values))
    maxval = max(max(dfdict[denominator][x].values), max(dfdict[numerator][x].values))
    range = [minval, maxval]
  
  # Override ranges and nbins if x_num contains only ints:
  if pd.api.types.is_integer_dtype(x_num):
    range = [min(min(x_num), min(x_denom))-0.5, max(max(x_num), max(x_denom))+0.5]
    nbins = int(range[1] - range[0])
  
  # Make histograms and bar plots for errors:
  hist_num, bins, _ = ax_top.hist(x_num, bins=nbins, range=range, label=numlab, histtype='step', weights=weights_num)
  hist_denom, _, _ = ax_top.hist(x_denom, bins=nbins, range=range, label=denomlab, histtype='step', weights=weights_denom)
  bincenters = bins[:-1]+np.diff(bins)[0]/2.
  err_num = np.sqrt(np.histogram(x_num, bins=nbins, range=range, weights=weights_num**2)[0])  
  err_denom = np.sqrt(np.histogram(x_denom, bins=nbins, range=range, weights=weights_denom**2)[0])
  band_num = ax_top.bar(bincenters, height=2*err_num, bottom=(hist_num-err_num), width=np.diff(bins), alpha=0.5, facecolor='tab:blue')
  band_denom = ax_top.bar(bincenters, height=2*err_denom, bottom=(hist_denom-err_denom), width=np.diff(bins), alpha=0.5, facecolor='tab:orange')

  # Fixing legend to include uncertainty by creating new legend handles but use the colors from the existing ones
  handles, labels = ax_top.get_legend_handles_labels()
  new_handles = [Line2D([], [], c=h.get_edgecolor()) for h in handles]
  ax_top.legend(handles=[(new_handles[0], band_num), (new_handles[1], band_denom)] , labels=labels, loc='upper right')

  # Make ratio and error:  
  ratio, ratioerr = utils.saferatio(hist_num, hist_denom, err_num, err_denom)
  ax_bottom.errorbar(bincenters, ratio, yerr=ratioerr, fmt='ko', label='ratio', markersize=4, zorder=2)
  
  # Add dashed line at 1.0
  xlinearr = np.linspace(ax_top.get_xlim()[0], ax_top.get_xlim()[1], 1000)
  ylinearr = np.ones(1000)
  ax_bottom.plot(xlinearr, ylinearr, linestyle='dashed', color='grey', zorder=1)
  
  if logy:
    ax_top.set_yscale('log')
    # Set min by lowest non-0 value
    ax_top.set_ylim(0.5*min( [min(hist_denom[hist_denom > 0]), min(hist_num[hist_num > 0])]), 2*max( [max(hist_denom), max(hist_num)]) )
  else:
    ax_top.set_ylim(0., max( [max(hist_denom), max(hist_num)]) )
  
  # Set labels and limits for axes:
  ax_top.set_ylabel(ylab, fontsize=13)
  ax_top.axes.xaxis.set_ticklabels([])
  ax_bottom.set_xlabel(xlab, fontsize=13)
  ax_bottom.set_ylabel('ratio', fontsize=13)
  ax_bottom.set_xlim(ax_top.get_xlim())
  ax_bottom.set_ylim(0., max(ratio))
  
  # Correct offset for potential exponential on x and y axes; fix layout:
  ax_top.yaxis._update_offset_text_position = types.MethodType(utils.top_offset, ax_top.yaxis)
  ax_bottom.xaxis._update_offset_text_position = types.MethodType(utils.bottom_offset, ax_bottom.xaxis)
  
  # ATLAS Label:
  if addinfo == "":
    fig.tight_layout(rect=(0, 0, 1, 0.94)) # default: left=0, bottom=0, right=1, top=1
    atlasify("Internal", outside=True, axes=ax_top) 
  else:
    fig.tight_layout(rect=(0, 0, 1, 0.92)) # default: left=0, bottom=0, right=1, top=1
    atlasify("Internal", addinfo, outside=True, axes=ax_top, sub_font_size=12) 
  atlasify(False, axes=ax_bottom)
  
  # Save:
  return utils.savefile(fig, output_dir, subdir, f'1dratio_{x}_{suffix}.pdf')
