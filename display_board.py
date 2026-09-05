from machine import Pin, I2C, SPI, PWM, ADC
import framebuf
import time


I2C_SDA = 6
I2C_SCL = 7

DC = 8
CS = 9
SCK = 10
MOSI = 11
RST = 12
BL = 25
VBAT_PIN = 29


class LCD_1inch28(framebuf.FrameBuffer):
    def __init__(self, cs_pin=CS, dc_pin=DC, rst_pin=RST, sck_pin=SCK,
                 mosi_pin=MOSI, bl_pin=BL, spi_id=1):
        self.width = 240
        self.height = 240

        self.cs = Pin(cs_pin, Pin.OUT)
        self.dc = Pin(dc_pin, Pin.OUT)
        self.rst = Pin(rst_pin, Pin.OUT)
        self.cs(1)
        self.dc(1)

        self.spi = SPI(spi_id, 100_000_000, polarity=0, phase=0,
                       sck=Pin(sck_pin), mosi=Pin(mosi_pin), miso=None)

        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)

        self.red = 0x07E0
        self.green = 0x001f
        self.blue = 0xf800
        self.white = 0xffff

        self.pwm = PWM(Pin(bl_pin))
        self.pwm.freq(5000)
        self.set_bl_pwm(65535)

        self.init_display()
        self.fill(self.white)
        self.show()

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytes([cmd & 0xFF]))
        self.cs(1)

    def write_data(self, *values):
        if len(values) == 1 and isinstance(values[0], (bytes, bytearray)):
            payload = bytes(values[0])
        else:
            payload = bytes([v & 0xFF for v in values])

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(payload)
        self.cs(1)

    def set_bl_pwm(self, duty):
        self.pwm.duty_u16(max(0, min(65535, duty)))

    def init_display(self):
        self.rst(1)
        time.sleep(0.01)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
        time.sleep(0.05)

        self.write_cmd(0xEF)
        self.write_cmd(0xEB)
        self.write_data(0x14)
        self.write_cmd(0xFE)
        self.write_cmd(0xEF)
        self.write_cmd(0xEB)
        self.write_data(0x14)
        self.write_cmd(0x84)
        self.write_data(0x40)
        self.write_cmd(0x85)
        self.write_data(0xFF)
        self.write_cmd(0x86)
        self.write_data(0xFF)
        self.write_cmd(0x87)
        self.write_data(0xFF)
        self.write_cmd(0x88)
        self.write_data(0x0A)
        self.write_cmd(0x89)
        self.write_data(0x21)
        self.write_cmd(0x8A)
        self.write_data(0x00)
        self.write_cmd(0x8B)
        self.write_data(0x80)
        self.write_cmd(0x8C)
        self.write_data(0x01)
        self.write_cmd(0x8D)
        self.write_data(0x01)
        self.write_cmd(0x8E)
        self.write_data(0xFF)
        self.write_cmd(0x8F)
        self.write_data(0xFF)
        self.write_cmd(0xB6)
        self.write_data(0x00, 0x20)
        self.write_cmd(0x36)
        self.write_data(0x98)
        self.write_cmd(0x3A)
        self.write_data(0x05)
        self.write_cmd(0x90)
        self.write_data(0x08, 0x08, 0x08, 0x08)
        self.write_cmd(0xBD)
        self.write_data(0x06)
        self.write_cmd(0xBC)
        self.write_data(0x00)
        self.write_cmd(0xFF)
        self.write_data(0x60, 0x01, 0x04)
        self.write_cmd(0xC3)
        self.write_data(0x13)
        self.write_cmd(0xC4)
        self.write_data(0x13)
        self.write_cmd(0xC9)
        self.write_data(0x22)
        self.write_cmd(0xBE)
        self.write_data(0x11)
        self.write_cmd(0xE1)
        self.write_data(0x10, 0x0E)
        self.write_cmd(0xDF)
        self.write_data(0x21, 0x0c, 0x02)
        self.write_cmd(0xF0)
        self.write_data(0x45, 0x09, 0x08, 0x08, 0x26, 0x2A)
        self.write_cmd(0xF1)
        self.write_data(0x43, 0x70, 0x72, 0x36, 0x37, 0x6F)
        self.write_cmd(0xF2)
        self.write_data(0x45, 0x09, 0x08, 0x08, 0x26, 0x2A)
        self.write_cmd(0xF3)
        self.write_data(0x43, 0x70, 0x72, 0x36, 0x37, 0x6F)
        self.write_cmd(0xED)
        self.write_data(0x1B, 0x0B)
        self.write_cmd(0xAE)
        self.write_data(0x77)
        self.write_cmd(0xCD)
        self.write_data(0x63)
        self.write_cmd(0x70)
        self.write_data(0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03)
        self.write_cmd(0xE8)
        self.write_data(0x34)
        self.write_cmd(0x62)
        self.write_data(0x18, 0x0D, 0x71, 0xED, 0x70, 0x70,
                        0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70)
        self.write_cmd(0x63)
        self.write_data(0x18, 0x11, 0x71, 0xF1, 0x70, 0x70,
                        0x18, 0x13, 0x71, 0xF3, 0x70, 0x70)
        self.write_cmd(0x64)
        self.write_data(0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07)
        self.write_cmd(0x66)
        self.write_data(0x3C, 0x00, 0xCD, 0x67, 0x45,
                        0x45, 0x10, 0x00, 0x00, 0x00)
        self.write_cmd(0x67)
        self.write_data(0x00, 0x3C, 0x00, 0x00, 0x00,
                        0x01, 0x54, 0x10, 0x32, 0x98)
        self.write_cmd(0x74)
        self.write_data(0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00)
        self.write_cmd(0x98)
        self.write_data(0x3e, 0x07)
        self.write_cmd(0x35)
        self.write_cmd(0x21)
        self.write_cmd(0x11)
        time.sleep(0.12)
        self.write_cmd(0x29)
        time.sleep(0.02)
        self.write_cmd(0x21)
        self.write_cmd(0x11)
        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00, 0x00, 0x00, 0xEF)
        self.write_cmd(0x2B)
        self.write_data(0x00, 0x00, 0x00, 0xEF)
        self.write_cmd(0x2C)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)


