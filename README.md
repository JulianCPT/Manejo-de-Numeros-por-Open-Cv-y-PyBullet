<div align="center">

![Header](https://capsule-render.vercel.app/api?type=waving&color=0:0B3D2E,50:14683F,100:1F8A4C&height=220&section=header&text=Manejo%20de%20N%C3%BAmeros&fontSize=46&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=OpenCV%20%C2%B7%20CNN%20%C2%B7%20SPI%20%C2%B7%20PyBullet%20%C2%B7%20ESP32&descAlignY=58&descSize=17)

*Ingeniería Mecatrónica · Universidad Militar Nueva Granada · Actividad 6 de Microcontroladores*

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&duration=3000&pause=800&color=3DDC84&center=true&vCenter=true&width=700&lines=%22Teclado+4x4+%E2%86%92+brazo+que+dibuja+d%C3%ADgitos%22;%22C%C3%A1mara+%2B+CNN+%E2%86%92+reconoce+el+d%C3%ADgito%22;%22ESP32+maestro+%E2%86%92+SPI+%E2%86%92+ESP32-S3+%E2%86%92+OLED%22" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Visión-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-CNN%20MNIST-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![PyBullet](https://img.shields.io/badge/PyBullet-Simulación-1F8A4C?style=for-the-badge&logo=python&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-Arduino-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![Status](https://img.shields.io/badge/estado-académico-6E40C9?style=for-the-badge)

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## ✨ ¿Qué hace este proyecto?

Actividad de **Microcontroladores** con dos ejercicios que trabajan con **dígitos (0–9)**. En el
Punto 1 un circuito con **ESP32** sirve de consola para un brazo robótico simulado en **PyBullet**
(*real-to-sim*); en el Punto 2 la **visión por computador** reconoce un dígito y lo lleva por
**SPI** entre dos microcontroladores hasta una pantalla **OLED**.

<div align="center">

| Punto | 🎛️ Entrada | 🧠 Procesamiento | 📤 Salida |
|:---:|:---|:---|:---|
| **1 · Brazo dibujando** | Teclado matricial 4×4 + LCD I2C (ESP32) | Python convierte cada dígito en trazos tipo *display de 7 segmentos* y calcula los ángulos del brazo | El brazo simulado en **PyBullet** dibuja el número y un lienzo de **OpenCV** lo muestra en 2D |
| **2 · Reconocimiento de dígitos** | Cámara web del PC | **OpenCV** aísla el dígito y una **CNN** entrenada con MNIST lo clasifica | **ESP32 maestro → SPI → ESP32-S3 esclavo → OLED** |

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 📑 Contenido

- [🧭 Resumen de los dos puntos](#-resumen-de-los-dos-puntos)
- [📸 Capturas](#-capturas)
- [🎥 Videos de funcionamiento](#-videos-de-funcionamiento)
- [📐 Arquitectura general](#-arquitectura-general)
- [🔎 Análisis del proyecto](#-análisis-del-proyecto)
- [📁 Estructura del repositorio](#-estructura-del-repositorio)
- [⚙️ Requisitos](#️-requisitos)
- [▶️ Paso a paso: cómo correrlo](#️-paso-a-paso-cómo-correrlo)
- [📡 Protocolos de comunicación](#-protocolos-de-comunicación)
- [🧩 Explicación del código](#-explicación-del-código-bloque-por-bloque)
- [🧠 Conceptos clave](#-conceptos-clave)
- [🛠️ Solución de problemas](#️-solución-de-problemas)
- [👤 Autor](#-autor)

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 🧭 Resumen de los dos puntos

### 🦾 Punto 1 — Brazo robótico que dibuja dígitos

Se digita un número en el **teclado 4×4**; la ESP32 lo muestra en la **LCD** y lo envía por serie.
Python lo recibe y el brazo de 2 grados de libertad **dibuja el dígito** sobre un lienzo vertical
imaginario, trazo por trazo, dejando un rastro en 3D (PyBullet) y en 2D (OpenCV).

<div align="center">

| Tecla | Acción en la LCD | Se envía por Serial | Efecto en Python |
|:---:|:---|:---:|:---|
| `0`–`9` | Agrega el dígito al número en pantalla | `D:<dígito>` | El brazo dibuja ese dígito |
| `*` | Borra el último dígito de la pantalla | — | — |
| `#` | Limpia el número de la pantalla | — | — |
| `A` | "Cerrando..." | `SALIR` | Cierra la simulación |
| `B` | "Lienzo limpio" | `LIMPIAR` | Borra el lienzo y el rastro 3D |
| `C` | "Volviendo home.." | `HOME` | Regresa el brazo a su posición inicial |

</div>

### 🔢 Punto 2 — Reconocimiento de dígitos con OpenCV, CNN y SPI

La cámara del PC mira un dígito escrito a mano. Python lo **preprocesa con OpenCV**, la **CNN** lo
clasifica y, si la predicción es confiable y estable, lo manda por serie a la **ESP32 maestra**.
Esta lo transmite por **SPI** a una **ESP32-S3 esclava**, que lo dibuja en grande en una **OLED**
y enciende un LED como confirmación.

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 📸 Capturas

### 🦾 Punto 1

<div align="center">

<table>
  <tr>
    <td align="center">
      <img src="docs/im%C3%A1genes/Punto%201/LCD%20en%20Funcionamiento.jpeg" height="300"/><br/>
      <sub>LCD mostrando el número digitado</sub>
    </td>
    <td align="center">
      <img src="docs/im%C3%A1genes/Punto%201/Montaje%20Completo%20en%20Funcionamiento.jpeg" height="300"/><br/>
      <sub>Montaje completo: teclado + simulación</sub>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <img src="docs/im%C3%A1genes/Punto%201/Vision%20de%20PyBullet%20Funcionando.jfif" width="720"/><br/>
      <sub>Vista de PyBullet con el brazo dibujando</sub>
    </td>
  </tr>
</table>

</div>

### 🔢 Punto 2

<div align="center">

<table>
  <tr>
    <td align="center">
      <img src="docs/im%C3%A1genes/Punto%202/Circuito%20Electrico.jpeg" height="420"/><br/>
      <sub>Circuito: ESP32 maestro, ESP32-S3 esclavo y OLED</sub>
    </td>
    <td align="center">
      <img src="docs/im%C3%A1genes/Punto%202/Montaje%20Completo.jpeg" height="420"/><br/>
      <sub>Montaje completo: PC con cámara + circuito</sub>
    </td>
  </tr>
</table>

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 🎥 Videos de funcionamiento

> GitHub no reproduce videos `.mp4` alojados en el repo directamente dentro del README,
> así que se dejan como enlaces descargables/reproducibles desde el navegador.

| Punto | Video | Qué muestra |
|:---:|:---|:---|
| 1 | ▶️ [**Montaje completo**](docs/videos/Punto%201/Video%20Funcionamiento%20Montaje%20Completo.mp4) | El teclado, la LCD y el brazo dibujando en PyBullet al mismo tiempo |
| 1 | ▶️ [**Funcionamiento de la LCD**](docs/videos/Punto%201/Video%20Funcionamiento%20LCD.mp4) | El número digitado apareciendo en la pantalla LCD |
| 2 | ▶️ [**Prueba del reconocimiento**](docs/videos/Punto%202/Prueba%20Reconocimiento%20de%20Digitos%20por%20OpenCV.mp4) | La cámara reconociendo dígitos y la OLED mostrándolos |

<div align="center">

**GIF de vista rápida:** el funcionamiento de cada punto en acción.

<table>
  <tr>
    <td align="center" valign="top" width="33%">
      <img src="docs/videos/Punto%201/GIF%20Punto%201.gif" width="100%" alt="GIF del Punto 1: brazo dibujando"/><br/>
      <sub>🟢 <b>Punto 1</b> · brazo dibujando</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="docs/videos/Punto%201/GIF%20Punto%201%20LCD.gif" width="100%" alt="GIF del Punto 1: teclado y LCD"/><br/>
      <sub>🟢 <b>Punto 1</b> · teclado y LCD</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="docs/videos/Punto%202/GIF%20Punto%202.gif" width="100%" alt="GIF del Punto 2: reconocimiento de dígitos"/><br/>
      <sub>🔴 <b>Punto 2</b> · reconocimiento de dígitos</sub>
    </td>
  </tr>
</table>

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 📐 Arquitectura general

Cada columna es un punto, con su propio color: 🔵 **Punto 1** y 🔴 **Punto 2**.

<div align="center">

<table>
  <tr>
    <td align="center" valign="top" width="50%">
      <img src="docs/im%C3%A1genes/Punto%201/diagrama-arquitectura-punto-1.svg" width="100%" alt="Arquitectura del Punto 1: teclado, ESP32, Python y brazo en PyBullet"/>
    </td>
    <td align="center" valign="top" width="50%">
      <img src="docs/im%C3%A1genes/Punto%202/diagrama-arquitectura-punto-2.svg" width="100%" alt="Arquitectura del Punto 2: cámara, OpenCV, CNN, SPI y OLED"/>
    </td>
  </tr>
</table>

</div>

| Símbolo | Significado |
|:---:|:---|
| **→** | Relación de un solo sentido: los datos fluyen en esa dirección |
| 🔌 **Serial USB** | Comunicación entre el PC y la ESP32 a 115200 baudios |
| 🔗 **Bus SPI** | Comunicación síncrona entre las dos placas (maestro → esclavo) |

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 🔎 Análisis del proyecto

**Decisiones de diseño**

| Decisión | Por qué se tomó |
|:---|:---|
| **ESP32 "tonta", PC "inteligente" (Punto 1)** | La ESP32 solo lee teclas y muestra en la LCD; la geometría y la simulación viven en Python, donde hay más cómputo y es más fácil depurar |
| **Dígitos como 7 segmentos** | Con solo 7 trazos posibles se dibujan los 10 dígitos, sin necesidad de fuentes ni trayectorias complejas |
| **Cinemática inversa pan-tilt** | Con 2 articulaciones (base y codo) basta una fórmula cerrada para apuntar a cualquier punto del lienzo |
| **Umbral adaptativo (Punto 2)** | Funciona mejor que un umbral fijo cuando la luz del cuarto cambia |
| **Centrado por centro de masa** | Es el mismo formato que usa MNIST, así que la CNN acierta más |
| **Votación de 5 + estabilidad de 3 s + confianza > 60 %** | Evita enviar un dígito equivocado por un parpadeo de la cámara |
| **Esclavo SPI "real" con `ESP32SPISlave`** | La librería `SPI.h` solo funciona como maestro; para ser esclavo hace falta el periférico en modo esclavo |
| **Tarea FreeRTOS + cola en el esclavo** | La tarea SPI espera transacciones sin timeout y le pasa el dígito a `loop()`, que maneja la OLED y el LED sin bloquear el bus |
| **ESP32-S3 como esclavo** | Se evitan los GPIO 19 y 20 (USB nativo del S3) y se usan pines libres para SPI e I2C |

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 📁 Estructura del repositorio

```
Manejo-de-Numeros-por-Open-Cv-y-PyBullet/
├── Punto 1 Brazo Dibujando/
│   ├── dibujo_pybullet.py                  # Simulación + cinemática + lienzo OpenCV (PC)
│   ├── brazo.urdf                          # Modelo del brazo: 2 GDL + pinza
│   └── teclado_lcd/
│       └── teclado_lcd.ino                 # ESP32: teclado 4x4 + LCD I2C -> Serial
├── Punto 2 Reconocimiento de Digitos/
│   ├── entrenar_modelo.py                  # Entrena la CNN con MNIST
│   ├── modelo_mnist_cnn.h5                 # Modelo ya entrenado
│   ├── reconocer_digito.py                 # Cámara + OpenCV + CNN + Serial (PC)
│   ├── esp32_maestro_spi/
│   │   └── esp32_maestro_spi.ino           # ESP32: Serial -> SPI (maestro)
│   └── esp32_s3_esclavo_spi_oled/
│       └── esp32_s3_esclavo_spi_oled.ino   # ESP32-S3: SPI (esclavo) -> OLED
├── docs/
│   ├── imágenes/                           # Capturas del montaje y diagramas (.svg), por punto
│   │   ├── Punto 1/
│   │   └── Punto 2/
│   └── videos/                             # Videos (.mp4) y GIFs de vista rápida, por punto
│       ├── Punto 1/
│       └── Punto 2/
└── README.md
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## ⚙️ Requisitos

<img src="https://skillicons.dev/icons?i=python,arduino,cpp,tensorflow,opencv&theme=dark" />

- ✅ Python 3.10+
- ✅ Arduino IDE con el paquete de placas **esp32 by Espressif Systems**
- ✅ **3 placas:** una ESP32 para el Punto 1, y para el Punto 2 una ESP32 (maestro) y una ESP32-S3 (esclavo)
- ✅ Teclado matricial 4×4, LCD 16×2 con módulo I2C, OLED SSD1306 128×64 (I2C) y una cámara web

### 🔩 Hardware: conexiones por punto

**Punto 1 — ESP32 (`teclado_lcd.ino`)**

| Elemento | Pines |
|:---|:---|
| Filas del teclado | GPIO 13, 12, 14, 27 |
| Columnas del teclado | GPIO 26, 25, 33, 32 |
| LCD I2C (dirección `0x27`) | SDA = GPIO 21, SCL = GPIO 22 |

**Punto 2 — SPI entre las dos placas (masa común obligatoria)**

| ESP32 maestro | ESP32-S3 esclavo | Señal |
|:---:|:---:|:---|
| GPIO 18 | GPIO 18 | SCLK |
| GPIO 23 (MOSI) | GPIO 14 | Datos maestro → esclavo |
| GPIO 19 (MISO) | GPIO 13 | Datos esclavo → maestro |
| GPIO 5 | GPIO 7 | CS |
| GND | GND | Tierra común |

| Elemento | Pines |
|:---|:---|
| OLED SSD1306 (`0x3C`) en la ESP32-S3 | SDA = GPIO 9, SCL = GPIO 8 |
| LED de confirmación en el esclavo | GPIO 6 |
| LED de confirmación en el maestro | GPIO 2 (LED de la placa) |

### 📦 Librerías de Python: qué hacen y por qué se eligieron

```bash
pip install pybullet pyserial opencv-python numpy tensorflow
```

| Librería | Para qué sirve | Dónde se usa |
|:---|:---|:---|
| `pybullet` | Simula el brazo con física y control de posición | `dibujo_pybullet.py` |
| `pyserial` | Comunicación USB con las ESP32 | Ambos puntos |
| `opencv-python` | Lienzo 2D (Punto 1); captura y preprocesamiento del dígito (Punto 2) | Ambos puntos |
| `numpy` | Arreglos de imagen y operaciones matemáticas | Ambos puntos |
| `tensorflow` | Entrena y ejecuta la CNN | `entrenar_modelo.py`, `reconocer_digito.py` |

### 🧰 Librerías de Arduino (firmware)

| Librería | Se usa en |
|:---|:---|
| `Keypad` (Mark Stanley, Alexander Brevig) | `teclado_lcd.ino` |
| `LiquidCrystal I2C` (Frank de Brabander) | `teclado_lcd.ino` |
| `ESP32SPISlave` (hideakitai) | `esp32_s3_esclavo_spi_oled.ino` |
| `Adafruit SSD1306` y `Adafruit GFX Library` | `esp32_s3_esclavo_spi_oled.ino` |

`SPI.h` y `Wire.h` vienen incluidas con el core de la ESP32.

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## ▶️ Paso a paso: cómo correrlo

### 🦾 Punto 1

1. Sube `teclado_lcd/teclado_lcd.ino` a la ESP32 y **cierra el Monitor Serial**.
2. Ejecuta, ajustando el puerto:
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

### 🔢 Punto 2

1. Sube `esp32_maestro_spi.ino` a la ESP32 y `esp32_s3_esclavo_spi_oled.ino` a la ESP32-S3.
2. Conecta el SPI y la OLED según las tablas de arriba (con **GND común**).
3. Conecta la ESP32 maestra al PC, **cierra el Monitor Serial** y ajusta el puerto en `reconocer_digito.py`:
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

Si la ESP32 maestra no está conectada, el programa **sigue funcionando solo con el reconocimiento visual**, sin enviar nada.

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 📡 Protocolos de comunicación

<div align="center">

| Punto | Enlace | Formato | Cuándo se envía | Ejemplo |
|:---:|:---|:---|:---:|:---|
| **1** | ESP32 → PC (UART 115200) | `D:<dígito>` · `LIMPIAR` · `HOME` · `SALIR` | Al presionar la tecla | `D:7` |
| **2** | PC → ESP32 maestro (UART 115200) | Un carácter `0`–`9` + `\n` | Cuando el dígito es estable | `7` |
| **2** | ESP32 maestro → ESP32-S3 (SPI, 1 MHz, modo 0) | 1 byte con el valor del dígito | Una vez por dígito reconocido | `0x07` |

</div>

<details>
<summary><b>📖 Cómo funciona la transacción SPI</b></summary>

1. El maestro baja `CS` y espera 10 ms.
2. Envía un byte con `SPI.transfer(dato)`.
3. Espera otros 10 ms y sube `CS`.
4. En el esclavo, `slave.transfer(...)` queda bloqueado en una tarea FreeRTOS hasta que el maestro completa la transacción; el primer byte recibido se pone en una cola.
5. `loop()` saca el dígito de la cola, valida que sea `≤ 9` (si no, lo descarta como ruido), lo dibuja en la OLED y enciende el LED 1 s.

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 🧩 Explicación del código, bloque por bloque

### 1️⃣ Punto 1 — `dibujo_pybullet.py` y `teclado_lcd.ino`

<details>
<summary><b>✏️ Dígitos como segmentos de 7 segmentos</b></summary>

Cada dígito se define con las letras de los segmentos que se encienden (`a`–`g`). Por ejemplo, el `7`
es `abc` y el `8` es `abcdefg`. Cada segmento se traduce a un trazo entre dos puntos de una rejilla
de 2×3 puntos, así que los 10 dígitos salen de la misma tabla.

</details>

<details>
<summary><b>📐 Cinemática inversa pan-tilt</b></summary>

Cada punto `(y, z)` del lienzo se convierte en dos ángulos:

```python
theta1 = atan2(y, d)             # joint_1: giro de la base
theta2 = atan2(hypot(d, y), z)   # joint_2: inclinación del codo
```

`d` es la distancia horizontal del codo al lienzo. Con eso el brazo "apunta" al punto, y como solo
hay dos articulaciones activas la solución es una fórmula cerrada, sin iterar.

</details>

<details>
<summary><b>🖊️ Pluma arriba / pluma abajo</b></summary>

Para ir al inicio de un trazo el brazo se mueve **sin dejar rastro**; durante el trazo se dibuja una
línea con `addUserDebugLine` en PyBullet y el mismo segmento en un lienzo 2D de OpenCV (ventana
*"Lo que escribio el robot"*). Al terminar cada dígito se guarda una imagen `digito_<n>.png`.

</details>

<details>
<summary><b>⌨️ Firmware: teclado + LCD (<code>teclado_lcd.ino</code>)</b></summary>

El teclado se lee con la librería `Keypad` (conectado directo a GPIO) y la LCD con
`LiquidCrystal_I2C`. Los dígitos se acumulan en pantalla y, además, cada uno se envía por
`Serial` como `D:<dígito>`. Las teclas `A`, `B` y `C` envían los comandos `SALIR`, `LIMPIAR` y `HOME`.

</details>

### 2️⃣ Punto 2 — `entrenar_modelo.py` y `reconocer_digito.py`

<details>
<summary><b>🧠 La CNN (<code>entrenar_modelo.py</code>)</b></summary>

| Capa | Detalle |
|:---|:---|
| `Conv2D` + `MaxPooling2D` | 32 filtros 3×3, ReLU |
| `Conv2D` + `MaxPooling2D` | 64 filtros 3×3, ReLU |
| `Flatten` | — |
| `Dense` | 128 neuronas, ReLU |
| `Dropout` | 0.5 |
| `Dense` | 10 neuronas, softmax (dígitos 0–9) |

Se entrena con **MNIST** durante 10 épocas con *data augmentation* (rotación de 10°, desplazamientos
del 10 % y zoom del 10 %) para que tolere dígitos escritos a mano frente a la cámara. El modelo se
guarda en `modelo_mnist_cnn.h5`.

</details>

<details>
<summary><b>👁️ Preprocesamiento con OpenCV (<code>reconocer_digito.py</code>)</b></summary>

Se toma un recuadro verde de `300×300 px` en el centro de la cámara y se lleva a formato **MNIST**:

1. Escala de grises + `GaussianBlur` de 5×5.
2. **Umbral adaptativo gaussiano** invertido (dígito oscuro → blanco).
3. `findContours`: se toma el contorno más grande y se ignoran los menores a `500 px²` (ruido).
4. Se recorta el dígito y se escala a **20×20** conservando la proporción.
5. Se pega en un lienzo de **28×28**, centrado por **centro de masa**, y se normaliza a `[0, 1]`.

</details>

<details>
<summary><b>🛡️ Filtros antes de enviar el dígito</b></summary>

| Filtro | Valor | Para qué |
|:---|:---:|:---|
| Confianza mínima de la CNN | `> 60 %` | Ignora predicciones dudosas |
| Votación mayoritaria | últimas `5` predicciones | Suaviza parpadeos entre clases |
| Estabilidad | `3 s` con el mismo número | Solo envía cuando el dígito se mantiene quieto |
| No repetir | mismo dígito que el último enviado | Evita reenviar el mismo número en bucle |

</details>

<details>
<summary><b>📟 Maestro SPI (<code>esp32_maestro_spi.ino</code>)</b></summary>

Lee una línea por serie, comprueba que sea **un solo carácter entre `0` y `9`** (si no, responde
`ERROR: Solo acepto digitos 0-9`), la envía con `enviar_spi()` y enciende el LED de la placa 2 s.
El SPI se configura a 1 MHz en modo 0; si el esclavo lee mal, el propio código sugiere bajar a 100 kHz.

</details>

<details>
<summary><b>🖥️ Esclavo SPI + OLED (<code>esp32_s3_esclavo_spi_oled.ino</code>)</b></summary>

```cpp
size_t recibidos = slave.transfer(tx_buf, rx_buf, BUFFER_SIZE);
if (recibidos > 0) { uint8_t d = rx_buf[0]; xQueueSend(colaDigitos, &d, 0); }
```

La **tarea SPI** (`tareaSPI`, fijada al núcleo 1) espera transacciones sin timeout para no dejar
transacciones abandonadas en el driver. `loop()` recibe el dígito de la cola, lo centra en la OLED
con `getTextBounds` y lo dibuja en tamaño 6. El LED se apaga por tiempo con `millis()`, sin `delay()`.

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 🧠 Conceptos clave

<details>
<summary><b>🔁 Real-to-Sim</b></summary>

Un **dispositivo físico real** (aquí, el teclado con la ESP32) controla un **modelo simulado**
(el brazo en PyBullet). Permite validar la interfaz y la lógica de control sin riesgo ni costo.

</details>

<details>
<summary><b>🔗 SPI maestro/esclavo</b></summary>

Bus síncrono de 4 hilos: `SCLK` (reloj), `MOSI` (maestro → esclavo), `MISO` (esclavo → maestro) y
`CS` (selección). El **maestro** genera el reloj y decide cuándo hablar; el **esclavo** solo responde
cuando `CS` está en bajo. Por eso el esclavo necesita el periférico en modo esclavo, y no basta `SPI.h`.

</details>

<details>
<summary><b>🧵 FreeRTOS: tareas y colas</b></summary>

Una **tarea** es un "hilo" que corre en paralelo; una **cola** es el buzón por el que dos tareas se
pasan datos de forma segura. Aquí, la tarea SPI deposita el dígito y `loop()` lo recoge.

</details>

<details>
<summary><b>👁️ Umbral adaptativo y contornos</b></summary>

El umbral adaptativo calcula un umbral distinto para cada vecindad de la imagen, así que tolera
sombras y luz desigual. `findContours` encuentra el borde de las figuras blancas; el más grande es el
dígito.

</details>

<details>
<summary><b>🧪 Red convolucional (CNN) y MNIST</b></summary>

Una CNN aprende filtros que detectan bordes y formas, y los combina para clasificar. **MNIST** es un
conjunto de 70 000 dígitos manuscritos de 28×28 píxeles en escala de grises, el estándar para
practicar reconocimiento de dígitos.

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

## 🛠️ Solución de problemas

| Problema | Posible solución |
|:---|:---|
| `ModuleNotFoundError` (`pybullet`, `serial`, `cv2`, `tensorflow`) | Ejecuta `pip install pybullet pyserial opencv-python numpy tensorflow` |
| `serial` instalado pero no funciona (`AttributeError: ... Serial`) | `pip uninstall serial` y luego `pip install pyserial` |
| `could not open port 'COM3'` | Cierra el **Monitor Serial** del Arduino IDE y revisa el puerto en el *Administrador de dispositivos* |
| El Punto 2 corre "solo con reconocimiento visual" | No se abrió el puerto serie: ajusta `PUERTO_SERIE` |
| No abre la cámara | Cierra otras apps que la usen o cambia el índice en `cv2.VideoCapture(0)` |
| Reconoce mal los dígitos | Más luz, trazo grueso y oscuro, fondo blanco liso y el dígito dentro del recuadro verde |
| No enciende la LCD | Prueba la dirección `0x3F` o ajusta el potenciómetro de contraste del módulo |
| El teclado no envía nada | Revisa que las 8 conexiones coincidan con la tabla y que la librería **Keypad** esté instalada |
| La OLED se queda en "ESPERANDO..." | Revisa CS/SCLK/MOSI, la **GND común** y la dirección `0x3C` |
| El esclavo recibe valores raros | Baja la frecuencia SPI del maestro a `100000`; el esclavo ignora valores mayores a 9 |
| El brazo no dibuja en modo serial | Confirma el puerto y los baudios (`115200`); el `.ino` envía `D:<dígito>` |
| Los GIF no se ven | GitHub los carga al abrir el README; si el repo es privado, verifica que estés logueado |

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0B3D2E,100:1F8A4C&height=3&section=header" width="100%"/>

<div align="center">

## 👤 Autor

**Julián** · Ingeniería Mecatrónica · Universidad Militar Nueva Granada

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:1F8A4C,50:14683F,100:0B3D2E&height=120&section=footer)

</div>
