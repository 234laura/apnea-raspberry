import time
from sensors.mpu6050_sensor import MPU6050


def main():
    sensor = MPU6050()

    try:
        sensor.setup()
        print("Leyendo acelerómetro... Ctrl + C para detener\n")

        while True:
            data = sensor.read_accel_g()
            print(
                f"ax={data['ax']:.3f} g | "
                f"ay={data['ay']:.3f} g | "
                f"az={data['az']:.3f} g | "
                f"|a|={data['magnitude']:.3f} g"
            )
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nPrueba detenida.")

    finally:
        sensor.close()


if __name__ == "__main__":
    main()