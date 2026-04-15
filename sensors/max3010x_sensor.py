from smbus2 import SMBus
import time


class MAX30102:
    I2C_ADDR = 0x57

    REG_INTR_STATUS_1 = 0x00
    REG_INTR_STATUS_2 = 0x01
    REG_FIFO_WR_PTR   = 0x04
    REG_OVF_COUNTER   = 0x05
    REG_FIFO_RD_PTR   = 0x06
    REG_FIFO_DATA     = 0x07
    REG_FIFO_CONFIG   = 0x08
    REG_MODE_CONFIG   = 0x09
    REG_SPO2_CONFIG   = 0x0A
    REG_LED1_PA       = 0x0C
    REG_LED2_PA       = 0x0D
    REG_PART_ID       = 0xFF

    def __init__(self, bus_id=1, address=I2C_ADDR, bus=None):
        self._own_bus = bus is None
        self.bus = bus if bus is not None else SMBus(bus_id)
        self.address = address

    def write_reg(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def read_reg(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def read_part_id(self):
        return self.read_reg(self.REG_PART_ID)

    def setup(self):
        time.sleep(0.2)
        _ = self.read_reg(self.REG_INTR_STATUS_1)
        _ = self.read_reg(self.REG_INTR_STATUS_2)

        self.write_reg(self.REG_FIFO_WR_PTR, 0x00)
        self.write_reg(self.REG_OVF_COUNTER, 0x00)
        self.write_reg(self.REG_FIFO_RD_PTR, 0x00)
        self.write_reg(self.REG_FIFO_CONFIG, 0x0F)
        self.write_reg(self.REG_MODE_CONFIG, 0x03)
        self.write_reg(self.REG_SPO2_CONFIG, 0x27)
        self.write_reg(self.REG_LED1_PA, 0x24)
        self.write_reg(self.REG_LED2_PA, 0x24)

        time.sleep(0.1)

    def read_sample(self):
        data = self.bus.read_i2c_block_data(self.address, self.REG_FIFO_DATA, 6)
        red = ((data[0] << 16) | (data[1] << 8) | data[2]) & 0x03FFFF
        ir  = ((data[3] << 16) | (data[4] << 8) | data[5]) & 0x03FFFF
        return {"red": red, "ir": ir}

    def close(self):
        if self._own_bus:
            self.bus.close()