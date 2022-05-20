import asyncio
import dataclasses

import imgui

import sdk.sdk as sdk
from sdk.utils import Vec3, calculate_circle
from OpenGL.GL import *
import math
from sdk.utils import Vec2, Vec3, w2s, benchmark
from async_lru import alru_cache

from utils.logger import Logger


class Drawing:

    @classmethod
    def line(cls, x1, y1, x2, y2, width, color):
        glLineWidth(width)
        glBegin(GL_LINES)
        glColor4f(*color)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()

    @classmethod
    def rect(cls, x1, y1, x2, y2, width, color):
        glLineWidth(width)
        glBegin(GL_POLYGON)
        glColor4f(*color)
        glVertex2f(x1, y1)
        glVertex2f(x2, y1)
        glVertex2f(x2, y2)
        glVertex2f(x1, y2)
        glEnd()

    @classmethod
    async def draw_circle_at(cls, world_pos: Vec3, radius, color, thickness=2, points=100):
        render = await sdk.Sdk.game.render()

        position = w2s(world_pos, render.view_proj_matrix)

        if position and Drawing.is_on_screen(position, 0, 0, render.width, render.height):

            points = calculate_circle(world_pos, render.view_proj_matrix, radius, points)

            if points:
                glLineWidth(thickness)
                glBegin(GL_LINE_STRIP)
                glColor4f(*color)

                for line in points:
                    glVertex2f(line.x, line.y)
                glEnd()

    @classmethod
    async def draw_text_at(cls, world_pos: Vec3, color, text):

        render = await sdk.Sdk.game.render()

        position = w2s(world_pos, render.view_proj_matrix)
        if position:
            if Drawing.is_on_screen(position, 0, 0, render.width, render.height):
                e = imgui.get_overlay_draw_list()
                e.add_text(position.x, position.y, color, text)

    @classmethod
    def draw_text(cls, pos: Vec2, color, text):
        if pos:
            e = imgui.get_overlay_draw_list()
            e.add_text(pos.x, pos.y, color, text)

    @classmethod
    def is_on_screen(cls, screen_pos: Vec2, offset_x, offset_y, width, height):
        return -offset_x < screen_pos.x < (
                width + offset_x) and -offset_y < screen_pos.y < (
                       height + offset_y)
