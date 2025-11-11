"""
Define the World3 clas

"""

from .plot_utils import plot_world_with_scales, plot_world_03, plot_world_03_compare
from .data_world3 import w3_code, w3_defs, var_color
from .scenarios_limits_to_growth import scenarios
import pydynamo.world3.data_world3

from pydynamo.core.system import System


class World3(System):
    """
    A World3 object is a System object with more convenient functions and some additional plotting functions, adapted for the manipulation of the World3 model 2003's version equations.
    """
    def __init__(self, scenario_number=2, sys=None):
        """Initialise a World3 object. By default, the scenario number is the second one, because it's the most "realistic" when we compare to the current situation (in 2022).
        """
        if not sys:
            ccode = w3_code.copy()
            changes = scenarios[scenario_number - 1]['changes']
            for cst, eq in changes.items():
                ccode.append(f'{cst} = {eq}')

        else:
            ccode = sys.code_lines.copy()
                
        super().__init__(ccode, True)
        self.add_comments(w3_defs)
        
    def copy(self):
        """Returns a copy of the system, with the same equations and constant values.
        """

        return World3(sys=self)

    def run(self, N=400, dt=0.5):
        """Run the system with 400 steps of 1/2 year.
        """
        super().run(N, dt)

    def plot_world(self, **kwargs):
        """Plot the main variables of the world, in the "Limits To Growth: the 30th years update" way. 

        Parameters
        ----------
        kwargs : 
            See pydynmao.world3.plot_utils.plot_world_03 arguments.
        """

        plot_world_03(self, with_legend=True, **kwargs)

    def plot_world_compare(self, s2, *args, **kwargs):
        """Compare in the main variables of the worlds, plotted in the "Limits To Growth: the 30th year update" way.

        Parameters
        ----------
        s2 :
            World3 object to compare (with simulation already run).

        args, kwargs :
            See pydynmao.world3.plot_utils.plot_world_03_compare arguments.
        """
        plot_world_03_compare(self, s2, with_legend=True, *args, **kwargs)
    
    def show_influence_graph(self, **kwargs):
        """See pydynamo.core.plot_system.show_influence_graph.
        """
        return super().show_influence_graph(colors=var_color, **kwargs)
