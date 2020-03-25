import argparse
import asyncio
from datetime import date
import logging
import os
from contextlib import contextmanager
from enum import Enum

from joycontrol import logging_default as log
from joycontrol.controller_state import ControllerState, button_push
from joycontrol.protocol import controller_protocol_factory, Controller
from joycontrol.server import create_hid_server


today = date.today()
current_switch_date = [int(today.year), int(today.month), int(today.day)]
YEAR = 0
MONTH = 1
DAY = 2
months_30 = {4, 6, 9, 11}


class Operation(Enum):
    GMAX = 1
    ROTOLOTTO = 2


# FINISHED
def isLeap(year: int):
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


async def switchDay_gmax(controller_state: ControllerState, connected=False):
    if not connected:
        await connectControl(controller_state)
        connected = True

    rollover_m = False
    rollover_y = False
    isLeapYear = isLeap(current_switch_date[YEAR])

    # press right to highlight day
    print("highlight day")
    await button_push(controller_state, 'right')
    await asyncio.sleep(0.5)
    # press up to add day
    print("add day")
    await button_push(controller_state, 'up')
    current_switch_date[DAY] += 1
    await asyncio.sleep(0.5)

    # if day rollback to 1 change month
    if current_switch_date[DAY] >= 29 and\
            current_switch_date[MONTH] == 2 and\
            not isLeapYear:
        rollover_m = True

    if current_switch_date[DAY] >= 30 and\
            current_switch_date[MONTH] == 2 and\
            isLeapYear:
        rollover_m = True

    if current_switch_date[DAY] >= 31 and\
            current_switch_date[MONTH] in months_30:
        rollover_m = True

    if current_switch_date[DAY] >= 32 and\
            current_switch_date[MONTH] not in months_30:
        rollover_m = True

    if rollover_m:  # go left then press up
        print("Go left to month")
        await button_push(controller_state, 'left')
        await asyncio.sleep(0.5)
        await button_push(controller_state, 'up')
        await asyncio.sleep(0.5)
        current_switch_date[DAY] = 1  # month rollover
        current_switch_date[MONTH] += 1

    if current_switch_date[MONTH] >= 13:
        rollover_y = True

    if rollover_y:  # go right twice then press up
        print("Go right to year")
        await button_push(controller_state, 'right')
        await asyncio.sleep(0.5)
        await button_push(controller_state, 'right')
        await asyncio.sleep(0.5)
        await button_push(controller_state, 'up')
        await asyncio.sleep(0.5)
        current_switch_date[MONTH] = 1
        current_switch_date[YEAR] += 1

    # press right 1+ second
    await button_push(controller_state, 'right', sec=1.5)
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'right', sec=1.2)
    await asyncio.sleep(0.5)

    # press ok
    await button_push(controller_state, 'a')
    await asyncio.sleep(1.5)
# END


async def switchDay_roto(controller_state: ControllerState, connected=False):
    if not connected:
        await connectControl(controller_state)
        connected = True

    # press right to highlight day
    print("highlight day")
    await button_push(controller_state, 'right')
    await asyncio.sleep(0.5)
    # press up to add day
    print("add day")
    await button_push(controller_state, 'up')
    await asyncio.sleep(0.5)
    # press right 1+ second
    await button_push(controller_state, 'right', sec=1.5)
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'right', sec=1.2)
    await asyncio.sleep(0.5)

    # press ok
    await button_push(controller_state, 'a')
    await asyncio.sleep(1.5)
# END


# FINISHED
async def switchDayAndReturn(controller_state: ControllerState, connected=False, first=True, operation=Operation.ROTOLOTTO):
    if not connected:
        await connectControl(controller_state)
        connected = True

    # exit game
    print("going home")
    await button_push(controller_state, 'home')
    await asyncio.sleep(1)
    # go to settings
    print("BBS")
    await button_push(controller_state, 'down', sec=1.0)
    await asyncio.sleep(0.3)
    print("Settings")
    await button_push(controller_state, 'right', sec=1.0)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.3)
    print("enter settings")
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.5)
    print("system")
    await button_push(controller_state, 'down', sec=2.0)
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
    # connect to the internet and disconnect to get current day
    if first:
        #today = date.today()
        # current_switch_date = [
        #    int(today.year), int(today.month), int(today.day)]
        current_switch_date[DAY] = 26
        current_switch_date[MONTH] = 3
        current_switch_date[YEAR] = 2020
        #print("sync with internet")
        # await button_push(controller_state, 'a')
        # await asyncio.sleep(1)
        #print("unsync from internet")
        # await button_push(controller_state, 'a')
        # await asyncio.sleep(1)
    print("Current date:")
    print(current_switch_date)
    print("date and time setting")
    await button_push(controller_state, 'down', sec=1)
    await button_push(controller_state, 'a')
    await asyncio.sleep(1)
    # switch day
    if operation == Operation.GMAX:
        await switchDay_gmax(controller_state, connected=connected)
    elif operation == Operation.ROTOLOTTO:
        await switchDay_roto(controller_state, connected=connected)
    else:
        raise KeyError(f'{operation} is not implemented yet')
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
        await connectControl(controller_state)
    # Get out
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
    # asuming you have to chose a profile
    await button_push(controller_state, 'a')
    await asyncio.sleep(17.5)  # wait for loading and gaining control back
    print("start screen")
    await button_push(controller_state, 'a')


# FINISHED
async def connectControl(controller_state: ControllerState):
    await controller_state.connect()  # asuming from sync controller
    # goto game
    await button_push(controller_state, 'home')
    print("get out of controller")
    await asyncio.sleep(2)
    await button_push(controller_state, 'home')
    print("enter game")
    await asyncio.sleep(3)
