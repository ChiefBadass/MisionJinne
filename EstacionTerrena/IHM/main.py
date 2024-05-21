import sys
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from communication import Communication
from dataBase import data_base
from PyQt5.QtWidgets import QPushButton

from graphs.grafica_aceleracion import GraficaAceleracion
from graphs.graph_altitude import graph_altitude
from graphs.graph_battery import graph_battery
from graphs.graph_free_fall import graph_free_fall
from graphs.graph_gyro import graph_gyro
from graphs.graph_pressure import graph_pressure
from graphs.graph_speed import graph_speed
from graphs.graph_temperature import graph_temperature
from graphs.graph_time import graph_time
from graphs.graph_distance import graph_distance

pg.setConfigOption('background', (33, 33, 33))
pg.setConfigOption('foreground', (197, 198, 199))
# Interface variables
app = QtWidgets.QApplication(sys.argv)
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()
view.setCentralItem(Layout)
view.show()
view.setWindowTitle('HORUS SPACE LAB - MISION JINNE')
view.resize(1200, 700)

# declare object for serial Communication
ser = Communication()
# declare object for storage in CSV
data_base = data_base()
# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(90)

# buttons style
boton_estilo = "background-color:rgb(29, 185, 84);color:rgb(0,0,0);font-size:14px;"
boton_emergencia_estilo = "background-color:rgb(255, 0, 0);color:rgb(255,255,255);font-size:14px; width: 200px; height: 100px;"

# Button 1
proxy = QtWidgets.QGraphicsProxyWidget()
save_button = QtWidgets.QPushButton('Iniciar almacenamiento')
save_button.setStyleSheet(boton_estilo)
save_button.clicked.connect(data_base.start)
proxy.setWidget(save_button)

# Button 2
proxy2 = QtWidgets.QGraphicsProxyWidget()
end_save_button = QtWidgets.QPushButton('Deneter almacenamiento')
end_save_button.setStyleSheet(boton_estilo)
end_save_button.clicked.connect(data_base.stop)
proxy2.setWidget(end_save_button)

# Button Emergency
proxy3 = QtWidgets.QGraphicsProxyWidget()
emergency_buttom = QtWidgets.QPushButton('Despliegue de Emergencia')
emergency_buttom.setStyleSheet(boton_emergencia_estilo)
emergency_buttom.clicked.connect(ser.paro_emergencia)
proxy3.setWidget(emergency_buttom)

# Inicializacion de graficas
grafica_altitud = graph_altitude()
grafica_aceleraciones = GraficaAceleracion()
grafica_giroscopio = graph_gyro()
grafica_presion = graph_pressure()
grafica_temperatura = graph_temperature()
grafica_distancia = graph_distance()
time = graph_time(font=font)
free_fall = graph_free_fall(font=font)


lb = Layout.addLayout(colspan=21)
lb.addItem(proxy)
lb.nextCol()
lb.addItem(proxy2)

Layout.nextRow()

l1 = Layout.addLayout(colspan=10, rowspan=2)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))

# Altitude, speed
l11.addItem(grafica_altitud)
l11.addItem(grafica_temperatura)

# l11.addItem(speed)
l1.nextRow()

# Acceleration, gyro, pressure, temperature
l12 = l1.addLayout(rowspan=1, border=(83, 83, 83))
l12.addItem(grafica_presion)
l12.addItem(grafica_aceleraciones)

# l12.addItem(pressure)
l1.nextRow()
l13 = l1.addLayout(rowspan=1, border=(83, 83, 83))
l13.addItem(grafica_giroscopio)
l13.addItem(grafica_distancia)
l1.nextRow()

# Time, battery and free fall graphs
l2 = l1.addLayout(rowspan=1, border=(83, 83, 83))
l2.setFixedHeight(100)
l2.addItem(time)
l2.nextCol()
l2.addItem(proxy3)
l2.nextCol()
l2.addItem(free_fall)

def update():
    try:
        datos = ser.obtener_datos_separados()

        grafica_temperatura.update(datos['temperatura'])
        grafica_presion.update(datos['presion'])
        grafica_altitud.update(datos['altitud'])
        grafica_aceleraciones.update(datos['aceleracion_x'], datos['aceleracion_y'], datos['aceleracion_z'])
        grafica_giroscopio.update(datos['gyro_x'], datos['gyro_y'], datos['gyro_z'])
        grafica_distancia.update(datos['latitud_carga_primaria'], datos['longitud_carga_primaria'], datos['latitud_carga_secundaria'], datos['longitud_carga_secundaria'], datos['distancia'])

        archivo = open('C:/Users/carlo/Documents/python/Mision_Jinne-main/flight_data.csv', 'a')
        archivo.write(f"{datos}/n")
        archivo.close()
    except IndexError:
        print('starting, please wait a moment')


if (ser.isOpen()) or (ser.dummyMode()):
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100)
else:
    print("something is wrong with the update call")
# Start Qt event loop unless running in interactive mode.

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()