class QMI8658:
    """6-axis IMU driver for the QMI8658 sensor."""

    def __init__(self, address=0x6B, i2c_id=1, sda_pin=I2C_SDA, scl_pin=I2C_SCL):
        self._address = address
        self._bus = I2C(id=i2c_id, sda=Pin(sda_pin),
                        scl=Pin(scl_pin), freq=100_000)

        if self.WhoAmI() != 0x05:
            raise RuntimeError("QMI8658 not found on I2C bus")

        self.Read_Revision()
        self.Config_apply()

    def _read_byte(self, cmd):
        return self._bus.readfrom_mem(self._address, cmd, 1)[0]

    def _read_block(self, reg, length=1):
        return self._bus.readfrom_mem(self._address, reg, length)

    def _write_byte(self, cmd, val):
        self._bus.writeto_mem(self._address, cmd, bytes([val & 0xFF]))

    def WhoAmI(self):
        return self._read_byte(0x00)

    def Read_Revision(self):
        return self._read_byte(0x01)

    def Config_apply(self):
        self._write_byte(0x02, 0x60)
        self._write_byte(0x03, 0x23)
        self._write_byte(0x04, 0x53)
        self._write_byte(0x05, 0x00)
        self._write_byte(0x06, 0x11)
        self._write_byte(0x07, 0x00)
        self._write_byte(0x08, 0x03)

    def Read_Raw_XYZ(self):
        raw_xyz = self._read_block(0x35, 12)
        xyz = [0, 0, 0, 0, 0, 0]

        for i in range(6):
            value = (raw_xyz[(i * 2) + 1] << 8) | raw_xyz[i * 2]
            if value >= 32767:
                value -= 65536
            xyz[i] = value
        return xyz

    def Read_XYZ(self):
        raw_xyz = self.Read_Raw_XYZ()
        acc_lsb_div = 1 << 12
        gyro_lsb_div = 64.0
        xyz = [0.0] * 6

        for i in range(3):
            xyz[i] = raw_xyz[i] / acc_lsb_div
            xyz[i + 3] = raw_xyz[i + 3] / gyro_lsb_div
        return xyz


