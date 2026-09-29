# reconocer_digito.py
# Reconoce dígitos escritos a mano usando la webcam y un modelo CNN MNIST.

# ------------------------------------------------------------------
# 0. Silenciar mensajes de TensorFlow (deben ir ANTES de importar TF)
# ------------------------------------------------------------------
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'    # Solo errores
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'   # Desactiva oneDNN

import cv2
import numpy as np
import tensorflow as tf
import serial
import time


# ------------------------------------------------------------------
# 1. Función de preprocesamiento estilo MNIST
# ------------------------------------------------------------------
def preprocesar_digito(roi):
    """
    Convierte un recorte BGR de la webcam en una imagen 28x28 tipo MNIST:
      - Fondo negro, dígito blanco
      - Centrado por centro de masa
      - Escalado a 20x20 con padding
    Devuelve (imagen_normalizada, caja) o (None, None) si no hay dígito.
    """
    if roi is None or roi.size == 0:
        return None, None

    # 1.1 Escala de grises
    gris = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # 1.2 Desenfoque suave (kernel pequeño para no cerrar el hueco del 0)
    blur = cv2.GaussianBlur(gris, (5, 5), 0)

    # 1.3 Umbral adaptativo (más robusto que uno fijo)
    umbral = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )

    # 1.4 Encontrar el contorno más grande (el dígito)
    contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None, None

    c = max(contornos, key=cv2.contourArea)
    if cv2.contourArea(c) < 500:      # Ignorar ruido
        return None, None

    # 1.5 Recortar el dígito
    x, y, w, h = cv2.boundingRect(c)
    digito = umbral[y:y+h, x:x+w]

    # 1.6 Reescalar manteniendo proporción a 20x20 (MNIST: 20x20 + margen)
    if w > h:
        nuevo_w = 20
        nuevo_h = max(1, int(round(20 * h / w)))
    else:
        nuevo_h = 20
        nuevo_w = max(1, int(round(20 * w / h)))

    digito = cv2.resize(digito, (nuevo_w, nuevo_h),
                        interpolation=cv2.INTER_AREA)

    # 1.7 Lienzo 28x28 negro y pegar centrado por centro de masa
    lienzo = np.zeros((28, 28), dtype=np.uint8)

    M = cv2.moments(digito)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    else:
        cx, cy = nuevo_w // 2, nuevo_h // 2

    desplaz_x = 14 - cx
    desplaz_y = 14 - cy

    for i in range(nuevo_h):
        for j in range(nuevo_w):
            yi = i + desplaz_y
            xj = j + desplaz_x
            if 0 <= yi < 28 and 0 <= xj < 28:
                lienzo[yi, xj] = digito[i, j]

    # 1.8 Normalizar a [0,1]
    lienzo = lienzo / 255.0

    return lienzo, (x, y, w, h)


# ------------------------------------------------------------------
# 2. Configuración del puerto serie
# ------------------------------------------------------------------
PUERTO_SERIE = "COM3"  # Cambia esto según tu puerto (COM3, COM4, etc.)
BAUDIOS = 115200

try:
    ser = serial.Serial(PUERTO_SERIE, BAUDIOS, timeout=1)
    time.sleep(2)
    print(f"Conectado al ESP32 en {PUERTO_SERIE}")
except serial.SerialException as e:
    print(f"No se pudo abrir puerto {PUERTO_SERIE}. Funcionará solo con reconocimiento visual.")
    ser = None

ultimo_digito_enviado = None
ultimo_tiempo_envio = 0
TIEMPO_MINIMO_ENTRE_ENVIOS = 1.0  # 1 segundo mínimo entre envíos

# ✅ ESTABILIDAD DE DETECCIÓN
digito_actual_estable = -1
tiempo_inicio_digito = 0
TIEMPO_ESTABILIDAD = 3.0  # Debe mantener el número 3 segundos antes de enviar


# ------------------------------------------------------------------
# 3. Cargar el modelo entrenado
# ------------------------------------------------------------------
modelo = tf.keras.models.load_model('modelo_mnist_cnn.h5')
print("Modelo cargado. Presiona 'q' para salir.")


# ------------------------------------------------------------------
# 4. Abrir la cámara
# ------------------------------------------------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

# Tamaño del cuadro de toma
LADO = 300

# Variables para suavizar la predicción (evita parpadeos)
historial = []
VENTANA = 5

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Centrar el cuadro dinámicamente
    alto, ancho = frame.shape[:2]
    x1 = (ancho - LADO) // 2
    y1 = (alto - LADO) // 2
    x2 = x1 + LADO
    y2 = y1 + LADO

    # 4.1 Dibujar el recuadro guía
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # 4.2 Recortar la ROI y preprocesar
    roi = frame[y1:y2, x1:x2]
    digito_procesado, bbox = preprocesar_digito(roi)

    if digito_procesado is not None:
        # 4.3 Predecir
        entrada = digito_procesado.reshape(1, 28, 28, 1)
        prediccion = modelo.predict(entrada, verbose=0)
        clase = int(np.argmax(prediccion))
        confianza = float(np.max(prediccion)) * 100

        # 4.4 Suavizar con votación mayoritaria
        historial.append(clase)
        if len(historial) > VENTANA:
            historial.pop(0)

        # Solo mostramos la clase si es la más repetida y confiable
        if confianza > 60:
            clase_estable = max(set(historial), key=historial.count)
            texto = f"Numero: {clase_estable} ({confianza:.1f}%)"
            cv2.putText(frame, texto, (x1, y1 - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)

            # ✅ VERIFICAR ESTABILIDAD (mismo número durante 3 segundos)
            ahora = time.time()
            
            if clase_estable != digito_actual_estable:
                # Cambió a un número diferente, reiniciar contador
                digito_actual_estable = clase_estable
                tiempo_inicio_digito = ahora
                tiempo_estable = 0
            else:
                # Mismo número, calcular cuánto tiempo lleva estable
                tiempo_estable = ahora - tiempo_inicio_digito
            
            # Mostrar tiempo restante en pantalla
            if tiempo_estable < TIEMPO_ESTABILIDAD:
                texto_tiempo = f"Estable en: {tiempo_estable:.1f}s / {TIEMPO_ESTABILIDAD}s"
                cv2.putText(frame, texto_tiempo, (x1, y1 + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (255, 165, 0), 2)

            # ✅ ENVIAR SOLO SI ESTUVO ESTABLE 3 SEGUNDOS
            if (tiempo_estable >= TIEMPO_ESTABILIDAD and
                clase_estable != ultimo_digito_enviado and 
                ser is not None):
                mensaje = f"{clase_estable}\n"
                ser.write(mensaje.encode('utf-8'))
                print(f"✅ ENVIADO AL ESP32 (estable 3s): {clase_estable}")
                ultimo_digito_enviado = clase_estable
                ultimo_tiempo_envio = ahora

        # 4.5 Mostrar el dígito preprocesado ampliado
        vista = (digito_procesado * 255).astype(np.uint8)
        vista = cv2.resize(vista, (200, 200),
                           interpolation=cv2.INTER_NEAREST)
        cv2.imshow('Digito procesado (28x28 ampliado)', vista)

    # 4.6 Mostrar frame principal
    cv2.imshow('Reconocimiento de digitos', frame)

    # 4.7 Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if ser is not None:
    ser.close()