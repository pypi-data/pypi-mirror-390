"""Functions to parse an entire pydynamo code and generate a System object. Also defines every political changes.
"""
import ast
import inspect

from .parse_equations import *
from .parse_dynamo_functions import get_dynamo_fun_params
from .specials import step, clip

def comment_from_equation(line):
    """Retrieve comment by removing '#' and additional spaces.
    """
    if '#' in line:
        return line.split('#', 1)[1].strip()
    return ''

def get_system_dicts(lines):
    """

    Parameters
    ----------
    lines : iterable(str)
        List of every equations.
    
    Returns
    -------

    (dict, dict, dict)
        Nodes (variable, constants and functions), equations (constant, update and initialisation) and comments parsed in the equations list.
    """
    
    all_eqs = {name: dict() for name in ['cst', 'update', 'init']}
    all_nodes = {name: set() for name in ['cst', 'var', 'fun']}
    comments = {}

    # For each equation, try to detect its type and retrive informations.
    for l in lines:
        root = ast.parse(l)
        type_is_identified = False
        
        for eq_type in all_eqs.keys():
            if is_eq_of_type(root, eq_type):
                type_is_identified = True

                # Get assigned node and equation arguments
                try:
                    node, args = get_pars_eq(root, eq_type)
                    args['raw_line'] = l.split('#')[0].strip()
                except:
                    raise Exception("Error while parsing line:\n"+l)
                
                # Add comment
                com = comment_from_equation(l)
                if com != '' or node not in comments:
                    comments[node] = com

                # Add equation
                all_eqs[eq_type][node] = args

                # Handle special functions
                new_line, fun_args = get_dynamo_fun_params(root, node)
                if new_line:
                    all_eqs[eq_type][node]['line'] = reformat_eq(new_line, args['args']['var'])
                if fun_args:
                    all_eqs[eq_type][node]['args']['fun'][fun_args['type']] = fun_args

                # Add assigned node
                if eq_type == 'cst':
                    all_nodes['cst'].add(node)
                else:
                    all_nodes['var'].add(node)

                # Add needed nodes
                for arg_node in args['args']['fun']:
                    if arg_node not in __builtins__:
                        all_nodes['fun'].add(arg_node)

                            
        if root.body and not type_is_identified:
            raise(SyntaxError(f"Invalid equation:\n {l}"))

    return all_nodes, all_eqs, comments


def list_from_file(filename, s=None, prepare=True):
    """Get a list of equatinos from a file with pydynamo equations.
    Parameters
    ----------
    filename : str
        Files in which every pydynamo equations are written.
    """
    check_file(filename)
    with open(filename, 'r') as f:
        return f.readlines()

def list_from_function(fun, s=None, prepare=True):
    """Get a list of equations from a function which lists pydynamo equations.

    Parameters
    ----------
    fun : function
        Function in which every pydynamo equations are written.

    Examples 
    --------
    Just write pydynamo equations inside a function, and create a System with it:
    >>> def custom_equations():
    >>>     pop.i = 100
    >>>     pop.k = pop.j /2 # Population
    >>> list_of_equations = list_from_function(custom_equations)
    """
    return [l.strip() for l in inspect.getsource(fun).split('\n')[1:]]

def check_file(filename):
    """Check if every line in the file can be parsed by the ast module. If not, raise an error.
    Parameters
    ----------
    filename : str
        Files in which every pydynamo equations are written.
    """
    with open(filename, 'r') as f:
        for i, l in enumerate(f.readlines()):
            try:
                ast.parse(l)
            except SyntaxError as e:
                e.filename = filename
                e.lineno = i + 1
                raise
