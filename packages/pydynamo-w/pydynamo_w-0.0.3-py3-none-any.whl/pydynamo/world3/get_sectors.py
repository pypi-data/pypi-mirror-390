"""Infomations about sectors of each variable.
"""

import re

def get_sectors(fname):
    """From the world3 pydynamo code get all sectors for each variable.
    
    Parameters
    ----------
    fname : str
        World3 pydynamo code file.
    """
    sectors = {}
    subsectors = {}

    with open(fname, 'r') as f:
        for l in f.readlines():
            if l.startswith('#'):
                if ' sector' in l:
                    sector = l[1:].strip()
                    subsector = ''
                elif ' subsector' in l:
                    subsector = l[1:].strip()

            else:
                try:
                    var = re.findall('^(\w*)[\. \=]', l)[0]
                    sectors[var] = sector
                    subsectors[var] = subsector

                except Exception as e:
                    assert l.strip() == '', 'error: ' + l + '\n' + repr(e)
    return sectors, subsectors

from collections import defaultdict
sector_color = defaultdict(lambda: '#888888', **{
    'Persistent pollution sector': '#19D9FF',
    'Population sector': '#CF4125',
    'Capital sector': '#0073E6',
    'Agricultural sector': '#66CC00',
    'Nonrenewable resource sector': '#8080FF',
})


# # Dict(variable: corresponding sector)
# var_sector, var_subsector = get_sectors('../limits_to_growth_pydynamo_code.py')

# # Dict(sector: [corresponding variables]
# sector_vars = {sector: [] for sector in var_sector.values()}
# for var in var_sector:
#     sector_vars[var_sector[var]].append(var)

# # Dict(variable: corresponding color)
# var_color = {v: sector_color[sector] for v, sector in var_sector.items()}

# Note: variables but also constants and tables are included
# import json

# for dico, filename in ((var_sector, 'var_sector.json'),
#                        (sector_vars, 'sector_vars.json'),
#                        (var_color, 'var_color.json')):
#     with open(filename, 'w+') as f:
#         json.dump(dico, f)
