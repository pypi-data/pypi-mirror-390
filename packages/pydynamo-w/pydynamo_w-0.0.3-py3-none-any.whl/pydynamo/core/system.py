"""Define the System class, base class to simulate system dynamics from equations.
"""
import inspect
import numpy as np
from itertools import chain
import re

from .specials import clip, Sample, step, Interpol
from .delays import Delay3, Dlinf3, Smooth
from .parse_dynamo_functions import instance_fun_names
from .parse_system import get_system_dicts, list_from_function, list_from_file
from math import log, exp, sqrt
np.seterr(all='raise')


class System:
    """
    Base class for system dynamics.

    A System stores 3 dictionnaries that contains:
        - nodes (constants, variables, and functions)
        - equations (constant values, updating equations and initialisation equations)
        - comments about nodes.

    From this dictionnaries, it generates the updating pattern
    and run the simulation.
    """
    
    from .plot_system import plot, plot_non_linearity, plot_compare, show_influence_graph
    from .politics import new_cst_politic, new_var_politic, new_table_politic, new_politic
    from .graph import get_cst_graph, get_init_graph, get_update_graph, get_influence_graph, set_order
    from .graph import assert_cst_acyclic, assert_init_acyclic, assert_update_acyclic
    
    def __init__(self, code=None, prepare=True):
        """Initialise a System, empty or from pydynamo code.

        Parameters
        ----------
        code : str, iterable(str) or function
            If str, open the file named `code` and read pydynamo equations inside (see `parse_system.nec_from_file`). If iterable(str), each element is a pydynamo equations (see `parse_system.nec_from_lines`). If function, read pydynamo equations written inside the function (see `parse_system.nec_system_from_fun`).
        
        prepare : bool
            If True, prepare the System to run (see `System.prepare`).

        Examples
        --------
        With a file:
        Suppose there is the following lines inside the file `pydynamo_equations.py`:
        ```
        pop.k = pop.j*2 # Population
        pop.i = popi
        popi = 25 # Initial population
        ```
        >>> s = System("pydynamo_equations.py')
        
        With a list of equations:
        >>> equations_list = ['pop.k = pop.j*2', 'pop.i = popi', 'popi = 25']
        >>> s = System(equations_list)

        With a function:
        >>> def equations_function():
        >>>     pop.k = pop.j*2 # Population
        >>>     pop.i = popi
        >>>     popi = 25 # Initial population
        >>> 
        >>> s = System(equations_function)
        """
        self.comments = {}
        # If code is given, create a System with equations
        if code:
            if isinstance(code, list):
                self.code_lines = code
            elif callable(code):
                self.code_lines = list_from_function(code)
            elif isinstance(code, str):
                self.code_lines = list_from_file(code)

            self.reset_eqs(prepare)
            
        # Otherwise, create an empty System
        else:
            self.nodes = {
                'cst': set(),
                'var': set(),
                'fun': set(),
            }
            
            self.eqs = {
                'cst': dict(),
                'update': dict(),
                'init': dict()
            }
            self.code_lines = []

        self.political_changed = set()
            
    def add_equations(self, new_code_lines):
        """Add new equations to the older ones. 
        In case there is a conflict for a same variable or constant, the last equation only is remembered.
        
        Parameters
        ----------
        new_code_lines : list(str)
            Pydynamo equations to add.
        """
        self.code_lines = self.code_lines + new_code_lines
        
    def reset_eqs(self, prepare=True):
        """Set all nodes, equations and comments.
        """
        self.nodes, self.eqs, new_comments = get_system_dicts(self.code_lines)

        # Keep old comments
        for node, comment in new_comments.items():
            if comment != '':
                self.comments[node] = comment
        
        if prepare:
            self.prepare()

    def add_comments(self, comments):
        """Add comments to the System.

        Parameters
        ----------
        comments : dict(str: str)
            Each node name and its comment.
        """

        for node, comment in comments.items():
            self.comments[node] = comment
            
    # Getters    
    def get_all_variable_names(self):
        """
        Get the set of all variables.

        Returns
        -------
        set(str):
            Set of names of all variables
        """
        return set(self.nodes['var'])

    def get_var_names(self):
        """Return every variables names.
        
        Returns
        -------
        list(str)
            List of variables names.
        """
        return list(self.nodes['var'])
    
    def get_var(self, name):
        """Get the variable array.

        Parameters
        ----------
        name: str
            Name of variable.

        Returns
        -------
        np.array(float):
            Array of values of the variable for the last run.
        """

        assert name in self.nodes['var'], f"{name} is not a variable"
        return getattr(self, name)
        
    
    def get_out_nodes(self, node, with_definitions=False):
        """Returns the list of the nodes using the node to be computed.

        Parameters
        ----------
        node: str
            Name of the node
        
        with_definitions: bool
            If yes, returns a dictionnary with each node definition.
        """
        
        out_nodes = [b for (a, b) in self.get_influence_graph().out_edges(node)]
        if with_definitions:
            return {a: self.definition(a) for a in out_nodes}
        else:
            return out_nodes
        
    def get_in_nodes(self, node, with_definitions=False):
        """Returns the list of the nodes that this node needs to be computed.

        Parameters
        ----------
        node: str
            Name of the node
        
        with_definitions: bool
            If yes, returns a dictionnary with each node definition.
        """
        
        in_nodes =  [a for (a, b) in self.get_influence_graph().in_edges(node)]
        if with_definitions:
            return {a: self.definition(a) for a in in_nodes}
        else:
            return in_nodes
    
    def get_at(self, var, t):
        """Returns the value of var at time t, or an interpolation if between rwo timestep values.
        
        Parameters
        ----------
        var : str
            Variable name.
        
        t : float
            Time.
        """
        assert var in self.nodes['var'], f"{var} is not a variable"
        assert var in dir(self), "Simulation hasn't been run yet !"
        assert t >= self.initial_time and t <= self.final_time, "{t} is out of bounds {self.initial_time}, {s.final_time}"

        if t == self.final_time:
            return getattr(self, var)[-1]
        
        idx1 = np.arange(len(self.time))[self.time <= t][-1]
        dd = (self.time[idx1] - t)/self.dt
        v = getattr(self, var)
        return v[idx1]*(1 - dd) + v[idx1 + 1]*dd

    def __getitem__(self, arg):
        """Get item at a certain date. See System.get_at.
        
        Parameters
        ----------
        arg : str, float
            Variable name and time.
        """
        try:
            name, year = arg
            return self.get_at(name, year)

        except TypeError:
            return getattr(self, arg)
        
    def get_time(self):
        """Returns the time array.

        Returns
        -------
        np.array(float):
            Array of system time.
        """
        return self.time

    def get_tabhl_args(self, name):
        """
        Get indications about a tabhl function.

        Parameters
        ----------
        name: str
            Name of the variable using a tabhl function.

        Returns
        -------
        np.array, np.array, str, str, str:
            x, f(x), x label, y label, title
        """

        
        if not 'tabhl_' + name in dir(self):
            # Case it's not a tabhl function, check if it's a clip from 1 to 2
            try:
                a, b, *_ = self.eqs['update'][name]['args']['fun']['clip']['args']
                name = re.sub(r'\.[jk]', '', b.strip())
            except KeyError:
                raise Exception(f"Error, {name} is not updated with a non linear function, and is not a switch between to variables with a non linear function") from None

        aa = list(self.eqs['update'][name]['args']['var'])
        argname = aa[0][0].split('.')[0]
        f = getattr(self, 'tabhl_' + name)
        x = np.linspace(f.xl, f.xh, 100)
        ylabel = name + '\n'+ self.definition(name)
        argop = self.eqs['update'][name]['args']['fun']['tabhl']['val'].strip()
        argop = re.sub(r'^\(|\)$', '',re.sub(r'\.[jk]', '', argop)).strip()
        xlabel = argop + ('\n'+ self.definition(argname) if argop==argname else '')
        return x, f(x), ylabel, xlabel, f"{name} non-linear function"

    def definition(self, node):
        """Get the definition of a node.

        Parameters
        ----------
        node : str
            Name of the variable or constant to get the definition.
        """
        try:
            return self.comments[node]
        except:
            return ''


    def equation(self, node):
        """Returns the reformatted equation of a variable or constant.

        Parameters
        ----------
        node : str
            Name of the variable or constant to show the equation.
        """
        
        for t, eqq in self.eqs.items():
            if node in eqq:
                try:
                    if 'tabhl' in eqq[node]['raw_line']:
                        return f'{node}.k = ' + re.sub('tabhl', f'NLF_{node}t', re.sub(r'\_([jk])', '.\\1', eqq[node]['line']))
                    return self.raw_equation(node)
                except:
                    print(node, eqq)
                    return ''

    def raw_equation(self, node):
        """Returns the pydynamo raw equation of a variable or constant.

        Parameters
        ----------
        node : str
            Name of the variable or constant to get the raw pydynamo equation.
        """
        for t, eqq in self.eqs.items():
            try:
                return eqq[node]['raw_line']
            except:
                pass
        return ''

    # Infos
    def is_initialized(self, var):
        """Indicates if a var is initialized or not.

        Parameters
        ----------
        var : str
            Variable name.
        """
        return var in self.eqs['init']

    def is_table(self, name):
        """Indicates if a name is a table.
        
        Parameters
        ----------
        name : str
            Name of the node.
        """
        if name in self.nodes['cst']:
            cst = getattr(self, name)
            if isinstance(cst, np.ndarray) or isinstance(cst, list):
                return True
        return False

    # Assertions
    def assert_cst_defined(self):
        """Assert that every constant has an equation to be computed.
        """
        for c in self.nodes['cst']:
            assert c in self.eqs['cst'], f'Error: Constant {c} is not defined in any constant equation'

    def assert_update_defined(self):
        """Assert that every variable has an updating equation to be computed.
        """
        for v in self.nodes['var']:
            assert v in self.eqs['update'], f'Error: Variable {v} is not updated in any equation'

    def assert_init_defined(self):
        """Assert that every variable has an initialisation or updated equation to be computed.
        """
        for v in self.nodes['var']:
            assert (v in self.eqs['init']
            or v in self.eqs['update']) , f'Error: Variable {v} neither updated nor initialized'

    # Functions setting
    def set_fun(self, node, fun_name, args, line):
        """Set an updating, initialisation or constant setting function to the System. It evaluates a lambda function with the line equation inside.
        
        Parameters
        ----------
        node : str
            Constant or variable name.
        
        fun_name : str
            Name of function
        
        args : iterable(str)
            Arguments of the function.
        
        line : str
            Formula with wich the `node` is computed (set, initialised orupdated).
        """
        line = line.strip()
        args_str = ', '.join(args)
        fun_str = f'lambda {args_str}: {line}'
        doc = f'Get the value of {node} depending on {args}'

        # Function settings
        fun = eval(fun_str)    
        fun.__name__ = fun_name
        fun.__doc__ = doc
        fun.__line__ = line
        fun.__okdic__ = True
        fun.__custom_repr__ = f"{fun_name}({args_str})"
        fun.__str__ = lambda : f'System custom function {fun_name}({args})'

        setattr(self, fun_name, fun)

    def set_all_funs(self):
        """For each equation, set the appropriate function to the System.
        """
        for eq_type in self.eqs:
            for node in self.eqs[eq_type]:
                getattr(self, f'set_{eq_type}_fun_from_dict')(node)

    def set_cst_fun_from_dict(self, node):
        """For each constant equation, set the appropriate function to the System.
        """
        args = self.eqs['cst'][node]['args']
        line = self.eqs['cst'][node]['line']

        self.set_fun(node,
                     'set_' + node,
                     args['cst'],
                     line)

    def set_update_fun_from_dict(self, node):
        """For each updating equation, set the appropriate function to the System.
        """
        args = self.eqs['update'][node]['args']
        line = self.eqs['update'][node]['line']
        
        args_vars = ['_'.join(v_i) for v_i in args['var']]
        args_cst = list(args['cst'])
        arg_fun = []
        for fun_type in self.eqs['update'][node]['args']['fun']:
            p =  self.eqs['update'][node]['args']['fun'][fun_type]
            if p:
                arg_fun.append(p['type'])
        if arg_fun:
            arg_fun.append('k')

        self.set_fun(node,
                     'update_' + node,
                     args_vars + args_cst + arg_fun,
                     line)

        
    def set_init_fun_from_dict(self, node):
        """For each initialisation equation, set the appropriate function to the System.
        """
        args = self.eqs['init'][node]['args']
        line = self.eqs['init'][node]['line']
        args_vars = [v + '_' + i for v, i in args['var']]
        args_cst = list(args['cst'])

        for fun_type in self.eqs['init'][node]['args']['fun']:
            p =  self.eqs['init'][node]['args']['fun'][fun_type]
            if p != {}:
                arg_fun.append('k')
                arg_fun.append(p['type'])

        self.set_fun(node,
                     'init_' + node,
                     args_vars + args_cst,
                     line)

    # Simulation
    def get_cst_val(self, cst, args):
        """Get the value of a constant according to its equation and arguments.
        
        Parameters
        ----------
        cst : str
            Name of the constant.
        
        args : dict(str, value)
            Values of each arguments.
        """
        fun = getattr(self, 'set_' + cst)
        try:
            value = None
            value = fun(**args)
            if '__iter__' in dir(value):
                value = np.array(value)
            return value

        except Exception as e:
            raise(Exception(f"Error setting {cst}\n"
                            f" wih function {fun.__custom_repr__}\n"
                            f" with given args: {', '.join(args)}\n"
                            f" and line:\n"
                            f"{self.eqs['cst'][cst]['line']}\n\n"
                            f"Error: {e}\n"
                            f"Arg values: {args}\n"
                            f"Returned value: {value}")) from None

    def set_cst(self, cst, args):
        """Set a constant according to its equation and arguments.
        
        Parameters
        ----------
        cst : str
            Name of the constant.
        
        args : dict(str, value)
            Values of each arguments.
        """
        setattr(self, cst, self.get_cst_val(cst, args))

    def set_all_csts(self):
        """Set every constant constant according to its equation and arguments ONLY IF the constant is not set yet.
        """
        
        for cst in self.set_order('cst'):
            try:
                arg_names = self.eqs['cst'][cst]['args']['cst']
                args = {name: getattr(self, name) for name in arg_names}
            except KeyError as k:
                use_eqs = '\n'.join(f"{node} = {self.eqs['cst'][node]['line']}"
                                    for node in G.successors(cst))
                raise Exception(f"Error in setting constants {cst}, used in:\n"
                                f"{use_eqs}\n"
                                f"Constant {k.args[0]} is never set.") from None

            if not cst in dir(self):
                self.set_cst(cst, args)

    def generate_var(self, var, N):
        """Initialise an empty array for a variable.
        
        Parameters
        ----------
        var : str
            Variable name.
        
        N : int
            Size of simulation.
        """
        setattr(self, var, np.full(N, np.nan))

    def generate_all_vars(self, N):
        """Initialise an empty array for every variable.
        
        Parameters
        ----------
        N : int
            Size of simulation.
        """
        for v in self.nodes['var']:
            self.generate_var(v, N)


    def set_special_fun(self, p):
        """Set the special function from its parameters.
        
        p : dict
            Parameters of the function to be set.
        """
        f_type = p['type']
        for f_name, f_Class in [('delay3', Delay3),
                                ('smooth', Smooth),
                                ('dlinf3', Dlinf3)]:
            if f_type == f_name:
                fun = f_Class(self.dt)
                setattr(self, p['fun'], fun)

        if f_type == 'tabhl':
            x_low = eval(p['x_low'])
            x_high = eval(p['x_high'])
            x_incr = eval(p['x_incr'])
            table = getattr(self, p['table'])
            fun = Interpol(x_low, x_high, x_incr, table)
            setattr(self, p['fun'], fun)

        if f_type == 'sample':
            isam = eval(p['isam'])
            fun = Sample(isam, self.time)
            setattr(self, p['fun'], fun)

        if f_type == 'step' or type =='clip':
            pass

    def step(self, hght, sttm, k):
        """Step function. See specials.step.
        """
        return step(hght, sttm, self.time[k])

    def clip(self, v2, v1, t, y):
        """Clip function. See specials.clip.
        """
        return clip(v2, v1, t, y)
    
    def set_all_special_functions(self):
        """
        Generate every special dynamo functions that are stored.
        Constants (especially tables and delays) have to be initialized before.
        """
        for node in self.eqs['update']:
            fun_dic = self.eqs['update'][node]['args']['fun']
            for fun_name, fun_args in fun_dic.items():
                if fun_args != {}:
                    self.set_special_fun(fun_args)

    def _init_all(self):
        """Initialise every variable. Iterate over the initialisaition order and set the first value of each variable.
        """
        for var in self.set_order('init'):
            if self.is_initialized(var):
                update_fun = getattr(self, 'init_' + var)
                args = self.eqs['init'][var]['args']
                var_args = {v + '_' + i: getattr(self, v)[0] for v, i in args['var']}
                fun_args = dict()

            else:
                update_fun = getattr(self, 'update_' + var)
                args = self.eqs['update'][var]['args']
                var_args = {v + '_' + i: getattr(self, v)[0] for v, i in args['var']}
                fun_args = dict()

                for fun_type in self.eqs['update'][var]['args']['fun']:
                    p = self.eqs['update'][var]['args']['fun'][fun_type]
                    if p != {}:
                        fun_args[p['type']] = getattr(self, p['fun'])
                        fun_args['k'] = 0
            cst_args = {c: getattr(self, c) for c in args['cst']}

            # Assert that there is no variables considered as constants etc.
            tps = {'cst', 'var', 'fun'}
            dd = locals()
            
            for t, n, tt in ((t, n, tt) for t in tps
                         for tt in tps.difference({t})
                         for n in dd[tt + '_args']):
                # if tt == 'var':
                #         n = re.sub(r'\_[jk]', '', n)
                
                if n in self.nodes[t]:
                    line = self.eqs['update'][n]['line']
                    if n in self.eqs['init']:
                        line = self.eqs['init'][n]['line']

                    msg = ''.join((
                    f'Wrong call of {n}',
                    f' (which is of type {t})\n',
                    f'{var} = ',
                    line))
                    raise(AssertionError(msg))            
            self._update_variable(var, 0, update_fun, {**var_args, **cst_args, **fun_args}, init=True)

    def set_update_loop(self):
        """
        Set the update loop list, stored as _update_loop.
        The list contains all information we need to update each variable,
        and is ordered in the topological order of the updating graph
        """
        self._update_loop = []
        for var, i in self.set_order('update'):
            if i == 'k':
                u = {'var': var}
                try:
                    args = self.eqs['update'][var]['args']

                    u['cst_args'] = {c: getattr(self, c) for c in args['cst']}
                    u['var_args'] = {v + '_' + ni: (getattr(self, v), 0 if ni == 'k' else -1)
                                     for v, ni in args['var']}
                    u['fun_args'] = dict()
                    for fun_type in self.eqs['update'][var]['args']['fun']:
                        p = self.eqs['update'][var]['args']['fun'][fun_type]
                        u['fun_args'][p['type']] =  getattr(self, p['fun'])
                        u['fun_args']['k'] = None

                    u['update_fun'] = getattr(self, 'update_' + var)
                    self._update_loop.append(u)

                except AttributeError as e:
                    line = self.eqs['update'][var]['line']
                    raise(AttributeError(f"In updating {var}:\n"
                                         f"{var} = {line}\n"
                                         f"{e}")) from e

                # Assert that there is no variables considered as constants etc.
                tps = {'cst', 'var', 'fun'}
                for t, n, tt in ((t, n, tt) for t in tps
                         for tt in tps.difference({t})
                         for n in u[tt + '_args']):
                    if tt == 'var':
                        n = re.sub(r'\_[jk]', '', n)
                    assert n not in self.nodes[t], ''.join((
                        f'Wrong call of {n}',
                        f' (which is of type {t})\n',
                        f'{var}.{i} = ',
                        self.eqs['update'][var]['line']))


    def _update_all_fast(self, k):
        """Update every variable. Iterate over the updating order graph and set the k-th value of each variable.
        
        Parameters
        ----------
        k : int
            Current number of step.
        """

        for u in self._update_loop:
            if 'k' in u['fun_args']:
                u['fun_args']['k'] = k
            self._update_variable(u['var'], k, u['update_fun'],
                        {**{v: t[k+i] for v, (t, i) in u['var_args'].items()},
                         **u['cst_args'],
                         **u['fun_args']})

    def _update_variable(self, var, k, fun, args, init=False):
        """Update a variable at step `k` from its function and arguments.
        
        Parameters
        ----------
        var : str
            Variable name.
        
        k : int
            Step number.
        
        fun : function
            Function which updates variable.
    
        args : dict(str, value)
            Arguments of the function with their values.

        init : bool
            Indicates if it's an initialisation update.
        """
        try:
            # getattr(self, var)[k] = fun(**args)
            # For (small) gain in perfs, uncomment above and comment beside
            value = None
            array = getattr(self, var)
            value = fun(**args)
            assert value is not np.nan, "Error, value is nan"
            array[k] = value
        except Exception as e:
            if not init:
                eq = self.eqs['update'][var]['line']
                err = "Error updating"
            else:
                eq = self.eqs['init'][var]['line']
                err = "Error initialising"
            raise(Exception(f"{err} {var}\n"
                            f" at index {k}\n"
                            f" wih function {fun.__custom_repr__}\n"
                            f" with given args {', '.join(args)}\n"
                            f" and line:\n"
                            f"{eq}\n\n"
                            f"Error: {e}\n"
                            f"Arg values: {args}"
                            f"Returned value: {value}"))


    def prepare(self):
        """Assert that all equations are well defined, ant that the updating graph is acyclic. Also set all updating functions and constants.
"""
        self.assert_cst_defined()
        self.assert_init_defined()
        self.assert_update_defined()
        self.assert_cst_acyclic()
        self.set_all_funs()
        self.set_all_csts()

    def change_functions_in_dict(self):
        """
        In case some functions are re-defined by user,
        modify dependencies in parameters.
        """
        for f_type in ('update', 'init'):
            for f_name in (name for name in dir(self)
                           if name.startswith(f'{f_type}_')):
                fun = getattr(self, f_name)
                var = f_name.split('_', 1)[1]
                if ('__okdic__' not in dir(fun)) or (not fun.__okdic__):
                    self.nodes['var'].add(var)
                    args = inspect.getargs(fun.__code__).args
                    if fun.__doc__:
                        self.comments[var] = fun.__doc__
                    fun.__doc__ = f"User defined, {f_type} {var}"
                    fun.__custom_repr__ = f_name
                    dargs = {'cst':set(), 'var':set(), 'fun':dict()}
                    for arg in args:
                        if len(arg) > 2 and arg[-2:] in {'_k', '_j'}:
                           dargs['var'].add((arg[:-2], arg[-1]))
                        else:
                           dargs['cst'].add(arg)
                    self.eqs[f_type][var] = {'args':dargs,'line': None}
                    fun.__okdic__ = True

    

    def run(self, N=None, dt=1):
        """
        After preparing and before running,
        an user can redefine some constants,
        or assign update or init functions,
        with the following syntax:
        >>> system.c = 1 # New value for constant c
        >>> # New function to update v1
        >>> # using variable v1 at index j and constant c1:
        >>> def new_update(v2_j, c1):
               \"""Variable 2 documentation\"""
        >>>    return v2_j + c1
        >>> system.update_v1 = new_update # New fct for updating v1
        >>> s.run(10, 1) # Run with new parameters
        """

        # Change functions if manually modified, then check acyclicity
        self.change_functions_in_dict()
        self.assert_update_acyclic()
        self.assert_init_acyclic()


        # Set time steps, either with N steps of dt,
        # or a defined intitial and final time
        try:
            if not N:
                N = int((self.final_time - self.initial_time)/dt)
            else:
                self.final_time = self.initial_time + N * dt
        except:
            raise Exception("Either pass N or define both final_time and initial_time")
        self.time = self.initial_time + np.arange(N)*dt
        self.dt = dt
        
        self.generate_all_vars(N)
        self.set_all_special_functions()
        self.set_update_loop()
        self._init_all()
        for k in range(1, N):
            self._update_all_fast(k)

    def copy(self, prepare=True):
        """Returns a copy of the model, with 

        Parameters
        ----------
        prepare : bool
            If yes, prepare the system to run.
        """
        
        s = System(self.code_lines.copy())
        for cst in self.nodes['cst']:
            setattr(s, cst, getattr(self, cst))
        return s

    
    def get_different_csts(self):
        """Returns every variable which value is different than in the equations and their, abnd its new value.
        
        Returns 
        -------
        dict(str: (float, float))
            Dictionnary with each name, and its corresponding old and new value.
        """
        dic_cst = {cst: getattr(self, cst) for cst in self.nodes['cst'] if cst in dir(self)}
        for c in dic_cst:
            delattr(self, c)
        self.set_all_csts()
        both =  {cst: (getattr(self, cst), dic_cst[cst]) for cst in dic_cst}
        def diff(a, b):
            try:
                if a!=b:
                    return True
                return False
            except: return any(a!=b)
        return {cst: (v1, v2) for cst, (v1, v2) in both.items() if diff(v1, v2)}
