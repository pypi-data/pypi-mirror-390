"""World2 model, originally designed by Jay Forrester in World Dynamics Hardcover – January 1, 1971.
"""
import json
import os

from pydynamo.core.system import System

w2_defs = json.load(open(os.path.join(os.path.dirname(__file__),'definitions_w2.json')))
w2_code = open(os.path.join(os.path.dirname(__file__),'code_pydynamo_w2.py')).readlines()
scales_w2={'nr': 1e12, 'ql':2,  'ci': 20e9,'p':8e9,'polr':40}


class World2(System):
    """
    A World2 object is a System object with more convenient functions and defaults, adapted for the manipulation of the Worl2 model.
    """
    def __init__(self):
        super().__init__(w2_code.copy())
        self.add_comments(w2_defs)


    def plot_world(self, **kwargs):
        """Plot world state: ressources, pollution, population, food, life quality.
        """
        self.plot(['nr', 'p', 'ql', 'fr', 'pol'], rescale=True, **kwargs)

    def run(self, N=400, dt=0.5):
        """Run with 400 steps of 1/2 year.
        """
        super().run(N, dt)
