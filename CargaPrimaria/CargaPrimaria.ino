#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_BMP280.h>
#include <MPU9250_asukiaaa.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include <PWMServo.h>
#define SS 10
#define RST 8
#define DIO0 2
byte CargaPrimaria = 0xFF;
byte CargaSecundaria = 0xCC;
byte EstacionTerrena = 0xBB;
String updateMessage = "";
int contador = 0;

Adafruit_BMP280 bmp;  // I2C
MPU9250_asukiaaa mpu;
PWMServo servo;

static const int RXPin = 3, TXPin = 4;
static const uint32_t GPSBaud = 9600;

TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

float aX, aY, aZ, aSqrt, gX, gY, gZ, mDirection, mX, mY, mZ;
float presion_inicial, altu, temp, pres;
double lat1 = 27.966641, lng1 = -110.919777, lat2 = 27.967768, lng2 = -110.919676;
double distance;


long lastSendTime = 0;  // last send time
int interval = 300;

int alturaMaxima = 2;
bool maximoAlcanzado = false;


void setup() {
  
  Serial.begin(115200);
  
  LoRa.setPins(SS, RST, DIO0);
  while (!Serial);
  LoRa.setSPIFrequency(433E6);
  Serial.println("Carga Primaria");

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  servo.attach(9);
  servo.write(45);

  bmp.begin(0x76);
  mpu.beginAccel();
  mpu.beginGyro();
  mpu.beginMag();
  //You can set your own offset for mag values
  mpu.magXOffset = -50;
  mpu.magYOffset = -55;
  mpu.magZOffset = -10;
  presion_inicial = bmp.readPressure() / 100;
  ss.begin(GPSBaud);
  LoRa.setTxPower(14);
}

void loop() {
  if (millis() - lastSendTime > interval) {
    while (ss.available() > 0)
      if (gps.encode(ss.read())) {
        lat1 = gps.location.lat();
        lng1 = gps.location.lng();        
        distance = gps.distanceBetween(lat1, lng1, lat2, lng2);
      }
      
    if (mpu.accelUpdate() == 0) {
       aX = mpu.accelX();
       aY = mpu.accelY();
       aZ = mpu.accelZ();
       aSqrt = mpu.accelSqrt();
     }
     if (mpu.gyroUpdate() == 0) {
       gX = mpu.gyroX();
       gY = mpu.gyroY();
       gZ = mpu.gyroZ();
     }
      if (mpu.magUpdate() == 0) {
       mX = mpu.magX();
       mY = mpu.magY();
       mZ = mpu.magZ();
       mDirection = mpu.magHorizDirection();
     }
  
    temp = (bmp.readTemperature()) - 2.45;
    pres = (bmp.readPressure() / 100);
    altu = (bmp.readAltitude(presion_inicial));  // this should be adjusted to your local forcase


    if(altu >= alturaMaxima){
      maximoAlcanzado = true;
    }

    if(altu <= 1 && maximoAlcanzado){
      //se activa el servo...
      servo.write(65);
    }
    

    if(updateMessage == "3312"){
      servo.write(90);//se activa el servo
    }

    

    // int count = 0;
    // if(altu >= 1 && altu <= 2 && maximoAlcanzado){
    //   while(count <= 25){
    //     sendMessageCS("listo");
    //     count++;
    //     delay(20);
    //   }
    // }

    // Serial.println(distance);
    sendMessage(String(contador++)+"t" + String(temp) + "," + "p" + String(pres) + "," + "a" + String(altu) + ","  + "x" + String(aX) + "," + "y" + String(aY) + "," + "z" + String(aZ) + "," + "g" + String(gX) + "," + "i" + String(gY) + "," + "r" + String(gZ) + "," + "l" + String(lat1, 6) + "," + "n" + String(lng1, 6) + "," + "u" + String(lat2, 6) + "," + "o" + String(lng2, 6) + "," + "d" + String(distance, 2) + "," + "m" + String(millis()));
    // sendMessage(String(contador++)+"yeap");
    // Serial.println("lat1" + String(lat1, 6) + "," + "lng1" + String(lng1, 6) + "," + "LAT2" + String(lat2) + "," + "LNG2" + String(lng2) + "," + "DI" + String(distance));

    lastSendTime = millis(); 
    interval = random(50) + 200;  
  }

  onReceive(LoRa.parsePacket());

  delay(50);
}

void sendMessage(String message) {
  LoRa.beginPacket();
  LoRa.write(EstacionTerrena);
  LoRa.print(message);
  LoRa.endPacket();
  Serial.println(message);
}

void sendMessageCS(String message) {
  LoRa.beginPacket();
  LoRa.write(CargaSecundaria);
  LoRa.write(CargaPrimaria);
  LoRa.write(message.length());
  LoRa.print(message);
  LoRa.endPacket();
  Serial.println("Sending packet a carga secundaria");
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
    updateMessage = myMessage;
    return;
  }

  char textoChar[20]; // Creamos un array de caracteres para almacenar el string
  myMessage.toCharArray(textoChar, 20); // Convertimos el string a un array de caracteres

  char *lat = strtok(textoChar, ","); 
  char *lng = strtok(NULL, ","); 

  lat2 = strtod(lat, NULL); 
  lng2 = strtod(lng, NULL);

  
}
