import dataclasses

import imgui

import sdk.sdk as sdk
from sdk.utils import Vec3
from OpenGL.GL import *
import math
from sdk.utils import Vec2, Vec3, w2s


class Drawing:

    @classmethod
    def _line(cls, x1, y1, x2, y2, width, color):
        glLineWidth(width)
        glBegin(GL_LINES)
        glColor4f(*color)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()

    @classmethod
    def draw_circle(cls, x, y, radius, sides, color):

        lines = []

        step = math.pi * 2 / sides
        count = 0
        a = 0
        while a < math.pi * 2:
            x1 = radius * math.cos(a) + x
            y1 = radius * math.sin(a) + y
            x2 = radius * math.cos(a + step) + x
            y2 = radius * math.sin(a + step) + y

            lines.append([Vec2(x1, y1), Vec2(x2, y2)])
            a += step

        for line in lines:
            start = line[0]
            stop = line[1]
            cls._line(start.x, start.y, stop.x, stop.y, 2, color)

    @classmethod
    async def draw_circle_at(cls, world_pos: Vec3, radius, color, thickness, points=800):
        render = await sdk.Sdk.game.render()
        lines = []
        step = 6.2831 / points
        step1 = step = math.pi * 2 / points
        theta = 0
        i = 0
        while i < points:
            world_space = Vec3(world_pos.x + radius * math.cos(theta), world_pos.y,
                               world_pos.z - radius * math.sin(theta))
            screen_space = w2s(world_space, render.view_proj_matrix)

            lines.append(Vec2(screen_space.x, screen_space.y))

            theta += step
            i += 1

        for line in lines:
            start = line
            """
            glBegin(GL_POINTS)
            glColor3f(1, 1, 1)
            glVertex2i(int(start.x), int(start.y))
            glEnd()
            """
            cls._line(int(start.x), int(start.y), int(start.x) + 2, int(start.y) + 2, 3, (255, 0, 0, 255))

    @classmethod
    async def draw_text_at(cls, world_pos: Vec3, color, text):

        render = await sdk.Sdk.game.render()

        position = w2s(world_pos, render.view_proj_matrix)
        if position.x > 0 and position.y > 0:
            e = imgui.get_overlay_draw_list()
            e.add_text(position.x, position.y, color, text)
