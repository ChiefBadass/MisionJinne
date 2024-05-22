#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_BMP280.h>
#include <MPU9250_asukiaaa.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include <Servo.h>

const PROGMEM byte CargaPrimaria = 0xFF;
const PROGMEM byte CargaSecundaria = 0xCC;
const PROGMEM byte EstacionTerrena = 0xBB;
String mensajeContingencia = "";

TinyGPSPlus gps;
SoftwareSerial ss(3, 4); // rx, tx
Adafruit_BMP280 bmp;  // I2C
MPU9250_asukiaaa mpu;
Servo servo;

float aceleracionX, aceleracionY, aceleracionZ;
float giroscopioX, giroscopioY, giroscopioZ;
float presionInicial, altura, temperatura, presion;
double latitudCargaPrimaria, longitudCargaPrimaria;
double latitudCargaSecundaria, longitudCargaSecundaria;
double distanciaEntreCargas;
String orientacion;

long ultimaVezQueSeEnvioUnMensaje = 0;
long tiempoEncendido = 0;
int intervalo = 300;

// se debe de cambiar!!!
const PROGMEM int alturaMaxima = 1;
const PROGMEM int alturaDespliegue = 0.5;

bool maximoAlcanzado = false;
bool mensajeEnviadoALaCargaSecundaria = false;
bool servoActivado = false;

String mensaje = "";

void setup() {
  Serial.begin(115200);
  activarServo(45);

  while (!Serial);
  LoRa.setSPIFrequency(433E6);
  Serial.println(F("Carga Primaria"));

  if (!LoRa.begin(433E6)) {
    Serial.println(F("Fallo en iniciar LoRa!"));
    while (1);
  }

  ss.begin(9600);
  bmp.begin(0x76);
  mpu.beginAccel();
  mpu.beginGyro();

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
        distanciaEntreCargas = gps.distanceBetween(gps.location.lat(), gps.location.lng(), latitudCargaSecundaria, longitudCargaSecundaria);
        orientacion = gps.cardinal(gps.courseTo(gps.location.lat(), gps.location.lng(), latitudCargaSecundaria, longitudCargaSecundaria));
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

    temperatura = (bmp.readTemperature()) - 2.45;
    presion = (bmp.readPressure() / 100);
    altura = (bmp.readAltitude(presionInicial));

    if (altura >= alturaMaxima) {
      maximoAlcanzado = true;
    }

    if (altura <= alturaDespliegue && maximoAlcanzado && !servoActivado) {
      //se activa el servo...
      activarServo(65);
      servoActivado = true;
    }


    if (mensajeContingencia == "c") {
      activarServo(65);
    }

    int contador = 0;
    if (altura <= 20 && maximoAlcanzado && !mensajeEnviadoALaCargaSecundaria) {
      while (contador <= 25) {
        enviarMensajeACargaSecundaria("listo");
        contador++;
        delay(20);
      }
    }

    mensaje += "t" + String(temperatura, 1) + ",";
    mensaje += "p" + String(presion, 1) + ",";
    mensaje += "a" + String(altura, 1) + ",";
    mensaje += "x" + String(aceleracionX, 1) + ",";
    mensaje += "y" + String(aceleracionY, 1) + ",";
    mensaje += "z" + String(aceleracionZ, 1) + ",";
    mensaje += "g" + String(giroscopioX, 1) + ",";
    mensaje += "i" + String(giroscopioY, 1) + ",";
    mensaje += "r" + String(giroscopioZ, 1) + ",";
    mensaje += "l" + String(latitudCargaPrimaria, 6) + ",";
    mensaje += "n" + String(longitudCargaPrimaria, 6) + ",";
    mensaje += "u" + String(latitudCargaSecundaria, 6) + ",";
    mensaje += "o" + String(longitudCargaSecundaria, 6) + ",";
    mensaje += "d" + String(distanciaEntreCargas) + ",";
    mensaje += "c" + String(orientacion);

    sendMessage(mensaje);

    ultimaVezQueSeEnvioUnMensaje = millis();
    intervalo = random(50) + 200;
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
  Serial.println(F("Sending packet a carga secundaria"));
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

  if (sender == EstacionTerrena) {
    mensajeContingencia = myMessage;
    return;
  }

  char textoChar[20];                    // Creamos un array de caracteres para almacenar el string
  myMessage.toCharArray(textoChar, 20);  // Convertimos el string a un array de caracteres

  char *lat = strtok(textoChar, ",");
  char *lng = strtok(NULL, ",");

  latitudCargaSecundaria = strtod(lat, NULL);
  longitudCargaSecundaria = strtod(lng, NULL);
}

void activarServo(int grados) {
  servo.attach(6);
  delay(200);
  servo.write(grados);
  delay(200);
  servo.detach();
}