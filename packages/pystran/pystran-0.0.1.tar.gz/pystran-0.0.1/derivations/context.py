"""
Mechanism for making python aware of the pystran package.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

import pystran
