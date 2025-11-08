# Niceplot: A python module to make nice looking plots so I don't re-do the same thing all the time.

## Installation:

To install, simply do:

```python
pip install niceplotpy
```

## Non-standard Dependencies: 

Niceplot uses the [atlasify](https://atlasify.readthedocs.io) and [uproot](https://uproot.readthedocs.io) packages.

## Usage: 

After installation, the the module can be used with:

```python
niceplot CONFIG_FILE
```
Where the `CONFIG_FILE` includes all information on which plots to make, variables to plot, etc. 

Currently supported plot types are: `1dratio`, `2dhist` and `2dscatter`. For detailled example config files, see: [example_configs](https://gitlab.cern.ch/jwuerzin/nice-plot/-/blob/master/example_configs/). Here a shortened example config file:

```yaml
input_file: 'data/susy.root'
output_dir: 'plots/GMSB_Factory'
treename: 'susy'
configurations:
  - name: 'GMSBpresel'
    addinfo: all GMSB models
    masklist:
      - "df['EWSummary_ExpCLs_Overall'] != -1."
    newvar: 
      - varname: 'min_m_mu_LR'
        formula: "df[['m_mu_L', 'm_mu_R']].values.min(axis=1)"
      - varname: 'min_m_chi'
        formula: "df[['m_chi_10', 'm_chi_20', 'm_chi_1p']].values.min(axis=1)"
  - name: 'GMSBgmuon'
    addinfo: $\Delta a_\mu$ selection applied
    seedfrom: 'GMSBpresel'
    masklist:
      - "(df['gm2_nom']-df['gm2_err']) <= (25.1e-10+5.9e-10)"
      - "(df['gm2_nom']+df['gm2_err']) >= (25.1e-10-5.9e-10)"
define: &ploting_common
  { type: 1dratio, denominator: 'GMSBgmuon', numerator: 'GMSBpresel', nbins: 30, ylab: no. of models, logy: True, subdir: 1dratio}
plots:

  # Loop over N1 BFs:
  - !for_loop
    - BF:
      - 'BF_chi_10_to_e_L'
      - 'BF_chi_10_to_e_R'
    # 1D histograms:
    - {<<: *ploting_common, x: !evaluate "${BF}" }
    # 2D histograms:
    - { type: 2dhist, x: 'min_m_chi', y: !evaluate "${BF}", range: [ [0, 2000], [0, 1.]], nbins: 20, addnumbers: True }
    - { type: 2dhist, x: 'min_m_chi', y: !evaluate "${BF}", z: 'EWSummary_ExpCLs_Overall', zopt: 'excl_frac', range: [ [0, 2000], [0, 1.]], nbins: 20, addnumbers: True, subdir: 'EWSummary_ExpCLs_Overall' }
  
  - { type: 2dscatter, x: 'BF_chi_10_to_gravitino_Z', y: 'BF_chi_10_to_gravitino_gam', z: 'EWSummary_ObsCLs_Overall', range: [ [0, 1.], [0, 1.]], subdir: '2dscatter'}
```

## ToDo:

- Move 2Dscatterplot grid to background.
- Add more options for plots:
  - data/MC plots