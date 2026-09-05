from collections import deque
from machine import Pin
import time


class Encoder:
    """Quadrature encoder with queue-based events."""

    EVENT_ENCODER_INCR = "encoder_incr"
    EVENT_ENCODER_DECR = "encoder_decr"
    EVENT_BUTTON_PRESS = "button_press"
    EVENT_BUTTON_RELEASE = "button_released"

    TRANSITIONS = {
        (0b00, 0b01): 1,
        (0b01, 0b11): 1,
        (0b11, 0b10): 1,
        (0b10, 0b00): 1,
        (0b00, 0b10): -1,
        (0b10, 0b11): -1,
        (0b11, 0b01): -1,
        (0b01, 0b00): -1,
    }

    def __init__(self, a_pin=1, b_pin=2, button_pin=3, debounce_us=1000,
                 queue_size=20):
        self.a = Pin(a_pin, Pin.IN, Pin.PULL_UP)
        self.b = Pin(b_pin, Pin.IN, Pin.PULL_UP)
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

        self.position = 0
        self.last_state = (self.a.value() << 1) | self.b.value()
        self.last_time = time.ticks_us()
        self.step = 0
        self.debounce_us = debounce_us
        self.button_pressed = False
        self.events = deque((),queue_size)

        self.a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                   handler=self._irq_handler)
        self.b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                   handler=self._irq_handler)
        self.button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
                        handler=self._button_irq_handler)


    def _irq_handler(self, pin):
        now = time.ticks_us()

        if time.ticks_diff(now, self.last_time) < self.debounce_us:
            return

        state = (self.a.value() << 1) | self.b.value()
        if state == self.last_state:
            return

        transition = self.TRANSITIONS.get((self.last_state, state), 0)

        if transition:
            self.step += transition
            if self.step >= 4:
                self.position -= 1
                self.step = 0
                self.events.append(self.EVENT_ENCODER_DECR)
            elif self.step <= -4:
                self.position += 1
                self.step = 0
                self.events.append(self.EVENT_ENCODER_INCR)
        else:
            self.step = 0

        self.last_state = state
        self.last_time = now

    def _button_irq_handler(self, pin):
        pressed = self.button.value() == 0
        if pressed and not self.button_pressed:
            self.events.append(self.EVENT_BUTTON_PRESS)
        elif not pressed and self.button_pressed:
            self.events.append(self.EVENT_BUTTON_RELEASE)
        self.button_pressed = pressed

    def is_button_pressed(self):
        return self.button.value() == 0

    def get_event(self):
        if len(self.events) == 0:
            return None
        return self.events.popleft()

    def reset(self):
        self.position = 0
        self.step = 0
        self.events.clear()
        self.last_state = (self.a.value() << 1) | self.b.value()
        self.last_time = time.ticks_us()


if __name__ == "__main__":
    encoder = Encoder()
    while True:
        event = encoder.get_event()
        if event is not None:
            print(event)
        time.sleep_ms(10)
