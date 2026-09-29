<div align="center">

![Header](https://capsule-render.vercel.app/api?type=waving&color=0:1B2A49,50:274472,100:3E5C9A&height=220&section=header&text=Manejo%20de%20N%C3%BAmeros&fontSize=46&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=OpenCV%20%C2%B7%20CNN%20%C2%B7%20SPI%20%C2%B7%20PyBullet&descAlignY=58&descSize=18)

*Ingeniería Mecatrónica · Universidad Militar Nueva Granada · Actividad 6 de Microcontroladores*

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Visión-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-CNN%20MNIST-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![PyBullet](https://img.shields.io/badge/PyBullet-Simulación-E63946?style=for-the-badge&logo=python&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-Arduino-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![Status](https://img.shields.io/badge/estado-académico-6E40C9?style=for-the-badge)

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:1B2A49,100:3E5C9A&height=3&section=header" width="100%"/>

## ✨ ¿Qué hace este proyecto?

Dos sistemas independientes que trabajan con **dígitos (0–9)** usando ESP32 y Python:

<div align="center">

| Punto | Entrada | Procesamiento | Salida |
|:---:|:---|:---|:---|
| **1 · Brazo dibujando** | Teclado 4x4 + LCD I2C en una ESP32 | Python convierte cada dígito en trazos tipo *display de 7 segmentos* y calcula los ángulos del brazo | Un brazo robótico simulado en **PyBullet** dibuja el número |
| **2 · Reconocimiento de dígitos** | Cámara web del PC | **OpenCV** aísla el dígito y una **CNN** (MNIST) lo clasifica | La ESP32 maestra lo envía por **SPI** a la ESP32 esclava, que lo muestra en una **OLED** |

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:1B2A49,100:3E5C9A&height=3&section=header" width="100%"/>

## 📑 Contenido

- [📁 Estructura del repositorio](#-estructura-del-repositorio)
- [⚙️ Requisitos e instalación](#️-requisitos-e-instalación)
- [🦾 Punto 1: brazo dibujando dígitos](#-punto-1-brazo-dibujando-dígitos)
- [🔢 Punto 2: reconocimiento de dígitos](#-punto-2-reconocimiento-de-dígitos)
- [📸 Evidencias](#-evidencias)
- [🛠️ Solución de problemas](#️-solución-de-problemas)
- [👤 Autor](#-autor)

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:1B2A49,100:3E5C9A&height=3&section=header" width="100%"/>

## 📁 Estructura del repositorio

```
Manejo-de-Numeros-por-Open-Cv-y-PyBullet/
├── Punto 1 Brazo Dibujando/
│   ├── dibujo_pybullet.py              # Simulación + cinemática + lienzo OpenCV (PC)
│   ├── brazo.urdf                      # Modelo del brazo: 2 GDL + pinza
│   └── teclado_lcd/
│       └── teclado_lcd.ino             # ESP32: teclado 4x4 + LCD I2C -> Serial
├── Punto 2 Reconocimiento de Digitos/
│   ├── entrenar_modelo.py              # Entrena la CNN con MNIST
│   ├── modelo_mnist_cnn.h5             # Modelo ya entrenado
│   ├── reconocer_digito.py             # Cámara + OpenCV + CNN + Serial (PC)
│   ├── esp32_maestro_spi/
│   │   └── esp32_maestro_spi.ino       # ESP32 A: Serial -> SPI (maestro)
│   └── esp32_esclavo_spi_oled/
│       └── esp32_esclavo_spi_oled.ino  # ESP32 B: SPI (esclavo) -> OLED
└── README.md
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:1B2A49,100:3E5C9A&height=3&section=header" width="100%"/>

## ⚙️ Requisitos e instalación

- ✅ Python 3.10+
- ✅ Arduino IDE con el paquete de placas **esp32 by Espressif Systems**
- ✅ 3 ESP32 en total: una para el Punto 1 y dos para el Punto 2
- ✅ Teclado matricial 4x4, LCD 16x2 con módulo I2C, pantalla OLED SSD1306 128x64 (I2C), cámara web
- ✅ Cable USB para conectar cada ESP32 al PC (en el Punto 2 solo la maestra necesita PC)

```bash
pip install pybullet pyserial opencv-python numpy tensorflow
```

**Librerías de Arduino** (Gestor de librerías):

| Librería | Se usa en |
|:---|:---|
| `Keypad` (Mark Stanley, Alexander Brevig) | `teclado_lcd.ino` |
| `LiquidCrystal I2C` (Frank de Brabander) | `teclado_lcd.ino` |
| `Adafruit SSD1306` y `Adafruit GFX Library` | `esp32_esclavo_spi_oled.ino` |

`SPI.h` y `Wire.h` vienen incluidas con el core de la ESP32.

| Librería de Python | Para qué sirve | Dónde se usa |
|:---|:---|:---|
| `pybullet` | Simula el brazo con física y control de posición | `dibujo_pybullet.py` |
| `pyserial` | Comunicación USB con las ESP32 | Ambos puntos |
| `opencv-python` | Lienzo 2D del Punto 1; captura y preprocesamiento del dígito en el Punto 2 | Ambos puntos |
| `numpy` | Arreglos de imagen | Ambos puntos |
| `tensorflow` | Entrena y ejecuta la CNN | `entrenar_modelo.py`, `reconocer_digito.py` |

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:1B2A49,100:3E5C9A&height=3&section=header" width="100%"/>

## 🦾 Punto 1: brazo dibujando dígitos

### 📐 Arquitectura

```
⌨️  Teclado 4x4 (GPIO) ──┐
                         ├─ ESP32 ── Serial USB 115200 ──▶ 🐍 dibujo_pybullet.py
🖥️  LCD 16x2 (I2C) ◀─────┘        "D:7\n", "LIMPIAR", "HOME", "SALIR"       │
                                                                             ├──▶ 🦾 PyBullet (rastro 3D)
                                                                             └──▶ 🖼️ OpenCV (lienzo 2D)
```

### 🔌 Conexiones (`teclado_lcd.ino`)

| Elemento | Pines de la ESP32 |
|:---|:---|
| Filas del teclado | GPIO 13, 12, 14, 27 |
| Columnas del teclado | GPIO 26, 25, 33, 32 |
| LCD I2C (dirección `0x27`) | SDA = GPIO 21, SCL = GPIO 22 |

> Si tu LCD no enciende, la dirección puede ser `0x3F`: cámbiala en `LiquidCrystal_I2C lcd(0x27, 16, 2)`.

### ⌨️ Teclas y comandos

<div align="center">

| Tecla | Acción en la LCD | Se envía por Serial | Efecto en Python |
|:---:|:---|:---:|:---|
| `0`–`9` | Agrega el dígito al número en pantalla | `D:<dígito>` | El brazo dibuja ese dígito |
| `*` | Borra el último dígito de la pantalla | — | — |
| `#` | Limpia el número de la pantalla | — | — |
| `A` | "Cerrando..." | `SALIR` | Cierra la simulación |
| `B` | "Lienzo limpio" | `LIMPIAR` | Borra el lienzo OpenCV y el rastro 3D |
| `C` | "Volviendo home.." | `HOME` | Regresa el brazo a la posición inicial |

</div>

### 🧠 Cómo dibuja el brazo (`dibujo_pybullet.py`)

1. **Dígitos como 7 segmentos.** Cada dígito se define como un conjunto de segmentos (`a`–`g`) sobre una rejilla de 2×3 puntos. Por ejemplo, el `7` es `abc` y el `8` es `abcdefg`.
2. **Trazos en el lienzo.** Cada segmento se convierte en un trazo entre dos puntos `(y, z)` en metros, sobre un lienzo vertical imaginario a `0.25 m` del codo (semiancho y semialto de `0.18 m`).
3. **Cinemática inversa pan-tilt.** Para cada punto se calculan los dos ángulos del brazo:
   ```python
   theta1 = atan2(y, d)                  # joint_1: giro de la base
   theta2 = atan2(hypot(d, y), z)        # joint_2: inclinación del codo
   ```
4. **Pluma arriba / abajo.** Para ir al inicio de un trazo el brazo se mueve sin dejar rastro; durante el trazo se dibuja una línea con `addUserDebugLine` en PyBullet y el mismo segmento en un lienzo 2D de OpenCV (ventana *"Lo que escribio el robot"*).
5. **Salida.** Al terminar cada dígito se guarda una imagen `digito_<n>.png`.

La pinza queda abierta y fija (`0.04 m`) durante toda la simulación: solo se mueven `joint_1` y `joint_2`.

### ▶️ Cómo correrlo

1. Sube `teclado_lcd/teclado_lcd.ino` a la ESP32 y **cierra el Monitor Serial**.
2. Entra a la carpeta del punto y ejecuta:
   ```bash
   cd "Punto 1 Brazo Dibujando"
   python dibujo_pybullet.py --puerto COM3
   ```
3. Digita números en el teclado y mira cómo los dibuja el brazo.

**Modo demo (sin hardware):** dibuja del 0 al 9 automáticamente. Se sale con la tecla `a` en la ventana de OpenCV.

```bash
python dibujo_pybullet.py --demo
```

| Argumento | Valor por defecto | Descripción |
|:---|:---:|:---|
| `--puerto` | `COM3` | Puerto serie (`/dev/ttyUSB0` en Linux/Mac) |
| `--baudios` | `115200` | Igual que `Serial.begin()` del `.ino` |
| `--demo` | — | Dibuja 0–9 sin ESP32 |

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:1B2A49,100:3E5C9A&height=3&section=header" width="100%"/>

## 🔢 Punto 2: reconocimiento de dígitos

### 📐 Arquitectura

```
📷 Cámara PC
   │
   ▼
🐍 reconocer_digito.py  ── OpenCV (preprocesa) ──▶ CNN (clasifica)
   │  Serial USB 115200: "7\n"
   ▼
📟 ESP32 A · MAESTRO SPI
   │  SPI (1 MHz, modo 0): 1 byte con el dígito
   ▼
📟 ESP32 B · ESCLAVO SPI ──▶ 🖥️ OLED SSD1306 (I2C) + LED
```

### 🧪 Preprocesamiento con OpenCV (`reconocer_digito.py`)

Se toma un recuadro verde de `300×300 px` en el centro de la cámara y se lleva a formato **MNIST** (dígito blanco sobre fondo negro, 28×28):

1. Escala de grises y `GaussianBlur` de 5×5.
2. **Umbral adaptativo gaussiano** invertido (más robusto a la iluminación que un umbral fijo).
3. `findContours`: se toma el contorno más grande e ignora los menores a `500 px²` (ruido).
4. Se recorta el dígito y se escala a **20×20** conservando la proporción.
5. Se pega en un lienzo de **28×28**, centrado por **centro de masa**, y se normaliza a `[0, 1]`.

### 🧠 Red neuronal (`entrenar_modelo.py`)

<div align="center">

| Capa | Detalle |
|:---|:---|
| `Conv2D` + `MaxPooling2D` | 32 filtros 3×3, ReLU |
| `Conv2D` + `MaxPooling2D` | 64 filtros 3×3, ReLU |
| `Flatten` | — |
| `Dense` | 128 neuronas, ReLU |
| `Dropout` | 0.5 |
| `Dense` | 10 neuronas, softmax (dígitos 0–9) |

</div>

Se entrena con **MNIST** durante 10 épocas, con *data augmentation* (rotación de 10°, desplazamientos de 10 % y zoom de 10 %) para que tolere dígitos escritos a mano frente a la cámara. El modelo queda guardado en `modelo_mnist_cnn.h5`, que ya viene incluido en el repositorio.

### 🛡️ Filtros para no enviar ruido

| Filtro | Valor | Para qué |
|:---|:---:|:---|
| Confianza mínima de la CNN | `> 60 %` | Ignora predicciones dudosas |
| Votación mayoritaria | últimas `5` predicciones | Suaviza parpadeos entre clases |
| Estabilidad | `3 s` con el mismo número | Solo envía cuando el dígito se mantiene quieto |
| No repetir | mismo dígito que el último enviado | Evita reenviar el mismo número en bucle |

### 🔌 Conexiones entre las dos ESP32

| ESP32 A (maestro) | ESP32 B (esclavo) | Señal |
|:---:|:---:|:---|
| GPIO 18 | GPIO 18 | SCLK |
| GPIO 23 | GPIO 23 | MOSI |
| GPIO 19 | GPIO 19 | MISO |
| GPIO 5 | GPIO 5 | CS |
| GND | GND | Tierra común (obligatoria) |

**OLED SSD1306 en la ESP32 B:** `SDA = GPIO 21`, `SCL = GPIO 22`, `VCC = 3.3 V`, `GND`, dirección `0x3C`.
**LED de confirmación** (ambas placas): `GPIO 2` con la resistencia de la propia placa o una de 220 Ω externa.

### 📡 Protocolo

- **PC → ESP32 A (Serial):** un solo carácter `0`–`9` terminado en `\n`. La maestra rechaza cualquier otra cosa.
- **ESP32 A → ESP32 B (SPI):** 1 byte con el valor numérico del dígito. La maestra baja `CS`, envía el byte y lo vuelve a subir. La esclava detecta `CS` en bajo (*polling*), lee el byte y lo muestra en la OLED.

### ▶️ Cómo correrlo

1. Sube `esp32_maestro_spi.ino` a la ESP32 A y `esp32_esclavo_spi_oled.ino` a la ESP32 B.
2. Conecta los pines SPI y la OLED según las tablas anteriores.
3. Conecta la ESP32 A al PC, **cierra el Monitor Serial** y ajusta el puerto en `reconocer_digito.py`:
   ```python
   PUERTO_SERIE = "COM3"
   ```
4. Ejecuta:
   ```bash
   cd "Punto 2 Reconocimiento de Digitos"
   python reconocer_digito.py
   ```
5. Muestra un dígito oscuro sobre hoja blanca dentro del recuadro verde y **mantenlo 3 segundos**. Con `q` se cierra el programa.

> Solo si quieres reentrenar la red: `python entrenar_modelo.py` (descarga MNIST y regenera `modelo_mnist_cnn.h5`).

Si la ESP32 A no está conectada, el programa **sigue funcionando solo con el reconocimiento visual**, sin enviar nada.

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:1B2A49,100:3E5C9A&height=3&section=header" width="100%"/>

## 📸 Evidencias

<!--
Cuando subas tus fotos/videos, crea la carpeta docs/ y usa este formato:

<div align="center">
<img src="docs/imagenes/brazo-dibujando.jpeg" width="480"/><br/>
<sub>Brazo dibujando un dígito en PyBullet</sub>
</div>

- ▶️ [Video del Punto 1](docs/videos/punto1.mp4)
- ▶️ [Video del Punto 2](docs/videos/punto2.mp4)
-->

*(Pendiente: capturas del montaje, del brazo dibujando y de la OLED mostrando el dígito.)*

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:1B2A49,100:3E5C9A&height=3&section=header" width="100%"/>

## 🛠️ Solución de problemas

| Problema | Causa probable / solución |
|:---|:---|
| `could not open port 'COM3'` | El Monitor Serial está abierto o el puerto es otro. Revisa el Administrador de dispositivos |
| El Punto 2 dice "solo con reconocimiento visual" | No se abrió el puerto serie: ajusta `PUERTO_SERIE` |
| No abre la cámara | Cierra otras apps que la usen o cambia el índice en `cv2.VideoCapture(0)` |
| Reconoce mal los dígitos | Más luz, trazo grueso y oscuro, fondo blanco liso y dígito dentro del recuadro verde |
| No enciende la LCD | Prueba la dirección `0x3F` o ajusta el potenciómetro de contraste del módulo |
| La OLED se queda en "ESPERANDO..." | Revisa CS/SCLK/MOSI, la **GND común** entre las dos ESP32 y la dirección `0x3C` |
| El brazo no dibuja nada en modo serial | El `.ino` envía `D:<dígito>`; confirma que el puerto y los baudios (`115200`) coinciden |

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:1B2A49,100:3E5C9A&height=3&section=header" width="100%"/>

## 👤 Autor

Proyecto académico de **Ingeniería Mecatrónica · Universidad Militar Nueva Granada**, desarrollado para la actividad 6 de la materia de Microcontroladores.
