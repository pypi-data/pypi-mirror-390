from .game_object import Component, GameObject
from .surface import SurfaceComponent
from .color import ColorComponent
from .transform import Transform
from .vmath_mini import Vector2d
import pygame as pg



class LabelComponent(Component):
    text: str
    font: pg.font.Font

    def __init__(self, text: str, font: pg.font.Font = None):
        self.text = text
        if font is None: font = pg.font.SysFont("consolas", 30)
        self.font = font

    def set_sys_font(self, name: str, size: int, bold = 0, italic = 0):
        self.font = pg.font.SysFont(name, size, bold, italic)

    def draw(self):
        surf = self.game_object.get_component(SurfaceComponent)
        text = self.font.render(self.text, 1, self.game_object.get_component(ColorComponent).color)

        surf.pg_surf.blit(text, ((surf.size - Vector2d.from_tuple(text.get_size())) / 2).as_tuple())

    def set_text(self, new_text: str, change_surf: bool = False):
        self.text = new_text
        if change_surf:
            surf = self.game_object.get_component(SurfaceComponent)
            text = self.font.render(self.text, 1, self.game_object.get_component(ColorComponent).color)
            text_size = Vector2d.from_tuple(text.get_size())
            surf_size = surf.size
            if (text_size.x > surf_size.x) or (text_size.y > surf_size.y):
                surf.pg_surf = pg.Surface(text_size.as_tuple(), pg.SRCALPHA, 32)
                surf.size = text_size
        self.game_object.need_blit_set_true()
        self.game_object.need_draw = 1