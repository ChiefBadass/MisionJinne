import random
import serial
import serial.tools.list_ports


class Communication:
    baudrate = ''
    portName = ''
    dummyPlug = False
    ports = serial.tools.list_ports.comports()
    ser = serial.Serial()
    
    def __init__(self):
        self.baudrate = 115200

        print("Puertos seriales disponibles: ")
        for port in sorted(self.ports):
            # obtener la lista de puetos: https://stackoverflow.com/a/52809180
            print(("{}".format(port)))
        self.portName = input("Escribe el nombre del puerto (ejemplo: /dev/ttyUSB0): ")
        try:
            self.ser = serial.Serial(self.portName, self.baudrate)
        except serial.serialutil.SerialException:
            print("No se pudo abrir el puerto: ", self.portName)
            #self.dummyPlug = True
            print("Dummy mode activado")

    def close(self):
        if (self.ser.isOpen()):
            self.ser.close()
        else:
            print(self.portName, " it's already closed")

    def isOpen(self):
        return self.ser.isOpen()

    def dummyMode(self):
        return self.dummyPlug

    def paro_emergencia(self):
        self.ser.write(b'paro_emergencia')
        print("paro_emergencia")
        return 0

    def obtener_datos_separados(self):
        try:
            if self.ser.in_waiting > 0:
                datos_obtenidos = self.ser.readline().decode('utf-8', errors='ignore').rstrip()
                datos = datos_obtenidos.split(',')
                temperatura, presion, altitud, aceleracion_x, aceleracion_y, aceleracion_z, gyro_x, gyro_y, gyro_z, direccion, latitud_carga_primaria, longitud_carga_primaria, latitud_carga_secundaria, longitud_carga_secundaria, distancia, tiempo = [None] * 16

                for dato in datos:
                    if dato.startswith('t'):
                        temperatura = float(dato.replace('t', ''))
                    elif dato.startswith('p'):
                        presion = float(dato.replace('p', ''))
                    elif dato.startswith('a'):
                        altitud = float(dato.replace('a', ''))
                    elif dato.startswith('x'):
                        aceleracion_x = float(dato.replace('x', ''))
                    elif dato.startswith('y'):
                        aceleracion_y = float(dato.replace('y', ''))
                    elif dato.startswith('z'):
                        aceleracion_z = float(dato.replace('z', ''))   
                    elif dato.startswith('g'):
                        gyro_x = float(dato.replace('g', ''))
                    elif dato.startswith('i'):
                        gyro_y = float(dato.replace('i', ''))
                    elif dato.startswith('r'):
                        gyro_z = float(dato.replace('r', ''))
                    elif dato.startswith('l'):
                        latitud_carga_primaria = float(dato.replace('l', ''))
                    elif dato.startswith('n'):
                        longitud_carga_primaria = float(dato.replace('n', ''))
                    elif dato.startswith('u'):
                        latitud_carga_secundaria = float(dato.replace('u', ''))
                    elif dato.startswith('o'):
                        longitud_carga_secundaria = float(dato.replace('o', ''))
                    elif dato.startswith('d'):
                        distancia = float(dato.replace('d', ''))

                datos_separados = {
                    'temperatura': temperatura,
                    'presion': presion,
                    'altitud': altitud,
                    'aceleracion_x': aceleracion_x,
                    'aceleracion_y': aceleracion_y,
                    'aceleracion_z': aceleracion_z,
                    'gyro_x': gyro_x,
                    'gyro_y': gyro_y,
                    'gyro_z': gyro_z,
                    'latitud_carga_primaria': latitud_carga_primaria,
                    'longitud_carga_secundaria': longitud_carga_primaria,
                    'latitud_carga_secundaria': latitud_carga_secundaria,
                    'longitud_carga_secundaria': longitud_carga_secundaria,
                    'distancia': distancia
                }

                return datos_separados
        except Exception as e:
            print(e)
            # print("fallo recepcion de datos")
