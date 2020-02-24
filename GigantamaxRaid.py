import argparse
import asyncio
from datetime import date
import logging
import os
from contextlib import contextmanager

from joycontrol import logging_default as log
from joycontrol.controller_state import ControllerState, button_push
from joycontrol.protocol import controller_protocol_factory, Controller
from joycontrol.server import create_hid_server

# NOTE there IS a way to force shiny raids but it's not compatible with this particular rolling method

logger = logging.getLogger(__name__)

today = date.today()
current_switch_date = [int(today.year),int(today.month),int(today.day)]
YEAR = 0
MONTH = 1
DAY = 2
months_30={4,6,9,11}

# FINISHED
def isLeap(year: int):
    year = year%10000
    leap = False
    if (year % 4) == 0:  
        if (year % 100) == 0:  
            if (year % 400) == 0:  
                return True  
            else:  
                return False  
        else:  
            return True   
    return False

async def switchDay(controller_state: ControllerState, connected=False):
    # start from the internet sync option
    rollover_m = False
    rollover_y = False
    
    # go down 1(+?) second
    # press A to modify date
    # add 1 day
    # if day rollback to 1 change month
    if current_switch_date[DAY] == 29 and\
    current_switch_date[MONTH] == 2 and\
    not isLeap(current_switch_date[YEAR]):
        current_switch_date[DAY] = 1 # february rollover
        current_switch_date[MONTH] = current_switch_date[MONTH] + 1
        rollover_m = True

    elif current_switch_date[DAY] == 30 and\
    current_switch_date[MONTH] == 2 and\
    isLeap(current_switch_date[YEAR]):
        current_switch_date[DAY] = 1 # february leap rollover
        current_switch_date[MONTH] = current_switch_date[MONTH] + 1
        rollover_m = True

    elif current_switch_date[DAY] == 31 and\
    current_switch_date[MONTH] in months_30:
        current_switch_date[DAY] = 1 # 30 days rollover
        current_switch_date[MONTH] = current_switch_date[MONTH] + 1
        rollover_m = True

    elif current_switch_date[DAY] == 32 and\
    current_switch_date[MONTH] not in months_30:
        current_switch_date[DAY] = 1 # 31 days rollover
        current_switch_date[MONTH] = current_switch_date[MONTH] + 1
        rollover_m = True
    
    if current_switch_date[MONTH] == 13:
        current_switch_date[MONTH] = 1 # happy new year
        rollover_y = True

    if rollover_m:
        pass # go left then press up

    if rollover_y:
        pass # go right twice then press up
    
    # press right 1+ second
    # press ok
# END


# FINISHED
async def switchDayAndReturn(controller_state: ControllerState, connected=False, first=True):
    if not connected:
        await controller_state.connect() # asuming from sync controller

        # goto game
        print("get out of controller")
        await button_push(controller_state, 'home')
        await asyncio.sleep(1)
        print("enter game")
        await button_push(controller_state, 'home')
        await asyncio.sleep(2)

    # exit game
    print("going home")
    await button_push(controller_state, 'home')
    await asyncio.sleep(0.3)
    # go to settings  
    print("BBS")
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.3)
    print("Settings")
    await button_push(controller_state, 'right', sec=0.5)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.3)
    print("enter settings")
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.5)
    print("system")
    await button_push(controller_state, 'down', sec=1.6)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)
    print("date and time")
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)
    print("date and time setting")
    await button_push(controller_state, 'down',sec=0.5)
    await button_push(controller_state, 'a')
    await asyncio.sleep(1)
    # connect to the internet and disconnect to get current day
    if first:
        today = date.today()
        current_switch_date = [int(today.year),int(today.month),int(today.day)]
        print("sync with internet")
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.5)
        print("unsync from internet")
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.5)
    # switch day
    await switchDay(controller_state,connected=True)
    # return home
    print("return home")
    await button_push(controller_state, 'home')
    await asyncio.sleep(2)
    # return to game
    print("enter game")
    await button_push(controller_state, 'home')
    await asyncio.sleep(2)

