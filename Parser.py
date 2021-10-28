from Controller import Controller

class Parser:
    def __init__(self, controller:Controller):
        self.controller = controller
        self.err_tokens = [
                'ERR_VALUE_MISMATCH_ROTATE_BASE', 'ERR_INVALID_RANGE_ROTATION_BASE',
                'ERR_VALUE_MISMATCH_UPPER_ARM', 'ERR_INVALID_RANGE_UPPER_ARM',
                'ERR_VALUE_MISMATCH_LOWER_ARM', 'ERR_INVALID_RANGE_LOWER_ARM'
                ]
        self.tokens = [
                'START', 'END',
                'LEFT', 'RIGHT', 'UP', 'DOWN',
                'ROTATE_BASE', 'ROTATE_UPPER_ARM', 'ROTATE_LOWER_ARM', 'COMMAND_GRIPPER',
                'OPEN_GRIPPER', 'CLOSE_GRIPPER',
                *self.err_tokens 
                ]

    def parse(self, sourcecode:str) -> None:
        cmds = sourcecode.split(';')
        cmds = list(filter(lambda cmd: cmd != '', cmds))
        # if not all(map(lambda c: c in self.tokens, cmds)):
        #     raise Exception('Invalid token')
        for cmd in cmds:
            if cmd == 'END':
                break
            self.__translate(cmd)

    def __translate(self, cmd:str):
        if cmd.startswith('START'):
            return
        elif cmd.startswith('ROTATE_BASE'):
            args = cmd.split('(')[1].split(',')
            args[-1] = args[-1].replace(')', '')
            args[0] = 'CLOCKWISE' if args[0] == 'RIGHT' else 'ANTICLOCKWISE'
            args[1] = int(args[1])
            self.controller.control_dcmotor(args[0], args[1])
        elif cmd.startswith('ROTATE_UPPER_ARM'):
            arg = 90 - int(cmd.split('(')[1].replace(')', ''))
            self.controller.control_arm(arg)
        elif cmd.startswith('ROTATE_LOWER_ARM'):
            arg = int(cmd.split('(')[1].replace(')', ''))
            self.controller.control_base(arg)
        elif cmd.startswith('COMMAND_GRIPPER'):
            arg = cmd.split('(')[1].replace(')', '')
            arg = 'OPEN' if arg == 'OPEN_GRIPPER' else 'CLOSE'
            self.controller.control_gripper(arg)
        else:
            raise Exception('Invalid token')
