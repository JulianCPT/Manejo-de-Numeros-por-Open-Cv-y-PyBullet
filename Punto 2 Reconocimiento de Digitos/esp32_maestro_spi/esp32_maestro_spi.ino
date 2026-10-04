#include <SPI.h>

#define MISO 19
#define MOSI 23
#define SCLK 18
#define CS   5

const int LED_PIN = 2;

int digito_actual = -1;

void enviar_spi(byte dato);

void setup() {
  Serial.begin(115200);
  delay(2000);

  while (Serial.available() > 0) {
    Serial.read();
  }

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  SPI.begin(SCLK, MISO, MOSI, CS);
  SPI.setFrequency(1000000);  // si el esclavo lee mal, prueba 100000
  SPI.setDataMode(SPI_MODE0);

  pinMode(CS, OUTPUT);
  digitalWrite(CS, HIGH);

  Serial.println("\n=== ESP32 MAESTRO SPI ===");
  Serial.println("Esperando digitos del PC...");
}

void loop() {
  if (Serial.available() > 0) {
    String datos = Serial.readStringUntil('\n');
    datos.trim();

    if (datos.length() > 0) {
      Serial.print("Recibido de PC: ");
      Serial.println(datos);

      if (datos.length() == 1 && datos[0] >= '0' && datos[0] <= '9') {
        digito_actual = datos.toInt();

        Serial.print("Enviando al esclavo SPI: ");
        Serial.println(digito_actual);

        enviar_spi(digito_actual);

        digitalWrite(LED_PIN, HIGH);
        delay(2000);
        digitalWrite(LED_PIN, LOW);

      } else {
        Serial.println("ERROR: Solo acepto digitos 0-9");
      }
    }
  }
}

void enviar_spi(byte dato) {
  digitalWrite(CS, LOW);
  delay(10);

  SPI.transfer(dato);

  delay(10);
  digitalWrite(CS, HIGH);

  Serial.println("Datos enviados por SPI");
}