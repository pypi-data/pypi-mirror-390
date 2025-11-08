"""Utility functions of niceplot package."""
import matplotlib
import matplotlib.pyplot as plt
import uproot as uproot
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

import structlog
import logging
log = structlog.get_logger()
structlog.stdlib.recreate_defaults(log_level=logging.INFO)  # so we have logger names

# Own imports:
from niceplot.reader import DotAccessibleDict

def printwelcome() -> None:
    from niceplot.__init__ import __version__,__author__,__credits__
    """Print Welcome message and package version number."""
    
    # Note: ASCII art generated with https://patorjk.com/software/taag/ (Small, Fitted)
    print("\n"+r"""  _  _  _                 _       _           __  
 | \| |(_) __  ___  _ __ | | ___ | |_  __ __ /  \ 
 | .` || |/ _|/ -_)| '_ \| |/ _ \|  _| \ V /| () |
 |_|\_||_|\__|\___|| .__/|_|\___/ \__|  \_/  \__/ 
                   |_|                            """+"\n")

    log.info(f"Welcome to Niceplot v{__version__}!")
    log.info(f"Author: {__author__} ({__credits__})")
    log.info("")
    
    return None

def popnonan(dic: dict, key: str, default) -> any:
    """Apply pop to dic for key and return default if None is returned."""
    retval = dic.pop(key, default)
    return default if retval is None else retval

def getaddinfo(conflist: list[dict], name: str) -> str:
    """Get and return addinfo entry from conflist for entry with name."""
    addinfo = None
    for conf in conflist:
        addinfo = conf.addinfo if conf.name == name else addinfo
    
    return addinfo

def getnicestr(string: str) -> str:
    """Function to get nice TeX version of string."""
    
    # Try to auto-generate nicestr:  
    leftlist = [""]
    rightlist = [""]
    matchdict = {
        # Functions:
        'BF' : ["\\mathrm{BF}(", ")"],
        'm' : ["m(", ")"],
        'Delta' : ["\\Delta(", ")"],
        'min' : ["\\mathrm{min}(", ")"],
        # SM:
        'h' : ["h", ""],
        'Z' : ["Z", ""],
        'gam' : ["\\gamma", ""],
        # SUSY:
        'chi' : ["\\tilde{\\chi}", ""],
        'gravitino' : ["\\tilde{G}", ""],
        'e' : ["\\tilde{e}", ""],
        'mu' : ["\\tilde{\\mu}", ""],
        'tau' : ["\\tilde{\\tau}", ""],
        'nu' : ["\\tilde{\\nu}_{", "}"],
        'gl' : ["\\tilde{g}", ""],
        'u' : ["\\tilde{u}", ""],
        'd' : ["\\tilde{d}", ""],
        't' : ["\\tilde{t}", ""],
        'b' : ["\\tilde{b}", ""],
        'L' : ["_L", ""],
        'R' : ["_R", ""],
        '1' : ["_1", ""],
        '2' : ["_2", ""],
        '10' : ["_1^0", ""],
        '20' : ["_2^0", ""],
        '30' : ["_3^0", ""],
        '40' : ["_4^0", ""],
        '1p' : ["_1^\\pm", ""],
        '2p' : ["_2^\\pm", ""],
        '3p' : ["_3^\\pm", ""],
        '4p' : ["_4^\\pm", ""],
        'Bino' : ["~\\mathrm{Bino}", ""],
        'Wino' : ["~\\mathrm{Wino}", ""],
        'Higgsino' : ["~\\mathrm{Higgsino}", ""],
        'fraction' : ["~\\mathrm{fraction}", ""],
        'frac' : ["~\\mathrm{fraction}", ""],
        # General tex:
        'to' : ["\\rightarrow", ""],
        'other' : ["\\rightarrow \\mathrm{Other}", ""],
        # Precision measurements:
        'gmuon' : ["\\Delta a_{\\mu}",""],
        # Prefixes:
        'SPfh' : ["", "\\mathrm{ (SPfh)}"],
        'SP' : ["", "\\mathrm{ (SP)}"],
        'SS' : ["", "\\mathrm{ (SS)}"],
        'GM2' : ["", "\\mathrm{ (GM2)}"],
    }
    
    for substr in string.split("_"):
        if substr in matchdict:
            leftlist += [matchdict[substr][0]]
            rightlist += [matchdict[substr][1]]
        # TODO: If no match found, might want to return input string instead of only using partials
        # else:
        #     leftlist += ["\\mathrm{"+substr+"}"]
        else:
            return string
    
    # Piece together full string from both lists:
    rightlist.reverse()
    fullstr = '$'+''.join(leftlist + rightlist)+'$'
    
    # Give last pass to re-change everything that may have been messed up by auto-gen:
    partdict = {
        "\\tilde{\\nu}_{\\tilde{\\mu}_L}" : "\\tilde{\\nu}_{\\mu}",
        "\\tilde{\\nu}_{\\tilde{e}_L}" : "\\tilde{\\nu}_{e}",
        "\\tilde{\\nu}_{\\tilde{\\tau}_1}" : "\\tilde{\\nu}_{\\tau 1}",
        "\\tilde{\\nu}_{\\tilde{\\tau}_2}" : "\\tilde{\\nu}_{\\tau 2}",
    }
    
    for key in partdict:
        fullstr = fullstr.replace(key, partdict[key]) if key in fullstr else fullstr
    
    # Add units where applicable:
    unitdict = {
        'm(' : " [GeV]",
    }
    for key in unitdict:
        fullstr = fullstr+unitdict[key] if key in fullstr else fullstr
    
    return fullstr

