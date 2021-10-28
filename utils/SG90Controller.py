import threading
import ctypes
from time import sleep
from gpiozero import AngularServo

class Rotator(threading.Thread):
    def __init__( self,
            pin:int=15,
            min_angle:int=-90,
            max_angle:int=90,
            min_pulse_width:float=500/1000000,
            max_pulse_width:float=2500/1000000,
            rotate_angle:int=0,
            name:str = 'SG90'):
        threading.Thread.__init__(self)
        self.rotate_angle = rotate_angle
        self.name = name
        self.sg90 = AngularServo(pin, 
                min_angle=min_angle, 
                max_angle=max_angle, 
                min_pulse_width=min_pulse_width,
                max_pulse_width=max_pulse_width)

    def change_rotate_angle(self, rotate_angle:int):
        self.rotate_angle = rotate_angle

    def run(self):
        try:
            self.sg90.angle = self.rotate_angle
            sleep(.5)
        except:
            print(f'Early stop {self.name}')
        return True

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

class SG90Controller:
    def __init__( self,
            pin:int=15,
            min_angle:int=-90,
            max_angle:int=90,
            min_pulse_width:float=500/1000000,
            max_pulse_width:float=2500/1000000,
            rotate_angle:int=0,
            name:str = 'SG90'):
        self.pin = pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_pulse_width = min_pulse_width
        self.max_pulse_width = max_pulse_width
        self.rotate_angle = rotate_angle
        self.name = name

    def set_angle(self, angle:int):
        self.rotate_angle = angle

    def start(self):
        servo = Rotator(self.pin,
                min_angle=self.min_angle,
                max_angle=self.max_angle,
                min_pulse_width=self.min_pulse_width,
                max_pulse_width=self.max_pulse_width,
                rotate_angle=self.rotate_angle,
                name= self.name)
        servo.start()
        while servo.is_alive():
            try:
                pass # Rotating
            except KeyboardInterrupt:
                # Early stop rotating
                servo.stop()
                break
        servo.join()
        return True
