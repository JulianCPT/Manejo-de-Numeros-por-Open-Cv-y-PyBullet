// ====================================================
// ESP32 MAESTRO SPI - RECIBE DÍGITOS Y ENVÍA POR SPI
// ====================================================

#include <SPI.h>

// ✅ CONFIGURACIÓN SPI MAESTRO
#define MISO 19   // GPIO19
#define MOSI 23   // GPIO23
#define SCLK 18   // GPIO18
#define CS   5    // GPIO5 (Chip Select)

// Pin del LED (opcional, para verificar recepción)
const int LED_PIN = 2;

// Variables para almacenar el dígito
int digito_actual = -1;

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  // Limpiar buffer
  while (Serial.available() > 0) {
    Serial.read();
  }
  
  // Configurar LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // ✅ INICIALIZAR SPI MAESTRO
  SPI.begin(SCLK, MISO, MOSI, CS);
  SPI.setFrequency(1000000);  // 1 MHz (puedes cambiar a 5000000 para 5 MHz)
  SPI.setDataMode(SPI_MODE0);
  
  pinMode(CS, OUTPUT);
  digitalWrite(CS, HIGH);  // CS inactivo (HIGH)
  
  Serial.println("\n=== ESP32 MAESTRO SPI ===");
  Serial.println("Esperando dígitos del PC...");
  Serial.println("Se enviarán al esclavo SPI por GPIO18 (SCLK), GPIO23 (MOSI)");
}

void loop() {
  // Recibir datos del puerto serie (PC)
  if (Serial.available() > 0) {
    String datos = Serial.readStringUntil('\n');
    datos.trim();
    
    if (datos.length() > 0) {
      Serial.print("Recibido de PC: ");
      Serial.println(datos);
      
      // Validar que sea un dígito (0-9)
      if (datos.length() == 1 && datos[0] >= '0' && datos[0] <= '9') {
        digito_actual = datos.toInt();
        
        Serial.print("Enviando al esclavo SPI: ");
        Serial.println(digito_actual);
        
        // ✅ ENVIAR POR SPI AL ESCLAVO
        enviar_spi(digito_actual);
        
        // ✅ LED se prende 1 segundo para confirmar envío
        digitalWrite(LED_PIN, HIGH);
        delay(1000);
        digitalWrite(LED_PIN, LOW);
        
      } else {
        Serial.println("ERROR: Solo acepto dígitos 0-9");
      }
    }
  }
}

// Función para enviar datos por SPI
void enviar_spi(byte dato) {
  digitalWrite(CS, LOW);   // ✅ Seleccionar esclavo (CS = LOW)
  delay(10);
  
  SPI.transfer(dato);      // ✅ Enviar byte
  
  delay(10);
  digitalWrite(CS, HIGH);  // ✅ Deseleccionar esclavo (CS = HIGH)
  
  Serial.println("Datos enviados por SPI");
}

/*
PINOUT ESP32 MAESTRO:
=====================
GPIO18 (SCLK) ------> SCLK del esclavo
GPIO23 (MOSI) ------> MOSI del esclavo
GPIO19 (MISO) ------> MISO del esclavo
GPIO5 (CS) ---------> CS del esclavo
GND ----------------> GND del esclavo

VELOCIDAD SPI: 1 MHz (puedes cambiar en SPI.setFrequency)

FLUJO:
======
1. PC envía dígito a puerto serie
2. ESP32 maestro recibe el dígito
3. Maestro envía por SPI al esclavo
4. Esclavo recibe y procesa
*/
