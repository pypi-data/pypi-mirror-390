import click
from tqdm import tqdm

import structlog
import logging
log = structlog.get_logger("niceplot.main")
structlog.stdlib.recreate_defaults(log_level=logging.INFO)  # so we have logger names

# Own imports:
from niceplot.draw1dratio import draw1dratio
from niceplot.draw2dhist import draw2dhist
from niceplot.draw2dscatter import draw2dscatter
import niceplot.utils as utils
from niceplot.reader import Reader

@click.command()
@click.argument('config_file')
def niceplot(config_file: str) -> None:
    """Module to make nice looking root plots in the ATLAS Style.
    See https://gitlab.cern.ch/jwuerzin/nice-plot or https://pypi.org/project/niceplotpy/ for documentation.
    """
    # Print welcome message and version number:
    utils.printwelcome()
    
    # Read in config file and prep corresponding dictionary with pandas.DataFrames:
    reader = Reader(config_file)   
    
    dfdict = reader.prepdfdict()

    savestr = "\n"

    # Loop over all configurations and plotting configs; Make one plot for all configs & plot configs:
    log.info("")
    log.info("Generating plots:")
    print()
    for plot in tqdm(reader.plots, desc="", unit="plots"):
        
        if plot.type == '1dratio':
            # Make one 1dratio plot with specific configuration:
            try: savestr += draw1dratio(
                dfdict=dfdict,
                x=plot.x,
                denominator=plot.denominator,
                numerator=plot.numerator,
                denomlab=utils.getaddinfo(reader.configurations, plot.denominator),
                numlab=utils.getaddinfo(reader.configurations, plot.numerator),
                weights=plot.weights,
                nbins=plot.nbins,
                range=plot.range,
                xlab=plot.xlab,
                ylab=plot.ylab,
                suffix=f"{plot.denominator}_over_{plot.numerator}",
                addinfo=plot.addinfo,
                logy=plot.logy,
                output_dir=reader.output_dir,
                subdir=plot.subdir
            ) 
            except: log.exception(f"1dratio plot failed for x: {plot.x}, denom: {utils.getaddinfo(reader.configurations, plot.denominator)}, num: {utils.getaddinfo(reader.configurations, plot.numerator)}!")
        elif plot.type == '2dhist':
            # Make one 2D (exclusion) Histogram for every dataframe configuration:
            for config in reader.configurations:
                # plot only for specified configs:
                if plot.configurations is not None and config.name not in plot.configurations: continue
                try: savestr += draw2dhist(
                    x=dfdict[config.name].get(plot.x),
                    y=dfdict[config.name].get(plot.y),
                    nbins=plot.nbins,
                    binrange=plot.range,
                    xlab=plot.xlab,
                    ylab=plot.ylab,
                    z=dfdict[config.name].get(plot.z),
                    zopt=plot.zopt,
                    suffix=config.name,
                    addinfo=config.addinfo,
                    output_dir=reader.output_dir,
                    subdir=plot.subdir,
                    addnumbers=plot.addnumbers,
                    doballs=plot.doballs
                )
                except: log.exception(f"2dhist plot failed for x: {plot.xlab}, y: {y.ylab}, zopt: {zopt}")
        elif plot.type == '2dscatter':
            # Make one 2D scatter plot for every dataframe configuration:
            for config in reader.configurations:
                # plot only for specified configs:
                if plot.configurations is not None and config.name not in plot.configurations: continue
                try: savestr += draw2dscatter(
                    x=dfdict[config.name].get(plot.x),
                    y=dfdict[config.name].get(plot.y),
                    z=dfdict[config.name].get(plot.z),
                    range=plot.range,
                    xlab=plot.xlab,
                    ylab=plot.ylab,
                    suffix=config.name,
                    addinfo=config.addinfo,
                    output_dir=reader.output_dir,
                    subdir=plot.subdir
                )
                except: log.exception(f"2dscatter plot failed for x: {plot.xlab}, y: {plot.ylab}, z: {plot.z}")
        else:
            log.fatal(f"Plot type {plot.type} not recognised! Supported types are: 1dratio, 2dhist and 2dscatter")
            exit()
     
    print()    
    log.info(savestr)
    log.info("Plots generated successfully. Have a great day!!")