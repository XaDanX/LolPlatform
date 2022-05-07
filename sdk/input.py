import asyncio

import keyboard, mouse
from ctypes import *


class Controller:

    @classmethod
    async def press_key(cls, key):
        keyboard.press(key)
        await asyncio.sleep(0.008)
        keyboard.release(key)

    @classmethod
    async def click_at(cls, x, y):
        mouse.move(x, y)

    @classmethod
    async def click_back(cls, x, y):
        x_b, y_b = mouse.get_position()
        mouse.move(x, y)
        mouse.press(mouse.RIGHT)
        await asyncio.sleep(0.001)
        mouse.release(mouse.RIGHT)
        await asyncio.sleep(0.001)
        mouse.move(x_b, y_b)

    @classmethod
    def mouse_input_lock(cls, lock):
        _ = windll.user32.BlockInput(lock)

