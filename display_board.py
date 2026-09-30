from machine import Pin, I2C, SPI, PWM, ADC
import framebuf
import time
import gc
from array import array
from micropython import const
import writer


I2C_SDA = 6
I2C_SCL = 7

DC = 8
CS = 9
SCK = 10
MOSI = 11
RST = 12
BL = 25
VBAT_PIN = 29

LX_LOGO = const("helixbyte_r5g6b5.bin")


def rgb888_to_rgb565(R: int, G: int, B: int):  # Convert RGB888 to RGB565
    return const((((G & 0b00011100) << 3) + ((B & 0b11111000) >> 3) << 8) + (R & 0b11111000)+((G & 0b11100000) >> 5))


def pict_to_fbuff(path, x, y):
    with open(path, 'rb') as f:
        data = bytearray(f.read())
    return framebuf.FrameBuffer(data, x, y, framebuf.RGB565)

class LCD_1inch28(framebuf.FrameBuffer):
    def __init__(self, cs_pin=CS, dc_pin=DC, rst_pin=RST, sck_pin=SCK,
                 mosi_pin=MOSI, bl_pin=BL, spi_id=1, version=None):
        self.width = 240
        self.height = 240

        self.blue = const(0x07E0)
        self.green = const(0x001f)
        self.red = const(0xf800)
        self.white = const(0xffff)
        self.black = const(0x0000)
        self.grey = rgb888_to_rgb565(85, 85, 85)
        self.light_grey = rgb888_to_rgb565(120, 120, 120)

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

        self.display_lxb_logo(version)

        gc.collect()
        import font.freesans20 as freesans20
        import font.font6 as font6
        self.font_writer_freesans20 = writer.Writer(self, freesans20)
        self.font_writer_font6 = writer.Writer(self, font6)
        gc.collect()



    def display_lxb_logo(self, version=None):
        # lxb_fbuf = zlib_pict_to_fbuff("helixbyte.z",89,120)
        gc.collect()


        width = 100
        heigth = 74
        lxb_fbuf = pict_to_fbuff(LX_LOGO, heigth, width)

        self.blit(lxb_fbuf, 120-(heigth//2), 120-(width//2))
        self.show()
        time.sleep(1.5)
        if version is not None:
            txt_len = 54  # can't use stinglen since we use default font to not use memory cause we loaded lxb logo
            self.text(version, 120-(txt_len//2), 200, self.grey)
            self.show()

        time.sleep(1)
        gc.collect()

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
    def __init__(self, adc_pin=VBAT_PIN, charger_pin=16, usb_vsys_pin=17,
                 v_divider=2.0, reference_voltage=3.3):
        self.adc = ADC(Pin(adc_pin))
        self.charger_state_pin = Pin(charger_pin, Pin.IN, Pin.PULL_UP)
        self.usb_vsys_pin = Pin(usb_vsys_pin, Pin.IN, Pin.PULL_DOWN)
        self.v_divider = v_divider
        self.reference_voltage = reference_voltage
        self._adc_samples = 8
        self._charge_step_interval_ms = 60000
        self._display_percentage = None
        self._last_charge_ramp_ms = time.ticks_ms()
        self._was_charging = False

    def _voltage_to_percentage(self, voltage):
        min_voltage = 3.0
        max_voltage = 4.2

        if voltage <= min_voltage:
            return 0
        if voltage >= max_voltage:
            return 100
        return int((voltage - min_voltage) * 100 / (max_voltage - min_voltage))

    def read_voltage(self):
        total = 0
        for _ in range(self._adc_samples):
            total += self.adc.read_u16()
        raw = total / self._adc_samples
        return (raw / 65535.0) * self.reference_voltage * self.v_divider

    def read_percentage(self):
        measured_percent = self._voltage_to_percentage(self.read_voltage())
        usb_plugged = bool(self.read_usb_plugged())
        charging_active = usb_plugged and (not bool(self.read_charging_state()))

        if self._display_percentage is None:
            self._display_percentage = measured_percent

        if charging_active:
            target_percent = min(99, measured_percent)
            now_ms = time.ticks_ms()

            if not self._was_charging:
                self._last_charge_ramp_ms = now_ms

            if target_percent > self._display_percentage:
                elapsed_ms = time.ticks_diff(now_ms, self._last_charge_ramp_ms)
                if elapsed_ms >= self._charge_step_interval_ms:
                    step_count = elapsed_ms // self._charge_step_interval_ms
                    increase = min(step_count, target_percent - self._display_percentage)
                    self._display_percentage += increase
                    self._last_charge_ramp_ms = time.ticks_add(
                        self._last_charge_ramp_ms,
                        increase * self._charge_step_interval_ms,
                    )
        else:
            # Outside active charging, displayed SOC never moves upward.
            if measured_percent < self._display_percentage:
                self._display_percentage = measured_percent
            self._last_charge_ramp_ms = time.ticks_ms()

        self._was_charging = charging_active
        return self._display_percentage

    def read_charging_state(self):
        return 1 if self.charger_state_pin.value() else 0

    def read_usb_plugged(self):
        return 1 if self.usb_vsys_pin.value() else 0


class RP2040DisplaySystem:
    def __init__(self, version=None):
        self.lcd = LCD_1inch28(version = version)
        self.imu = QMI8658()
        self.battery = BatteryMonitor()

        self.lcd_timer_padding_x = None

    def display_battery_level(self, percent=None, charging_flag=None,
                              usb_plugged=None):
        if percent is None:
            percent = self.battery.read_percentage()
        if charging_flag is None:
            charging_flag = self.battery.read_charging_state()
        if usb_plugged is None:
            usb_plugged = self.battery.read_usb_plugged()
        charging_active = bool(usb_plugged) and (not bool(charging_flag))

        battery_x = 90
        battery_y = 206
        battery_w = 50
        battery_h = 24
        terminal_w = 5
        inner_w = battery_w - 4
        inner_h = battery_h - 4

        if charging_active:
            shown_percent = min(percent, 99)
            fill_ratio = max(0.0, min(1.0, shown_percent / 100.0))
            fill_color = self.lcd.green
        elif usb_plugged:
            shown_percent = max(0, min(100, percent))
            fill_ratio = max(0.0, min(1.0, shown_percent / 100.0))
            fill_color = self.lcd.green
        else:
            shown_percent = max(0, min(100, percent))
            fill_ratio = max(0.0, min(1.0, shown_percent / 100.0))
            fill_color = self.lcd.grey

        fill_w = int(inner_w * fill_ratio)

        self.lcd.rect(battery_x, battery_y, battery_w, battery_h, self.lcd.white)
        self.lcd.rect(battery_x + battery_w, battery_y + 7,
                      terminal_w, battery_h - 14, self.lcd.white)
        self.lcd.vline(battery_x + battery_w - 1, battery_y + 8,
                       battery_h - 16, self.lcd.black)
        self.lcd.vline(battery_x + battery_w , battery_y + 8,
                       battery_h - 16, self.lcd.black)
        self.lcd.fill_rect(battery_x + 2, battery_y + 2,
                           inner_w, inner_h, self.lcd.black)
        if fill_w > 0:
            self.lcd.fill_rect(battery_x + 2, battery_y + 2,
                               fill_w, inner_h, fill_color)

        if charging_active:
            bolt_x = battery_x + 38
            bolt_y = battery_y + 3
            self.lcd.poly(bolt_x, bolt_y, array(
                "h", [7, 0, 3, 7, 8, 7, 2, 16, 6, 9, 1, 9]), self.lcd.white, True)

        shown_text = str(shown_percent)
        text_x = 98 if shown_percent >= 100 else 106
        self.lcd.font_writer_freesans20.text(shown_text, text_x, 208,
                                             self.lcd.white)

    def _show_state_text(self, text):
        self.lcd.fill(self.lcd.black)
        self.lcd.font_writer_freesans20.text(text, 30, 110, self.lcd.white)
        self.display_battery_level()
        self.lcd.show()

    def gui_init(self):
        self.lcd.fill(self.lcd.black)
        txt = "Place the Cable Release"
        text_width = self.lcd.font_writer_freesans20.stringlen(txt)
        text_x = (self.lcd.width - text_width) // 2
        self.lcd.font_writer_freesans20.text(txt, text_x, 110, self.lcd.white)
        self.display_battery_level()
        self.lcd.show()

    def gui_wait_for_trigger(self, timer_label="00:00:01"):
        self.lcd.fill(self.lcd.black)

        if self.lcd_timer_padding_x is None:
            text_width = self.lcd.font_writer_freesans20.stringlen(timer_label)
            self.lcd_timer_padding_x = (self.lcd.width - text_width) // 2

        txt = "Select Trigger Time"
        text_width = self.lcd.font_writer_freesans20.stringlen(txt)
        text_x = (self.lcd.width - text_width) // 2
        self.lcd.font_writer_freesans20.text(txt, text_x, 40, self.lcd.white)
        self.lcd.font_writer_freesans20.text(timer_label, self.lcd_timer_padding_x, 110, self.lcd.white)
        self.display_battery_level()
        self.lcd.show()

    def gui_trigger(self):
        pass

    def gui_wait_for_release(self, timer_label="00:00:00"):
        self.lcd.fill(self.lcd.black)

        if self.lcd_timer_padding_x is None:
            text_width = self.lcd.font_writer_freesans20.stringlen(timer_label)
            self.lcd_timer_padding_x = (self.lcd.width - text_width) // 2

        txt = "Wait For Release"
        text_width = self.lcd.font_writer_freesans20.stringlen(txt)
        text_x = (self.lcd.width - text_width) // 2
        self.lcd.font_writer_freesans20.text(txt, text_x, 40, self.lcd.white)
        self.lcd.font_writer_freesans20.text(timer_label, self.lcd_timer_padding_x, 110, self.lcd.white)
        self.display_battery_level()
        self.lcd.show()

    def gui_release(self):
        pass

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
        battery_percent = self.battery.read_percentage()
        charging_flag = self.battery.read_charging_state()
        usb_plugged = self.battery.read_usb_plugged()
        self.lcd.text("BAT={:3d}%, {}, {}".format(battery_percent,
                               charging_flag,
                               usb_plugged),
              50, 225, self.lcd.white)
        self.lcd.show()


if __name__ == "__main__":
    display = RP2040DisplaySystem()
    display.lcd.set_bl_pwm(65535)

    while True:
        xyz = display.imu.Read_XYZ()
        voltage = display.battery.read_voltage()
        display.update_screen(0, xyz, voltage, False)
        time.sleep(0.1)
