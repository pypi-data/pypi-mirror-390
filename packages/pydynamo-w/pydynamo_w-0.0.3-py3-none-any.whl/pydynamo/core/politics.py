"""Functions to add new politics in a System object.
"""
import re

def new_politic(self, name, date, new_val):
        """Implements a new politic for some constant, table or variable from a certain date. PLEASE DO NOT ADD 2 NEW POLITICS ON THE SAME VARIABLE OR CONSTANT !

        Parameters
        ----------
        name: str
            Name of a constant, table or variable we want to change.

        date: float
            date from which the new value will be activated.

        new_val: float, array or string
            If name refers to a constant, a float with the new value. If name srefers to a table, an array of the sime size as the older one. If name refers to a variable, a string with the new value.

        """
        assert name not in self.political_changed, f"New politics have already been implemented on \"{name}\". Reset the system, or apply a politic over an other variable or constant."
        if name in self.nodes['cst']:
            n = getattr(self, name)
            if '__iter__' in dir(n):
                self.new_table_politic(name[:-1], date, new_val)
            else:
                self.new_cst_politic(name, date, new_val)
            self.political_changed.add(name)
        elif name in self.nodes['var']:
            self.new_var_politic(name, date, new_val)
            self.political_changed.add(name)
        else:
            raise NameError(f'No variable or constant named "{name}" in the System')

def new_cst_politic(self, cst, date, new_value):
    """Add a new equations to `s` for the constant `cst`, which becomes a variable changing from its former value to `new_value` after the `date`.
    
    Parameters
    ----------
    s : System
        The system to implement the new politic.
    cst : str
        Constant name.
    date : float
        Date of politic application.
    new_value : float
        The new value that `cst` will take after the date `date`.
    """
    assert cst in self.eqs['cst'], f"{cst} is not a constant"
    initval= self.eqs['cst'][cst]['line']
    del self.eqs['cst'][cst]

    # New equations
    eq_clip = f"{cst}.k = clip({cst}_X2, {cst}_X1, time.k, {cst}_date) # {self.definition(cst)} " 
    eq_date = f"{cst}_date = {date} # Date of {cst} change"
    eq_cst1 = f"{cst}_X1 = {initval} # {self.definition({cst})} before {cst}_date"
    eq_cst2 = f"{cst}_X2 = {new_value} # {self.definition({cst})} after {cst}_date"

    # Change every call of cst to a call of cst.k
    for i in range(len(self.code_lines)):
        self.code_lines[i] = re.sub(r'(?<!\w)'+str(cst)+r'(?!\w)', f'{cst}.k', self.code_lines[i])
        
    self.add_equations([eq_clip, eq_date, eq_cst1, eq_cst2])
    self.reset_eqs()


def new_table_politic(self, var, date, new_value):
    """Add a new equations to `s` for the table used by the variable `var`. The table changes from its former value to `new_value` after the `date`.
    
    Parameters
    ----------
    s : System
        The system to implement the new politic.
    var : str
        Variable name.
    date : float
        Date of politic application.
    new_value : list(float)
        The new value that the table will take after the date `date`.
    """
    assert f'tabhl' in self.eqs['update'][var]['args']['fun'], f"{var} hasn't tabhl function"
    
    table_name = self.eqs['update'][var]['args']['fun']['tabhl']['table']
    table_init_val = self.eqs['cst'][table_name]['line']
    var_line = self.eqs['update'][var]['raw_line']

    # Define new equations
    eq_table_1 = f"{table_name}_X1 = {table_init_val} # {self.definition(table_name)} before {date}"
    eq_table_2 = f"{table_name}_X2 = {', '.join([str(v) for v in new_value])} # {self.definition(table_name)} after {date}"    
    eq_var_1 = var_line.replace(f'{var}.k', f'{var}_X1.k').replace(table_name, table_name + '_X1')
    eq_var_2 = var_line.replace(f'{var}.k', f'{var}_X2.k').replace(table_name, table_name + '_X2')
    eq_var = f"{var}.k = clip({var}_X2.k, {var}_X1.k, time.k, {date}) # {self.definition(var)}"

    self.add_equations([eq_table_1, eq_table_2, eq_var_1, eq_var_2, eq_var])
    self.reset_eqs()

def new_var_politic(self, var, date, eq2):
    """Add a new equations to `s` for the variable `var`, which changes from its former value to `new_value` after the `date`.
    
    Parameters
    ----------
    s : System
        The system to implement the new politic.
    var : str
        Variable name.
    date : float
        Date of politic application.
    new_value : str
        The new value, written with the pydynamo syntax, that the variable `var` will take after the date `date`.
    """
    assert var in self.eqs['update'], f"{var} is not a variable"
    first_line = self.eqs['update'][var]['raw_line'].split('=')[1]
    line_init = None
    if var in self.eqs['init']:
        line_init = self.eqs['init'][var]['raw_line'].split('=')[1]
    del self.eqs['update'][var]

    # Define new equations
    eq_clip = f"{var}.k = clip({var}_X2.k, {var}_X1.k, time.k, {var}_date) # {self.definition(var)}"
    eq_date = f"{var}_date = {date} # Date of {var} change"
    eq_var1 = f"{var}_X1.k = {first_line} # {self.definition(var)} before {var}_date"
    eq_var2 = f"{var}_X2.k = {eq2} # {self.definition(var)} after {var}_date"
    eq_init1 = ''
    eq_init2 = ''
    if line_init:
        eq_init1 = f"{var}_X1.i = {line_init}"
    eq_init2 = f"{var}_X2.i = 0"

    self.add_equations([eq_clip, eq_date, eq_var1, eq_var2, eq_init1, eq_init2])
    self.reset_eqs()

