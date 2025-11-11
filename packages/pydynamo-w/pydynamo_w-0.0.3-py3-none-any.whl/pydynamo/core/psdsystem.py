"""System class which creates a System from a Pysd model.
"""

import networkx as nx
import numpy as np
import re
from .system import System

class PsdSystem(System):
    """System which initialises with a Pysd model.
    """
    def __init__(self, model):
        """Intialise from a Pysd model. Comments are retrieved from code.

        Parameters
        ----------
        mode : PySD.model
            Model from which the System is created.

        """
        self.model = model
        self.caracs = {}
        self.comments = {}
        
        for n in self.model.components._dependencies:
            try :
                doc = getattr(self.model.components, n).__doc__
                car = {}
                coms = []
                for l in doc.split('\n'):
                    if ':' in l:
                        key, val = l.split(':')
                        car[key.strip()] = val.strip()
                    else:
                        coms.append(l)
                car['Comment'] = re.sub('  *', ' ', ' '.join(coms))
                self.caracs[n] = car
                
                try:
                    self.comments[n] = f"{car['Real Name']} [{car['Units']}]: {car['Comment']}"
                except Exception as e:
                    if any(i in n for i in {'smooth', 'integ', 'delay'}):
                        self.comments[n] = ''
                    else:
                        print(f'Counlnt find comment for var {n}', e)
                        raise e
            except Exception as e:
                if 'active' not in n:
                    print(f'Problem for car of {n}')
                    raise e
            
        self.df_run = None
        
    def get_influence_graph(self):
        """Get the graph of influences: an arrow from A to B if B needs A (at initialisation or updating step) to be computed.

    Returns
    -------
    networkx.DiGraph
        Graph of influences.
    """
        G = nx.Graph()
        for var, deps in self.model.components._dependencies.items():
            for dep, i in deps.items():
                if i is not None:
                    G.add_edge(dep, var)
        return G

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
        
        if self.caracs[name]['Type'] == 'lookup':
            try:
                x, y = np.array(eval(self.caracs[name]['Original Eqn'])).T
                ylabel = self.caracs[name]['Units']
                return x, y, ylabel, '', ''
            except Exception as e:
                print('no such !')
                raise e
        return None, None, '', '', ''
    
    def get_var_names(self):
        """Return every variables names.
        
        Returns
        -------
        list(str)
            List of variables names.
        """
        return list(self.model.components._dependencies.keys())

    def get_time(self):
        """Returns the time array.

        Returns
        -------
        np.array(float):
            Array of system time.
        """
        return np.arange(self.model.time.initial_time(), self.model.time.final_time()+self.model.time.time_step()/2, self.model.time.time_step())

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
        if self.df_run is None:
            return self.get_time()*0
        else:
            return self.df_run[name]

    def run(self):
        """Run PySD model.
        """
        self.df_run = self.model.run()

    def equation(self, name):
        """Returns the reformatted equation of a variable or constant.

        Parameters
        ----------
        node : str
            Name of the variable or constant to show the equation.
        """
        try:
            return self.caracs[name]['Original Eqn']
        except:
            return ""