class BatteryMonitor:
    def __init__(self, adc_pin=VBAT_PIN, v_divider=2.0, reference_voltage=3.3):
        self.adc = ADC(Pin(adc_pin))
        self.v_divider = v_divider
        self.reference_voltage = reference_voltage

    def read_voltage(self):
        raw = self.adc.read_u16()
        return (raw / 65535.0) * self.reference_voltage * self.v_divider

    def read_percentage(self):
        voltage = self.read_voltage()
        min_voltage = 3.0
        max_voltage = 4.2

        if voltage <= min_voltage:
            return 0
        if voltage >= max_voltage:
            return 100

        return int((voltage - min_voltage) * 100 / (max_voltage - min_voltage))


class RP2040DisplaySystem:
    def __init__(self):
        self.lcd = LCD_1inch28()
        self.imu = QMI8658()
        self.battery = BatteryMonitor()

    def display_battery_level(self, percent=None):
        if percent is None:
            percent = self.battery.read_percentage()
        self.lcd.text("BAT {}%".format(percent), 95, 220, 0x0000)

    def _show_state_text(self, text):
        self.lcd.fill(self.lcd.white)
        self.lcd.text(text, 30, 110, 0x0000)
        self.display_battery_level()
        self.lcd.show()

    def gui_init(self):
        self._show_state_text("Init")

    def gui_wait_for_trigger(self, timer_label="00:00:01"):
        self.lcd.fill(self.lcd.white)
        self.lcd.text("WaitForTrigger", 15, 40, 0x0000)
        self.lcd.text(timer_label, 45, 110, 0x0000)
        self.display_battery_level()
        self.lcd.show()

    def gui_trigger(self):
        self._show_state_text("Trigger")

    def gui_wait_for_release(self, timer_label="00:00:00"):
        self.lcd.fill(self.lcd.white)
        self.lcd.text("WaitForRelease", 15, 40, 0x0000)
        self.lcd.text(timer_label, 45, 110, 0x0000)
        self.display_battery_level()
        self.lcd.show()

    def gui_release(self):
        self._show_state_text("Release")

    def update_screen(self, encoder_position, imu_values=None,
                      battery_voltage=None, button_pressed=False):
        if imu_values is None:
            imu_values = self.imu.Read_XYZ()
        if battery_voltage is None:
            battery_voltage = self.battery.read_voltage()

        button_text = "BTN=ON" if button_pressed else "BTN=OFF"

        self.lcd.fill(self.lcd.white)
        self.lcd.fill_rect(0, 0, 240, 40, self.lcd.red)
        self.lcd.text("RP2040-LCD-1.28", 60, 25, self.lcd.white)

        self.lcd.fill_rect(0, 40, 240, 40, self.lcd.blue)
        self.lcd.text("ENC={} {}".format(encoder_position, button_text),
                      20, 57, self.lcd.white)

        self.lcd.fill_rect(0, 80, 120, 120, 0x1805)
        self.lcd.text(
            "ACC_X={:+.2f}".format(imu_values[0]), 20, 97, self.lcd.white)
        self.lcd.text(
            "ACC_Y={:+.2f}".format(imu_values[1]), 20, 137, self.lcd.white)
        self.lcd.text(
            "ACC_Z={:+.2f}".format(imu_values[2]), 20, 177, self.lcd.white)

        self.lcd.fill_rect(120, 80, 120, 120, 0xF073)
        self.lcd.text(
            "GYR_X={:+3.2f}".format(imu_values[3]), 125, 97, self.lcd.white)
        self.lcd.text(
            "GYR_Y={:+3.2f}".format(imu_values[4]), 125, 137, self.lcd.white)
        self.lcd.text(
            "GYR_Z={:+3.2f}".format(imu_values[5]), 125, 177, self.lcd.white)

        self.lcd.fill_rect(0, 200, 240, 40, 0x180f)
        self.lcd.text("VBAT={:.2f}V".format(battery_voltage), 80, 210, self.lcd.white)
        self.lcd.text("BAT={:3d}%".format(self.battery.read_percentage()),
                      95, 225, self.lcd.white)
        self.lcd.show()


if __name__ == "__main__":
    display = RP2040DisplaySystem()
    display.lcd.set_bl_pwm(65535)

    while True:
        xyz = display.imu.Read_XYZ()
        voltage = display.battery.read_voltage()
        display.update_screen(0, xyz, voltage, False)
        time.sleep(0.1)
