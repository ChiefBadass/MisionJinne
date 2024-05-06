#include <SPI.h>
#include <LoRa.h>

byte EstacionTerrena = 0xBB;
byte CargaPrimaria = 0xFF;
byte CargaSecundaria = 0xCC;
String inString = "";   //hold incoming characters
String myMessage = "";  // hold compleye message


long lastSendTime = 0;        // last send time
int interval = 300;  
void setup() {
  Serial.begin(115200);


  while (!Serial);
  LoRa.setSPIFrequency(433E6);
  Serial.println("Estacion Terrena");
  

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  

  
}

void loop() {
  int count = 0;

  if(Serial.available()){
    String emergencia = Serial.readString();
    if(emergencia = "paro_emergencia"){
      while(count <= 25){
        sendMessage("3312");
        count++;
        delay(10);
      }
    }
  }
  
  onReceive(LoRa.parsePacket());
  
}

void sendMessage(String message) {
  LoRa.beginPacket();
  LoRa.write(CargaPrimaria);
  LoRa.write(EstacionTerrena);
  LoRa.write(message.length());
  LoRa.print(message);
  LoRa.endPacket();
  Serial.println(message);
}

void onReceive(int packetSize){
  
if (packetSize == 0) return; 
  

  int recipient = LoRa.read();
  
  String myMessage = "";
  if (recipient !=  EstacionTerrena) {
    Serial.println("This message is not for me.");
    return;                            
  }
  
  while (LoRa.available()) {
    myMessage += (char)LoRa.read();
  }
 
    
  Serial.println(myMessage);
  
}