import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from communication import Communication
from dataBase import data_base
from graphs.graph_acceleration import graph_acceleration
from graphs.graph_altitude import graph_altitude
from graphs.graph_battery import graph_battery
from graphs.graph_free_fall import graph_free_fall
from graphs.graph_gyro import graph_gyro
from graphs.graph_pressure import graph_pressure
from graphs.graph_speed import graph_speed
from graphs.graph_temperature import graph_temperature
from graphs.graph_time import graph_time


class FlightMonitoringWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Flight Monitoring')
        self.resize(1200, 700)

        # Interface variables
        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout()
        self.view.setCentralItem(self.layout)
        self.view.setWindowTitle('Flight monitoring')

        # declare object for serial Communication
        self.ser = Communication()
        # declare object for storage in CSV
        self.data_base = data_base()

        self.setup_ui()

    def setup_ui(self):
        # Fonts for text items
        font = QtGui.QFont()
        font.setPixelSize(90)

        # buttons style
        style = "background-color:rgb(29, 185, 84);color:rgb(0,0,0);font-size:14px;"

        # Declare graphs
        # Button 1
        proxy = QtWidgets.QGraphicsProxyWidget()
        save_button = QPushButton('Start storage')
        save_button.setStyleSheet(style)
        save_button.clicked.connect(self.data_base.start)
        proxy.setWidget(save_button)

        # Button 2
        proxy2 = QtWidgets.QGraphicsProxyWidget()
        end_save_button = QPushButton('Stop storage')
        end_save_button.setStyleSheet(style)
        end_save_button.clicked.connect(self.data_base.stop)
        proxy2.setWidget(end_save_button)

        # Altitude graph
        altitude = graph_altitude()
        # Speed graph
        speed = graph_speed()
        # Acceleration graph
        acceleration = graph_acceleration()
        # Gyro graph
        gyro = graph_gyro()
        # Pressure Graph
        pressure = graph_pressure()
        # Temperature graph
        temperature = graph_temperature()
        # Time graph
        time = graph_time(font=font)
        # Battery graph
        battery = graph_battery(font=font)
        # Free fall graph
        free_fall = graph_free_fall(font=font)

        ## Setting the graphs in the layout
        # Title at top
        text = """"""
        self.layout.addLabel(text, col=1, colspan=21)
        self.layout.nextRow()

        # Put vertical label on left side
        self.layout.addLabel('LIDER - ATL research hotbed', angle=-90, rowspan=3)
        self.layout.nextRow()

        lb = self.layout.addLayout(colspan=21)
        lb.addItem(proxy)
        lb.nextCol()
        lb.addItem(proxy2)

        self.layout.nextRow()

        l1 = self.layout.addLayout(colspan=20, rowspan=2)
        l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))

        # Altitude, speed
        l11.addItem(altitude)
        l11.addItem(speed)
        l1.nextRow()

        # Acceleration, gyro, pressure, temperature
        l12 = l1.addLayout(rowspan=1, border=(83, 83, 83))
        l12.addItem(acceleration)
        l12.addItem(gyro)
        l12.addItem(pressure)
        l12.addItem(temperature)

        # Time, battery and free fall graphs
        l2 = self.layout.addLayout(border=(83, 83, 83))
        l2.addItem(time)
        l2.nextRow()
        l2.addItem(battery)
        l2.nextRow()
        l2.addItem(free_fall)

        if (self.ser.isOpen()) or (self.ser.dummyMode()):
            timer = pg.QtCore.QTimer()
            timer.timeout.connect(self.update)
            timer.start(500)
        else:
            print("something is wrong with the update call")

    def update(self):
        try:
            value_chain = []
            value_chain = self.ser.getData()
            self.altitude.update(value_chain[1])
            self.speed.update(value_chain[8], value_chain[9], value_chain[10])
            self.time.update(value_chain[0])
            self.acceleration.update(value_chain[8], value_chain[9], value_chain[10])
            self.gyro.update(value_chain[5], value_chain[6], value_chain[7])
            self.pressure.update(value_chain[4])
            self.temperature.update(value_chain[3])
            self.free_fall.update(value_chain[2])
            self.data_base.guardar(value_chain)
        except IndexError:
            print('starting, please wait a moment')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = FlightMonitoringWindow()
    main_window.show()
    sys.exit(app.exec_())
