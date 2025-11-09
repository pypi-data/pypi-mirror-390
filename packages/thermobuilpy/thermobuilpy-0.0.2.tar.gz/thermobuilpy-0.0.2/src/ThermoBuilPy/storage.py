import numpy as np
import matplotlib.pyplot as plt
from abc import abstractmethod
from .component import Component
CP_Water = 4.186/3.6 # Specific heat capacity of water in Wh/kg (?)#TODO

def temp_to_Q(temp,cap):
        return temp * cap

class Storage(Component):
    @abstractmethod
    def get_temp(self):
        pass
    @abstractmethod
    def get_temp_res(self):
        pass
    
class ThermalStorage(Storage):
    _series_map = {
        'Name': 'name',
        'Capacity': 'cap',
        'Temperature': lambda self: self.get_temp(),
        }
    def __init__(self,name):
        Component.__init__(self,name)
        self.col=None
        self.cap=None
        self.temp=None
        self.__Q=None
        self.mass=None  # Volume, if applicable
    @classmethod
    def fromPDSeries(cls, pdSeries):
        return cls.newStorage(
            cap=pdSeries['Capacity'],
            temp=pdSeries['Temperature'],
            name=pdSeries['Name'])
    @classmethod    
    def newStorage(cls,cap,temp,name=None):
        storage = cls(name)
        storage.cap = cap
        storage.__Q = temp_to_Q(temp, cap)
        return storage
    
    @classmethod
    def newStorageByMass(cls,mass,cp,temp,name=None):
        storage = cls(name)
        storage.cap = mass * cp
        storage.mass=mass
        storage.__Q = temp_to_Q(temp, storage.cap)
        return storage
    
    def sim_prep(self, num_steps=None):
        if num_steps:
            self.__Q_res = np.zeros(num_steps+1)
        else:
            self.__Q_res = []
    
    def set_col(self,col:int):
        self.col = col
    
    def set_Q(self, Q, t):
        self.__Q = Q
        if isinstance(self.__Q_res,np.ndarray):
            self.__Q_res[t] = Q
        else:
            self.__Q_res.append(Q)
    
    def set_temp(self,temp):
        self.__Q = temp_to_Q(temp, self.cap)
    
    def get_Q(self):
        return self.__Q
    
    def get_temp(self):
        return self.__Q / self.cap 
    
    def get_temp_res(self):
        return np.array(self.__Q_res) / self.cap
    
    def get_Q_res(self):
        try:
            return self.__Q_res
        except:
            raise Exception('First run the simulation, then get get results.')
    
    def plot_temp_res(self,ax,color=None):
        temp_res = self.get_temp_res()
        if color:
            ax.plot(temp_res,label=self.name,color=color)
        else:
            ax.plot(temp_res,label=self.name)


class ExtStorage(Storage):
    _series_map = {
        'Name': 'name',
        'Temperature': lambda self: self.get_temp(),
        }
    def __init__(self,name,temp):
        Component.__init__(self,name)
        self.__temp = temp
        self.__temp_res = []
    @classmethod
    def newExtStorage(cls,name=None,temp=0):
        storage = cls(name,temp)
        return storage
    
    def sim_prep(self, num_steps=None):
        self.Q_sum = 0
        if num_steps:
            self.__q_res = np.zeros(num_steps+1)
        else:
            self.__q_res = []
    
    def add_q(self, q, t=None):
        self.Q_sum += q
        if t:
            self.__q_res[t] = q
    def set_temp(self,temp):
        self.__temp = temp
    def get_temp(self):
        return self.__temp
    def get_q_res(self):
        return self.__q_res
    def save_temp(self):
        self.__temp_res.append(self.__temp)
    def get_temp_res(self):
        return np.array(self.__temp_res)
    @classmethod
    def fromPDSeries(cls, pdSeries):
        return cls.newExtStorage(
            temp=pdSeries['Temperature'],
            name=pdSeries['Name'])