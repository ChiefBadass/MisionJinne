import sys
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from communication import Communication
from dataBase import data_base
from PyQt5.QtWidgets import QPushButton
from graphs.graph_acceleration import graph_acceleration
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
style = "background-color:rgb(29, 185, 84);color:rgb(0,0,0);font-size:14px;"
styleE = "background-color:rgb(255, 0, 0);color:rgb(255,255,255);font-size:14px; width: 200px; height: 100px;"


# Declare graphs
# Button 1
# proxy = QtWidgets.QGraphicsProxyWidget()
# save_button = QtWidgets.QPushButton('Iniciar almacenamiento')
# save_button.setStyleSheet(style)
# save_button.clicked.connect(data_base.start)
# proxy.setWidget(save_button)


# Button 2
# proxy2 = QtWidgets.QGraphicsProxyWidget()
# end_save_button = QtWidgets.QPushButton('Deneter almacenamiento')
# end_save_button.setStyleSheet(style)
# end_save_button.clicked.connect(data_base.stop)
# proxy2.setWidget(end_save_button)
# Button Emergency
proxy3 = QtWidgets.QGraphicsProxyWidget()
emergency_buttom = QtWidgets.QPushButton('Despliegue de Emergencia')
emergency_buttom.setStyleSheet(styleE)
emergency_buttom.clicked.connect(ser.paro_emergencia)
proxy3.setWidget(emergency_buttom)

# Altitude graph
altitude = graph_altitude()
# Speed graph
speed = graph_speed()
# Acceleration graph
# acceleration = graph_acceleration()
# Gyro graph
gyro = graph_gyro()
# Pressure Graph
pressure = graph_pressure()
# Temperature graph
temperature = graph_temperature()

distance = graph_distance()
# Time graph
time = graph_time(font=font)
# Battery graph
# battery = graph_battery(font=font)
# Free fall graph
free_fall = graph_free_fall(font=font)


# lb = Layout.addLayout(colspan=21)
# lb.addItem(proxy)
# lb.nextCol()
# lb.addItem(proxy2)

# Layout.nextRow()

l1 = Layout.addLayout(colspan=10, rowspan=2)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))

# Altitude, speed
l11.addItem(altitude)
l11.addItem(temperature)

# l11.addItem(speed)
l1.nextRow()

# Acceleration, gyro, pressure, temperature
l12 = l1.addLayout(rowspan=1, border=(83, 83, 83))
l12.addItem(pressure)
l12.addItem(speed)

# l12.addItem(pressure)
l1.nextRow()
l13 = l1.addLayout(rowspan=1, border=(83, 83, 83))
l13.addItem(gyro)
l13.addItem(distance)
l1.nextRow()

# Time, battery and free fall graphs
l2 = l1.addLayout(rowspan=1, border=(83, 83, 83))
l2.setFixedHeight(100)
l2.addItem(time)
l2.nextCol()
l2.addItem(proxy3)
l2.nextCol()
l2.addItem(free_fall)

# you have to put the position of the CSV stored in the value_chain list
# that represent the date you want to visualize


def update():
    try:
        value_chain = ser.getData()
        # value_chain = [1, 3]
        temperature.update(value_chain[0])
        pressure.update(value_chain[1])
        altitude.update(value_chain[2])
        speed.update(value_chain[3], value_chain[4], value_chain[5])
        gyro.update(value_chain[6], value_chain[7], value_chain[8])
        time.update(value_chain[15])
        distance.update(value_chain[10], value_chain[11], value_chain[12], value_chain[13], value_chain[14])
        archivo = open('C:/Users/carlo/Documents/python/Mision_Jinne-main/flight_data.csv', 'a')
        archivo.write(f"{value_chain}\n")
        archivo.close()
        
        #acceleration.update(value_chain[3], value_chain[4], value_chain[5])
        
        # free_fall.update(value_chain[2])
        #data_base.guardar(value_chain)

        

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