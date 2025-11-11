""" Functions used to get appropriate parameters in case a pydnamo "special function" (smooth, tabhl ...) is read in an equation.
"""

import ast
from astunparse import unparse
from .parse_equations import reformat_eq

# List of special functions to handle
instance_fun_names = {'smooth', 'sample', 'dlinf3', 'delay3', 'tabhl', 'step'}

   
def change_and_get_params(node, node_name):
    """Get information needed to call the special function in the `node`, and also change the `node` to include appropriate parameter names.

    Parameters
    ----------
    node : ast.Module
        Function call to handle.
    node_name : str
        Name of the node (variable or constant) which uses this function to be upated. This name is useful to determine the new name of the function (es: `tabhl_io` for the funciton `tabhl` and the updated variable `io`.
    
    Returns
    -------
    dict
        All useful information to generate the special function. Depends on the type of the function.
    """
    name = node.func.id

    # For every type of special function, different treatments apply.
    
    if name == 'tabhl':
        params = {'table': node.args[0].id,
                'val': unparse(node.args[1]),
                'x_low': unparse(node.args[2]),
                'x_high': unparse(node.args[3]),
                'x_incr': unparse(node.args[4])}
        new_fun_name = f"tabhl_{node_name}"
        params['fun'] = new_fun_name
        node.args = [node.args[1]]


    elif name in  {'smooth', 'dlinf3', 'delay3'}:
        params = {'val': node.args[0].value.id,
                  'delay': unparse(node.args[1]).strip()}
        new_fun_name = f"{name}_{node_name}"
        params['fun'] = new_fun_name
        node.args = [node.args[0], node.args[1], ast.Name('k')]

        
    elif name == 'sample':
        params = {'fun': f'sample_{node_name}',
                  'isam': unparse(node.args[2])}
        node.args.append(ast.Name('k'))

    elif name == 'step':
        params = {'fun': 'step'}
        node.args.append(ast.Name('k'))
        
        
    params['type'] = name
    return params
    
def get_dynamo_fun_params(root, node_name):
    """Get information needed to execute the equation `node`, and also change `node` with appropriate parameters.

    Parameters
    ----------
    node : ast.Module
        Equation.
    node_name : str
        Name of the node (variable or constant) which uses this function to be upated. This name is useful to determine the new name of the function (es: `tabhl_io` for the funciton `tabhl` and the updated variable `io`.
    
    Returns
    -------
    (ast.Module, dict)
        The modified node and all useful information to generate the equation.
    """
    root = root.body[0].value

    # The node is walked through to detect and change a special function call
    # Only one special DYNAMO function is allowed in an equation ...
    for node in ast.walk(root):
        if isinstance(node, ast.Call):
            if node.func.id in instance_fun_names:
                 params = change_and_get_params(node, node_name)
                 return root, params
    return (None, None)
