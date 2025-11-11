"""Functions of System which handles networks.
"""
import networkx as nx
import re

# Graph
def get_cst_graph(self):
    """Get the graph of influences for constants: an arrow from constant A to constant B if B needs A to be computed.

    Returns
    -------
    networkx.DiGraph
        Graph of constant influences.
    """
    G = nx.DiGraph()
    for c in self.eqs['cst']:
        G.add_node(c)
        args = self.eqs['cst'][c]['args']
        for node_type in args:
            for node in args[node_type]:
                if node_type == 'var':
                    raise(Exception(
                        f'Constant {c} is set with a variable ({"_".join(node)}):\n'
                        f'{c} = {self.eqs["cst"][c]["line"]}'))
                if node_type == 'cst':
                    G.add_edge(node, c)
    return G

def get_init_graph(self):
    """Get the graph of influences for variables at initialisation: an arrow from variable A to variable B if B needs A to be computed.

    Returns
    -------
    networkx.DiGraph
        Graph of variable initialisation influences.
    """
    G = nx.DiGraph()
    for v in self.eqs['init']:
        G.add_node(v)
        args = self.eqs['init'][v]['args']
        for av, ai in args['var']:
            if av in self.eqs['update']:
                G.add_edge(av, v)
    for v in self.eqs['update']:
        if not self.is_initialized(v):
            G.add_node(v)
            args = self.eqs['update'][v]['args']
            for av, ai in args['var']:
                if av in self.eqs['update']:
                    G.add_edge(av, v)
    return G

def get_update_graph(self):
    """Get the graph of influences for variables and their indices at updating step: an arrow from variable (A, i) to variable (B, k) if (B, k) needs (A, i) to be computed.

    Returns
    -------
    networkx.DiGraph
        Graph of variable influences at updating step.
    """
    G = nx.DiGraph()
    for v in self.eqs['update']:
        G.add_node((v, 'k'))
        args = self.eqs['update'][v]['args']
        for av, ai in args['var']:
            if av in self.eqs['update']:
                G.add_edge((av, ai), (v, 'k'))
    return G

def get_update_graph_quotient(self):
    """Get the graph of influences for variables at updating step: an arrow from variable A to variable B if B needs A to be computed.

    Returns
    -------
    networkx.DiGraph
        Graph of variable influences at updating step.
    """
    G = nx.DiGraph()
    for v in self.eqs['update']:
        G.add_node(v)
        args = self.eqs['update'][v]['args']
        for av, _ in args['var']:
            if av in self.eqs['update']:
                G.add_edge(av, v)
    return G

def get_influence_graph(self):
    """Get the graph of influences: an arrow from A to B if B needs A (at initialisation or updating step) to be computed.

    Returns
    -------
    networkx.DiGraph
        Graph of influences.
    """
    G = nx.DiGraph()
    for v in self.eqs['update']:
        G.add_node(v)
        args = self.eqs['update'][v]['args']
        for av, _ in args['var']:
            if av in self.eqs['update']:
                G.add_edge(av, v)
        for ac in args['cst']:
            if ac in self.eqs['cst']:
                G.add_edge(ac, v)

    for v in self.eqs['init']:
        G.add_node(v)
        args = self.eqs['init'][v]['args']
        for av, _ in args['var']:
            if av in self.eqs['init']:
                G.add_edge(av, v)
        for ac in args['cst']:
            if ac in self.eqs['cst']:
                G.add_edge(ac, v)

    for c in self.eqs['cst']:
        G.add_node(c)
        args =  self.eqs['cst'][c]['args']
        for ac in args['cst']:
            if ac in self.eqs['cst']:
                G.add_edge(ac, c)
    return G

def set_order(self, gtype):
    """Returns the order to set constants, intitialize or update variables.

    Parameters
    ----------
    gtype : str
        Type of graph, either 'cst', 'init', or 'update'.
    """
    if gtype == 'cst':
        G = self.get_cst_graph()
    elif gtype == 'init':
        G = self.get_init_graph()
    elif gtype == 'update':
        G = self.get_update_graph()
    else:
        raise Exception("Wrong type of graph")
    return nx.topological_sort(G)

def assert_update_acyclic(self):
    """Assert that the updating graph is acyclic, and print the cycle in case there is some.
    """
    G = self.get_update_graph()
    b = '\\'
    assert nx.is_directed_acyclic_graph(G), \
        "Update is not acyclic:\n"\
         + "\n".join(f"{'.'.join(j)} <- {'.'.join(i)}: "
                     f"{'.'.join(j)} = {re.sub(b+'_([jk])', '.'+b+'1',self.eqs['update'][j[0]]['line'])}"
                     for i, j in reversed(nx.find_cycle(G)))\
         + "\nPlease design an update scheme that is not cyclic."

def assert_init_acyclic(self):
    """Assert that the initialisation graph is acyclic, and print the cycle in case there is some.
    """
    G = self.get_init_graph()
    if not nx.is_directed_acyclic_graph(G):
        msg = "Initialisation is not acyclic:\n"
        for i, j in reversed(nx.find_cycle(G)):
            line = self.eqs['update'][j]['line']
            if j in self.eqs['init']:
                line = self.eqs['init'][j]['line']
            msg += f"{j} <- {i}: "
            msg += f"{j}.i = {line} \n"
        msg +="Please design an initialisation scheme that is not cyclic."
        raise AssertionError(msg)

def assert_cst_acyclic(self):
    """Assert that the constant setting graph is acyclic.
    """
    assert nx.is_directed_acyclic_graph(self.get_cst_graph()),\
            ("Cycle detected for constant equations",
             nx.find_cycle(self.get_update_graph()))
