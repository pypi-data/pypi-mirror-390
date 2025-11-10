# pygbm
Geometric Brownian Motions simulation exercise from C1 example class

## Features
Simulation of GBM
Easy Python API
Command-line tool
Path plotting
Save plots to file

## Installation
Install pygbm using pip:
`$ pip install pygbm`

or from source files using:
`$ pip install -e /path/to/source`

## Dependencies
∙Python 3.9+
∙matplotlib
∙numpy

## Usage
∙Example code:

```
from pygbm.gbm_simulation import GBMSimulator
simulator = GBMSimulator(y0=1.0, mu=0.05, sigma=0.2)
t_values, y_values = simulator.simulate_path(T=1.0, N=100)
simulator.plot_path(t_values, y_values)

```
∙Baseline example plot see gbm_plot.png

∙For the command-line interface, one should be able to run something like:
` pygbm --y0 1.0 --mu 0.05 --sigma 0.2 --T 1.0 --N 100 --output gbm_plot.png `, this command should produce a plot of the simulated path as an output.

## Documentation
Link to the [document page (to be added)]

## Contribution
Contributors via pull requests are welcome.

## License
MIT License 

