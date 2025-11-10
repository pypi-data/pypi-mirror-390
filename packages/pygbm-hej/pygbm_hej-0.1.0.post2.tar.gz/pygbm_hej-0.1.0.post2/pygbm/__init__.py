#'pygbm'/__init__.py

#Import the main base class for easy access
from .base_pygbm import BaseGBM

#Import specific module classes
from .gbm_simulator.gbm_simulator import GBMSimulator

#Import version information for package
from .version import __version__

#Print package version for confirmation
print(f"pygbm package version: {__version__}")