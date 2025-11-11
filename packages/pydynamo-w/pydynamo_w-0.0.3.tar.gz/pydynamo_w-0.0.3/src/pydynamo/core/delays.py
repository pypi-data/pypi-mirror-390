"""Functions implementing a delayed smooth effect in pydynamo.
"""
import numpy as np

class Smooth:
    """
    Delay information function of the 1st order for smoothing.
    Returns a class that is callable as a function (see Call parameters) at a given step k.

    Parameters
    ----------
    dt : float
        time step.

    Call parameters
    ---------------
    delay_time : float
        delay parameter. Higher delay increases smoothing.
    val : float
        current value to smooth
    k : int
        current loop index.
    """
    def __init__(self, dt):
        self.state = None
        self.k = 0
        self.dt = dt

    def initialise(self, init_value):
        self.state = init_value

    def ddt(self, value, delay_time):
        self.state = self.state + (value - self.state)/delay_time*self.dt
    
    def __call__(self, val_k, delay_time, k):
        if self.state is None:
            if k == 0 or k == 1:
                self.initialise(val_k)
            else:
                raise Exception('Bad call of smooth')
            
        if k == self.k + 1:
            res = self.state
            self.ddt(val_k, delay_time)
            self.k = self.k + 1
            return res
        
        if k != self.k:
            raise Exception("Bad call of smooth function")
        
        return self.state

class Dlinf3:
    """
    Delay information function of the 3st order for smoothing. 
    Returns a class that is callable as a function (see Call parameters) at a given step k.

    Parameters
    ----------
    dt : float
        time step.

    Call parameters
    ---------------
    delay_time : float
        delay parameter. Higher delay increases smoothing.
    val : float
        current value to smooth
    k : int
        current loop index.
    """
    def __init__(self, dt):
        self.state = None
        self.k = 0
        self.dt = dt

    def initialise(self, init_value):
        self.state = np.ones(3)*init_value

    def ddt(self, value, delay_time):
        targets = np.roll(self.state, 1, axis=0)
        targets[0] = value
        
        self.state = self.state + (targets - self.state)*3/delay_time*self.dt
    
    def __call__(self, val_k, delay_time, k):
        if self.state is None:
            self.initialise(val_k)
                
        if k == self.k + 1:
            self.ddt(val_k, delay_time)
            self.k = self.k + 1
            
        if k != self.k:
            raise Exception("Bad call of dlinf3 function")
        
        return self.state[-1]
    
class Delay3:
    """
    Delay function of the 3rd order. Returns a class that is callable as a
    function (see Call parameters) at a given step k.
    
    Parameters
    ----------
    dt : float
        time step.

    Call parameters
    ---------------
    delay_time : float
        delay parameter. Higher delay increases smoothing.
    val_k : float
        current value to delay
    k : int
        current loop index.
    """

    def __init__(self, dt):
        self.state = None
        self.k = 0
        self.dt = dt

    def initialise(self, init_value, delay_time):
        self.state = np.ones(3)*init_value*delay_time

    def ddt(self, value, delay_time):
        outf = self.state/delay_time
        inf = np.roll(outf, 1, axis=0)
        inf[0] = value
        self.state = self.state + (inf - outf)*3*self.dt
    
    def __call__(self, val_k, delay_time, k):
        if self.state is None:
            self.initialise(val_k, delay_time)
                
        if k == self.k + 1:
            self.ddt(val_k, delay_time)
            self.k = self.k + 1
            
        if k != self.k:
            raise Exception("Bad call of delay function")
        
        return self.state[-1]/delay_time

Dlinf3 = Delay3
