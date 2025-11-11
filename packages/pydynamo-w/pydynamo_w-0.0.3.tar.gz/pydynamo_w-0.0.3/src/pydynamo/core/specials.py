"""Special functions that are used in pydynamo equations.
"""
import numpy as np

def step(hght, sttm, t):
    """
    If sttm is a variable (ndarray), th step time is determined by the method
    described in section 2.4.2.
    If hght is a variable, the step function has the effect of a gate function
    that "opens" the gate allowwing step to equal hght after time sttm.
    The step will equal 0 until the step time (and any time that time is less
    than sttm).

    step = 0 if TIME < sttm
    step = hght otherwise

    Parameters
    ---------
    hght: float

    sttm: float:

    t : float
        current time value.
    """

    if sttm >= t:
        return hght
    return 0

def clip(func2, func1, t, t_switch):
    """
    Logical function used as time switch to change parameter value.

    Parameters
    ----------
    func2 : any

    func1 : any

    t : float
        current time value.
    t_switch : float
        time threshold.

    Returns
    -------
    func2 if t>t_switch, else func1.

    """
    
    if t <= t_switch:
        return func1
    else:
        return func2

class Sample:
        """
        When called, returns a the last stored value unless some intervals is reached.
        """
        def __init__(self, isam, time):
            self.current_value = isam
            self.time = time
        # Useful to let params in order to ensure they are calculated before
        def __call__(self, x_k, intval_k, isam, k):

            if k == 0:
                self.current_next_date = intval_k
                self.current_value = isam

            elif self.current_next_date <= self.time[k]:
                self.current_next_date = self.time[k] + intval_k
                self.current_value = x_k

            return self.current_value

class Interpol:
    """Custom interpolate, because scipy's one is slow and overkill"""
    def __init__(self, x_low, x_high, x_incr, table):
        self.xl = x_low
        self.xh = x_high
        self.table = table
        self.xi = x_incr

    # def __call__(self, x):
    #     if '__iter__' in dir(x):
    #         return np.array([self.call_i(xi) for xi in x])
    #     return self.call_i(x)
    def __call__(self, x):
        try:
            if x < self.xl:
                return self.table[0]
            if x >= self.xh:
                return self.table[-1]
            i = int((x - self.xl)//self.xi)
            return self.table[i] + ((x-self.xl)/self.xi - i)*(self.table[i+1] - self.table[i])
        except:
            # Case a vector is entered
            if '__iter__' in dir(x):
                return np.array([self.__call__(xi) for xi in x])
