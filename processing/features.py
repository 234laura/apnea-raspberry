from collections import deque
from statistics import mean, median


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


class PPGEstimator:
    def __init__(self, fs=25, window_seconds=8):
        self.fs = fs
        self.maxlen = fs * window_seconds
        self.red = deque(maxlen=self.maxlen)
        self.ir = deque(maxlen=self.maxlen)

    def add_sample(self, red, ir):
        self.red.append(float(red))
        self.ir.append(float(ir))

    def ready(self):
        return len(self.ir) >= int(self.fs * 4)

    def _moving_average(self, data, k=5):
        if len(data) < k:
            return list(data)

        out = []
        half = k // 2
        for i in range(len(data)):
            a = max(0, i - half)
            b = min(len(data), i + half + 1)
            out.append(sum(data[a:b]) / (b - a))
        return out

    def _detrend(self, data, k=25):
        baseline = self._moving_average(data, k=k)
        return [x - b for x, b in zip(data, baseline)]

    def estimate_hr(self):
        if not self.ready():
            return None

        ir = list(self.ir)
        signal = self._detrend(ir, k=max(5, self.fs))
        smooth = self._moving_average(signal, k=5)

        peak_threshold = 0.5 * max(smooth) if smooth else 0
        min_distance = int(0.4 * self.fs)  # evita dobles picos >150 bpm

        peaks = []
        last_peak = -10**9

        for i in range(1, len(smooth) - 1):
            if (
                smooth[i] > peak_threshold
                and smooth[i] > smooth[i - 1]
                and smooth[i] >= smooth[i + 1]
                and (i - last_peak) >= min_distance
            ):
                peaks.append(i)
                last_peak = i

        if len(peaks) < 2:
            return None

        intervals = [(peaks[i] - peaks[i - 1]) / self.fs for i in range(1, len(peaks))]
        ibi = median(intervals)

        if ibi <= 0:
            return None

        bpm = 60.0 / ibi

        if 35 <= bpm <= 220:
            return round(bpm, 1)
        return None

    def estimate_spo2(self):
        if not self.ready():
            return None

        red = list(self.red)
        ir = list(self.ir)

        dc_red = mean(red)
        dc_ir = mean(ir)

        if dc_red <= 0 or dc_ir <= 0:
            return None

        ac_red = max(red) - min(red)
        ac_ir = max(ir) - min(ir)

        if ac_ir <= 0:
            return None

        # Aproximación de ingeniería para prototipo
        r = (ac_red / dc_red) / (ac_ir / dc_ir)

        spo2 = 110 - 25 * r

        if spo2 < 70:
            spo2 = 70
        if spo2 > 100:
            spo2 = 100

        return round(spo2, 1)

    def estimate_vitals(self):
        return {
            "fc": self.estimate_hr(),
            "spo2": self.estimate_spo2(),
        }


def preparar_variables_para_prolog(vitales, movimiento, pausa_seg):
    fc = vitales["fc"] if vitales["fc"] is not None else 0
    spo2 = vitales["spo2"] if vitales["spo2"] is not None else 0

    return {
        "fc": fc,
        "spo2": spo2,
        "movimiento": movimiento,
        "pausa_seg": pausa_seg
    }