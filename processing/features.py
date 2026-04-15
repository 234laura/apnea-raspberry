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
    def __init__(
        self,
        fs=25,
        window_seconds=8,
        finger_on_threshold=12000,
        finger_off_threshold=4000,
    ):
        self.fs = fs
        self.maxlen = fs * window_seconds

        self.finger_on_threshold = finger_on_threshold
        self.finger_off_threshold = finger_off_threshold

        self.red = deque(maxlen=self.maxlen)
        self.ir = deque(maxlen=self.maxlen)

        self.finger_present = False

        self.fc_hist = deque(maxlen=5)
        self.spo2_hist = deque(maxlen=5)

    def reset_buffers(self):
        self.red.clear()
        self.ir.clear()
        self.fc_hist.clear()
        self.spo2_hist.clear()

    def add_sample(self, red, ir):
        red = float(red)
        ir = float(ir)

        self.red.append(red)
        self.ir.append(ir)

        recientes = list(self.ir)[-min(len(self.ir), self.fs):]
        ir_med = median(recientes) if recientes else 0

        if not self.finger_present and ir_med > self.finger_on_threshold:
            self.finger_present = True

        elif self.finger_present and ir_med < self.finger_off_threshold:
            self.finger_present = False
            self.reset_buffers()

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

    def hay_dedo(self):
        return self.finger_present

    def _senal_suficiente(self):
        return len(self.ir) >= int(self.fs * 5)

    def estimate_hr_raw(self):
        if not self.hay_dedo():
            return None

        if not self._senal_suficiente():
            return None

        ir = list(self.ir)
        signal = self._detrend(ir, k=max(5, self.fs))
        smooth = self._moving_average(signal, k=5)

        if not smooth:
            return None

        max_val = max(smooth)
        min_val = min(smooth)
        amp = max_val - min_val

        if amp <= 0:
            return None

        peak_threshold = min_val + 0.6 * amp
        min_distance = int(0.45 * self.fs)

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

        if 45 <= bpm <= 180:
            return round(bpm, 1)

        return None

    def estimate_spo2_raw(self):
        if not self.hay_dedo():
            return None

        if not self._senal_suficiente():
            return None

        red = list(self.red)
        ir = list(self.ir)

        dc_red = mean(red)
        dc_ir = mean(ir)

        if dc_red <= 0 or dc_ir <= 0:
            return None

        ac_red = max(red) - min(red)
        ac_ir = max(ir) - min(ir)

        if ac_red <= 0 or ac_ir <= 0:
            return None

        r = (ac_red / dc_red) / (ac_ir / dc_ir)
        spo2 = 104 - 17 * r

        if spo2 < 70:
            spo2 = 70
        if spo2 > 100:
            spo2 = 100

        return round(spo2, 1)

    def estimate_vitals(self):
        if not self.hay_dedo():
            return {"fc": None, "spo2": None, "status": "SIN_DEDO"}

        if not self._senal_suficiente():
            return {"fc": None, "spo2": None, "status": "CALCULANDO"}

        fc_raw = self.estimate_hr_raw()
        spo2_raw = self.estimate_spo2_raw()

        if fc_raw is None or spo2_raw is None:
            return {"fc": None, "spo2": None, "status": "CALCULANDO"}

        self.fc_hist.append(fc_raw)
        self.spo2_hist.append(spo2_raw)

        fc = round(median(self.fc_hist), 1)
        spo2 = round(median(self.spo2_hist), 1)

        return {
            "fc": fc,
            "spo2": spo2,
            "status": "VALIDO"
        }


def preparar_variables_para_prolog(vitales, movimiento, pausa_seg):
    return {
        "fc": vitales["fc"],
        "spo2": vitales["spo2"],
        "movimiento": movimiento,
        "pausa_seg": pausa_seg
    }