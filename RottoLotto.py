
import asyncio
from PokemonCommons import *
logger = logging.getLogger(__name__)

import logging
from joycontrol import logging_default as log
from joycontrol.controller_state import ControllerState, button_push
from joycontrol.protocol import controller_protocol_factory, Controller
from joycontrol.server import create_hid_server


async def rottoLotto(controller_state: ControllerState, connected=False, first=True):
    if not connected:
        await connectControl(controller_state)
    # Press A for prompt
    await button_push(controller_state, 'a')
    print("trigger Rottom")
    await asyncio.sleep(0.7)
    # A again for decision box
    await button_push(controller_state, 'a')
    print("open decision box")
    await asyncio.sleep(0.7)
    # Dowm 1 for rotto lotto
    await button_push(controller_state, 'down')
    print("highlight rotto lotto")
    await asyncio.sleep(0.7)
    # A to chose(end loto id center)
    await button_push(controller_state, 'a')
    print("chose rotto lotto")
    await asyncio.sleep(0.7)
    # A to chose(end loto id center)
    await button_push(controller_state, 'a')
    print("roll text: connected to servers")
    await asyncio.sleep(10.7)
    # A change text(end you could)
    await button_push(controller_state, 'a')
    print('roll text: well draw a number')
    await asyncio.sleep(0.7)
    # A  change text(end prices)
    await button_push(controller_state, 'a')
    print('roll text: fabulous prizes')
    await asyncio.sleep(0.7)
    # A save
    await button_push(controller_state, 'a')
    print('Trigger save')
    await asyncio.sleep(2)  # wait 5 segundos
    # A(end text progress)
    await button_push(controller_state, 'a')
    print('roll text: saved progress')
    await asyncio.sleep(0.7)
    # A(end to you)
    await button_push(controller_state, 'a')
    print('Roll text: best of luck')
    await asyncio.sleep(2)  # wait 2
    # A(...)
    await button_push(controller_state, 'a')
    print('Roll text: "..."')
    await asyncio.sleep(0.7)
    # A Number
    await button_push(controller_state, 'a')
    print('Roll text: [ID NUMER]')
    await asyncio.sleep(0.7)
    # A(ID number)
    await button_push(controller_state, 'a')
    print('Roll text: "lets see if it matchesID NUMER"')
    await asyncio.sleep(4)  # Wait 10
    # A(Congrats)
    await button_push(controller_state, 'a')
    print('roll text: "Congrats"')
    await asyncio.sleep(0.7)
    # A(name of poke)
    await button_push(controller_state, 'a')
    print('Roll text: it matches [NAME OF POKE]')
    await asyncio.sleep(0.7)
    # A(number of digits matched)
    await button_push(controller_state, 'a')
    print('Roll text: [NUMBER OF MATCHED DIGITS]')
    await asyncio.sleep(0.7)
    # A(prize)
    await button_push(controller_state, 'a')
    print('Roll text: [PRIZE]')
    await asyncio.sleep(2)
    # A(you obtained item)
    await button_push(controller_state, 'a')
    print('roll text: [OBTAIN ITEM]')
    await asyncio.sleep(0.7)
    # A(put item in bag)
    await button_push(controller_state, 'a')
    print('roll text: [PUT ITEM IN BAG]')
    await asyncio.sleep(0.7)
    # A(next attempt)
    await button_push(controller_state, 'a')
    print('roll text: "see you next attempt"')
    await asyncio.sleep(0.7)
    # A(exit texxt)
    await button_push(controller_state, 'a')
    print('[EXIT TEXT]')
    await asyncio.sleep(2)
    # A(exit texxt)
    for _ in range(10):
        await button_push(controller_state, 'b')
        await asyncio.sleep(0.3)
    print('clean text buffer')
    # CHANGE DAY
    await switchDayAndReturn(controller_state, connected=True, first=first)


async def _main(controller, capture_file=None, spi_flash=None):
    factory = controller_protocol_factory(controller, spi_flash=spi_flash)
    transport, protocol = await create_hid_server(factory, 17, 19, capture_file=capture_file)

    controller_state = protocol.get_controller_state()

    await connectControl(controller_state)

    first = True
    while True:
        await rottoLotto(controller_state, connected=True, first=first)
        first = False

    logger.info('Stopping communication...')
    await transport.close()

if __name__ == '__main__':
    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    # setup logging
    log.configure()

    parser = argparse.ArgumentParser()
    # parser.add_argument('controller', help='JOYCON_R, JOYCON_L or PRO_CONTROLLER')
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
        loop.run_until_complete(
            _main(controller, capture_file=capture_file, spi_flash=spi_flash))
