import time

from encoder import Encoder
from servo_motor_driver import ServoMotorDriver
from display_board import RP2040DisplaySystem

STATE_INIT = 0
STATE_WAIT_FOR_TRIGGER = 1
STATE_TRIGGER = 2
STATE_WAIT_FOR_RELEASE = 3
STATE_RELEASE = 4


class RobotController:
    def __init__(self):
        self.encoder = Encoder(a_pin=1, b_pin=2)
        self.servo = ServoMotorDriver(pin_id=0)
        self.display = RP2040DisplaySystem()

        self.display.lcd.set_bl_pwm(65535)
        self.servo.set_angle(90)
        time.sleep_ms(200)
        self.servo.release_motor()

        self.state = STATE_INIT
        self.state_started_ms = time.ticks_ms()
        self.wait_release_seconds = 1
        self.last_release_display_seconds = None
        self.set_state(STATE_INIT)

    def _format_hhmmss(self, total_seconds):
        total_seconds = max(0, int(total_seconds))
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    def _step_wait_release_seconds(self, direction):
        value = self.wait_release_seconds
        steps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                 20, 30, 40, 50, 60,
                 90, 120, 150, 180, 210, 240, 270, 300,
                 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000,
                 1800, 3600, 5400, 7200, 9000, 10800, 12600, 14400, 16200, 18000]

        if direction > 0:
            for step in steps:
                if value < step:
                    self.wait_release_seconds = step
                    break
            else:
                self.wait_release_seconds = 10800
        else:
            for step in reversed(steps):
                if value > step:
                    self.wait_release_seconds = step
                    break
            else:
                self.wait_release_seconds = 1

    def _refresh_wait_for_release_display(self):
        elapsed_ms = time.ticks_diff(time.ticks_ms(), self.state_started_ms)
        remaining_seconds = max(0, self.wait_release_seconds - (elapsed_ms // 1000))

        if remaining_seconds != self.last_release_display_seconds:
            # for long release, retract a bit the motor after 2 seconds
            if self.wait_release_seconds - remaining_seconds == 2:
                self.servo.set_angle(130)

            # for long release, stop the motor after 3 seconds
            if self.wait_release_seconds - remaining_seconds == 3:
                self.servo.release_motor()

            self.last_release_display_seconds = remaining_seconds
            self.display.gui_wait_for_release(
                self._format_hhmmss(remaining_seconds))

    def set_state(self, new_state):
        self.state = new_state
        self.state_started_ms = time.ticks_ms()

        if new_state == STATE_INIT:
            self.display.gui_init()
        elif new_state == STATE_WAIT_FOR_TRIGGER:
            self.servo.set_angle(50)
            time.sleep_ms(200)
            self.servo.release_motor()
            self.display.gui_wait_for_trigger(
                self._format_hhmmss(self.wait_release_seconds))
        elif new_state == STATE_TRIGGER:
            self.servo.set_angle(180)
            self.display.gui_trigger()
        elif new_state == STATE_WAIT_FOR_RELEASE:
            self.last_release_display_seconds = None
            self._refresh_wait_for_release_display()
        elif new_state == STATE_RELEASE:
            self.servo.set_angle(0)
            self.display.gui_release()
            time.sleep_ms(800)
            self.servo.set_angle(50)
            time.sleep_ms(200)
            self.servo.release_motor()

    def process_events(self):
        event = self.encoder.get_event()

        if self.state == STATE_INIT:
            if event == Encoder.EVENT_BUTTON_PRESS:
                self.set_state(STATE_WAIT_FOR_TRIGGER)
            return

        if self.state == STATE_WAIT_FOR_TRIGGER:
            if event == Encoder.EVENT_ENCODER_INCR:
                self._step_wait_release_seconds(1)
                self.display.gui_wait_for_trigger(
                    self._format_hhmmss(self.wait_release_seconds))
            elif event == Encoder.EVENT_ENCODER_DECR:
                self._step_wait_release_seconds(-1)
                self.display.gui_wait_for_trigger(
                    self._format_hhmmss(self.wait_release_seconds))
            elif event == Encoder.EVENT_BUTTON_PRESS:
                self.set_state(STATE_TRIGGER)
            return

        if self.state == STATE_TRIGGER:
            self.set_state(STATE_WAIT_FOR_RELEASE)
            return

        if self.state == STATE_WAIT_FOR_RELEASE:
            self._refresh_wait_for_release_display()
            if time.ticks_diff(time.ticks_ms(), self.state_started_ms) >= (self.wait_release_seconds * 1000):
                self.set_state(STATE_RELEASE)
            return

        if self.state == STATE_RELEASE:
            self.set_state(STATE_WAIT_FOR_TRIGGER)
            return

    def run(self):
        while True:
            self.process_events()
            time.sleep_ms(1)


def main():
    controller = RobotController()
    controller.run()


if __name__ == "__main__":
    main()
