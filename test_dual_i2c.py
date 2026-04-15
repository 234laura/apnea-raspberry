import time
from smbus2 import SMBus
from sensors.mpu6050_sensor import MPU6050
from sensors.max3010x_sensor import MAX30102


def main():
    bus = SMBus(1)
    accel = MPU6050(bus=bus)
    max_sensor = MAX30102(bus=bus)

    try:
        print("PART_ID max    =", hex(max_sensor.read_part_id()))
        time.sleep(0.2)
        print("WHO_AM_I accel =", hex(accel.who_am_i()))
        time.sleep(0.2)

        print("\nSetup MAX primero...")
        max_sensor.setup()
        time.sleep(0.5)

        print("Leyendo una muestra MAX...")
        datos_max = max_sensor.read_sample()
        print(f"RED={datos_max['red']} | IR={datos_max['ir']}")
        time.sleep(0.5)

        print("\nSetup acelerómetro después...")
        accel.setup()
        time.sleep(0.5)

        print("Leyendo acelerómetro...")
        datos_acc = accel.read_accel_g()
        print(
            f"ax={datos_acc['ax']:.3f} | "
            f"ay={datos_acc['ay']:.3f} | "
            f"az={datos_acc['az']:.3f}"
        )

    except Exception as e:
        print("Error:", repr(e))

    finally:
        bus.close()


if __name__ == "__main__":
    main()