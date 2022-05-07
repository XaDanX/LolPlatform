import dataclasses

import imgui

import sdk.sdk as sdk
from sdk.utils import Vec3
from OpenGL.GL import *
import math
from sdk.utils import Vec2, Vec3, w2s, benchmark
from async_lru import alru_cache


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
    async def draw_circle_at(cls, world_pos: Vec3, radius, color, thickness=2, points=100):
        render = await sdk.Sdk.game.render()
        lines = []
        step = math.pi * 2 / points
        theta = 0

        while theta <= math.pi * 2:
            world_space = Vec3(world_pos.x + radius * math.cos(theta), world_pos.y,
                               world_pos.z + radius * math.sin(theta))
            screen_space = w2s(world_space, render.view_proj_matrix)

            if screen_space:
                lines.append(Vec2(screen_space.x, screen_space.y))

            theta += step

        if lines:
            glLineWidth(thickness)
            glBegin(GL_LINE_STRIP)
            glColor4f(*color)

            for line in lines:
                glVertex2f(line.x, line.y)
            glEnd()


    @classmethod
    async def draw_text_at(cls, world_pos: Vec3, color, text):

        render = sdk.Sdk.game.render()

        position = w2s(world_pos, render.view_proj_matrix)
        if position.x > 0 and position.y > 0 and Drawing.is_on_screen(position, render.width / 2, render.height / 2,
                                                                      render.width, render.height):
            e = imgui.get_overlay_draw_list()
            e.add_text(position.x, position.y, color, text)

    @classmethod
    def is_on_screen(cls, screen_pos: Vec2, offset_x, offset_y, width, height):
        return screen_pos.x > -offset_x and offset_x < (width + offset_x) and screen_pos.y > -offset_y and offset_y < (
                height + offset_y)
