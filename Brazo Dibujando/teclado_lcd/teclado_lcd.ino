/*
  Punto 1 - Teclado I2C + LCD
  ---------------------------------------------
  - Teclado matricial 4x4 conectado directamente a pines digitales (filas/columnas).
  - LCD 16x2 conectado por I2C (dirección típica 0x27, cambiar si el escaneo I2C da otra).
  - Al presionar un dígito (0-9), se muestra en el LCD y se envía por Serial
    en el formato "D:<numero>\n" para que el script de Python (PyBullet) lo reciba
    y mueva el brazo a dibujar esa figura.

  Librerías necesarias (Arduino IDE > Library Manager):
    - Keypad by Mark Stanley / Alexander Brevig
    - LiquidCrystal_I2C by Frank de Brabander (o similar)
*/

#include <Wire.h>
#include <Keypad.h>
#include <LiquidCrystal_I2C.h>

// --- LCD I2C ---
LiquidCrystal_I2C lcd(0x27, 16, 2);   // dirección, columnas, filas

// --- Teclado 4x4 ---
const byte FILAS = 4;
const byte COLUMNAS = 4;

char teclas[FILAS][COLUMNAS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

// Ajusta estos pines según tu conexión física real
byte pinesFilas[FILAS]    = {13, 12, 14, 27};
byte pinesColumnas[COLUMNAS] = {26, 25, 33, 32};

Keypad teclado = Keypad(makeKeymap(teclas), pinesFilas, pinesColumnas, FILAS, COLUMNAS);

String numeroActual = "";

void setup() {
  Serial.begin(115200);
  Wire.begin();

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Ingrese numero:");
}

void loop() {
  char tecla = teclado.getKey();

  if (tecla) {
    if (tecla >= '0' && tecla <= '9') {
      // Dígito normal: se agrega al número en pantalla
      numeroActual += tecla;
      lcd.setCursor(0, 1);
      lcd.print("                "); // limpiar línea
      lcd.setCursor(0, 1);
      lcd.print(numeroActual);

      // Envía el dígito individual para que el brazo lo dibuje de inmediato
      Serial.print("D:");
      Serial.println(tecla);
    }
    else if (tecla == '#') {
      // '#' = confirmar / limpiar número acumulado en pantalla
      lcd.setCursor(0, 1);
      lcd.print("                ");
      numeroActual = "";
    }
    else if (tecla == '*') {
      // '*' = borrar último dígito
      if (numeroActual.length() > 0) {
        numeroActual.remove(numeroActual.length() - 1);
      }
      lcd.setCursor(0, 1);
      lcd.print("                ");
      lcd.setCursor(0, 1);
      lcd.print(numeroActual);
    }
    else if (tecla == 'A') {
      // 'A' = cerrar la simulacion en la PC
      lcd.setCursor(0, 0);
      lcd.print("Cerrando...     ");
      Serial.println("SALIR");
    }
    else if (tecla == 'B') {
      // 'B' = borrar el trazo dibujado para empezar un numero nuevo
      lcd.setCursor(0, 0);
      lcd.print("Lienzo limpio   ");
      Serial.println("LIMPIAR");
      numeroActual = "";
      lcd.setCursor(0, 1);
      lcd.print("                ");
    }
    else if (tecla == 'C') {
      // 'C' = regresar el brazo a la posicion home (inicial)
      lcd.setCursor(0, 0);
      lcd.print("Volviendo home..");
      Serial.println("HOME");
    }
  }
}
