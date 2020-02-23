import argparse
import asyncio
import logging
import os
from contextlib import contextmanager

from joycontrol import logging_default as log
from joycontrol.controller_state import ControllerState, button_push
from joycontrol.protocol import controller_protocol_factory, Controller
from joycontrol.server import create_hid_server

from ShinyRaid import shinyRaid

logger = logging.getLogger(__name__)

async def gigantamaxRaid(controller_state: ControllerState,connected=False):
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
    keepLooking = True
    while keepLooking:
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
        # so far so good
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
        await asyncio.sleep(10)

    check = input("force shiny?")
    if check == "y" or check == "yes": # async def test_controller_buttons(controller_state: ControllerState):
        shinyRaid(controller_state, connected=True)

async def _main(controller, capture_file=None, spi_flash=None):
    factory = controller_protocol_factory(controller, spi_flash=spi_flash)
    transport, protocol = await create_hid_server(factory, 17, 19, capture_file=capture_file)
    controller_state = protocol.get_controller_state()

    await gigantamaxRaid(controller_state)

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
