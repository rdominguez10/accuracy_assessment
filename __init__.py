#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 16:17:57 2020

@author: laige
"""

from .qgis_minimal_plugin import MinimalPlugin

def classFactory(iface):
    return MinimalPlugin(iface)
