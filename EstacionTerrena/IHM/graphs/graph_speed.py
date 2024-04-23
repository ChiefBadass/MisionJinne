import pyqtgraph as pg
import numpy as np
import math

class graph_speed(pg.PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title='Acelerometro', viewBox=None, axisItems=None, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)

        self.addLegend()
        self.vel_plot = self.plot(pen=(29, 185, 84), name="Velocidad")
        self.acc_up_plot = self.plot(pen=(255, 0, 0), name="Aceleracion Subida")  # Aceleración de subida en rojo
        self.acc_down_plot = self.plot(pen=(0, 0, 255), name="Aceleracion Bajada")  # Aceleración de bajada en azul
        self.vel_data = np.linspace(0, 0, 30)
        self.acc_up_data = np.linspace(0, 0, 30)
        self.acc_down_data = np.linspace(0, 0, 30)
        self.ptr = 0
        self.vzo = 0

    def update(self, vx, vy, vz):
        # 500 es dt
        if self.ptr == 0:
            self.vzo = float(vz)
            
        self.sum = math.pow(float(vx), 2) + math.pow(float(vy), 2) + math.pow(float(vz), 2)
        self.vel = math.sqrt(self.sum)
        self.vel_data[:-1] = self.vel_data[1:]
        self.vel_data[-1] = self.vel

        a = float(vz) - self.vzo
        
        # Determinar si el CanSat está subiendo o cayendo
        if a > -1:
            self.acc_up_data[:-1] = a
            self.acc_up_data[-1] = a
            self.acc_down_data[:-1] = 0
            self.acc_down_data[-1] = 0
        else:
            self.acc_up_data[:-1] = 0
            self.acc_up_data[-1] = 0
            self.acc_down_data[:-1] = a
            self.acc_down_data[-1] = a
        
        self.vzo = float(vz)
        self.ptr += 1
        self.vel_plot.setData(self.vel_data)
        self.vel_plot.setPos(self.ptr, 0)

        self.acc_up_plot.setData(self.acc_up_data)
        self.acc_up_plot.setPos(self.ptr, 0)

        self.acc_down_plot.setData(self.acc_down_data)
        self.acc_down_plot.setPos(self.ptr, 0)