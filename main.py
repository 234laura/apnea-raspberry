import time
from logic.prolog_brigde import MotorApneaProlog
from sensors.mpu6050_sensor import MPU6050
from sensors.max3010x_sensor import MAX30102
from processing.features import (
    calcular_movimiento,
    calcular_pausa_desde_historial,
    estimar_fc_spo2_provisional,
    preparar_variables_para_prolog,
)


def main():
    motor = MotorApneaProlog("apnea_rules.pl")
    accel = MPU6050()
    max_sensor = MAX30102()

    historial_mov = []
    dt = 1.0

    try:
        accel.setup()
        max_sensor.setup()

        print("\n--- MPU6050 real + MAX30102 real + Prolog ---\n")

        while True:
            datos_acc = accel.read_accel_g()
            datos_max = max_sensor.read_sample()

            movimiento = calcular_movimiento(datos_acc)

            historial_mov.append(movimiento)
            if len(historial_mov) > 60:
                historial_mov.pop(0)

            pausa_seg = calcular_pausa_desde_historial(
                historial_mov,
                umbral=0.03,
                dt=dt
            )

            vitales = estimar_fc_spo2_provisional(datos_max)

            variables = preparar_variables_para_prolog(
                vitales,
                movimiento,
                pausa_seg
            )

            estado = motor.evaluar(
                fc=variables["fc"],
                spo2=variables["spo2"],
                movimiento=variables["movimiento"],
                pausa_seg=variables["pausa_seg"]
            )

            print(
                f"RED={datos_max['red']} | "
                f"IR={datos_max['ir']} | "
                f"FC={variables['fc']} | "
                f"SpO2={variables['spo2']} | "
                f"ax={datos_acc['ax']:.3f} | "
                f"ay={datos_acc['ay']:.3f} | "
                f"az={datos_acc['az']:.3f} | "
                f"Mov={variables['movimiento']:.3f} | "
                f"Pausa={variables['pausa_seg']} s | "
                f"Estado={estado}"
            )

            time.sleep(dt)

    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario.")

    finally:
        accel.close()
        max_sensor.close()


if __name__ == "__main__":
    main()