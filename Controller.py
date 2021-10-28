# import RPi.GPIO as GPIO          
from typing import Union
from utils import *

class Controller:
    def __init__(self,
            # pin_numbering_scheme:str='BOARD',
            sg90_pin:int=15,
            sg90_min_angle:int=-90,
            sg90_max_angle:int=90,
            sg90_min_pulse_width:float=500/1000000,
            sg90_max_pulse_width:float=2500/1000000,
            sg90_rotate_angle:int=0,
            sg90_name:str='Gripper',
            dcmotor_backward_pin:int=16,
            dcmotor_forward_pin:int=20,
            dcmotor_ena:int=21,
            dcmotor_pwm:bool=True,
            dcmotor_clockwise:bool=True,
            dcmotor_rotate_angle:int=0,
            limitsw_pin1:int=6,
            limitsw_pin2:int=7,
            limitsw_start_delay:float=.5,
            mg996r_base_pin:int=24,
            mg996r_base_min_angle:int=-90,
            mg996r_base_max_angle:int=90,
            mg996r_base_min_pulse_width:float=700/1000000,
            mg996r_base_max_pulse_width:float=2537/1000000,
            mg996r_base_rotate_angle:int=0,
            mg996r_base_name:str='Joint_1',
            mg996r_arm_pin:int=25,
            mg996r_arm_min_angle:int=-90,
            mg996r_arm_max_angle:int=90,
            mg996r_arm_min_pulse_width:float=700/1000000,
            mg996r_arm_max_pulse_width:float=2537/1000000,
            mg996r_arm_rotate_angle:int=0,
            mg996r_arm_name:str='Joint_2'):
        # self.pin_mode = pin_numbering_scheme
        self.gripper = SG90Controller(
                pin=sg90_pin, 
                min_angle=sg90_min_angle,
                max_angle=sg90_max_angle,
                min_pulse_width=sg90_min_pulse_width,
                max_pulse_width=sg90_max_pulse_width,
                rotate_angle=sg90_rotate_angle,
                name=sg90_name)
        self.dc_motor = DCMotorController(
                dc_backward_pin=dcmotor_backward_pin,
                dc_forward_pin=dcmotor_forward_pin,
                dc_ena=dcmotor_ena,
                dc_pwm=dcmotor_pwm,
                dc_clockwise=dcmotor_clockwise,
                limit_pin1=limitsw_pin1,
                limit_pin2=limitsw_pin2,
                rotate_angle=dcmotor_rotate_angle,
                start_limitsw_delay=limitsw_start_delay)
        self.base_joint = MG996rController(
                pin=mg996r_base_pin,
                min_angle=mg996r_base_min_angle,
                max_angle=mg996r_base_max_angle,
                min_pulse_width=mg996r_base_min_pulse_width,
                max_pulse_width=mg996r_base_max_pulse_width,
                rotate_angle=mg996r_base_rotate_angle,
                name=mg996r_base_name)
        self.arm_joint = MG996rController(
                pin=mg996r_arm_pin,
                min_angle=mg996r_arm_min_angle,
                max_angle=mg996r_arm_max_angle,
                min_pulse_width=mg996r_arm_min_pulse_width,
                max_pulse_width=mg996r_arm_max_pulse_width,
                rotate_angle=mg996r_arm_rotate_angle,
                name=mg996r_arm_name)

    # def __set_mode(self):
    #     if self.pin_mode == 'BOARD':
    #         GPIO.setmode(GPIO.BOARD)
    #     elif self.pin_mode == 'BCM':
    #         GPIO.setmode(GPIO.BCM)
    #     else:
    #         raise Exception('Incorrect numberring scheme')

    def control_gripper(self, cmd:Union[int, str, bool]):
        if isinstance(cmd, str):
            if cmd.upper() == 'CLOSE':
                self.gripper.set_angle(-90)
            elif cmd.upper() == 'OPEN':
                self.gripper.set_angle(0)
            else:
                return False
        elif isinstance(cmd, int):
            if cmd == 0:
                self.gripper.set_angle(-90)
            elif cmd == 1:
                self.gripper.set_angle(0)
            else:
                return False
        elif isinstance(cmd, bool):
            if not cmd:
                self.gripper.set_angle(-90)
            else:
                self.gripper.set_angle(0)
        else:
            return False
        return self.gripper.start()

    def control_dcmotor(self, direction:Union[str, int, bool], angle:int):
        # self.__set_mode()
        if isinstance(direction, str):
            if direction.upper() == 'CLOCKWISE':
                self.dc_motor.set_direction(True)
            elif direction.upper() == 'ANTICLOCKWISE' or direction.upper() == 'ANTI-CLOCKWISE':
                self.dc_motor.set_direction(False)
            else:
                return False
        elif isinstance(direction, int):
            if direction == 0:
                self.dc_motor.set_direction(False)
            elif direction == 1:
                self.dc_motor.set_direction(True)
            else:
                return False
        elif isinstance(direction, bool):
            self.dc_motor.set_direction(direction)
        else:
            return False
        if not isinstance(angle, int):
            raise Exception('DC motor rotation angle must be integer')
        else:
            if angle < 0:
                raise Exception('DC motor rotation angle must greater than 0')
            elif angle > 180:
                raise Exception('DC motor rotation angle must less than 180')
            else:
                self.dc_motor.set_angle(angle)
        return self.dc_motor.start()

    def control_base(self, angle:int):
        # negative = forward, positive = backward, 0 = perpendicular
        if not isinstance(angle, int):
            raise Exception('MG996r servo rotation angle must be integer')
        else:
            if angle < 0:
                raise Exception('MG996r(base) servo rotation angle must greater than 0')
            elif angle > 90:
                raise Exception('MG996r(base) servo rotation angle must less than 90')
            else:
                self.base_joint.set_angle(-angle) # move forward only
        return self.base_joint.start()

    def control_arm(self, angle:int):
        # negative = backward, positive = forward, 0 = perpendicular
        if not isinstance(angle, int):
            raise Exception('MG996r(arm) servo rotation angle must be integer')
        else:
            if angle < 0:
                raise Exception('MG996r(arm) servo rotation angle must greater than 0')
            elif angle > 90:
                raise Exception('MG996r(arm) servo rotation angle must less than 90')
            else:
                self.arm_joint.set_angle(angle)
        return self.arm_joint.start()