def bottom_offset(self, bboxes, bboxes2):
    """Function for correcting offset of exponent label on x-axis."""
    pad = plt.rcParams["xtick.major.size"] + plt.rcParams["xtick.major.pad"]
    bottom = self.axes.bbox.ymin
    self.offsetText.set(va="top", ha="left") 
    oy = bottom - pad * self.figure.dpi / 72.0
    # self.offsetText.set_position((1, oy))
    self.offsetText.set_position((1+0.01, oy))

def top_offset(self, bboxes, bboxes2):
    """Function for correcting offset of exponent label on y-axis."""
    pad = plt.rcParams["xtick.major.size"] + plt.rcParams["xtick.major.pad"]
    top = self.axes.bbox.ymax
    self.offsetText.set(va="top", ha="left") 
    oy = top + pad * self.figure.dpi / 72.0
    # self.offsetText.set_position((1, oy))
    self.offsetText.set_position((-0.1, oy*1.03))
    
def saferatio(numlist: list, denomlist: list, numerr: list, denomerr: list) -> tuple[list, list]:
    """
    Function for calculate safe ratio numlist/denomlist and the corresponding (weighted) Poisson uncertianty.
    Uses numerr and denomerr as (weighted) Poisson uncertainties.
    Replacing infinities in the ratio by -1. Returns (ratio, ratioerr).
    """
    ratio = [numlist[i]/denomlist[i] if denomlist[i] != 0 else -1. for i in range(len(numlist))]
    # Assume Poissionian errors on both numlist and denomlist; set unc. to 0 for invalid ratio values:
    ratioerr = [np.abs(ratio[i])*np.sqrt( (numerr[i]/numlist[i])**2 + (denomerr[i]/denomlist[i])**2 ) if (denomlist[i] != 0 and numlist[i] != 0) else 0 for i in range(len(numlist))]
    
    return ratio, ratioerr
        
def savefile(fig: matplotlib.figure.Figure, dirn: str, subdir: str, filen: str) -> None:
    """Make plot directory dirn/subdir if it does not exist already and save fig into filen in dirn."""
    # Combine dirn and subdir; Make dir and parents if they don't exist already:
    outdir = f"{dirn}/{subdir}"
    Path(outdir).mkdir(parents=True, exist_ok=True)
    
    # Save file and close plot:
    filepath = f'{outdir}/{filen}'
    savestr = f"Saving plot: {filepath}\n"
    fig.savefig(filepath)
    plt.close(fig)
    
    return savestr
    
def frac_excl(z: pd.core.series.Series) -> float:
    """Aggregation function for calculating fraction of excluded models."""
    return len(z[ z.abs() < 0.05 ])/len(z)

def get_simplified_limit(x: str, y: str, z: pd.core.series.Series) -> pd.core.frame.DataFrame:
    """Checks if simplified limit exists for z-option in x-y plane and returns df with limit."""
    from pkg_resources import resource_filename
    import os
    
    try:
      CLssuffix = "Exp" if "Exp" in z.name else "Obs"
    except:
      CLssuffix = "Obs"
    
    csv_dir = resource_filename('niceplot', f'data/')
    matching_files = [filen for filen in os.listdir(csv_dir) if (CLssuffix in filen and f"_{x}_" in filen and f"_{y}_" in filen)]

    if len(matching_files) > 1:
        raise ValueError("More matches for csv files found than expected!")
    elif len(matching_files) == 0:
        return None
    else:
        return pd.read_csv(os.path.join(csv_dir, matching_files[0]))