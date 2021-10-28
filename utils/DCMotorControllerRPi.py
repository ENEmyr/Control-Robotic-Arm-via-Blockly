import RPi.GPIO as GPIO          
import threading
import ctypes
from time import sleep

class Rotator(threading.Thread):
    def __init__(self, 
            rotate_angle: int,
            in1: int=38, 
            in2: int=36, 
            ena: int=40,
            duty_cycle: int=75,
            clockwise: bool=True
            ):
        threading.Thread.__init__(self)
        self.rotate_angle = rotate_angle
        self.in1 = in1
        self.in2 = in2
        self.ena = ena
        self.clockwise = clockwise
        GPIO.setup(self.in1,GPIO.OUT)
        GPIO.setup(self.in2,GPIO.OUT)
        GPIO.setup(self.ena,GPIO.OUT)
        GPIO.output(self.in1,GPIO.LOW)
        GPIO.output(self.in2,GPIO.LOW)
        self.p = GPIO.PWM(self.ena,2000)
        self.p.start(25)
        self.p.ChangeDutyCycle(duty_cycle)

    def change_duty_cycle(self, duty_cycle: int=75):
        self.p.ChangeDutyCycle(duty_cycle)

    def change_direction(self, clockwise: bool=True):
        self.clockwise = clockwise

    def stop_rotate(self):
        GPIO.output(self.in1,GPIO.LOW)
        GPIO.output(self.in2,GPIO.LOW)

    def change_rotate_angle(self, angle:int):
        self.rotate_angle = angle

    def clean(self):
        GPIO.cleanup()

    def run(self):
        try:
            if self.clockwise:
                # clockwise
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.HIGH)
            else:
                # anti-clockwise
                GPIO.output(self.in1, GPIO.HIGH)
                GPIO.output(self.in2, GPIO.LOW)
            sleep(self.rotate_angle*(42/1000))
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
    def __init__(self, pin1: int=26, pin2: int=31):
        threading.Thread.__init__(self)
        self.pin1 = pin1
        self.pin2 = pin2
        GPIO.setup(self.pin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def clean(self):
        GPIO.cleanup()

    def run(self):
        try:
            while True:
                limit_switch_1 = GPIO.input(self.pin1)
                limit_switch_2 = GPIO.input(self.pin2)
                if limit_switch_1 == 0 or limit_switch_2 == 0:
                    if limit_switch_1 == 0:
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
            dc_in1:int = 38,
            dc_in2:int = 36,
            dc_ena:int = 40,
            dc_duty_cycle:int = 75,
            dc_clockwise:bool = True,
            limit_pin1:int = 26,
            limit_pin2:int = 31,
            rotate_angle:int = 0,
            start_limitsw_delay:float = .5
            ):
        self.rotate_angle = rotate_angle
        self.dc_in1 = dc_in1
        self.dc_in2 = dc_in2
        self.dc_ena = dc_ena
        self.dc_duty_cycle = dc_duty_cycle
        self.dc_clockwise = dc_clockwise
        self.limit_pin1 = limit_pin1
        self.limit_pin2 = limit_pin2
        self.start_limitsw_delay = start_limitsw_delay

    def set_angle(self, angle:int):
        self.rotate_angle = angle

    def set_direction(self, clockwise:bool):
        self.dc_clockwise = clockwise

    def set_duty_cycle(self, duty_cycle:int):
        self.dc_duty_cycle = duty_cycle

    def start(self, clockwise:bool = None, rotate_angle:int = None):
        dc_motor = Rotator(
                self.rotate_angle, 
                in1=self.dc_in1, 
                in2=self.dc_in2, 
                ena=self.dc_ena, 
                duty_cycle=self.dc_duty_cycle, 
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
                dc_motor.clean()
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
            dc_motor.clean()
            sleep(.5)
        dc_motor.join()
        limit_switcher.join()
        return True

def main():
    GPIO.setmode(GPIO.BOARD)
    dc_controller = DCMotorController(
            dc_in1=38,
            dc_in2=36,
            dc_ena=40,
            dc_duty_cycle=75,
            dc_clockwise=True,
            limit_pin1=26,
            limit_pin2=31,
            rotate_angle=0,
            start_limitsw_delay=.5
            )
    dc_controller.set_angle(360)
    dc_controller.set_direction(True)
    dc_controller.start()

if __name__ == "__main__":
    main()
