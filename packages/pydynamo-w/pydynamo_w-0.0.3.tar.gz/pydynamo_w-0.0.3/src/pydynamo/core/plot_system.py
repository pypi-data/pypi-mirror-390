"""Functions used by a System instance to plot curves.

"""

import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network as pyvisNetwork

def plot(self, v_names=None, rescale=False, show_comments=True, filter_no=None, scales=None, colors=None, title='', linestyle='-', outside_legend_number=2, legend=True, **kwargs):
    """Plot the curves of the last simulation for indicated variables.

    Parameters
    ----------
    v_names : iterable(str)
        Variable to plot names. If None, all variables are plotted.

    rescale : bool
        If yes, all curves are normalized between 0 and 1.

    show_comments: bool
        If yes, comments are shown in the legend.

    filter_no: iterable(str)
        Names of variables that won't appear in the plot.

    scales: dict(str, float)
        Scales of variables. Variables are divided by their respective scales on the plot.

    colors: dict(str, str)
        Colors of each variable.

    title: str
        Title of the plot.

    linestyle: str
        Linestyle of the plot.

    outside_legend_number: int
        Number of lines from which legend is plotted outside the graph.

    legend: bool
        If yes, the legend is drawn.

    **kwargs
        Arguments for matplotlib.pyplot.plt

    Returns
    -------
    list(matplotlib.lines.Line2D)
        List of plotted lines

    """

    assert 'time' in dir(self), "No simulation have been run for the system !"

    if not v_names:
        v_names = self.get_all_variable_names()
        
    if isinstance(v_names, str):
        v_names = [v_names]
        
    if filter_no:
        v_names = [n for n in v_names if n not in filter_no]

    lines = []
    
    for name in v_names:
        v = getattr(self, name)

        if self.is_table(name):
            raise Exception(f"Error, {name} is a table and can't be plotted")
        # Case it's a constant
        try:
            v[0]
        except:
            v = v+self.get_time()*0
            
        if scales and name in scales:
            try:
                v = v/scales[name]
            except FloatingPointError:
                v = 1 + 0 * v
        elif rescale:
            v = v/max(abs(v))
        
        label = name     
        if show_comments:
            label = label + ' (' + self.definition(name).split('\n')[0].capitalize() + ')'
        try:
            color = colors[name]
        except:
            color = None
            
        lines.append(plt.plot(self.get_time(), v, label=label, color=color, linestyle=linestyle, **kwargs)[0])

    if rescale:
        plt.ylabel('Rescaled values')

    plt.xlabel('Time')
    
    if legend:
        if len(v_names) > outside_legend_number:
            plt.legend(loc='center left', bbox_to_anchor=[1, 0.8])
        else:
            plt.legend(loc='center left')
            
    plt.title(title)

    return lines
        
def show_influence_graph(self, variables=None, depth=1, show_init_val=True, in_notebook=True, options=None, colors=None):
    """Show variables influence newtork with the Pyvis library.
    
    Parameters
    ----------
    show_init_val : bool
        If True, show the initial value for a variable.
    
    in_notebook : bool
        If True, network appears as a Widget in the notebook.

    options : dict
        Pyvis options.
    
    colors : dict
        Colors of each variable and constant.
    """
    
    G = self.get_influence_graph()
    Gq = pyvisNetwork(notebook=in_notebook, directed=True)
    
    # If some variables are focused, only retrieve its neighbors
    if variables is not None:
        if isinstance(variables, str):
            variables = [variables]
        setvars = set()
        for v in variables:
            for p in nx.dfs_successors(G, v, depth+1):
                setvars.add(p)
            for p in nx.dfs_successors(G.reverse(), v, depth+1):
                setvars.add(p)

        G = G.subgraph(setvars)
    
    for a in sorted(G.nodes):
        com = self.definition(a).split('\n')[0]
        node = a
        title = f"{com}\n{self.raw_equation(a)}"
        col = colors[a] if colors and a in colors else None
        
        if show_init_val == True:
            if a in self.nodes['var']:
                title = f'{title}\nInit: {getattr(self, a)[0]:.2f}'
                    
        Gq.add_node(node, title=title, color=col)
    
    for a, b in sorted(G.edges):
        nodea, nodeb = (a, b)
        Gq.add_edge(nodea, nodeb)
    
    if options:
        Gq.show_buttons(options)
    
    return Gq


def plot_non_linearity(self, var, **kwargs):
    """Plot the non linear functions with which the variable is computed.

    Parameters
    ----------
    name : str
        Variable name.

    **kwargs
        Arguments for matplotlib.pyplot.plot

    Returns
    -------
    matplotlib.lines.Line2D
        Plotted line
    """
    
    assert 'time' in dir(self), "No simulation yet! Please run the system."
    
    x, y, ylabel, xlabel, title = self.get_tabhl_args(var)
    
    if x is not None and y is not None:
        l = plt.plot(x, y, **kwargs)[0]
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.title(title)

    return l

def plot_compare(self, s2, v_names, scales=None, rescale=False, *args, **kwargs):
    """Show the variables of 2 different systems.

        Parameters
        ----------
        s2: System
            Other system to compare whith.

        v_names: iterable(str)
            Names of variables or constant to plot.

        scales: dict(str, float)
            Scales of variables. Variables are divided by their respective scales on the plot.

        rescale: bool
            If yes, If yes, variables are normalized between 0 and 1.

        *args
            Argument list for the pydynamo.core.plot_system.plot function.

        **kwargs
            Arguments for the pydynamo.core.plot_system.plot function.
    Returns
    -------
    (list(matplotlib.lines.Line2D), list(matplotlib.lines.Line2D))
        First and second compared lines.

    """

    assert 'time' in dir(self) and 'time' in dir(s2), "No simulation yet! Please run the system before."
    
    # remove tables
    v_names = [v for v in v_names if not isinstance(getattr(self,v), list)]
    
    if not scales and rescale:
        scales= {}
        for v in v_names:
            try:
                scales[v] = max(max(getattr(self, v)), max(getattr(s2, v)))
            except TypeError:
                scales[v] = max(getattr(self, v), getattr(s2, v))

    lines = []
    
    lines.append(plot(self, v_names, *args, **kwargs, linestyle='-', scales=scales))
    plt.gca().set_prop_cycle(None)
    lines.append(plot(s2, v_names, *args, **kwargs, linestyle='--', scales=scales, legend=False))
    return lines
    
    
        
