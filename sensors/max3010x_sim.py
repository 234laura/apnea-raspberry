import random


def leer_max30102_simulado(escenario="aleatorio"):
    if escenario == "normal":
        return {
            "fc": random.randint(60, 90),
            "spo2": random.randint(95, 99)
        }

    if escenario == "moderada":
        return {
            "fc": random.randint(55, 105),
            "spo2": random.randint(90, 93)
        }

    if escenario == "grave":
        return {
            "fc": random.randint(45, 120),
            "spo2": random.randint(82, 89)
        }

    # modo aleatorio
    return {
        "fc": random.randint(45, 120),
        "spo2": random.randint(82, 99)
    }