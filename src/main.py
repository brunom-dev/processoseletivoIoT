import machine
import time

print("Teste")

class IndustrialController:
    """
    Implementa uma Máquina de Estados Finita (FSM) para controle de um equipamento.
    Utiliza temporização não-bloqueante para garantir responsividade contínua do hardware.
    """

    def __init__(self):
        self.led_run = machine.Pin(18, machine.Pin.OUT)  # LED Verde
        self.led_idle = machine.Pin(19, machine.Pin.OUT)  # LED Vermelho
        self.btn = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

        self.STATE_IDLE = 0
        self.STATE_RUNNING = 1
        self.STATE_COOLDOWN = 2

        self.current_state = self.STATE_IDLE
        self.last_btn_state = 1
        self.last_debounce_time = 0
        self.state_start_time = 0
        self.cooldown_toggle_time = 0
        self.cooldown_led_state = 0

        self.DEBOUNCE_DELAY = 50
        self.RUNNING_DURATION = 5000
        self.COOLDOWN_DURATION = 3000
        self.BLINK_INTERVAL = 250

        self.set_state(self.STATE_IDLE)

    def set_state(self, new_state):
        """Transita o sistema para um novo estado e reinicia os temporizadores."""
        self.current_state = new_state
        self.state_start_time = time.ticks_ms()

        if new_state == self.STATE_IDLE:
            print("[ESTADO] IDLE (Aguardando)")
            self.led_run.value(0)
            self.led_idle.value(1)

        elif new_state == self.STATE_RUNNING:
            print("[ESTADO] RUNNING (Operando)")
            self.led_run.value(1)
            self.led_idle.value(0)

        elif new_state == self.STATE_COOLDOWN:
            print("[ESTADO] COLDDOWN (Resfriamento)")
            self.cooldown_toggle_time = time.ticks_ms()

    def check_button(self):
        """Verifica o botão utilizando debounce não-bloqueante."""
        current_time = time.ticks_ms()
        btn_reading = self.btn.value()

        # botão pressionado
        if btn_reading == 0 and self.last_btn_state == 1:
            if time.ticks_diff(current_time, self.last_debounce_time) > self.DEBOUNCE_DELAY:
                self.last_btn_state = 0
                self.last_debounce_time = current_time
                return True  # Botão validado como clicado

        # botão solto
        elif btn_reading == 1 and self.last_btn_state == 0:
            if time.ticks_diff(current_time, self.last_debounce_time) > self.DEBOUNCE_DELAY:
                self.last_btn_state = 1
                self.last_debounce_time = current_time

        return False

    def update(self):
        """Processa a lógica de transição de estados."""
        current_time = time.ticks_ms()
        button_pressed = self.check_button()

        if self.current_state == self.STATE_IDLE:
            if button_pressed:
                self.set_state(self.STATE_RUNNING)

        elif self.current_state == self.STATE_RUNNING:
            if time.ticks_diff(current_time, self.state_start_time) >= self.RUNNING_DURATION:
                self.set_state(self.STATE_COOLDOWN)

        elif self.current_state == self.STATE_COOLDOWN:
            if time.ticks_diff(current_time, self.cooldown_toggle_time) >= self.BLINK_INTERVAL:
                self.cooldown_toggle_time = current_time
                self.cooldown_led_state = not self.cooldown_led_state
                self.led_run.value(self.cooldown_led_state)
                self.led_idle.value(not self.cooldown_led_state)

            if time.ticks_diff(current_time, self.state_start_time) >= self.COOLDOWN_DURATION:
                self.set_state(self.STATE_IDLE)


if __name__ == '__main__':
    controller = IndustrialController()

    while True:
        controller.update()
        time.sleep_ms(10)
