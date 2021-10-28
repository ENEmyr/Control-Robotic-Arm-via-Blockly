import threading
import ctypes
from gpiozero import Motor, InputDevice
from time import sleep

class Rotator(threading.Thread):
    def __init__(self, 
            rotate_angle: int,
            backward_pin: int=16, 
            forward_pin: int=20, 
            ena: int=21,
            pwm: bool=True,
            clockwise: bool=True
            ):
        threading.Thread.__init__(self)
        self.rotate_angle = rotate_angle
        self.backward_pin = backward_pin
        self.forward_pin = forward_pin
        self.ena = ena
        self.pwm = pwm
        self.clockwise = clockwise
        self.dc_motor = Motor(self.forward_pin, self.backward_pin, self.ena, self.pwm)

    def change_direction(self, clockwise: bool=True):
        self.clockwise = clockwise

    def stop_rotate(self):
        self.dc_motor.stop()

    def change_rotate_angle(self, angle:int):
        self.rotate_angle = angle

    def run(self):
        try:
            if self.clockwise:
                # clockwise
                self.dc_motor.forward()
            else:
                # anti-clockwise
                self.dc_motor.backward()
            sleep(self.rotate_angle*(30/1000))
        except:
            print("Early stop DC motor")

    def __get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop(self):
        thread_id = self.__get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)

class Limitor(threading.Thread):
    def __init__(self, pin1: int=6, pin2: int=7):
        threading.Thread.__init__(self)
        self.pin1 = pin1
        self.pin2 = pin2
        self.limit_switch_1 = InputDevice(self.pin1, pull_up=True)
        self.limit_switch_2 = InputDevice(self.pin2, pull_up=True)

    def run(self):
        try:
            while True:
                if self.limit_switch_1.value == 1 or self.limit_switch_2.value == 1:
                    if self.limit_switch_1.value == 1:
                        print(f'Limit switcher 1({self.pin1}) HIT')
                    else:
                        print(f'Limit switcher 2({self.pin2}) HIT')
                    break
                sleep(.2)
        except:
            print("Early stop limit switcher")

    def __get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop(self):
        thread_id = self.__get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)

class DCMotorController:
    def __init__(self, 
            dc_backward_pin:int = 16,
            dc_forward_pin:int = 20,
            dc_ena:int = 21,
            dc_pwm:bool = True,
            dc_clockwise:bool = True,
            limit_pin1:int = 6,
            limit_pin2:int = 7,
            rotate_angle:int = 0,
            start_limitsw_delay:float = .5
            ):
        self.rotate_angle = rotate_angle
        self.dc_backward_pin = dc_backward_pin
        self.dc_forward_pin = dc_forward_pin
        self.dc_ena = dc_ena
        self.dc_pwm = dc_pwm
        self.dc_clockwise = dc_clockwise
        self.limit_pin1 = limit_pin1
        self.limit_pin2 = limit_pin2
        self.start_limitsw_delay = start_limitsw_delay

    def set_angle(self, angle:int):
        self.rotate_angle = angle

    def set_direction(self, clockwise:bool):
        self.dc_clockwise = clockwise

    def start(self, clockwise:bool = None, rotate_angle:int = None):
        dc_motor = Rotator(
                self.rotate_angle, 
                backward_pin=self.dc_backward_pin, 
                forward_pin=self.dc_forward_pin, 
                ena=self.dc_ena, 
                pwm=self.dc_pwm, 
                clockwise=self.dc_clockwise)
        limit_switcher = Limitor(self.limit_pin1, self.limit_pin2)
        rotate_angle = self.rotate_angle if rotate_angle == None else rotate_angle
        clockwise = self.dc_clockwise if clockwise == None else clockwise
        dc_motor.change_rotate_angle(rotate_angle)
        dc_motor.change_direction(clockwise)
        dc_motor.start()
        sleep(self.start_limitsw_delay)
        limit_switcher.start()
        while dc_motor.is_alive() and limit_switcher.is_alive():
            try:
                pass # Rotating
            except KeyboardInterrupt:
                # Early stop rotating
                dc_motor.stop()
                limit_switcher.stop()
                sleep(.5)
                break
        else:
            # Stop rotating
            if not dc_motor.is_alive():
                # Stop limit switcher because dc motor reach the desire angle
                limit_switcher.stop()
            else:
                # Stop dc motor because limit switcher got hit
                dc_motor.stop_rotate()
                dc_motor.stop()
            sleep(.5)
        dc_motor.join()
        limit_switcher.join()
        return True
