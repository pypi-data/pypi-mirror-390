from .storage import ThermalStorage
from .connection import Conduction,FreeConvection
from .component import Component
CP_Water = 4.186/3.6 # Specific heat capacity of water in Wh/kg (?)#TODO
import matplotlib.pyplot as plt
class StratifiedStorage(Component):
    _series_map = {
        'Name': 'name',
        'Layers': 'layers',
        'Conductions': 'conductions',
        'FreeConvections': 'freeConvections'
    }
    def __init__(self,name):
        Component.__init__(self,name)
        self.layers:list[ThermalStorage] = []
        self.conductions:list[Conduction] = []
        self.freeConvections:list[FreeConvection] = []
    
    @classmethod
    def newStratifiedStorageByMasses(cls, layerMasses:list,layerTemperatures:list,conductionCoeff:list[float]|float,freeConvectionMassFlow:list[float]|float=0,cpFluid=CP_Water, name=None): #TODO name: Stratified or MultiLayer?
        storage = cls(name)
        if not isinstance(conductionCoeff,list):
            conductionCoeff = [conductionCoeff] * (len(layerMasses) - 1)
        if not isinstance(freeConvectionMassFlow,list):
            freeConvectionMassFlow = [freeConvectionMassFlow] * (len(layerMasses) - 1)
        if not len(layerMasses) == len(layerTemperatures) == len(conductionCoeff)+1:
            raise ValueError("layerVolumes and layerTemperatures must have the same length.")
        
        for i in range(len(layerMasses)):
            storage.layers.append(ThermalStorage.newStorageByMass(layerMasses[i], cpFluid, layerTemperatures[i]))
        for i, cond_coeff in enumerate(conductionCoeff):
            storage.conductions.append(
                Conduction(
                    storage1=storage.layers[i],
                    storage2=storage.layers[i+1],
                    coeff=cond_coeff
                )
            )
        for i, mFlow in enumerate(freeConvectionMassFlow):
            storage.freeConvections.append(
                FreeConvection.newFreeConvection(
                    storage1=storage.layers[i],
                    storage2=storage.layers[i+1],
                    massFlow=mFlow,
                    cpFluid=cpFluid
                    )
                )
        return storage
    
    @classmethod
    def newStratifiedStorageByCapacities(cls, layerCapacities:list,layerTemperatures:list,conductionCoeff:list[float]|float,freeConvectionMassFlow:list[float]|float=0,cpFluid=CP_Water, name=None): #TODO name: Stratified or MultiLayer?
        storage = cls(name)
        if not isinstance(conductionCoeff,list):
            conductionCoeff = [conductionCoeff] * (len(layerCapacities) - 1)
        if not isinstance(freeConvectionMassFlow,list):
            freeConvectionMassFlow = [freeConvectionMassFlow] * (len(layerCapacities) - 1)
        if not len(layerCapacities) == len(layerTemperatures) == len(conductionCoeff)+1:
            raise ValueError("layerCapacities and layerTemperatures must have the same length.")
        
        for i in range(len(layerCapacities)):
            storage.layers.append(ThermalStorage.newStorage(layerCapacities[i],layerTemperatures[i]))
        for i, cond_coeff in enumerate(conductionCoeff):
            storage.conductions.append(
                Conduction(
                    storage1=storage.layers[i],
                    storage2=storage.layers[i+1],
                    coeff=cond_coeff
                )
            )
        for i, mFlow in enumerate(freeConvectionMassFlow):
            storage.freeConvections.append(
                FreeConvection.newFreeConvection(
                    storage1=storage.layers[i],
                    storage2=storage.layers[i+1],
                    massFlow=mFlow,
                    cpFluid=cpFluid
                    )
                )
        return storage
    
    def updateConductionCoeffs(self, conductionCoeff:list[float]|float):
        if not isinstance(conductionCoeff,list):
            conductionCoeff = [conductionCoeff] * (len(self.layers) - 1)
        if not len(conductionCoeff) == len(self.layers) - 1:
            raise ValueError("conductionCoeff must have length equal to number of layers - 1.")
        for i,cond in enumerate(self.conductions):
            cond.coeff = conductionCoeff[i]
    
    
    def getLayers(self, start:int, end:int):
        if start < 0 or end >= len(self.layers) :
            raise IndexError("Invalid layer indices.")
        if start<end:
            return self.layers[start:end+1]
        else:
            return list(reversed(self.layers[end:start+1]))
        
    def getLayer(self, i:int):
        if i<0 or i> len(self.layers)-1:
            raise ValueError(f'Storage has {len(self.layers)} layers. Index must be 0<=i<{len(self.layers)}')
        return self.layers[i]
    
    def plot_temp_res(self):
        for i,layer in enumerate(self.layers):
            plt.plot(layer.get_temp_res(), label=layer.name)
        plt.title(f'Temperature of {self.name} Layers Over Time')
        plt.xlabel('Time Step')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        plt.show()