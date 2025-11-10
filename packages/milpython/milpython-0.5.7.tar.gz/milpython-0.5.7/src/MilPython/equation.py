from .lpStateVar import *
class Equation:
    '''Simple class for new equations. The Format is alway: Sum(stateVar*factor) >sense< b'''
    def __init__(self,var_lst:list,sense:str,b:float,description:str):
        """
        Args:
            var_lst (list): each items of the list represents one variable in equation, format of each item (time dependent): [stateVar,factor,timestep]; for additional variables: [stateVar,factor] 
            sense (str): ">","=" or "<"
            b (float): right side of equation
        """        
        for var in var_lst:
            if len(var)==3 and (isinstance(var[0],LPStateVar_add) or isinstance(var[0],LPStateVar_Decision_add)):
                raise ValueError(f'The variable {var[0].name} is not time dependent and must not be called with a time stemp')
            if len(var)==2 and (isinstance(var[0],LPStateVar_timedep) or isinstance(var[0],LPStateVar_Decision_timedep)):
                raise ValueError(f'The variable {var[0].name} is time dependent and has to be called with a time stemp')

        self.var_lst = var_lst
        self.sense = sense
        self.b = b
        self.description=description