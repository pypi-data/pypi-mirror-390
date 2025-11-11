"""
Functions to convert a file in DYNAMO to pydynamo syntax.
"""

import re

def convert_dynamo_file(DYNAMO_file, pydynamo_file):
    """Create a new file with pydynamo equations from DYNAMO equations file.
    
    Parameters
    ----------
    DYNAMO_file : str
        File name of DYNAMO code.
    pydynamo_file : File name of the pydynamo code which will be created.
    """
    with open(new_file, 'w+') as nf:
        with open(filename, 'r') as f:
            for l in f.readlines():
                nf.write(dy2pydy(l))
                
def dy2pydy(l):
    """Convert a DYNAMO equation line to a pydynamo syntax equation.
    
    Parameters
    ---------
    l : str
        DYNAMO equation.
    """ 
    l = re.sub('^[ATRCLS] ', '', l)
    l = re.sub('^N (\w*)', '\\1.i', l)        
    l = re.sub('(?!<\w)smooth\((\w+?)\.k(?!\w)', 'smooth(\\1.j',l)
    l = re.sub('\.kl', '.k', l)
    l = re.sub('\.jk', '.j', l)
    return l
