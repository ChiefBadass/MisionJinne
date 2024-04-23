#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_BMP280.h>
#include <MPU9250_asukiaaa.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include <Servo.h>

byte CargaPrimaria = 0xFF;
byte CargaSecundaria = 0xCC;
byte EstacionTerrena = 0xBB;
String mensajeContingencia = "";

static const int RxPinGPS = 3, TxPinGPS = 4;
static const uint32_t GPSBaud = 9600;

TinyGPSPlus gps;
SoftwareSerial ss(RxPinGPS, TxPinGPS);
Adafruit_BMP280 bmp;  // I2C
MPU9250_asukiaaa mpu;
Servo servo;

float aceleracionX, aceleracionY, aceleracionZ;
float giroscopioX, giroscopioY, giroscopioZ;
float direccionMagnetometro, magnetometroX, magnetometroY, magnetometroZ;
float presionInicial, altura, temperatura, presion;
double latitudCargaPrimaria, longitudCargaPrimaria;
double latitudCargaSecundaria, longitudCargaSecundaria;
double distanciaEntreCargas;

long ultimaVezQueSeEnvioUnMensaje = 0;
long tiempoEncendido = 0;
int intervalo = 300;

// se debe de cambiar!!!
int alturaMaxima = 2;
int alturaDespliegue = 1;

bool maximoAlcanzado = false;
bool mensajeEnviadoALaCargaSecundaria = false;

String mensaje = "";

void setup() {
  Serial.begin(115200);
  servo.attach(6);
  servo.write(0);
  
  while (!Serial);
  LoRa.setSPIFrequency(433E6);
  Serial.println("Carga Primaria");

  if (!LoRa.begin(433E6)) {
    Serial.println("Fallo en iniciar LoRa!");
    while (1);
  }

  ss.begin(GPSBaud);
  bmp.begin(0x76);
  mpu.beginAccel();
  mpu.beginGyro();
  mpu.beginMag();

  mpu.magXOffset = -50;
  mpu.magYOffset = -55;
  mpu.magZOffset = -10;

  presionInicial = bmp.readPressure() / 100;
}

void loop() {
  mensaje = "";
  tiempoEncendido = millis();

  if (tiempoEncendido - ultimaVezQueSeEnvioUnMensaje > intervalo) {
    while (ss.available() > 0)
      if (gps.encode(ss.read())) {
        latitudCargaPrimaria = gps.location.lat();
        longitudCargaPrimaria = gps.location.lng();        
        distanciaEntreCargas = haversine(latitudCargaPrimaria, longitudCargaPrimaria, latitudCargaSecundaria, longitudCargaSecundaria);
      }

    if (mpu.accelUpdate() == 0) {
       aceleracionX = mpu.accelX();
       aceleracionY = mpu.accelY();
       aceleracionZ = mpu.accelZ();
     }
     if (mpu.gyroUpdate() == 0) {
       giroscopioX = mpu.gyroX();
       giroscopioY = mpu.gyroY();
       giroscopioZ = mpu.gyroZ();
     }
      if (mpu.magUpdate() == 0) {
       magnetometroX = mpu.magX();
       magnetometroY = mpu.magY();
       magnetometroZ = mpu.magZ();
       direccionMagnetometro = mpu.magHorizDirection();
     }
  
    temperatura = (bmp.readTemperature()) - 2.45;
    presion = (bmp.readPressure() / 100);
    altura = (bmp.readAltitude(presionInicial));

    if(altura >= alturaMaxima){
      maximoAlcanzado = true;
    }

    if(altura <= alturaDespliegue && maximoAlcanzado){
      //se activa el servo...
      servo.write(90);
    }
    

    if(mensajeContingencia == "c"){
      servo.write(90);//se activa el servo
    }

    int contador = 0;
    if(altura <= 20 && maximoAlcanzado && !mensajeEnviadoALaCargaSecundaria){
      while(contador <= 25){
        enviarMensajeACargaSecundaria("listo");
        contador++;
        delay(20);
      }
    }

    mensaje += "t" + String(temperatura) + ",";
    mensaje += "p" + String(presion) + ",";
    mensaje += "a" + String(altura) + ",";
    mensaje += "t" + String(temperatura) + ",";
    mensaje += "t" + String(temperatura) + ",";
    mensaje += "AX" + String(aceleracionX) + ",";
    mensaje += "AY" + String(aceleracionY) + ",";
    mensaje += "AZ" + String(aceleracionZ) + ",";
    mensaje += "GX" + String(giroscopioX) + ",";
    mensaje += "GY" + String(giroscopioY) + ",";
    mensaje += "GZ" + String(giroscopioZ) + ",";
    mensaje += "DM" + String(direccionMagnetometro)+ ",";
    mensaje += "lat1" + String(latitudCargaPrimaria, 6) + ",";
    mensaje += "lng1" + String(longitudCargaPrimaria, 6) + ",";
    mensaje += "LAT2" + String(latitudCargaSecundaria, 6) + ",";
    mensaje += "LNG2" + String(longitudCargaSecundaria, 6) + ",";
    mensaje += "DI" + String(distanciaEntreCargas) + ",";
    mensaje += "TM" + String(tiempoEncendido);

    sendMessage(mensaje);


    ultimaVezQueSeEnvioUnMensaje = millis(); 
    intervalo = random(145) + 100;  
  }

  onReceive(LoRa.parsePacket());

  delay(50);
}

void sendMessage(String message) {
  LoRa.beginPacket();
  LoRa.write(EstacionTerrena);
  LoRa.write(CargaPrimaria);
  LoRa.write(message.length());
  LoRa.print(message);
  LoRa.endPacket();
  Serial.println(message);
}

void enviarMensajeACargaSecundaria(String message) {
  LoRa.beginPacket();
  LoRa.write(CargaSecundaria);
  LoRa.write(CargaPrimaria);
  LoRa.write(message.length());
  LoRa.print(message);
  LoRa.endPacket();
  Serial.println("Sending packet a carga secundaria");
  mensajeEnviadoALaCargaSecundaria = true;
}

void onReceive(int packetSize) {
  if (packetSize == 0) return;
  int recipient = LoRa.read();
  byte sender = LoRa.read();
  byte myMessageLength = LoRa.read();
  String myMessage = "";

  if (recipient != CargaPrimaria) return;  // skip rest of function

  while (LoRa.available()) {
    myMessage += (char)LoRa.read();
  }

  if (myMessageLength != myMessage.length()) return;         
  
  if(sender == EstacionTerrena){
    mensajeContingencia = myMessage;
    return;
  }

  char textoChar[20]; // Creamos un array de caracteres para almacenar el string
  myMessage.toCharArray(textoChar, 20); // Convertimos el string a un array de caracteres

  char *lat = strtok(textoChar, ","); 
  char *lng = strtok(NULL, ","); 

  latitudCargaSecundaria = strtod(lat, NULL); 
  longitudCargaSecundaria = strtod(lng, NULL);

  
}
double haversine(float lat1, float lng1, float lat2, double lng2) {
  double R = 6371.0;
  lat1 = radians(lat1);
  lng1 = radians(lng1);
  lat2 = radians(lat2);
  lng2 = radians(lng2);
  double dlat = lat2 - lat1;
  double dlon = lng2 - lng1;
  double a = sin(dlat / 2) * sin(dlat / 2) +
             cos(lat1) * cos(lat2) * sin(dlon / 2) * sin(dlon / 2);
  double c = 2 * atan2(sqrt(a), sqrt(1 - a));
  double distance = R * c;
  return distance * 1000;
}