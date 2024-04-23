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
                temperatura, presion, altitud, aceleracion_x, aceleracion_y, aceleracion_z, gyro_x, gyro_y, gyro_z, direccion, latitud1, longitud1, latitud2, longitud2, distancia, tiempo = [None] * 16

                for dato in datos:
                    if dato.startswith('t'):
                        temperatura = float(dato.replace('t', ''))
                    elif dato.startswith('p'):
                        presion = float(dato.replace('p', ''))
                    elif dato.startswith('a'):
                        altitud = float(dato.replace('a', ''))
                    elif dato.startswith('AX'):
                        aceleracion_x = float(dato.replace('AX', ''))
                    elif dato.startswith('AY'):
                        aceleracion_y = float(dato.replace('AY', ''))
                    elif dato.startswith('AZ'):
                        aceleracion_z = float(dato.replace('AZ', ''))   
                    elif dato.startswith('GX'):
                        gyro_x = float(dato.replace('GX', ''))
                    elif dato.startswith('GY'):
                        gyro_y = float(dato.replace('GY', ''))
                    elif dato.startswith('GZ'):
                        gyro_z = float(dato.replace('GZ', ''))
                    elif dato.startswith('DM'):
                        direccion = float(dato.replace('DM', ''))
                    elif dato.startswith('lat1'):
                        latitud1 = float(dato.replace('lat1', ''))
                    elif dato.startswith('lng1'):
                        longitud1 = float(dato.replace('lng1', ''))
                    elif dato.startswith('LAT2'):
                        latitud2 = float(dato.replace('LAT2', ''))
                    elif dato.startswith('LNG2'):
                        longitud2 = float(dato.replace('LNG2', ''))
                    elif dato.startswith('DI'):
                        distancia = float(dato.replace('DI', ''))
                    elif dato.startswith('TM'):
                        tiempo = float(dato.replace('TM', ''))

                datos_separados = [temperatura, presion, altitud, aceleracion_x, aceleracion_y, aceleracion_z, gyro_x, gyro_y, gyro_z, direccion, latitud1, longitud1, latitud2, longitud2, distancia, tiempo]

                return datos_separados
        except Exception as e:
            print(e)
            # print("fallo recepcion de datos")
