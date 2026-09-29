"""
Punto 1 - Simulacion de brazo robotico dibujando en PyBullet
--------------------------------------------------------------
Recibe digitos (0-9) por puerto Serial desde el ESP32/Arduino
(formato "D:<digito>\n") y mueve el brazo (brazo.urdf) para que
la punta trace la forma del digito, estilo display de 7 segmentos,
sobre un "lienzo" vertical imaginario ubicado frente al robot.

Requisitos:
    pip install pybullet pyserial opencv-python numpy

Uso:
    python dibujo_pybullet.py            # espera datos reales por serial
    python dibujo_pybullet.py --demo     # dibuja 0..9 automaticamente (sin hardware)
"""

import time
import math
import argparse

import numpy as np
import cv2
import pybullet as p
import pybullet_data

GRIPPER_LINK = 2  # indice del link "gripper_base" (punta del brazo) en el URDF

# --- Lienzo 2D (OpenCV): para "ver" lo que el robot escribio ---
LADO_PX = 400
MARGEN_PX = 40
canvas = np.zeros((LADO_PX, LADO_PX, 3), dtype=np.uint8)


def punto_a_pixel(y_offset, z_offset):
    """Convierte (y_offset, z_offset) del lienzo real (metros) a pixeles."""
    escala = (LADO_PX / 2 - MARGEN_PX) / max(ANCHO_LIENZO, ALTO_LIENZO)
    px = int(LADO_PX / 2 + y_offset * escala)
    py = int(LADO_PX / 2 - z_offset * escala)  # eje Y invertido (imagen crece hacia abajo)
    return px, py

# ------------------------------------------------------------------
# 1) Geometria del brazo (tomada del URDF) y parametros del lienzo
# ------------------------------------------------------------------
ALTURA_CODO = 0.5      # altura (z) del joint_2 respecto al suelo, fija (ver URDF)
L2 = 0.35               # longitud efectiva codo -> punta (brazo2 + pinza)
PROFUNDIDAD_LIENZO = 0.25   # distancia (eje X) del codo al lienzo vertical
ANCHO_LIENZO = 0.18          # medio-ancho del trazo (m)
ALTO_LIENZO = 0.18            # medio-alto del trazo (m)

JOINT_BASE = 0   # joint_1 (Z) -> nombre "joint_1"
JOINT_CODO = 1   # joint_2 (Y) -> nombre "joint_2"
JOINT_DEDO_IZQ = 3   # joint_dedo_izq (prismatic, limite 0.0-0.04)
JOINT_DEDO_DER = 4   # joint_dedo_der (prismatic, limite 0.0-0.04)
APERTURA_PINZA = 0.04   # maxima apertura segun el URDF -> pinza abierta


def ik_pan_tilt(y_offset, z_offset):
    """Convierte un punto del lienzo (y_offset, z_offset) en angulos
    (theta1, theta2) usando el modelo pan-tilt del brazo."""
    d = PROFUNDIDAD_LIENZO
    r_horizontal = math.hypot(d, y_offset)
    theta1 = math.atan2(y_offset, d)
    theta2 = math.atan2(r_horizontal, z_offset)
    return theta1, theta2


# ------------------------------------------------------------------
# 2) Definicion de los digitos como trazos tipo 7 segmentos
#    Grid: x en [0,1] (izq->der), y en [0,2] (abajo->arriba)
# ------------------------------------------------------------------
PUNTOS = {
    "sup_izq": (0, 2), "sup_der": (1, 2),
    "med_izq": (0, 1), "med_der": (1, 1),
    "inf_izq": (0, 0), "inf_der": (1, 0),
}

SEGMENTOS = {
    "a": ("sup_izq", "sup_der"),
    "b": ("sup_der", "med_der"),
    "c": ("med_der", "inf_der"),
    "d": ("inf_izq", "inf_der"),
    "e": ("med_izq", "inf_izq"),
    "f": ("sup_izq", "med_izq"),
    "g": ("med_izq", "med_der"),
}

