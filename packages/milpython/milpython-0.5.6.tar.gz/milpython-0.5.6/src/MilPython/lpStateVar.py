import matplotlib.pyplot as plt

class LPStateVar:
    '''
    Abstract class (only create objects of the inheriting classes)
    Defines state variables for linear optimization
    Contains name, unit, lower and upper bound and space for comments
    when optimizing, the optimized results for the variable are stored under self.result
    '''
    def __init__(self,name:str,unit:str=None,lb:float=0,ub:float=float('inf'),vtype='C',comment:str=None):
        """Init-Method for abstract LPStateVar-class. Has to be run by inheriting classes init-fun

        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.

        Raises:
            Exception: Only create objects of the inheriting classes
        """        
        if self.__class__.__name__ == 'LPStateVar':
            raise Exception('This class is abstract and is not used for instantiation. Please create objects of the inheriting classes time or addition')
        self.pos:int=None
        self.name:str=name
        self.lb:float=lb
        self.ub:float=ub
        self.vtype:chr=vtype
        self.unit:str=unit
        self.result = None
        self.comment:str=comment
    
    def __repr__(self):
        return f"StateVar(name='{self.name}')"
    
class LPStateVar_timedep(LPStateVar):
    '''
    Class for time-dependent state variables
    A variable of this type is automatically created for each time step
    self.pos corresponds to the position of the variable in time step zero.
    '''
    def __init__(self, name, unit=None,  lb=0, ub=float('inf'),vtype='C', comment=None):
        """
        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.
        """        
        super().__init__(name, unit, lb, ub, vtype, comment)
    
    def plot_result(self):
        '''Simple method for plotting the time histories of the optimization result for this variable'''
        if self.result is None:
            print('The optimization must be performed first')
            return
        plt.plot(self.result)
        plt.title(self.name)
        plt.ylabel(self.unit)
        plt.xlabel('steps')
        plt.show()
    
    def __repr__(self):
        if self.result is not None:
            self.plot_result()
        return f"StateVar(name='{self.name}')"

class LPStateVar_add(LPStateVar):
    '''Class for additional variables that only occur once (and not in every time step) '''
    def __init__(self, name, unit=None, lb=0, ub=float('inf'),vtype='C', comment=None):
        """
        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.
        """        
        super().__init__(name, unit, lb, ub, vtype, comment)

class LPStateVar_Decision_timedep:
    '''
    Class for timedependent decision variables, all belonging variables are saved here
    Args:
        name(str): name of variable
        decision_dict(dict): Dictionary containing all possible options with all associated properties. 
            E.g.:
                {'opt1': {'price': 100, 'p_max': 500},
                'opt2': {'price': 200, 'p_max': 1000},
                'opt3': {'price': 50, 'p_max': 200}}
        comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.
    '''
    def __init__(self,name:str,decision_dict:dict,comment):
        self.name=name
        self.decision_dict = decision_dict
        self.comment = comment
        self.var_lst=[]
    
    def add_bin_vars(self,bin_var_lst):
        '''for saving the list of binary variables (one per option)'''
        self.bin_var_lst = bin_var_lst
    
    def add_property_var(self,key,var):
        '''
        for adding a property variable to the list (one per property)
        this method also adds the variable as an variable of this self-object
        '''
        setattr(self,key,var)
        self.var_lst.append(var)
        
    def get_result(self):
        '''for illustrating the results'''
        if self.bin_var_lst[0].result is None:
            raise Exception('Run optimization first! (Or no different options available)')
        chosen_option_list = []
        result_lst = []
        for t in range(len(self.bin_var_lst[0].result)): #TODO: this is a bit ugly
            var = next(obj for obj in self.bin_var_lst if obj.result[t] == 1)
            chosen_option_list.append(var)
            if not 'opt_' in var.name:
                raise Exception('Error trying to read results.')
            idx_str = var.name.split('_')[-1]
            if not idx_str.isdigit():
                raise Exception('option variable have unexpexted name')
            result_lst.append(int(idx_str))
                
        plt.plot(result_lst)
        plt.title(self.name)
        plt.xlabel('steps')        
        plt.yticks(list(range(len(self.bin_var_lst))),[f'Opt. {nr}' for nr in list(range(len(self.bin_var_lst)))])
        plt.grid()        
        plt.show()
        self.result_lst = result_lst
        return result_lst


class LPStateVar_Decision_add:
    '''
    Class for non timedependent decision variables, all belonging variables are saved here
    Args:
        name(str): name of variable
        decision_dict(dict): Dictionary containing all possible options with all associated properties. 
            E.g.:
                {'opt1': {'price': 100, 'p_max': 500},
                'opt2': {'price': 200, 'p_max': 1000},
                'opt3': {'price': 50, 'p_max': 200}}
        comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.
    '''
    def __init__(self,name,decision_dict,comment):
        self.name=name
        self.decision_dict = decision_dict
        self.comment = comment
        self.var_lst=[]
    
    def add_bin_vars(self,bin_var_lst):
        '''for saving the list of binary variables (one per option)'''
        self.bin_var_lst = bin_var_lst
    
    def add_property_var(self,key,var):
        '''
        for adding a property variable to the list (one per property)
        this method also adds the variable as an variable of this self-object
        '''
        setattr(self,key,var)
        self.var_lst.append(var)
        
    def get_result(self):
        '''for illustrating the results'''
        if self.bin_var_lst[0].result == None:
            raise Exception('Run optimization first! (Or no different options available)')
        chosen_option = next(obj for obj in self.bin_var_lst if obj.result == 1)
        print('---Optimization result----')
        print(f'Best option: {chosen_option.name}')
        for var in self.var_lst:
            print(f'    - {var.name}: {var.result}')
        self.result_dict = {chosen_option.name:{var.name: var.result for var in self.var_lst}}
        return self.result_dict