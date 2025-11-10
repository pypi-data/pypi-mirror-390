import numpy as np
from .lpStateVar import *
from .lpInputdata import LPInputdata
from scipy.sparse import coo_matrix, csc_matrix
from .equation import Equation as Eq
from collections import defaultdict
import sympy as sp

class LPObject:
    def __init__(self,inputdata:LPInputdata,name:str,comment:str):
        '''Constructor of the general Linear Programming Object'''
        if self.__class__.__name__ == 'LPObject':
            raise Exception('This is an abstract class. Please only create objects of the inheriting class')
        self.inputdata = inputdata
        self.name = name
        self.comment = comment
        self.stateVar_lst:list[LPStateVar]=[]
        self.eq_lst=[]

    def add_time_var(self,name:str,unit:str='',lb:float=0,ub:float=np.inf,vtype='C',comment:str='')->LPStateVar_timedep:
        """adds a new timedependent statevariable to the LPObject; returns the statvar-object, which should be saved as a variable in the LPObject

        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.

        Returns:
            LPStateVar_timedep: _description_
        """      
        var = LPStateVar_timedep(name,unit,lb,ub,vtype,comment)
        self.stateVar_lst.append(var)
        return var
    
    def add_additional_var(self,name:str,unit:str='',lb:float=0,ub:float=np.inf,vtype='C',comment:str='')->LPStateVar_add:
        """adds a new additional, time-independent statevariable to the LPObject; returns the statvar-object, which should be saved as a variable in the LPObject

        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.

        Returns:
            LPStateVar_add: _description_
        """        
        var = LPStateVar_add(name,unit,lb,ub,vtype,comment)
        self.stateVar_lst.append(var)
        return var
    
    def add_decision_var_timedep(self,name:str,decision_dict:dict,inputdata:LPInputdata,comment:str=''):
        """adds a new timedependent decision variable; builds all necessary variables and sets up requiered equations

        Args:
            name (str): name of variable
            decision_dict(dict): Dictionary containing all possible options with all associated properties. 
                E.g.:
                    {'opt1': {'price': 100, 'p_max': 500},
                    'opt2': {'price': 200, 'p_max': 1000},
                    'opt3': {'price': 50, 'p_max': 200}}
            inputdata (LPInputdata): inputdata-object
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.

        Returns:
            LPStateVar_Decision_timedep: newly generated variable object containing all further variables
        """
        dec_var = LPStateVar_Decision_timedep(name,decision_dict,comment)        # LPStateVar_Decision_add stores dict and all binary and property variables
        bin_var_lst = [self.add_time_var(name=f'{name}_opt_{i}',vtype='B') for i in range(len(decision_dict))]
        dec_var.add_bin_vars(bin_var_lst)
        
        for t in range(inputdata.steps):
            eq_var_lst = [[var,1,t] for var in bin_var_lst]
            self.add_eq(eq_var_lst,'=',1)
        for key in next(iter(decision_dict.values())):
            cleaned_key = key.replace(" ", "_")
            var=self.add_time_var(name=cleaned_key,lb=-np.inf)#TODO: add optional unit?
            dec_var.add_property_var(cleaned_key,var)
            
            for t in range(inputdata.steps):
                eq_var_lst=[]
                eq_var_lst.append([var,1,t])
                values_lst=[decision_dict[opt][key] for opt in decision_dict]
                for i in range(len(decision_dict)):
                    eq_var_lst.append([bin_var_lst[i],-values_lst[i],t])
                self.add_eq(eq_var_lst)
        return dec_var
    
    def add_decision_var_add(self,name:str,decision_dict:dict,comment:str=''):
        """adds a new none timedependent decision variable; builds all necessary variables and sets up requiered equations

        Args:
            name (str): name of variable
            decision_dict(dict): Dictionary containing all possible options with all associated properties. 
                E.g.:
                    {'opt1': {'price': 100, 'p_max': 500},
                    'opt2': {'price': 200, 'p_max': 1000},
                    'opt3': {'price': 50, 'p_max': 200}}
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.

        Returns:
            LPStateVar_Decision_timedep: newly generated variable object containing all further variables
        """
        dec_var = LPStateVar_Decision_add(name,decision_dict,comment)
        bin_var_lst = [self.add_additional_var(name=f'{name}_opt_{i}',vtype='B') for i in range(len(decision_dict))]
        dec_var.add_bin_vars(bin_var_lst)
        eq_var_lst = [[var,1] for var in bin_var_lst]
        self.add_eq(eq_var_lst,'=',1)
        for key in next(iter(decision_dict.values())):
            eq_var_lst=[]
            cleaned_key = key.replace(" ", "_")
            var=self.add_additional_var(name=cleaned_key,lb=-np.inf)#TODO: add optional unit?
            dec_var.add_property_var(cleaned_key,var)
            eq_var_lst.append([var,1])
            values_lst=[decision_dict[opt][key] for opt in decision_dict]
            for i in range(len(decision_dict)):
                eq_var_lst.append([bin_var_lst[i],-values_lst[i]])
            self.add_eq(eq_var_lst)
        return dec_var
        
    
    def add_eq(self,var_lst,sense='E',b=0,description=''):
        """Adds an equation to the equation system; automatically adds eq to eq_lst of this object

        Args:
            var_lst (list): each items of the list represents one variable in equation, format of each item (time dependent): [stateVar,factor,timestep]; for additional variables: [stateVar,factor] 
            sense (str): ">","=" or "<"
            b (float): right side of equation
            description (str): optiional short description of equation
        """
        if any(not isinstance(var,list) for var in var_lst):
            raise ValueError('var_lst has to be a list of lists')
        if any(len(var)==2 and (isinstance(var[0],LPStateVar_timedep) or isinstance(var[0],LPStateVar_Decision_timedep)) for var in var_lst):
            if any(len(var)==3 for var in var_lst):
                raise ValueError('If short form for time dependent variables is used, all variables have to be in short form')
            for t in range(self.inputdata.steps):
                if isinstance(b,list) or isinstance(b,np.ndarray):
                    b_t = b[t]
                else:
                    b_t = b
                var_lst_t = [sublist.copy() for sublist in var_lst]
                for i,var in enumerate(var_lst):
                    if isinstance(var[1],list)or isinstance(var[1],np.ndarray):
                        var_lst_t[i][1] = var[1][t]
                    if isinstance(var[0],LPStateVar_timedep) or isinstance(var[0],LPStateVar_Decision_timedep):
                        var_lst_t[i].append(t)
                self.eq_lst.append(Eq(var_lst_t,sense,b_t,description))
        else:
            self.eq_lst.append(Eq(var_lst,sense,b,description))
    
    def add_switch(self,switch:LPStateVar,var1:LPStateVar,var2:LPStateVar,description='',big_M=1e6):
        """
        Adds equations that implement a switch between two state variables so that only one of the two variables can ever be unequal to 0. 
        Works for both timedependent and additional variables.
        The binary switch variable has to be implemented manually in the init.
        The switch variable takes the value 1 if var1 is active and 0 if var2 is active.
        ! If the boundaries are infinite, the boundaries will be set to -big_M and big_M instead.
        """
        self.description = description
        if switch.vtype is not 'B':
            raise ValueError('Switch variable has to be binary')
        if not isinstance(var1,LPStateVar) or not isinstance(var2,LPStateVar):
            raise ValueError('The variables have to be state variables')
        
        var1_lb = var1.lb if np.isfinite(var1.lb) else -big_M
        var1_ub = var1.ub if np.isfinite(var1.ub) else big_M
        var2_lb = var2.lb if np.isfinite(var2.lb) else -big_M
        var2_ub = var2.ub if np.isfinite(var2.ub) else big_M
        
        self.add_eq([[var1,1],
                     [switch,-var1_ub]],
                     '<',0)
        self.add_eq([[var1,1],
                     [switch,-var1_lb]],
                     '>',0)
        self.add_eq([[var2,1],
                     [switch,var2_ub]],
                     '<',var2_ub)
        self.add_eq([[var2,1],
                     [switch,var2_lb]],
                     '>',var2_lb)
    
    def getStateVars(self)->list[LPStateVar]:
        '''returns list of state_vars'''
        return self.stateVar_lst
                
    def def_equations(self):
        '''Has to be overritten by inheriting class'''
        pass
    
    def return_eqs(self):
        '''Changes format of local equations so lpmain can take them'''
        num_vars = sum(len(eq.var_lst) for eq in self.eq_lst)
        self.idx=0
        self.eq_nr=0
        self.row = np.zeros(shape=(num_vars,))
        self.col = np.zeros(shape=(num_vars,))
        self.data = np.zeros(shape=(num_vars,))
        self.senses=[]
        self.beq = []
        
        for eq in self.eq_lst:
            for var in eq.var_lst: 
                if len(var) == 2:
                    var.append(0)
                self.row[self.idx] = self.eq_nr
                self.col[self.idx] = var[0].pos + var[2] * self.inputdata.num_vars_timedep
                self.data[self.idx] = var[1]
                self.idx+=1
            self.senses.append(eq.sense)
            self.beq.append(eq.b)
            self.eq_nr+=1
        Aeq_temp = coo_matrix((self.data,(self.row,self.col)),shape=(self.eq_nr,self.inputdata.num_vars))
        return Aeq_temp,self.beq,self.senses   
     
    
    def str_equation(self,equation):
        min_time_step = min(time_step for _, _, time_step in equation.var_lst)
        sorted_var_lst = sorted(equation.var_lst, key=lambda x: x[0].name)  # sort by variable name
        str_lst = [f"{var_state.name},{str(var_coef)},{str(time_step - min_time_step)}" for var_state, var_coef, time_step in sorted_var_lst]
        return ','.join(str_lst) + equation.sense + str(equation.b)


    def return_grouped_eqs(self):
        grouped = defaultdict(list)
        for eqn in self.eq_lst:
            key = self.str_equation(eqn)
            grouped[key].append(eqn)
        grouped_lst = list(grouped.values())
        return grouped_lst
    
    def round_scientific(self,number):
        # Konvertiere die Zahl zuerst in eine wissenschaftliche Darstellung
        scientific_str = "{:e}".format(number)

        # Zerlege die formatierte Zahl in Mantisse und Exponent
        mantissa_str, exponent_str = scientific_str.split('e')

        # Umwandle die Teile wieder in Zahlen
        mantissa = float(mantissa_str)
        exponent = int(exponent_str)

        # Runde die Mantisse auf 3 Nachkommastellen
        mantissa_rounded = round(mantissa, 5)

        # Setze die gerundete wissenschaftliche Darstellung zusammen
        rounded_scientific = "{}e{:02d}".format(mantissa_rounded, exponent)

        return float(rounded_scientific)
    
    def summarize_intervals(self,lst):
        output = []
        i = 0
        while i < len(lst):
            start = lst[i]
            while i+1 < len(lst) and lst[i+1] == lst[i]+1:
                i += 1
            end = lst[i]
            if start == end:
                output.append(str(start))
            else:
                output.append(f'{start}-{end}')
            i += 1
        return ', '.join(output)
    
    def format_string(self,s):
        if "_" in s:
            parts = s.split('_', 1)
            parts[1] = parts[1].replace('_', ',')
            return parts[0] + "_{" + parts[1] + "}"
        else:
            return s   # Wenn kein Unterstrich vorhanden ist, geben wir den Ursprungsstring zurück