DIGITOS = {
    "0": "abcdef",
    "1": "bc",
    "2": "abged",
    "3": "abgcd",
    "4": "fgbc",
    "5": "afgcd",
    "6": "afgecd",
    "7": "abc",
    "8": "abcdefg",
    "9": "abcdfg",
}


def trazos_para_digito(digito):
    """Devuelve una lista de trazos; cada trazo es una lista de puntos
    (y_offset, z_offset) en metros, listos para pluma abajo/arriba."""
    trazos = []
    for seg in DIGITOS[digito]:
        p1_key, p2_key = SEGMENTOS[seg]
        gx1, gy1 = PUNTOS[p1_key]
        gx2, gy2 = PUNTOS[p2_key]

        # Grid normalizado [0,1]x[0,2] -> coordenadas del lienzo (metros)
        y1 = (gx1 - 0.5) * 2 * ANCHO_LIENZO
        z1 = (gy1 - 1.0) * ALTO_LIENZO
        y2 = (gx2 - 0.5) * 2 * ANCHO_LIENZO
        z2 = (gy2 - 1.0) * ALTO_LIENZO

        trazos.append([(y1, z1), (y2, z2)])
    return trazos


# ------------------------------------------------------------------
# 3) Simulacion PyBullet
# ------------------------------------------------------------------
def mover_a(robot_id, y_offset, z_offset, pasos=15, pluma_abajo=False):
    theta1, theta2 = ik_pan_tilt(y_offset, z_offset)
    punto_anterior = p.getLinkState(robot_id, GRIPPER_LINK)[0]
    for i in range(pasos):
        p.setJointMotorControl2(robot_id, JOINT_BASE, p.POSITION_CONTROL,
                                 targetPosition=theta1, force=100)
        p.setJointMotorControl2(robot_id, JOINT_CODO, p.POSITION_CONTROL,
                                 targetPosition=theta2, force=80)
        p.stepSimulation()

        if pluma_abajo:
            # Rastro en vivo dentro de la ventana 3D de PyBullet
            punto_actual = p.getLinkState(robot_id, GRIPPER_LINK)[0]
            p.addUserDebugLine(punto_anterior, punto_actual,
                                lineColorRGB=[1, 1, 1], lineWidth=2, lifeTime=0)
            punto_anterior = punto_actual

        time.sleep(1.0 / 120.0)


def dibujar_digito(robot_id, digito):
    if digito not in DIGITOS:
        print(f"Digito no soportado: {digito}")
        return

    print(f"Dibujando: {digito}")
    for trazo in trazos_para_digito(digito):
        # "levantar pluma": ir al inicio del trazo (sin dibujar, es el salto)
        y0, z0 = trazo[0]
        mover_a(robot_id, y0, z0, pasos=25, pluma_abajo=False)
        for (y, z) in trazo[1:]:
            y_prev, z_prev = y0, z0
            mover_a(robot_id, y, z, pasos=25, pluma_abajo=True)  # trazo real
            # Lienzo 2D (OpenCV): dibuja el mismo segmento que se acaba de trazar
            pt1 = punto_a_pixel(y_prev, z_prev)
            pt2 = punto_a_pixel(y, z)
            cv2.line(canvas, pt1, pt2, (255, 255, 255), 3)
            cv2.imshow("Lo que escribio el robot", canvas)
            cv2.waitKey(1)
            y0, z0 = y, z

    cv2.imwrite(f"digito_{digito}.png", canvas)


