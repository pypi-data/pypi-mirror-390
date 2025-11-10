# This file is part of atooms
# Copyright 2010-2024, Daniele Coslovich

"""
Simulation framework for systems of interacting particles.

`atooms` provides a generic simulation interface that abstracts out
most of the common parts of particle-based simulations. It uses
callbacks to analyze and process simulation data on the fly.
"""

from .core import Simulation
from .observers import *
from .reports import *
