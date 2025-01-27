import time
import logging
import nova
import constants as constant
from classes.osc import VRChatOSC

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    osc = VRChatOSC(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)
    while True:
        try:
            print("Program Starting...")
            nova.run_code()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            osc.send_message(f"System Error: {e}")
            osc.set_typing_indicator(True)
            time.sleep(5)
            pass


if __name__ == '__main__':
    main()
