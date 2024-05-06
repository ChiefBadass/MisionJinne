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

        print("the available ports are (if none appear, press any letter): ")
        for port in sorted(self.ports):
            # obtener la lista de puetos: https://stackoverflow.com/a/52809180
            print(("{}".format(port)))
        self.portName = input("write serial port name (ex: /dev/ttyUSB0): ")
        try:
            self.ser = serial.Serial(self.portName, self.baudrate)
        except serial.serialutil.SerialException:
            print("Can't open : ", self.portName)
            #self.dummyPlug = True
            print("Dummy mode activated")

    def close(self):
        if (self.ser.isOpen()):
            self.ser.close()
        else:
            print(self.portName, " it's already closed")

    def getData(self):
        # if (self.dummyMode == False):
        #     # value = self.ser.readline()  # read line (single value) from the serial port
        #     # decoded_bytes = str(value[0:len(value) - 2].decode("utf-8"))
        #     # # print(decoded_bytes)
        #     # value_chain = decoded_bytes.split(",")
        #     value_chain = self.obtener_datos_separados()

        # else:
        
        value_chain = self.obtener_datos_separados()

        return value_chain

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
                temperatura, presion, altitud, aceleracion_x, aceleracion_y, aceleracion_z, gyro_x, gyro_y, gyro_z, latitud1, longitud1, latitud2, longitud2, distancia, tiempo = [None] * 16

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
                        latitud1 = float(dato.replace('l', ''))
                    elif dato.startswith('n'):
                        longitud1 = float(dato.replace('n', ''))
                    elif dato.startswith('u'):
                        latitud2 = float(dato.replace('u', ''))
                    elif dato.startswith('o'):
                        longitud2 = float(dato.replace('o', ''))
                    elif dato.startswith('d'):
                        distancia = float(dato.replace('d', ''))
                    elif dato.startswith('m'):
                        tiempo = float(dato.replace('m', ''))

                datos_separados = [temperatura, presion, altitud, aceleracion_x, aceleracion_y, aceleracion_z, gyro_x, gyro_y, gyro_z, latitud1, longitud1, latitud2, longitud2, distancia, tiempo]

                return datos_separados
        except Exception as e:
            print(e)
            # print("fallo recepcion de datos")
