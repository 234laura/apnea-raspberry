import time
from sensors.max3010x_sensor import MAX30102


def main():
    sensor = MAX30102()

    try:
        print("PART_ID =", hex(sensor.read_part_id()))
        sensor.setup()

        print("Leyendo MAX30102... pon el dedo sobre el sensor. Ctrl+C para detener.\n")

        while True:
            sample = sensor.read_sample()
            print(f"RED={sample['red']} | IR={sample['ir']}")
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nPrueba detenida.")

    except Exception as e:
        print("Error:", repr(e))

    finally:
        sensor.close()


if __name__ == "__main__":
    main()