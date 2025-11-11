"""DEPRECIATED. Some functions to read definitions from a file in markdown format, usefull for translation.
"""
def read_translated_defs(filename):
    """Reads definitions in markdown format (see begin_sentence)
    and returns the definitions dictionnary.
    
    Parameters
    ----------
    filename : str
        File in which are stored the definitions in Markdown format.
    """
    defs = {}
    with open(filename, 'r') as f:
        var_name = ''
        for l in f.readlines():
            if l.startswith('##'):
                var_name = l[2:].strip()
                defs[var_name] = []
            elif l.startswith('- '):
                defs[var_name].append(l[2:].strip())
    return defs

begin_sentence = """# World3 definitions
Definitions in french and english, but differently formatted,
in order to write transalations by hand more easily.
Go to file get_definitions.py to convert this file to jso.

Syntax:
Variable name should begin by a '## ' and definitions in english and then french are at the two next lines begining by a '- '.
"""

def write_translated_defs(filename, defs):
    """Write definitions that are in the dictionnary defs
    in markdown format in the filename.

    Parameters
    ----------
    filename : str
        File in which to write the definitions in markdown format.
    defs : dict
        Definitions.
    """
    
    with open(filename, 'w+') as f:
       f.write(begin_sentence)
       for k in defs:
           f.write(f'## {k}\n')
           f.write(f'- {defs[k][0]}\n')
           f.write(f'- {defs[k][1]}\n')

        
# import json

# From markdown to definitions dict
# translated_defs = read_translated_defs('translated_defs.md')

# From definitions dict to markdown
# with open('translated_defs.json', 'w+') as f:
    # json.dump(translated_defs, f)

# # From json to dict    
# with open('translated_defs.json', 'r') as f:
#     translated_defs = json.load(f)
    