def iniciar_simulacion():
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)
    p.loadURDF("plane.urdf")
    robot_id = p.loadURDF("brazo.urdf", basePosition=[0, 0, 0], useFixedBase=True)

    # Camara fija de frente al robot (ajusta estos valores a tu gusto)
    p.resetDebugVisualizerCamera(
        cameraDistance=1.0,      # que tan alejada esta la camara
        cameraYaw=90,            # giro horizontal (0=eje X, 90=eje Y de frente)
        cameraPitch=-15,         # inclinacion (negativo = mirando un poco hacia abajo)
        cameraTargetPosition=[0, 0, 0.4]   # punto al que mira (altura del brazo)
    )

    # Posicion inicial
    p.setJointMotorControl2(robot_id, JOINT_BASE, p.POSITION_CONTROL, targetPosition=0)
    p.setJointMotorControl2(robot_id, JOINT_CODO, p.POSITION_CONTROL, targetPosition=0)
    # Pinza abierta y fija asi durante toda la simulacion (no se usa para agarrar)
    p.setJointMotorControl2(robot_id, JOINT_DEDO_IZQ, p.POSITION_CONTROL,
                             targetPosition=APERTURA_PINZA, force=20)
    p.setJointMotorControl2(robot_id, JOINT_DEDO_DER, p.POSITION_CONTROL,
                             targetPosition=APERTURA_PINZA, force=20)
    for _ in range(60):
        p.stepSimulation()
        time.sleep(1.0 / 120.0)

    return robot_id


# ------------------------------------------------------------------
# 4) Lectura por Serial (hardware real) o modo demo
# ------------------------------------------------------------------
def loop_serial(robot_id, puerto="COM3", baudios=115200):
    import serial  # pyserial
    ser = serial.Serial(puerto, baudios, timeout=1)
    print(f"Escuchando en {puerto} @ {baudios} baudios... ('B' limpia el lienzo, 'C' vuelve a home, 'A' cierra)")
    try:
        while True:
            linea = ser.readline().decode(errors="ignore").strip()
            if linea == "SALIR":
                print("Boton A recibido: cerrando simulacion.")
                break
            elif linea == "LIMPIAR":
                print("Boton B recibido: limpiando lienzo.")
                limpiar_lienzo()
            elif linea == "HOME":
                print("Boton C recibido: volviendo a home.")
                ir_a_home(robot_id)
            elif linea.startswith("D:"):
                digito = linea[2:].strip()
                dibujar_digito(robot_id, digito)
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        cv2.destroyAllWindows()
        p.disconnect()


def ir_a_home(robot_id):
    """Regresa el brazo a la posicion inicial (theta1=0, theta2=0) de forma suave."""
    print("Regresando a home...")
    pasos = 60
    theta1_actual, theta2_actual = p.getJointState(robot_id, JOINT_BASE)[0], p.getJointState(robot_id, JOINT_CODO)[0]
    for i in range(pasos):
        frac = (i + 1) / pasos
        theta1 = theta1_actual * (1 - frac)
        theta2 = theta2_actual * (1 - frac)
        p.setJointMotorControl2(robot_id, JOINT_BASE, p.POSITION_CONTROL, targetPosition=theta1, force=100)
        p.setJointMotorControl2(robot_id, JOINT_CODO, p.POSITION_CONTROL, targetPosition=theta2, force=80)
        p.stepSimulation()
        time.sleep(1.0 / 120.0)


def limpiar_lienzo():
    canvas[:] = 0
    cv2.imshow("Lo que escribio el robot", canvas)
    cv2.waitKey(1)
    p.removeAllUserDebugItems()   # borra tambien el rastro 3D en PyBullet


def loop_demo(robot_id):
    for d in "0123456789":
        limpiar_lienzo()
        dibujar_digito(robot_id, d)
        # revisa si se presiono 'a' en la ventana de OpenCV para salir antes
        if cv2.waitKey(1000) & 0xFF == ord('a'):
            print("Tecla 'a' recibida: cerrando simulacion.")
            cv2.destroyAllWindows()
            p.disconnect()
            return
    print("Demo terminada. Presiona 'a' en la ventana de OpenCV para salir.")
    while True:
        if cv2.waitKey(0) & 0xFF == ord('a'):
            break
    cv2.destroyAllWindows()
    p.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Dibuja 0-9 sin hardware")
    parser.add_argument("--puerto", default="COM3", help="Puerto serial (ej. COM3 o /dev/ttyUSB0)")
    parser.add_argument("--baudios", type=int, default=115200)
    args = parser.parse_args()

    robot = iniciar_simulacion()

    if args.demo:
        loop_demo(robot)
    else:
        loop_serial(robot, args.puerto, args.baudios)
