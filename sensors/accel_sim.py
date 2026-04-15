import random


def leer_acelerometro_simulado(escenario="aleatorio"):
    if escenario == "normal":
        return {
            "movimiento": round(random.uniform(0.10, 0.35), 3),
            "pausa_seg": random.randint(0, 4)
        }

    if escenario == "moderada":
        return {
            "movimiento": round(random.uniform(0.02, 0.08), 3),
            "pausa_seg": random.randint(10, 18)
        }

    if escenario == "grave":
        return {
            "movimiento": round(random.uniform(0.00, 0.03), 3),
            "pausa_seg": random.randint(20, 35)
        }

    # modo aleatorio
    return {
        "movimiento": round(random.uniform(0.00, 0.35), 3),
        "pausa_seg": random.randint(0, 35)
    }