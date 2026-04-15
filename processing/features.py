def calcular_movimiento(datos_acc):
    return abs(datos_acc["magnitude"] - 1.0)


def calcular_pausa_desde_historial(historial_mov, umbral=0.03, dt=1.0):
    segundos = 0.0
    for mov in reversed(historial_mov):
        if mov < umbral:
            segundos += dt
        else:
            break
    return int(segundos)


def estimar_fc_spo2_provisional(datos_max):
    red = datos_max["red"]
    ir = datos_max["ir"]

    # Solo para integración del sistema, no clínico
    if red > 50000 and ir > 50000:
        fc = 75
        spo2 = 96
    elif red > 5000 and ir > 5000:
        fc = 68
        spo2 = 93
    else:
        fc = 55
        spo2 = 85

    return {
        "fc": fc,
        "spo2": spo2
    }


def preparar_variables_para_prolog(vitales, movimiento, pausa_seg):
    return {
        "fc": vitales["fc"],
        "spo2": vitales["spo2"],
        "movimiento": movimiento,
        "pausa_seg": pausa_seg
    }