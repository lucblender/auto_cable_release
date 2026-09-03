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

        self.state = STATE_INIT
        self.state_started_ms = time.ticks_ms()
        self.set_state(STATE_INIT)

    def set_state(self, new_state):
        self.state = new_state
        self.state_started_ms = time.ticks_ms()

        if new_state == STATE_INIT:
            self.display.gui_init()
        elif new_state == STATE_WAIT_FOR_TRIGGER:
            self.servo.set_angle(0)
            self.display.gui_wait_for_trigger()
        elif new_state == STATE_TRIGGER:
            self.servo.set_angle(180)
            self.display.gui_trigger()
        elif new_state == STATE_WAIT_FOR_RELEASE:
            self.display.gui_wait_for_release()
        elif new_state == STATE_RELEASE:
            self.servo.set_angle(0)
            self.display.gui_release()

    def process_events(self):
        event = self.encoder.get_event()

        if self.state == STATE_INIT:
            if event == Encoder.EVENT_BUTTON_PRESS:
                self.set_state(STATE_WAIT_FOR_TRIGGER)
            return

        if self.state == STATE_WAIT_FOR_TRIGGER:
            if event == Encoder.EVENT_BUTTON_PRESS:
                self.set_state(STATE_TRIGGER)
            return

        if self.state == STATE_TRIGGER:
            self.set_state(STATE_WAIT_FOR_RELEASE)
            return

        if self.state == STATE_WAIT_FOR_RELEASE:
            if time.ticks_diff(time.ticks_ms(), self.state_started_ms) >= 5000:
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
