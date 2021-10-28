from time import sleep
from Controller import Controller
from Client import Client
from Parser import Parser

def test():
    robotic_arm = Controller(
            sg90_pin=15,
            sg90_min_angle=-90,
            sg90_max_angle=90,
            sg90_min_pulse_width=500/1000000,
            sg90_max_pulse_width=2500/1000000,
            sg90_rotate_angle=0,
            sg90_name='Gripper',
            dcmotor_backward_pin=20,
            dcmotor_forward_pin=16,
            dcmotor_ena=21,
            dcmotor_pwm=True,
            dcmotor_clockwise=True,
            dcmotor_rotate_angle=0,
            limitsw_pin1=6,
            limitsw_pin2=7,
            limitsw_start_delay=.5,
            mg996r_base_pin=24,
            mg996r_base_min_angle=-90,
            mg996r_base_max_angle=90,
            mg996r_base_min_pulse_width=700/1000000,
            mg996r_base_max_pulse_width=2537/1000000,
            mg996r_base_rotate_angle=0,
            mg996r_base_name='Joint_1',
            mg996r_arm_pin=25,
            mg996r_arm_min_angle=90,
            mg996r_arm_max_angle=-90,
            mg996r_arm_min_pulse_width=700/1000000,
            mg996r_arm_max_pulse_width=2537/1000000,
            mg996r_arm_rotate_angle=0,
            mg996r_arm_name='Joint_2')
    try:
        print('dc clockwise 90')
        robotic_arm.control_dcmotor('clockwise', 90)
        sleep(5)

        print('joint_1 90') # forward
        robotic_arm.control_base(90)
        sleep(5)

        print('joint_1 0') # perpendicular
        robotic_arm.control_base(0)
        sleep(5)

        print('joint_2 0') # forward
        robotic_arm.control_arm(0)
        sleep(5)

        print('joint_2 90') # perpendicular
        robotic_arm.control_arm(90)
        sleep(5)

        print('gripper close')
        robotic_arm.control_gripper('close')
        sleep(5)

        print('gripper open')
        robotic_arm.control_gripper('open')
        sleep(5)

        print('dc anti-clockwise 90')
        robotic_arm.control_dcmotor('anti-clockwise', 90)
        sleep(5)

    except:
        exit(1)

def main():
    robotic_arm = Controller(
            sg90_pin=15,
            sg90_min_angle=-90,
            sg90_max_angle=90,
            sg90_min_pulse_width=500/1000000,
            sg90_max_pulse_width=2500/1000000,
            sg90_rotate_angle=0,
            sg90_name='Gripper',
            dcmotor_backward_pin=20,
            dcmotor_forward_pin=16,
            dcmotor_ena=21,
            dcmotor_pwm=True,
            dcmotor_clockwise=True,
            dcmotor_rotate_angle=0,
            limitsw_pin1=6,
            limitsw_pin2=7,
            limitsw_start_delay=.5,
            mg996r_base_pin=24,
            mg996r_base_min_angle=-90,
            mg996r_base_max_angle=90,
            mg996r_base_min_pulse_width=700/1000000,
            mg996r_base_max_pulse_width=2537/1000000,
            mg996r_base_rotate_angle=0,
            mg996r_base_name='Joint_1',
            mg996r_arm_pin=25,
            mg996r_arm_min_angle=90,
            mg996r_arm_max_angle=-90,
            mg996r_arm_min_pulse_width=700/1000000,
            mg996r_arm_max_pulse_width=2537/1000000,
            mg996r_arm_rotate_angle=0,
            mg996r_arm_name='Joint_2')
    client = Client(subs=['controlCode'])
    parser = Parser(robotic_arm)
    def on_run():
        try:
            code = client.sub("controlCode")
            if code != None:
                if type(code) == bytes:
                    code = code.decode('utf-8')
                parser.parse(code)
                client.pub("controlCode", "")
            else:
                # print("Idle")
                pass
            sleep(1)
        except KeyboardInterrupt:
            raise KeyboardInterrupt

    try:
        client.connect(on_run)
    except KeyboardInterrupt:
        print('Terminated')
        exit(1)
    except Exception as err:
        print('Unknown error: ', err)

if __name__ == '__main__':
    main()
    test()
