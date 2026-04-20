import time
import logging
from collections import deque

from logic.prolog_brigde import MotorApneaProlog
from sensors.mpu6050_sensor import MPU6050
from sensors.max3010x_sensor import MAX30102
from processing.features import (
    calcular_movimiento,
    calcular_pausa_desde_historial,
    preparar_variables_para_prolog,
    PPGEstimator,
)

try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO_DISPONIBLE = True
except ImportError:
    GPIO_DISPONIBLE = False

# ── Pines GPIO (BCM) ──────────────────────────────────────────
PIN_VERDE    = 14   # normal
PIN_AMARILLO = 15   # moderada
PIN_ROJO     = 27   # grave

PINES = [PIN_VERDE, PIN_AMARILLO, PIN_ROJO]

ESTADO_A_PIN = {
    "normal":    PIN_VERDE,
    "moderada":  PIN_AMARILLO,
    "grave":     PIN_ROJO,
    "sin_datos": PIN_ROJO,
}

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    filename="apnea_log.txt",
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ── Constantes ────────────────────────────────────────────────
FS           = 25
DT           = 1 / FS
UMBRAL_MOV   = 0.03
VENTANA_SPO2 = 10


def setup_leds():
    if not GPIO_DISPONIBLE:
        return
    for pin in PINES:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)


def set_led(estado: str):
    if not GPIO_DISPONIBLE:
        icono = {"normal": "🟢", "moderada": "🟡", "grave": "🔴"}.get(estado, "⚫")
        print(f"[LED] {icono} {estado.upper()}")
        return
    for pin in PINES:
        GPIO.output(pin, GPIO.LOW)
    pin_activo = ESTADO_A_PIN.get(estado)
    if pin_activo is not None:
        GPIO.output(pin_activo, GPIO.HIGH)


def apagar_leds():
    if not GPIO_DISPONIBLE:
        return
    for pin in PINES:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()


def calcular_tendencia_spo2(historial: deque) -> float:
    n = len(historial)
    if n < 2:
        return 0.0
    return (historial[-1] - historial[0]) / n


def main():
    setup_leds()

    motor      = MotorApneaProlog("apnea_rules.pl")
    accel      = MPU6050(bus_id=3)
    max_sensor = MAX30102(bus_id=1)

    ppg = PPGEstimator(
        fs=FS,
        window_seconds=8,
        finger_on_threshold=8000,
        finger_off_threshold=2500,
    )

    historial_mov  = deque(maxlen=60)
    historial_spo2 = deque(maxlen=VENTANA_SPO2)
    ultimo_reporte = time.time()

    try:
        accel.setup()
        max_sensor.setup()

        print("\n━━━ Monitor de Apnea del Sueño ━━━")
        print("GPIO 14=Verde(normal) | 15=Amarillo(moderada) | 17=Rojo(grave)\n")

        while True:
            datos_acc = accel.read_accel_g()
            datos_max = max_sensor.read_sample()

            ppg.add_sample(datos_max["red"], datos_max["ir"])

            movimiento = calcular_movimiento(datos_acc)
            historial_mov.append(movimiento)

            ahora = time.time()
            if ahora - ultimo_reporte >= 1.0:

                vitales       = ppg.estimate_vitals()
                sensor_status = vitales["status"]

                if sensor_status == "VALIDO":
                    historial_spo2.append(vitales["spo2"])
                    tendencia = calcular_tendencia_spo2(historial_spo2)

                    pausa_seg = calcular_pausa_desde_historial(
                        list(historial_mov),
                        umbral=UMBRAL_MOV,
                        dt=1.0,
                    )

                    variables = preparar_variables_para_prolog(
                        vitales, movimiento, pausa_seg,
                    )

                    estado = motor.evaluar(
                        fc=variables["fc"],
                        spo2=variables["spo2"],
                        movimiento=variables["movimiento"],
                        pausa_seg=variables["pausa_seg"],
                        tendencia_spo2=tendencia,
                    )

                    set_led(estado)

                    icono = {"normal": "🟢", "moderada": "🟡", "grave": "🔴"}.get(estado, "⚫")
                    print(
                        f"[{sensor_status}] {icono} "
                        f"RED={datos_max['red']:6d} | "
                        f"IR={datos_max['ir']:6d} | "
                        f"FC={variables['fc']:5.1f} bpm | "
                        f"SpO2={variables['spo2']:5.1f}% | "
                        f"TendSpO2={tendencia:+.2f} | "
                        f"ax={datos_acc['ax']:+.3f} "
                        f"ay={datos_acc['ay']:+.3f} "
                        f"az={datos_acc['az']:+.3f} | "
                        f"Mov={movimiento:.3f} | "
                        f"Pausa={pausa_seg:4.1f} s | "
                        f"Estado={estado.upper()}"
                    )

                    if estado == "grave":
                        logging.warning(
                            f"GRAVE | FC={variables['fc']:.1f} SpO2={variables['spo2']:.1f}% "
                            f"Pausa={pausa_seg:.1f}s TendSpO2={tendencia:+.2f}"
                        )
                    elif estado == "moderada":
                        logging.info(
                            f"MODERADA | FC={variables['fc']:.1f} SpO2={variables['spo2']:.1f}% "
                            f"Pausa={pausa_seg:.1f}s TendSpO2={tendencia:+.2f}"
                        )

                else:
                    historial_spo2.clear()
                    historial_mov.clear()
                    set_led("NO_EVALUADO")

                    print(
                        f"[{sensor_status}] ⚫ "
                        f"RED={datos_max['red']:6d} | "
                        f"IR={datos_max['ir']:6d} | "
                        f"FC=  --- | SpO2=  --- | "
                        f"ax={datos_acc['ax']:+.3f} "
                        f"ay={datos_acc['ay']:+.3f} "
                        f"az={datos_acc['az']:+.3f} | "
                        f"Mov={movimiento:.3f} | "
                        f"Pausa= --- | Estado=NO_EVALUADO"
                    )

                ultimo_reporte = ahora

            time.sleep(DT)

    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario.")

    finally:
        accel.close()
        max_sensor.close()
        apagar_leds()


if __name__ == "__main__":
    main()