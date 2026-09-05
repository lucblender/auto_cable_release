from machine import Pin, PWM
from time import sleep


class ServoMotorDriver:
    """Simple PWM-based servo driver for a 0-180 degree servo."""

    def __init__(self, pin_id=0, frequency=50, min_angle=0, max_angle=180,
                 min_duty=1802, max_duty=7864):
        self.pin = Pin(pin_id, Pin.OUT)
        self.pwm = PWM(self.pin)
        self.frequency = frequency
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_duty = min_duty
        self.max_duty = max_duty

        self.pwm.freq(self.frequency)
        self.angle = min_angle
        self.set_angle(self.angle)

    def deg_to_duty(self, angle):
        angle = max(self.min_angle, min(self.max_angle, angle))
        span = self.max_duty - self.min_duty
        return int((angle / (self.max_angle - self.min_angle)) * span + self.min_duty)

    def set_angle(self, angle):
        angle = max(self.min_angle, min(self.max_angle, angle))
        self.angle = angle
        self.pwm.duty_u16(self.deg_to_duty(angle))
        return self.angle

    def release_motor(self):
        self.pwm.duty_u16(0)

    def sweep(self, start=None, end=None, delay=0.5):
        if start is None:
            start = self.min_angle
        if end is None:
            end = self.max_angle

        start = max(self.min_angle, min(self.max_angle, start))
        end = max(self.min_angle, min(self.max_angle, end))

        step = 1 if end >= start else -1
        for angle in range(start, end + step, step):
            self.set_angle(angle)
            sleep(delay)

    def deinit(self):
        self.pwm.deinit()


if __name__ == "__main__":
    servo = ServoMotorDriver()
    try:
        servo.sweep(0, 180, 0.2)
        servo.sweep(180, 0, 0.2)
    finally:
        servo.deinit()