# FINISHED
async def restartGame(controller_state: ControllerState, connected=False):
    if not connected:
        await controller_state.connect() # asuming from sync controller

        # goto game
        print("get out of controller")
        await button_push(controller_state, 'home')
        await asyncio.sleep(1)
        print("enter game")
        await button_push(controller_state, 'home')
        await asyncio.sleep(2)
    
    #Get out
    print("going home")
    await button_push(controller_state, 'home')
    await asyncio.sleep(1)
    print("Close game")
    await button_push(controller_state, 'x')
    await asyncio.sleep(0.8)
    print("confirm close")
    await button_push(controller_state, 'a')
    await asyncio.sleep(3)
    print("open again")
    await button_push(controller_state, 'a')
    await asyncio.sleep(1)
    print("choose profile")
    await button_push(controller_state, 'a') # asuming you have to chose a profile
    await asyncio.sleep(17.5) # wait for loading and gaining control back
    print("start screen")
    await button_push(controller_state, 'a')

# FINISHED
async def purpleBeam(controller_state: ControllerState,connected=False):
    if not connected:
        await controller_state.connect() # asuming from sync controller

        # goto game
        print("get out of controller")
        await button_push(controller_state, 'home')
        await asyncio.sleep(1)
        print("enter game")
        await button_push(controller_state, 'home')
        await asyncio.sleep(2)


    # asuming in front of den
    # safety save
    print("pause menu")
    await button_push(controller_state, 'x')
    await asyncio.sleep(1)
    print("save")
    await button_push(controller_state, 'r')
    await asyncio.sleep(2)
    print("confirm save")
    await button_push(controller_state, 'a')
    await asyncio.sleep(4)

    # check for gigantamax pkmn in loop
    while True:
        print("trigger wishing piece")
        await button_push(controller_state, 'a')
        await asyncio.sleep(1)
        print("confirm")
        await button_push(controller_state, 'a')
        await asyncio.sleep(1)
        print("confirm save")
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.8)
        print("exit game")
        await button_push(controller_state, 'home')
        check = input("Was it purple? ")
        if check == "y" or check == "yes":
            break
        print("restart game")
        await restartGame(controller_state,connected=True)
        await asyncio.sleep(10)

    first=True
    while True:
        # enter den check pkmn
        print("enter den")
        await button_push(controller_state, 'a')
        check = input("Was it gigantamax? ")
        if check == "y" or check == "yes":
            break
        print("invite others")
        await button_push(controller_state, 'a')
        await asyncio.sleep(1.5)
        print("switch day and return")
        await switchDayAndReturn(controller_state, connected=True,first=first)
        first=False
        print("exit raid")
        await button_push(controller_state, 'b')
        await asyncio.sleep(1.5)
        print("confirm exit")
        await button_push(controller_state, 'a')
        await asyncio.sleep(4)

async def _main(controller, capture_file=None, spi_flash=None):
    factory = controller_protocol_factory(controller, spi_flash=spi_flash)
    transport, protocol = await create_hid_server(factory, 17, 19, capture_file=capture_file)
    controller_state = protocol.get_controller_state()

    await purpleBeam(controller_state)

    logger.info('Stopping communication...')
    await transport.close()

if __name__ == '__main__':
    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    # setup logging
    log.configure()

    parser = argparse.ArgumentParser()
    #parser.add_argument('controller', help='JOYCON_R, JOYCON_L or PRO_CONTROLLER')
    parser.add_argument('-l', '--log')
    parser.add_argument('--spi_flash')
    args = parser.parse_args()

    """
    if args.controller == 'JOYCON_R':
        controller = Controller.JOYCON_R
    elif args.controller == 'JOYCON_L':
        controller = Controller.JOYCON_L
    elif args.controller == 'PRO_CONTROLLER':
        controller = Controller.PRO_CONTROLLER
    else:
        raise ValueError(f'Unknown controller "{args.controller}".')
    """
    controller = Controller.PRO_CONTROLLER

    spi_flash = None
    if args.spi_flash:
        with open(args.spi_flash, 'rb') as spi_flash_file:
            spi_flash = spi_flash_file.read()

    # creates file if arg is given
    @contextmanager
    def get_output(path=None):
        """
        Opens file if path is given
        """
        if path is not None:
            file = open(path, 'wb')
            yield file
            file.close()
        else:
            yield None

    with get_output(args.log) as capture_file:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_main(controller, capture_file=capture_file, spi_flash=spi_flash))
