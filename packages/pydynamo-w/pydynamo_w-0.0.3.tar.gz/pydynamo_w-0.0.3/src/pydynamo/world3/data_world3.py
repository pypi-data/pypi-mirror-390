"""
Data used to build world3 model.

Pydynamo code, colors, definitions
"""

from .get_sectors import get_sectors, sector_color

import os
import json

code_file = os.path.join(os.path.dirname(__file__),'code_pydynamo_w3.py')

w3_defs = json.load(open(os.path.join(os.path.dirname(__file__),'definitions_w3.json')))
w3_code = open(code_file).readlines()

var_sector, var_subsector = get_sectors(code_file)
sector_vars = {sector: [] for sector in var_sector.values()}
for var in var_sector:
    sector_vars[var_sector[var]].append(var)
    
var_color = {v: sector_color[sector] for v, sector in var_sector.items()}
