import antolib
import time
from configs import BrokerConfig as config

class Client:
    def __init__(self,
        subs = [],
        username=config.Username,
        key=config.Key,
        thing=config.Thing,
        destructor=lambda: print('\nStop')
        ):
        # subs is a dictionary pair between key and channel name to subscribe
        self.anto = antolib.Anto(
            user=username,
            key=key,
            thing=thing
        )
        self.__destructor = destructor
        self.subs_val = {}
        if len(subs) != 0:
            for ch in subs: 
                self.subs_val[ch] = None

    def __on_data(self, channel, msg):
        if msg:
            self.subs_val[str(channel)] = msg
        else:
            self.subs_val[str(channel)] = None


    def __connected_callbacks(self):
        if len(self.subs_val.keys()) != 0:
            for ch in self.subs_val:
                self.anto.sub(ch)

    def sub(self, channel):
        if channel in self.subs_val.keys():
            return self.subs_val[channel]
        else:
            return None

    def pub(self, channel, msg):
        self.anto.pub(channel=channel, msg=msg)

    def connect(self, fn):
        self.anto.mqtt.onConnected(self.__connected_callbacks)
        self.anto.mqtt.onData(self.__on_data)
        self.anto.mqtt.connect()
        self.__loop(fn)
        try:
            self.anto.mqtt.onConnected(self.__connected_callbacks)
            self.anto.mqtt.onData(self.__on_data)
            self.anto.mqtt.connect()
            self.__loop(fn)
        except KeyboardInterrupt:
            self.__destructor()
        except:
            pass

    def __loop(self, fn):
        self.anto.loop(fn)

def main():
    device = Client(subs=["controlCode"])
    def on_run():
        try:
            code = device.sub("controlCode")
            if code != None:
                print(str(code))
            else:
                print("Nothing")
            time.sleep(1)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
    device.connect(on_run)

if __name__ == "__main__":
    main()
