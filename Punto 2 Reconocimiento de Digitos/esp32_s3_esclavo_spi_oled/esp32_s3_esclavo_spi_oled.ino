// ====================================================
// ESP32-S3 ESCLAVO SPI REAL + PANTALLA OLED I2C
// Librería: ESP32SPISlave (hideakitai)
//
// Cambio clave: el SPI se atiende en una tarea FreeRTOS dedicada,
// SIN timeout, para no dejar transacciones abandonadas en el driver.
// El OLED y el LED se manejan en loop().
// ====================================================

#include <ESP32SPISlave.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// SPI esclavo (en S3, GPIO19 y GPIO20 son USB nativo: no usarlos)
#define PIN_MISO 13
#define PIN_MOSI 14
#define PIN_SCLK 18
#define PIN_CS   7

// OLED I2C
#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT 64
#define OLED_ADDR     0x3C
#define PIN_SDA       9
#define PIN_SCL       8

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
ESP32SPISlave slave;

static constexpr size_t BUFFER_SIZE = 8;  // múltiplo de 4
uint8_t rx_buf[BUFFER_SIZE] __attribute__((aligned(4)));
uint8_t tx_buf[BUFFER_SIZE] __attribute__((aligned(4)));

const int LED_PIN = 6;

// LED no bloqueante
unsigned long led_momento_prendido = 0;
bool led_prendido = false;
const unsigned long LED_DURACION_MS = 1000;

// Cola para pasar dígitos de la tarea SPI a loop()
QueueHandle_t colaDigitos;

// ----------------------------------------------------
// Tarea SPI: espera transacciones sin timeout
// ----------------------------------------------------
void tareaSPI(void *param) {
  for (;;) {
    memset(rx_buf, 0, BUFFER_SIZE);
    memset(tx_buf, 0, BUFFER_SIZE);

    // Bloquea hasta que el maestro inicia y termina una transacción
    size_t recibidos = slave.transfer(tx_buf, rx_buf, BUFFER_SIZE);

    if (recibidos > 0) {
      uint8_t d = rx_buf[0];
      xQueueSend(colaDigitos, &d, 0);
    }
  }
}

void mostrar_digito_oled(uint8_t digito) {
  char numero[2];
  numero[0] = '0' + (digito % 10);
  numero[1] = '\0';

  display.clearDisplay();
  display.setTextSize(6);
  display.setTextColor(SSD1306_WHITE);

  int16_t x1, y1;
  uint16_t w, h;
  display.getTextBounds(numero, 0, 0, &x1, &y1, &w, &h);

  int x_pos = (SCREEN_WIDTH - (int)w) / 2;
  int y_pos = (SCREEN_HEIGHT - (int)h) / 2;
  if (x_pos < 0) x_pos = 0;
  if (y_pos < 0) y_pos = 0;

  display.setCursor(x_pos, y_pos);
  display.print(numero);

  char linea_info[32];
  snprintf(linea_info, sizeof(linea_info), "Digito: %d (SPI real)", digito);
  display.setTextSize(1);
  display.setCursor(0, 56);
  display.print(linea_info);

  display.display();
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Causa del último reinicio (4=panic, 6/7=watchdog, 15=brownout)
  Serial.printf("Motivo de reinicio: %d\n", (int)esp_reset_reason());

  // OLED
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(400000);
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("ERROR: OLED no encontrada en 0x3C");
  }
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 25);
  display.println("ESPERANDO...");
  display.display();

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // SPI esclavo en HSPI (existe en ESP32 clásico y en S3)
  slave.setDataMode(SPI_MODE0);
  slave.begin(HSPI, PIN_SCLK, PIN_MISO, PIN_MOSI, PIN_CS);

  // Cola y tarea SPI
  colaDigitos = xQueueCreate(8, sizeof(uint8_t));
  xTaskCreatePinnedToCore(tareaSPI, "spi", 4096, NULL, 2, NULL, 1);

  Serial.println("=== ESP32 ESCLAVO SPI (modo real) + OLED ===");
  Serial.println("Esperando datos del maestro...");
}

void loop() {
  // Apagar LED por tiempo, sin delay()
  if (led_prendido && (millis() - led_momento_prendido >= LED_DURACION_MS)) {
    digitalWrite(LED_PIN, LOW);
    led_prendido = false;
  }

  uint8_t digito;
  if (xQueueReceive(colaDigitos, &digito, 10 / portTICK_PERIOD_MS) == pdTRUE) {
    Serial.printf("Recibido del maestro: %d\n", digito);

    if (digito <= 9) {
      mostrar_digito_oled(digito);
      digitalWrite(LED_PIN, HIGH);
      led_prendido = true;
      led_momento_prendido = millis();
    } else {
      Serial.println("Valor fuera de rango (ruido en el bus), se ignora.");
    }
  }
}

/*
PINOUT ESCLAVO (ESP32-S3):
GPIO18 (SCLK) <- SCLK maestro (GPIO18)
GPIO14 (MOSI) <- MOSI maestro (GPIO23)
GPIO13 (MISO) -> MISO maestro (GPIO19)
GPIO7  (CS)   <- CS maestro (GPIO5)
GND común
OLED: SDA=GPIO9, SCL=GPIO8, LED=GPIO6
*/
