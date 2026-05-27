#!/usr/bin/env python
__author__ = "J Gomez-Dans"
__copyright__ = "Copyright 2017, 2018 J Gomez-Dans"
__version__ = "2.1.0"
__license__ = "GPLv3"
__email__ = "j.gomez-dans@ucl.ac.uk"

from .spectral_library import get_spectra

spectral_lib = get_spectra()
from .prospect_d import run_prospect
from .sail_model import (
    geocily,
    geocone,
    geocyli,
    run_progeosail,
    run_prosail,
    run_sail,
    run_thermal_sail,
)
