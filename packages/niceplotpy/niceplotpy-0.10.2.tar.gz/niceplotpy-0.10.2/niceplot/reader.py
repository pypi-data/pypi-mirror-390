import uproot
import time
import pandas
import awkward as ak
import os
from tqdm import tqdm

import structlog
import logging
log = structlog.get_logger()
structlog.stdlib.recreate_defaults(log_level=logging.INFO)  # so we have logger names

from niceplot.process_yaml import read_yaml

class DotAccessibleDict:
    """Class for making dicts accessible by dots."""
    def __init__(self, dictionary):
        self._dict = dictionary
        pass

    def __getattr__(self, key):
        value = self._dict.get(key)
        
        if isinstance(value, dict):
            return DotAccessibleDict(value)
        elif isinstance(value, list):
            return [DotAccessibleDict(item) if isinstance(item, dict) else item for item in value]
        else:
            return value
    

class Reader(DotAccessibleDict):
    """Yaml Reader class for reading yaml config files, casting into useable format and prepping pandas dfs for plotting."""
    def __init__(self, config_file: str) -> None:
        log.info(f"Making reader based on config file: {config_file}")
        super().__init__(self.readconfig(config_file))
        
        pass
    
    def readconfig(self, filen: str) -> dict:
        """Read yaml config file for plotting and return dictionary."""
        with open(filen, 'r') as yaml_file:
            yaml_dict = read_yaml(yaml_file)
            
        return yaml_dict
    
    def getcollist(self) -> list:
        """Make a list of columns in df needed to make plots."""
        grab_columns = []
        newvarnames = []
        # Add variables from masks and variable definitions:
        for config in self.configurations:
            if config.masklist is not None:
                for mask in config.masklist:
                    grab_columns += self.reducetovar(mask)
            if config.newvar is not None:
                for newvar in config.newvar:
                    newvarnames += [newvar.varname]
                    grab_columns += self.reducetovar(newvar.formula)

        # Add variables for x and y axes:
        for plot in self.plots:
            if plot.x is not None:
                grab_columns += [plot.x,]
            if plot.y is not None:
                grab_columns += [plot.y,]
            if plot.z is not None:
                grab_columns += [plot.z,]

        # Add weights:
        for plot in self.plots:
            if plot.weights is not None:
                grab_columns += [plot.weights,]
        
        # If txtfilter is provided, add model id:
        if self.txtfilter is not None:
            grab_columns += ['model',]
            
        # Remove duplicate items and variables defined in config:
        grab_columns = list(set(grab_columns))
        for newvarname in newvarnames:
            grab_columns.remove(newvarname) if newvarname in grab_columns else grab_columns
        
        return grab_columns

    def reducetovar(self, longstr: str) -> list:
        """Reduce longstr to list of variable names contained in df."""
        longstr = longstr.replace(" ", "")
        varlist = []
        
        if "['" in longstr and "']" in longstr:
            # Select parts of selection between square brackets:
            for i in range(longstr.count("['")):
                substr = longstr.split("['")[i+1].split("']")[0]
                if ("','") in substr:
                    varlist += substr.split("','")
                else:
                    varlist += [substr,]

        return varlist

    def makemask(self, df: pandas.DataFrame, masklist: list[str]) -> pandas.core.series.Series:
        """Function for making mask for dataframe df from masklist provided in config. df needs to be function input to support call of eval()."""    
        for mask in masklist:
            try: eval(mask)
            except: log.fatal(f"Evaluation of mask {mask} failed! Did you forget to include df[] ?")
            try:
                fullmask &= eval(mask)
            except:
                fullmask = eval(mask)
                
        return fullmask

    def addnewvar(self, df: pandas.DataFrame, varname: str, formula: str) -> pandas.DataFrame:
        """Add new variable with varname defined by formula to df."""
        df[varname] = eval(formula)
        
        return df

    def prepdfdict(self) -> dict[pandas.DataFrame]:
        """Function to return dictionary with prepped pandas.DataFrames for plotting."""

        # Open file(s) with uproot and store tree(s):        
        if os.path.isdir(self.input_file):
            
            log.info("input_file is directory. Will run over all files inside it.")
            
            filelist = [os.path.join(self.input_file, filen) for filen in os.listdir(self.input_file)]
        else:
            filelist = [self.input_file]
        
        log.info(f"Made input file list: {filelist}")

        # Get list of columns to read:
        grab_columns = self.getcollist()
        # Make dataframe for every configuration:
        dfdict = {}
        for config in self.configurations:
            starttime = time.time()
            # build one df for every configuration; copy other df if seed is provided.
            if config.seedfrom is not None:
                dfdict[config.name] = dfdict[config.seedfrom]
            else:
                # Use uproot to read into akarrays, concat & transform into pandas df:
                akarr = ak.Array([])
                if self.firstn: log.warning(f"Will only loop over the first {self.firstn} entires!")
                
                log.info()
                log.info(f"Generating DataFrames for config {config.name}:")
                print()
                for filen in tqdm(filelist, desc="", unit="df"):

                    with uproot.open(filen, compression=uproot.LZMA(9))[self.treename] as tree:
                        # if firstn is provided, only run over firstn entries:
                        if self.firstn:
                            if len(akarr) >= self.firstn: continue

                        # Read into akarr:
                        akarr = ak.concatenate([akarr, tree.arrays(grab_columns, library='ak', entry_stop=self.firstn)])
                                
                dfdict[config.name] = ak.to_dataframe(akarr)
                
                # If txtfilter is provided, filter dfcict to only contain models also in txt:
                if self.txtfilter is not None:
                    log.warning("Selected filter file! Will filter models...")
                    filterdf = pandas.read_csv(self.txtfilter, header=None, names=['file', 'model', 'modelName', 'numEvents'])
                    
                    log.warning(f"No. models pre-filter: {len(dfdict[config.name])}")
                    dfdict[config.name] = dfdict[config.name][dfdict[config.name]['model'].isin(filterdf['model'])]
                    log.warning(f"No. models post-filter: {len(dfdict[config.name])}")
                
                print()
            
            # Add new variables to dataframe:
            if config.newvar is not None:
                for var in config.newvar:
                    dfdict[config.name] = self.addnewvar(dfdict[config.name], var.varname, var.formula)  
            
            log.info(f"Total time to read config {config.name} into df: {time.time() - starttime:.2f} s") 
            
            # Make mask for constraints if masklist is provided and apply:
            if config.masklist is not None:
                constraints_mask = self.makemask(dfdict[config.name], config.masklist)
                dfdict[config.name] = dfdict[config.name][constraints_mask]

        return dfdict