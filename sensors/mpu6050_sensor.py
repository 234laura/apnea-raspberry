from smbus2 import SMBus
import math


class MPU6050:
    I2C_ADDR = 0x68
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    WHO_AM_I = 0x75

    def __init__(self, bus_id=1, address=I2C_ADDR, bus=None):
        self._own_bus = bus is None
        self.bus = bus if bus is not None else SMBus(bus_id)
        self.address = address

    def write_reg(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def read_reg(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def read_word_2c(self, reg):
        high = self.bus.read_byte_data(self.address, reg)
        low = self.bus.read_byte_data(self.address, reg + 1)
        value = (high << 8) | low
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value

    def who_am_i(self):
        return self.read_reg(self.WHO_AM_I)

    def setup(self):
        self.write_reg(self.PWR_MGMT_1, 0)

    def read_accel_g(self):
        ax = self.read_word_2c(self.ACCEL_XOUT_H) / 16384.0
        ay = self.read_word_2c(self.ACCEL_XOUT_H + 2) / 16384.0
        az = self.read_word_2c(self.ACCEL_XOUT_H + 4) / 16384.0
        magnitude = math.sqrt(ax**2 + ay**2 + az**2)
        return {"ax": ax, "ay": ay, "az": az, "magnitude": magnitude}

    def close(self):
        if self._own_bus:
            self.bus.close()