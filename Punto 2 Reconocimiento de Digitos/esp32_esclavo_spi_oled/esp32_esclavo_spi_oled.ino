// ====================================================
// ESP32 ESCLAVO SPI + PANTALLA OLED I2C (CORREGIDO)
// ====================================================

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ✅ CONFIGURACIÓN SPI ESCLAVO
#define MISO 19   // GPIO19
#define MOSI 23   // GPIO23
#define SCLK 18   // GPIO18
#define CS   5    // GPIO5 (Chip Select)

// ✅ CONFIGURACIÓN OLED I2C
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDR 0x3C  // Dirección I2C típica (0x3C o 0x3D)

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Pin del LED
const int LED_PIN = 2;

// Variable para almacenar el dígito recibido
volatile byte digito_recibido = 0;
volatile boolean nuevo_dato = false;

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  // ✅ INICIALIZAR PANTALLA OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("ERROR: No se encontró pantalla OLED en 0x3C");
  } else {
    Serial.println("Pantalla OLED inicializada");
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(20, 25);
    display.println("ESPERANDO...");
    display.display();
  }
  
  // Configurar LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // ✅ CONFIGURAR SPI COMO ESCLAVO
  SPI.begin(SCLK, MISO, MOSI, CS);
  SPI.setFrequency(1000000);  // 1 MHz
  SPI.setDataMode(SPI_MODE0);
  
  // Configurar CS como entrada (detecta cambios)
  pinMode(CS, INPUT);
  
  Serial.println("\n=== ESP32 ESCLAVO SPI + OLED ===");
  Serial.println("Esperando datos del maestro...");
}

void loop() {
  // ✅ VERIFICAR SI CS ESTÁ BAJO (maestro activo)
  if (digitalRead(CS) == LOW) {
    delay(10);  // Pequeño delay para estabilidad
    
    // Leer byte del SPI
    digito_recibido = SPI.transfer(0);
    
    Serial.print("Recibido del maestro: ");
    Serial.println(digito_recibido);
    
    // ✅ MOSTRAR EN PANTALLA OLED
    mostrar_digito_oled(digito_recibido);
    
    // ✅ ENCENDER LED 1 SEGUNDO
    digitalWrite(LED_PIN, HIGH);
    delay(1000);
    digitalWrite(LED_PIN, LOW);
    
    // Esperar a que maestro suelte CS
    while (digitalRead(CS) == LOW) {
      delay(10);
    }
    delay(100);  // Delay antes de siguiente lectura
  }
  
  delay(10);
}

// ✅ FUNCIÓN PARA MOSTRAR DÍGITO EN OLED
void mostrar_digito_oled(byte digito) {
  display.clearDisplay();
  
  // Mostrar el número grande en el centro
  display.setTextSize(6);  // Texto muy grande
  display.setTextColor(SSD1306_WHITE);
  
  // Centrar horizontalmente el número
  int16_t x1, y1;
  uint16_t w, h;
  
  String numero = String(digito);
  display.getTextBounds(numero, 0, 0, &x1, &y1, &w, &h);
  
  int x_pos = (SCREEN_WIDTH - w) / 2;
  int y_pos = (SCREEN_HEIGHT - h) / 2;
  
  display.setCursor(x_pos, y_pos);
  display.println(numero);
  
  // Mostrar información adicional en la parte inferior
  display.setTextSize(1);
  display.setCursor(0, 56);
  display.print("Digito: ");
  display.print(digito);
  display.println(" (recibido por SPI)");
  
  display.display();
}

/*
PINOUT ESP32 ESCLAVO CON OLED:
==============================

SPI (Comunicación con maestro):
GPIO18 (SCLK) <------ SCLK del maestro
GPIO23 (MOSI) <------ MOSI del maestro
GPIO19 (MISO) ------> MISO del maestro
GPIO5 (CS) <--------- CS del maestro
GND ----------------> GND del maestro

I2C (Pantalla OLED):
GPIO21 (SDA) ------> SDA OLED
GPIO22 (SCL) ------> SCL OLED
GND ----------------> GND OLED
3.3V ----------------> VCC OLED

LED (con resistencia 220Ω):
GPIO2 -------> Resistencia 220Ω --------> Ánodo LED
GND ---------> Cátodo LED

CAMBIO PRINCIPAL:
=================
Se quitó SPI.attachInterrupt() porque ESP32 no lo soporta.
En su lugar se usa polling: el loop() verifica constantemente
si CS está bajo (maestro activo) para leer datos.

FUNCIONAMIENTO:
===============
1. Maestro pone CS en LOW
2. Maestro envía byte por MOSI
3. Loop detecta CS bajo y lee el byte
4. Muestra en OLED
5. Enciende LED 1 segundo
6. Espera a que maestro suelte CS
*/
