from typing import Callable
import pygame as pg

from .sprite import SpriteComponent
from .game_object import Component
from .vmath_mini import Vector2d
from .surface import SurfaceComponent


class AnimationObject:
    texture: pg.Surface
    frame_size: Vector2d
    frame_order: list[Vector2d]
    loop: bool
    back_and_forth: bool

    def __init__(self, sprite_nickname: str = "", loop: bool = 0, back_and_forth: bool = 0, frame_size: Vector2d = Vector2d()):
        self.texture = SpriteComponent.get_by_nickname(sprite_nickname)
        self.loop = loop
        self.back_and_forth = back_and_forth
        self.frame_size = frame_size
        self.frame_order = []

    def set_frame_order(self, frame_order: list[Vector2d]):
        self.frame_order = frame_order

class AnimationComponent(Component):
    downloaded: dict[str, AnimationObject] = {}
    anim_obj: AnimationObject
    frames: list[pg.Surface]
    tpf: int
    _tick: int
    _frame: int
    _stop: bool
    _back: bool
    _on_stop: Callable
    _args: list

    def __init__(self, nickname: str = "", size: Vector2d = Vector2d(0, 0), tpf: int = 1):
        prenickname = ":"
        if nickname != "" and (prenickname + nickname) in AnimationComponent.downloaded:
            self.anim_obj = AnimationComponent.downloaded[(prenickname + nickname)]
        else:
            raise ValueError(f"can not find animation \"{nickname}\"")
        self._tick = 0
        self._frame = 0
        self._stop = False
        self._back = False
        self._on_stop = lambda:0
        self._args = []
        self.tpf = tpf
        self.frames = []
        for pos in self.anim_obj.frame_order:
            self.frames.append(pg.transform.scale(self.anim_obj.texture.subsurface(pg.Rect(pos.as_tuple(), self.anim_obj.frame_size.as_tuple())), size.as_tuple()))
    
    def iteration(self):
        if self._stop:
            return
        self._tick += 1
        if self._tick == self.tpf:
            self._tick = 0
            if self._back:
                self._frame -= 1
            else:
                self._frame += 1
            if not (-1 < self._frame < len(self.anim_obj.frame_order)):
                if not self.anim_obj.loop:
                    self._stop = True
                    self._on_stop(*self._args)
                elif self.anim_obj.back_and_forth:
                    self._back = not self._back
                    if self._back:
                        self._frame -= 2
                    else:
                        self._frame += 2
                else:
                    self._frame = 0
            self.game_object.need_draw = 1
            self.game_object.need_blit_set_true()

    def draw(self):
        if self._stop:
            return
        surf = self.game_object.get_component(SurfaceComponent)
        surf.pg_surf.blit(self.frames[self._frame], ((surf.size - Vector2d.from_tuple(self.frames[self._frame].get_size())) / 2).as_tuple())

    def set_on_stop(self, func: Callable, args: list):
        self._on_stop = func
        self._args = args

    @staticmethod
    def new_animation(nickname: str = "", anim_obj: AnimationObject = None):
        prenickname = ":"
        if (prenickname + nickname) in AnimationComponent.downloaded:
            raise KeyError(f"Sprite with nickname '{nickname}' already exists.")
        if anim_obj is None:
            raise ValueError("'anim_obj' must be provided")
        AnimationComponent.downloaded[(prenickname + nickname)] = anim_obj
    
    @staticmethod
    def is_downloaded(nickname: str = None) -> bool:
        if nickname is None:
            raise ValueError("'nickname' must be provided.")
        prenickname = ":"
        return (prenickname + nickname) in AnimationComponent.downloaded