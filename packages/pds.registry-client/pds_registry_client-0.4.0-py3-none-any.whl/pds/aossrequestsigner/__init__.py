# -*- coding: utf-8 -*-
"""PDS Registry Client."""
import importlib.resources


__version__ = importlib.resources.files(__name__).joinpath("VERSION.txt").read_text().strip()
