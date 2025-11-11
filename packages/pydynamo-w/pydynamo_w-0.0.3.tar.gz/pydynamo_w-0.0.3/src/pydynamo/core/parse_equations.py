"""Functions used to read and parse equations written with a pydynamo syntax. There is functions to get the equation type (constant, update, initialisation) and the arguments (variables, constants, indices)."""

import ast
import astunparse
import re

# Functions that are not considered as pydynamo "special functions" 
math_fun = {'sqrt', 'exp', 'log'} # Math functions that we can use
not_parse_fun = math_fun.union(__builtins__) # Merged with all builtins

def change_points_to_underscores(line, variables):
    """Change the points of indices `k` and `j` to underscores.

    Parameters
    ----------
    line : str
        Equation to change.
    variables : iterable((str, str))
        List of (variable name, index name) in the equation.

    Returns
    -------
    str
        Equation changed.
    """ 
    for v, i in variables:
        line = re.sub(f'(?!<\w){v}.{i}(?!\w)', f'{v}_{i}', line)
    return line

def reformat_eq(root, variables):
    """Format a parsed equation to a string equation.

    Parameters
    ----------
    root : ast.Module
        Equation.
    variables : iterable((str, str))
        List of (variable name, index name) in the equation.

    Returns
    -------
    str
        Equation on string format.
    """
    line = astunparse.unparse(root)
    line = change_points_to_underscores(line, variables)
    return line.strip()

def is_eq(root):
    """Determines if a parsed line is an equation or not.
    
    Parameters
    ----------
    root : ast.Module
        Equation.

     Returns
    -------
    bool
        True if `root` is an equation (of type Assign), False otherwise.
    """
    try:
        return isinstance(root.body[0], ast.Assign)
    except:
        return False

def is_cst_eq(root):
    """Determines if a parsed line is an equation for a constant or not.
    
    Parameters
    ----------
    root : ast.Module
        Equation.
    """
    if is_eq(root):
        return isinstance(root.body[0].targets[0], ast.Name)

def is_variable_eq(root):
    """Determines if a parsed line is an equation for a variable or not.
    
    Parameters
    ----------
    root : ast.Module
        Equation.
    """
    if is_eq(root):
        return isinstance(root.body[0].targets[0], ast.Attribute)

def is_update_eq(root):
    """Determines if an equation for a variable is an update equation or not.
    
    Parameters
    ----------
    root : ast.Module
        Equation.
    """
    return is_variable_eq(root) and root.body[0].targets[0].attr == 'k'

def is_init_eq(root):
    """Determines if an equation for a variable is an initialisation equation or not.
    
    Parameters
    ----------
    root : ast.Module
        Equation.
    """
    return is_variable_eq(root) and root.body[0].targets[0].attr == 'i'

def is_eq_of_type(root, eq_type):
    """Determines if an equation is of a certain type ('cst', 'init', 'update').
    
    Parameters
    ----------
    root : ast.Module
        Equation.
    eq_type : str
        Equation type, one of 'cst', 'init', 'update'.
    """
    if is_cst_eq(root):
        return  'cst'  == eq_type
    if is_init_eq(root):
        return 'init'  == eq_type
    if is_update_eq(root):
        return 'update' == eq_type
    return False

def get_pars_update_eq(line):
    """Get parameters of an equation if it's an update equation.
    
    Parameters
    ----------
    line : str
        Equation.
    
    Returns
    -------
    (str, dict)
        Tuple with the name of the updated variable, and a dictionnary containing the arguments and the new equation line.
    """
    root = ast.parse(line)
    assert is_update_eq(root), f'Not an update equation: {line}'
    var = root.body[0].targets[0].value.id
    args = get_var_cst_fun(root.body[0].value)
    return (var,
            {'args': args,
             'line': reformat_eq(root.body[0].value, args['var'])})

def get_pars_init_eq(line):
    """Get parameters of an equation if it's an initialisation equation.
    
    Parameters
    ----------
    line : str
        Equation.
    
    Returns
    -------
    (str, dict)
        Tuple with the name of the initialized variable, and a dictionnary containing the arguments and the new equation line.
    """
    root = ast.parse(line)
    assert is_init_eq(root), f'Not a initialisation equation: {line}'
    var = root.body[0].targets[0].value.id
    args = get_var_cst_fun(root.body[0].value)
    return (var,
            {'args': args,
             'line': reformat_eq(root.body[0].value, args['var'])})

def get_pars_cst_eq(line):
    """Get parameters of an equation if it's an constant equation.
    
    Parameters
    ----------
    line : str
        Equation.
    
    Returns
    -------
    (str, dict)
        Tuple with the name of the constant, and a dictionnary containing the arguments and the new equation line.
    """
    root = ast.parse(line)
    assert is_cst_eq(root), f'Not an constant equation: {line}'
    cst = root.body[0].targets[0].id
    args = get_var_cst_fun(root.body[0].value)
    return (cst,
            {'args': args,
             'line': reformat_eq(root.body[0].value, args['var'])})

def get_var_cst_fun(root):
    """Get every constants, variables and special functions contained in the equation.
    
    Parameters
    ----------
    root : ast.Module
        Equation.
    
    Returns
    -------
    dict(str: set)
        A dictionnary which contains the set of constants, variables and functions names.
    {'cst': set(str), 'var': set((str, str)), 'fun': dict(str: {'args': list(str), 'type': str, 'fun': str})}
    """
    list_params = list()
    all_names = set()
    all_vars = set()
    all_nps_funs = set()
    all_fun = dict()
    for node in ast.walk(root):
        if isinstance(node, ast.Name):
            all_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            all_vars.add((node.value.id, node.attr))
        elif isinstance(node, ast.Call):
            assert isinstance(node.func, ast.Name), f"Function call can only be a name: {astunparse.unparse(node.func)}"
            if node.func.id not in not_parse_fun:
                arg_fun = {'args': [astunparse.unparse(arg)
                                              for arg in node.args],
                           'type': node.func.id,
                           'fun': node.func.id}
                all_fun[node.func.id] = arg_fun
            else:
                all_nps_funs.add(node.func.id)
    return {'cst': {c for c in all_names.difference(v for v, i in all_vars).difference(all_fun).difference(all_nps_funs)
                    if c not in math_fun},
            'var': all_vars,
            'fun': all_fun}

def get_pars_eq(root, eq_type):
    """Get parameters of an equation.
    
    Parameters
    ----------
    root : ast.Module
        Equation.
    eq_type : str
        Equation type, one of 'cst', 'init', 'update'.
    Returns
    -------
    (str, dict) 
        Variable or constant name, and parameters.
    """
    if 'cst'  == eq_type:
        return get_pars_cst_eq(root)
    elif 'update'  == eq_type:
        return get_pars_update_eq(root)
    elif 'init'  == eq_type:
        return get_pars_init_eq(root)
    return (None,
            {'var': set(),
             'fun': set()})
