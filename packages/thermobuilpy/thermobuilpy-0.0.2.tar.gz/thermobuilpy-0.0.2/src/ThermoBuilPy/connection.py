from .component import Component
from .storage import Storage,ThermalStorage,ExtStorage
import numpy as np
CP_Water = 4.186/3.6 # Specific heat capacity of water in Wh/kg (?)#TODO
class Connection(Component):
    def get_heatflow_res(self):
        raise NotImplementedError("This method should be implemented in subclasses.")
    def set_simulation_parameter(self,method,stepsize):
        self.simulation_method = method
        self.stepsize = stepsize

class Conduction(Connection):
    _series_map = {
        'Name': 'name',
        'Storage1': 'storage1.name',
        'Storage2': 'storage2.name',
        'Coeff': 'coeff'}
    def __init__(self, storage1, storage2,coeff,name=None):
        Component.__init__(self,name)
        self.coeff=coeff
        self.storage1:Storage = storage1
        self.storage2:Storage = storage2
        self.storages = [storage1, storage2]
            
    @classmethod
    def newConduction(cls,storage1:Storage,storage2,coeff:float,name:str=None):
        cls=cls(storage1,storage2,coeff,name)
        return cls
    
    def get_heatflow_res(self):
        from .thermalSystem import SimulationMethod
        t1_res = self.storage1.get_temp_res()
        t2_res = self.storage2.get_temp_res()
        match self.simulation_method:
            case SimulationMethod.EXPLICIT_EULER:
                return self.coeff * (t1_res[:-1] - t2_res[:-1])
            case SimulationMethod.IMPLICIT_EULER:
                return self.coeff * (t1_res[1:] - t2_res[1:])
            case SimulationMethod.CRANK_NICOLSON:
                expl=self.coeff * (t1_res[:-1] - t2_res[:-1])
                impl=self.coeff * (t1_res[1:] - t2_res[1:])
                return 0.5 * (expl + impl)
        
class GeneralHeatTransfer(Connection):
    '''
    ! This is only for cases where the other methods don't work.
    It only sets the equations for the targetStorage.
    If you want to set up a connection between multiple storages and can't use the other methods, you have to set up the connection for all storages individually.
    '''
    _series_map = {
        'Name': 'name',
        'TargetStorage': 'targestStorage.name',
        'StorageList': 'storageList',
        'CoeffList': 'coeffList',
        'b': 'b'
    }
    def __init__(self,name):
        Component.__init__(self,name)
        self.targestStorage:ThermalStorage = None
        self.storageList:list[Storage] = None
        self.coeffList:list[float] = None
        self.b:float=None
    
    @classmethod
    def newGeneralHeatTransfer(cls, targetStorage:ThermalStorage,storageList:list[Storage],coeffList:list[float],b:float=0, name=None):#TODO was ist mit extStorages
        con = cls(name)
        con.targestStorage = targetStorage
        con.storageList= storageList
        con.coeffList = coeffList
        con.b = b
        return con
        

class FreeConvection(Connection):
    '''
    Free convection in stratified storages between layer a and b where a is below b if temp(a) > temp(b) with given mass flow
    '''
    _series_map = {
        'Name': 'name',
        'Storage1': 'storage1.name',
        'Storage2': 'storage2.name',
        'MassFlow': lambda self: self.get_mFlow(),
        'CpFluid': 'cpFluid',
        'Tolerance': 'tolerance'
    }
    def __init__(self,name):
        Component.__init__(self,name)
        self.storage1:ThermalStorage = None
        self.storage2:ThermalStorage = None
        self.__massFlow:float = None
        self.__massFlow_res = []
        self.tolerance:float = None
        self.cpFluid = None
        
    @classmethod
    def newFreeConvection(cls, storage1:ThermalStorage, storage2:ThermalStorage, massFlow:float, cpFluid=CP_Water, tolerance=0.1,name=None):
        con = cls(name)
        con.storage1 = storage1
        con.storage2 = storage2
        con.__massFlow = massFlow
        con.cpFluid = cpFluid
        con.tolerance = tolerance
        return con
    
    def set_mFlow(self, mFlow):
        if mFlow<0:
            raise ValueError("mFlow must be non-negative. For flows in opposite direction set up a seperate ForcedFlow.")
        self.__massFlow = mFlow
    def get_mFlow(self):
        return self.__massFlow
    def save_massFlow(self):
        self.__massFlow_res.append(self.__massFlow)
    def get_massFlow_res(self):
        return self.__massFlow_res
    
class ForcedConvection(Connection):
    _series_map = {
        'Name': 'name',
        'StorageList': 'storageList',
        'MassFlow': lambda self: self.get_mFlow(),
        'CpFluid': 'cpFluid'
    }
    def __init__(self,name):
        Component.__init__(self,name)
        self.storageList = None
        self.__massFlow = None
        self.cpFluid = None
        self.__massFlow_res = []
        
    def set_mFlow(self, mFlow):
        if mFlow<0:
            raise ValueError("mFlow must be non-negative. For flows in opposite direction set up a seperate ForcedFlow.")
        self.__massFlow = mFlow
        
    def get_mFlow(self):
        return self.__massFlow
    
    def save_massFlow(self):
        self.__massFlow_res.append(self.__massFlow)
    def get_massFlow_res(self):
        return np.array(self.__massFlow_res)
    
    def get_heatflow_res(self):
        from .thermalSystem import SimulationMethod
        temp_res_list = [storage.get_temp_res() for storage in self.storageList]
        match self.simulation_method:
            case SimulationMethod.EXPLICIT_EULER:
                q_lst=[]
                for i in range(len(self.storageList)-1):
                    t1_res = temp_res_list[i][:-1]
                    q = self.get_massFlow_res()[:-1] * self.cpFluid * t1_res
                    q_lst.append(q)
                return q_lst
            case SimulationMethod.IMPLICIT_EULER:
                q_lst=[]
                for i in range(len(self.storageList)-1):
                    t1_res = temp_res_list[i][1:]
                    q = self.get_massFlow_res()[1:] * self.cpFluid * t1_res
                    q_lst.append(q)
                return q_lst
            case SimulationMethod.CRANK_NICOLSON:
                q_lst=[]
                for i in range(len(self.storageList)-1):
                    t1_res_expl = temp_res_list[i][:-1]
                    q_expl = self.get_massFlow_res()[:-1] * self.cpFluid * t1_res_expl
                    t1_res_impl = temp_res_list[i][1:]
                    q_impl = self.get_massFlow_res()[1:] * self.cpFluid * t1_res_impl
                    q_lst.append((q_expl+q_impl)/2)
                return q_lst
    
    @classmethod
    def newForcedConvection(cls,storageList:list[Storage], massFlow, name=None, cpFluid=CP_Water):
        flow = cls(name)
        flow.cpFluid = cpFluid
        storageList = [x for sub in storageList for x in (sub if isinstance(sub, list) else [sub])]
        if not isinstance(storageList, list):
            raise TypeError("storageList must be a list of ThermalStorage objects")
        if not all(isinstance(storage, Storage) for storage in storageList):
            raise TypeError("All elements in storageList must be instances of Storage")
        flow.storageList = storageList
        flow.__massFlow = massFlow
        return flow
    