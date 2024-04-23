#include <SPI.h>
#include <LoRa.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

static const int RXPin = 3, TXPin = 4;
static const uint32_t GPSBaud = 9600;

TinyGPSPlus gps;

//The serial connection to the GPS device
SoftwareSerial gss(RXPin, TXPin);

double lat;
double lng;

byte CargaSecundaria = 0xCC;
byte CargaPrimaria = 0xFF;
byte EstacionTerrena = 0xBB;
String myMessage = "";
String updateMessage = "listo";
int counter = 1;
int c = 0;

void setup() {
  Serial.begin(115200);
  gss.begin(GPSBaud);
  while (!Serial);
  
  Serial.println("Carga Secundaria");
  
  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
}


void loop() {
  int packetSize = LoRa.parsePacket();
  
  if (packetSize != 0) {
    Serial.println(c);
    int recipient = LoRa.read();
    byte sender = LoRa.read();
    byte messageLength = LoRa.read();

    if (recipient != CargaSecundaria) return; 

    // read packet
    while (LoRa.available()) {
      updateMessage += (char)LoRa.read();
    }

    if (messageLength != updateMessage.length()) return;

    Serial.print("Received packet '" + String(packetSize));
    Serial.println(" Message: " + updateMessage);
  }

  if (updateMessage == "listo") {
    while (gss.available() > 0)
      if (gps.encode(gss.read())) {
        lat = gps.location.lat();
        lng = gps.location.lng();
      }
    Serial.println("Sending packet: ");
    // send packet
    myMessage = String(lat, 6) + "," + String(lng, 6);
    Serial.println(myMessage);
    
    LoRa.beginPacket();
    LoRa.write(CargaPrimaria);
    LoRa.write(CargaSecundaria);
    LoRa.write(myMessage.length());
    LoRa.print(myMessage);
    LoRa.endPacket();
    delay(400);
  }
  
  
}
