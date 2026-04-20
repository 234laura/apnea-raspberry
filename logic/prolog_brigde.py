from pyswip import Prolog


class MotorApneaProlog:
    def __init__(self, rules_path="apnea_rules.pl"):
        self.prolog = Prolog()
        self.prolog.consult(rules_path)

    def limpiar_hechos(self):
        for predicado in [
            "frecuencia_cardiaca(_)",
            "spo2(_)",
            "movimiento(_)",
            "pausa_respiratoria_seg(_)",
            "tendencia_spo2(_)",
        ]:
            list(self.prolog.query(f"retractall({predicado})"))

    def evaluar(self, fc, spo2, movimiento, pausa_seg, tendencia_spo2=0.0):
        self.limpiar_hechos()

        self.prolog.assertz(f"frecuencia_cardiaca({int(fc)})")
        self.prolog.assertz(f"spo2({int(spo2)})")
        self.prolog.assertz(f"movimiento({float(movimiento)})")
        self.prolog.assertz(f"pausa_respiratoria_seg({int(pausa_seg)})")
        self.prolog.assertz(f"tendencia_spo2({float(tendencia_spo2)})")

        resultado = list(self.prolog.query("clasificacion(X)"))
        return resultado[0]["X"] if resultado else "desconocido"