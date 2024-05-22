import sys
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from communication import Communication
from dataBase import data_base
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon, QPixmap

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
pg.setConfigOption('background', (236, 236, 236))
pg.setConfigOption('foreground', (0, 0, 0))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('HORUS SPACE LAB - MISION JINNE')
        self.setWindowIcon(QIcon('xd.jpg'))  # Añadir el icono aquí
        self.resize(1200, 700)

        # Declarar objetos de comunicación y almacenamiento
        self.ser = Communication()
        self.data_base = data_base()

        # Crear el widget central
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Crear un layout vertical para el widget central
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Crear el widget para el título
        title_bar = QtWidgets.QWidget()
        title_bar.setFixedHeight(50)  # Ajusta la altura del título
        title_bar.setStyleSheet("background-color: #1E1D4F;")  # Color de fondo del título

        # Crear el label para el texto del título
        title_label = QtWidgets.QLabel("HORUS SPACE LAB - MISION JINNE")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: white; 
            font-size: 20px;
            font-weight: bold;
        """)
        
        # Crear el label para el icono del título
        icon_label = QtWidgets.QLabel()
        pixmap = QPixmap('xd.jpg')  # Asegúrate de que 'logo.png' está en el directorio correcto
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(200, 200)  # Ajustar el tamaño del icono

        # Añadir el label al widget del título
        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)

        # Crear la vista y el layout de pyqtgraph
        view = pg.GraphicsView()
        graphics_layout = pg.GraphicsLayout()
        view.setCentralItem(graphics_layout)

        # Añadir widgets al layout
        layout.addWidget(title_bar)
        layout.addWidget(view)

        # Inicialización de gráficos y botones
        self.initialize_graphics_and_buttons(graphics_layout)

        # Configuración del temporizador de actualización
        self.setup_update_timer()

    def initialize_graphics_and_buttons(self, Layout):
        # Fonts for text items
        font = QtGui.QFont()
        font.setPixelSize(90)

        # Buttons style
        boton_estilo = "background-color:rgb(29, 185, 84);color:rgb(0,0,0);font-size:14px;"
        boton_emergencia_estilo = "background-color:rgb(255, 0, 0);color:rgb(255,255,255);font-size:14px; width: 200px; height: 100px;"

    

        # Button Emergency
        proxy3 = QtWidgets.QGraphicsProxyWidget()
        emergency_button = QtWidgets.QPushButton('Despliegue de Emergencia')
        emergency_button.setStyleSheet(boton_emergencia_estilo)
        emergency_button.clicked.connect(self.ser.paro_emergencia)
        proxy3.setWidget(emergency_button)

        # Inicialización de gráficos como atributos de la clase
        self.grafica_altitud = graph_altitude()
        self.grafica_aceleraciones = GraficaAceleracion()
        self.grafica_giroscopio = graph_gyro()
        self.grafica_presion = graph_pressure()
        self.grafica_temperatura = graph_temperature()
        self.grafica_distancia = graph_distance()
        self.time = graph_time(font=font)
        self.free_fall = graph_free_fall(font=font)

       

        l1 = Layout.addLayout(colspan=10, rowspan=2)
        l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))

        # Altitude, speed
        l11.addItem(self.grafica_altitud)
        l11.addItem(self.grafica_temperatura)

        l1.nextRow()

        # Acceleration, gyro, pressure, temperature
        l12 = l1.addLayout(rowspan=1, border=(83, 83, 83))
        l12.addItem(self.grafica_presion)
        l12.addItem(self.grafica_aceleraciones)

        l1.nextRow()
        l13 = l1.addLayout(rowspan=1, border=(83, 83, 83))
        l13.addItem(self.grafica_giroscopio)
        l13.addItem(self.grafica_distancia)
        l1.nextRow()

        # Time, battery and free fall graphs
        l2 = l1.addLayout(rowspan=1, border=(83, 83, 83))
        l2.setFixedHeight(100)
        l2.addItem(self.time)
        l2.nextCol()
        l2.addItem(self.free_fall)
        l2.nextCol()
        
        l2.addItem(proxy3)

    def setup_update_timer(self):
        if self.ser.isOpen() or self.ser.dummyMode():
            self.timer = pg.QtCore.QTimer()
            self.timer.timeout.connect(self.update)
            self.timer.start(100)
        else:
            print("something is wrong with the update call")

    def update(self):
        try:
            datos = self.ser.obtener_datos_separados()

            self.grafica_temperatura.update(datos['temperatura'])
            self.grafica_presion.update(datos['presion'])
            self.grafica_altitud.update(datos['altitud'])
            self.grafica_aceleraciones.update(datos['aceleracion_x'], datos['aceleracion_y'], datos['aceleracion_z'])
            self.grafica_giroscopio.update(datos['gyro_x'], datos['gyro_y'], datos['gyro_z'])
            self.grafica_distancia.update(datos['latitud_carga_primaria'], datos['longitud_carga_primaria'], datos['latitud_carga_secundaria'], datos['longitud_carga_secundaria'], datos['distancia'])

            with open('C:/Users/carlo/Documents/python/Mision_Jinne-main/flight_data.csv', 'a') as archivo:
                archivo.write(f"{datos}\n")
        except IndexError:
            print('starting, please wait a moment')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())