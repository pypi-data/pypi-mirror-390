import time
import pygame

from .helper import vector2d, Context, Color, Camera, EngineError, is_colliding, rotate, Script, circle_rect_collision
from .objects import GameObject, Group, UIGroup
import tkinter as tk
from tkinter import ttk

from .ui_elements import UIElement
# -----------------------------
# Number / String Input Objects
# -----------------------------
class NumberInputObj:
    def __init__(self, var: tk.DoubleVar, default=0, dtype="int"):
        self.var = var
        self.default = default
        self.dtype = dtype

    @property
    def value(self):
        try:
            # Try converting to float; fallback to default if empty or invalid
            val = self.var.get()
            if val == "":
                return self.default
            if self.dtype == "int":
                return int(val)
            return float(val)
        except Exception:
            return self.default

    @value.setter
    def value(self, v):
        self.var.set(v)

class StringInputObj:
    def __init__(self, var: tk.StringVar, default=""):
        self.var = var
        self.default = default

    @property
    def value(self):
        val = self.var.get()
        if val == "":
            return self.default
        return val

    @value.setter
    def value(self, v):
        self.var.set(v)

# -----------------------------
# Settings Window
# -----------------------------
class SettingsWindow:
    _root = None  # single hidden root

    def __init__(self, title="Settings"):
        if SettingsWindow._root is None:
            SettingsWindow._root = tk.Tk()
            SettingsWindow._root.withdraw()  # hide main root

        self.root = tk.Toplevel(SettingsWindow._root)
        self.root.title(title)
        self.inputs = {}

        self.container = ttk.Frame(self.root, padding=20)
        self.container.pack(fill="both", expand=True)

        self.linked_inputs = {}

    def add_number_input(self, label, default=0, dtype="int"):
        var = tk.StringVar(master=self.root, value=str(default))
        frame = ttk.Frame(self.container)
        frame.pack(fill="x", pady=2)
        ttk.Label(frame, text=label).pack(side="left")
        ttk.Entry(frame, textvariable=var).pack(side="right")
        input_obj = NumberInputObj(var, default, dtype)
        self.inputs[label] = input_obj
        return input_obj

    def add_string_input(self, label, default=""):
        var = tk.StringVar(master=self.root, value=default)
        frame = ttk.Frame(self.container)
        frame.pack(fill="x", pady=2)
        ttk.Label(frame, text=label).pack(side="left")
        ttk.Entry(frame, textvariable=var).pack(side="right")
        input_obj = StringInputObj(var, default)
        self.inputs[label] = input_obj
        return input_obj


    def add_linked_number_input(self, label, obj, attr_name, default=None, dtype="int"):
        initial_value = default if default is not None else getattr(obj, attr_name)
        self.add_number_input(label, initial_value, dtype=dtype)
        self.linked_inputs[label] = (obj, attr_name)

    def update(self):
        self.root.update()
        for linked_input, (obj, attr_name) in self.linked_inputs.items():
            setattr(obj, attr_name, self.inputs[linked_input].value)

class Engine:
    def __init__(self, width:int=500, height:int=500, name:str="GamEngine2D", resizable:bool=True, background_color:Color=Color.black, background_image:str=None) -> None:
        if not pygame.get_init():
            pygame.init()

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        flags = pygame.RESIZABLE if resizable else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption(name)

        self.clock = pygame.time.Clock()
        self.camera = Camera(screen_size=vector2d(width, height))
        self.objects = []
        self.groups = []
        self.ui_groups = []
        self.ui_elements = []
        self.background_color = background_color
        self._background_image_path = background_image
        self.background_image_path = background_image
        self.global_scripts = []

        self.context = Context()
        self.context.functions.draw_circle = self.draw_circle
        self.context.functions.draw_circle_outline = self.draw_circle_outline
        self.context.functions.draw_text = self.draw_text
        self.context.functions.is_colliding = self.is_colliding
        self.context.functions.is_colliding_objects = self.is_colliding_objects
        self.context.functions.draw_rect = self.draw_rect
        self.context.functions.draw_rect_outline = self.draw_rect_outline
        self.context.functions.get_objects_with_prefix = self.get_objects_starting_with
        self.context.functions.create_sound = self.create_sound
        self.context.functions.play_sound = self.play_sound
        self.context.functions.is_colliding_pos = self.is_colliding_pos
        self.context.functions.draw_line_start_end = self.draw_line_start_end
        self.context.groups = self.groups
        self.context.message = self.message
        self.context.ui_groups = self.ui_groups
        self.context.screen_size = vector2d(width, height)
        self.context.game_objects = self.objects
        self.context.ui_elements = self.ui_elements
        self.context.camera = self.camera

    def on_frame(self, context, objects, camera):
        pass

    def on_init(self, context, objects, camera):
        pass

    def on_end(self, context, objects, camera):
        pass

    def on_pause(self, context, objects, camera, dt, screen):
        pass

    def draw_circle(self, pos: vector2d, radius: int, color: Color):
        screen_pos = self.camera.world_to_screen(pos).totuple()
        pygame.draw.circle(surface=self.screen, color=color.to_rgb(), center=screen_pos, radius=int(radius * self.camera.zoom))


    def is_colliding(self, obj1, obj2_name):
        try:
            obj2 = [obj for obj in self.objects if obj.name == obj2_name][0]
        except IndexError:
            raise EngineError(f"Error, game object with name '{obj2_name}' not found")

        if not isinstance(obj1, GameObject):
            raise EngineError(f"Error, {obj1.name} is not a GameObject")

        if not isinstance(obj2, GameObject):
            raise EngineError(f"Error, {obj2.name} is not a GameObject")

        # --- Handle Rectangle–Rectangle collision ---
        if hasattr(obj1, "get_corners") and hasattr(obj2, "get_corners"):
            return is_colliding(obj1.get_corners(), obj2.get_corners())

        # --- Handle Circle–Circle collision ---
        elif hasattr(obj1, "radius") and hasattr(obj2, "radius"):
            dist = (obj1.pos - obj2.pos).magnitude()
            return dist <= (obj1.radius + obj2.radius)

        # --- Handle Circle–Rectangle collision ---
        elif hasattr(obj1, "radius") and hasattr(obj2, "get_corners"):
            return circle_rect_collision(obj1, obj2)
        elif hasattr(obj2, "radius") and hasattr(obj1, "get_corners"):
            return circle_rect_collision(obj2, obj1)

        else:
            raise EngineError(f"Error, unsupported collision pair: '{obj1.name}' and '{obj2.name}'")

    def is_colliding_objects(self, obj1: GameObject, obj2: GameObject):
        if not isinstance(obj1, GameObject):
            raise EngineError(f"Error, {obj1.name} is not a GameObject")

        if not isinstance(obj2, GameObject):
            raise EngineError(f"Error, {obj2.name} is not a GameObject")

        # --- Handle Rectangle–Rectangle collision ---
        if hasattr(obj1, "get_corners") and hasattr(obj2, "get_corners"):
            return is_colliding(obj1.get_corners(), obj2.get_corners())

        # --- Handle Circle–Circle collision ---
        elif hasattr(obj1, "radius") and hasattr(obj2, "radius"):
            dist = (obj1.pos - obj2.pos).magnitude()
            return dist <= (obj1.radius + obj2.radius)

        # --- Handle Circle–Rectangle collision ---
        elif hasattr(obj1, "radius") and hasattr(obj2, "get_corners"):
            return circle_rect_collision(obj1, obj2)
        elif hasattr(obj2, "radius") and hasattr(obj1, "get_corners"):
            return circle_rect_collision(obj2, obj1)

        else:
            raise EngineError(f"Error, unsupported collision pair: '{obj1.name}' and '{obj2.name}'")

    def is_colliding_pos(self, pos, name):
        try:
            obj = [obj for obj in self.objects if obj.name == name][0]
        except IndexError:
            raise EngineError(f"Error, game object with name '{name}' not found")

        if not hasattr(obj, "get_corners"):
            raise EngineError(f"Error, game object with name '{obj.name}' has no get_corners method")

        return is_colliding(obj.get_corners(), [pos])

    def draw_text(self, text: str, pos: vector2d, color: Color, font_size=18, center=False):
        """Draw text at world position (pos)."""
        font = pygame.font.SysFont("Arial", font_size)
        text_surface = font.render(text, True, color.to_rgb())
        screen_pos = self.camera.world_to_screen(pos).totuple()

        if center:
            rect = text_surface.get_rect(center=(int(screen_pos[0]), int(screen_pos[1])))
        else:
            rect = text_surface.get_rect(topleft=(int(screen_pos[0]), int(screen_pos[1])))

        self.screen.blit(text_surface, rect)

    def draw_circle_outline(self, pos=vector2d.zero, radius=10, color=Color.white, line_thickness=10):
         screen_pos = self.camera.world_to_screen(pos).totuple()
         pygame.draw.circle(self.screen, color.to_rgb(), screen_pos, int(radius * self.camera.zoom), width=line_thickness)

    def draw_line(self, pos=vector2d.zero, length=100, rotation=0, thickness=10, color=Color.white):
        screen_pos = self.camera.world_to_screen(pos).totuple()
        ends = [screen_pos + length / 2, screen_pos - length / 2]
        for i in range(len(ends)):
            ends[i] = rotate(ends[i], rotation)

        pygame.draw.line(self.screen, color.to_rgb(), ends[0], ends[1], thickness)

    def draw_line_start_end(self, start, end, thickness=10, color=Color.white):
        start = self.camera.world_to_screen(start)
        end = self.camera.world_to_screen(end)
        pygame.draw.line(self.screen, color.to_rgb(), start.totuple(), end.totuple(), thickness)

    def draw_rect(self, pos: vector2d, color: Color = Color.white, size: vector2d = vector2d(40, 40),
                  texture: str | pygame.Surface = None, rotation: float = 0):
        screen_pos = self.camera.world_to_screen(pos)
        w, h = int(size.x), int(size.y)
        half_size = size / 2
        half_size.x = int(half_size.x)
        half_size.y = int(half_size.y)

        # Rotate corners for polygon (color-only)
        corners = [
            vector2d(half_size.x, half_size.y),
            vector2d(-half_size.x, half_size.y),
            vector2d(-half_size.x, -half_size.y),
            vector2d(half_size.x, -half_size.y),
        ]
        corners = [rotate((corner + screen_pos), rotation).totuple() for corner in corners]

        if texture:
            if isinstance(texture, str):
                surf = pygame.image.load(texture).convert_alpha()
            else:
                surf = texture  # already a Surface
            surf = pygame.transform.scale(surf, (w, h))
            if rotation != 0:
                surf = pygame.transform.rotate(surf, -rotation)  # rotate surface
            rect = surf.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))  # <-- center aligned
            self.screen.blit(surf, rect)
        else:
            pygame.draw.polygon(self.screen, color.to_rgb(), corners, 0)

    def draw_rect_outline(self, pos: vector2d, color: Color = Color.white, size: vector2d = vector2d(40, 40), width: int = 10) -> None:
        screen_pos = self.camera.world_to_screen(pos)
        half_size = size / 2
        half_size.x = int(half_size.x)
        half_size.y = int(half_size.y)

        corners = [
            vector2d(half_size.x, half_size.y),
            vector2d(-half_size.x, half_size.y),
            vector2d(-half_size.x, -half_size.y),
            vector2d(half_size.x, -half_size.y),
        ]

        corners = [(corner + screen_pos).totuple() for corner in corners]

        pygame.draw.polygon(self.screen, color.to_rgb(), corners, width=width)

    def add_object(self, obj: GameObject):
        self.objects.append(obj)

    def add_ui_element(self, element: UIElement):
        self.ui_elements.append(element)

    def init_all_scripts(self):
        for obj in self.objects:
            obj.init_scripts()

    def get_objects_starting_with(self, prefix):
        objs = []
        for obj in self.objects:
            if obj.name.startswith(prefix):
                objs.append(obj)

        return objs

    def run(self, fps=60, dynamic_view=True, zoom=None, pan=None):
        self.on_init(self.context, self.objects, self.camera)
        self.context.start_time = time.monotonic()
        self.init_all_scripts()
        running = True

        dragging = False
        last_mouse_pos = None
        mouse_holding = False
        self.context.fps = fps

        if zoom is None:
            zoom = dynamic_view

        if pan is None:
            pan = dynamic_view

        self.context.pan = pan
        self.context.zoom = zoom

        while running:
            if self.background_image is not None:
                self.background_image = pygame.transform.scale(self.background_image, self.screen.get_size())
            dt = self.clock.get_time() / 1000
            self.on_frame(self.context, self.objects, self.camera)

            if self.background_image is not None:
                self.screen.blit(self.background_image, (0, 0))

            self.context.mouse_down_pos = None
            self.context.mouse_hold_pos = None
            self.context.mouse_up_pos = None
            self.context.mouse_down = None
            self.context.mouse_down_screen = None

            self.context.keys_pressed = []
            self.context.keys_released = []

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if pan:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            # save click start position
                            screen_pos = vector2d.fromtuple(event.pos)
                            world_pos = self.camera.screen_to_world(screen_pos)
                            self.context.mouse_down_pos = world_pos
                            dragging = True
                            last_mouse_pos = screen_pos

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            dragging = False
                            screen_pos = vector2d.fromtuple(event.pos)
                            world_pos = self.camera.screen_to_world(screen_pos)
                            self.context.mouse_up_pos = world_pos

                    elif event.type == pygame.MOUSEMOTION and dragging:
                        mouse_pos = vector2d(*event.pos)
                        delta = mouse_pos - last_mouse_pos
                        delta.y = -delta.y
                        self.camera.pos -= delta * (1 / self.camera.zoom)
                        last_mouse_pos = mouse_pos
                if zoom:
                    if event.type == pygame.MOUSEWHEEL:
                        zoom_factor = 1.1 if event.y > 0 else 0.9
                        mouse_world = self.camera.screen_to_world(vector2d(*pygame.mouse.get_pos()))
                        self.camera.zoom_at(zoom_factor, mouse_world)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        screen_pos = vector2d.fromtuple(event.pos)
                        world_pos = self.camera.screen_to_world(screen_pos)
                        self.context.mouse_down_pos = world_pos
                        dragging = True
                        last_mouse_pos = screen_pos

                        if self.context.mouse_down is None:
                            self.context.mouse_down = world_pos
                            self.context.mouse_down_screen = screen_pos - self.context.screen_size / 2

                if event.type == pygame.KEYDOWN:
                    key_name = pygame.key.name(event.key)
                    self.context.keys_pressed.append(key_name)
                    self.context.keys_held.add(key_name)

                if event.type == pygame.KEYUP:
                    key_name = pygame.key.name(event.key)
                    self.context.keys_released.append(key_name)
                    self.context.keys_held.discard(key_name)

            if self.background_image is not None:
                self.screen.blit(self.background_image, (0, 0))
            else:
                self.screen.fill(self.background_color.to_rgb())

                # --- draw other objects (your rectangles, etc.) ---
            screen_mouse = vector2d.fromtuple(pygame.mouse.get_pos())
            self.context.mouse_pos_screen = screen_mouse
            world_pos = self.camera.screen_to_world(screen_mouse)
            self.context.mouse_pos_world = vector2d(world_pos.x, -world_pos.y)

            pressed = pygame.mouse.get_pressed()
            if pressed[0]:
                self.context.mouse_hold_pos = self.context.mouse_pos_world

            w, h = self.screen.get_size()
            self.context.screen_size = vector2d(w, h)
            self.camera.screen_size = vector2d(w, h)

            self.context.update()

            if not self.context.pause:
                for obj in self.objects:
                    obj.update(dt)

                self.update_global_scripts(dt)

            if not self.context.hide_all:
                for obj in self.objects:
                    obj.draw(self.screen, self.camera)

            pressed = pygame.mouse.get_pressed()
            for element in self.ui_elements:
                element.draw(
                    self.screen,
                    self.camera,
                    self.context.mouse_down_screen,
                    self.context.mouse_pos_screen - self.context.screen_size / 2,
                    mouse_pressed=pressed[0]
                )
            if self.context.pause:
                self.on_pause(self.context, self.objects, self.camera, dt, self.screen)

            for setting in self.context.settings:
                setting.update()

            for di, delay in enumerate(self.context.delays):
                delay.update()
                if delay.finished:
                    self.context.delays.pop(di)

            pygame.display.flip()
            self.clock.tick(fps)

            screen_mouse = vector2d.fromtuple(pygame.mouse.get_pos())
            self.context.mouse_pos_screen = screen_mouse
            self.context.mouse_pos_world = self.camera.screen_to_world(screen_mouse)
            if self.context.end:
                running = False

            self.context.fps = self.clock.get_fps()
            zoom = self.context.zoom
            pan = self.context.pan

        self.on_end(self.context, self.objects, self.camera)
        pygame.quit()

    def remove_object(self, name):
        for io, obj in enumerate(self.objects):
            if obj.name == name:
                self.objects.pop(io)

    def create_sound(self, name, path):
        sound = pygame.mixer.Sound(path)
        self.context.sounds[name] = sound

    def play_sound(self, name):
        sound = self.context.sounds[name]
        sound.play()

    def add_group(self, group):
        if not isinstance(group, Group):
            raise EngineError("Error, tried to add group that isn't of type Group")

        self.groups.append(group)
        self.objects += group.get_all_children()

    def add_ui_group(self, group):
        if not isinstance(group, UIGroup):
            raise EngineError("Error, tried to add group that isn't of type UIGroup")

        self.ui_groups.append(group)
        self.ui_elements += group.get_all_children()

    def attach(self, script_path):
        script = Script(self, script_path, self.context)
        script.init_instance()
        self.global_scripts.append(script)

    def update_global_scripts(self, dt):
        for script in self.global_scripts:
            script.update(dt)

    def message(self, message, obj_name, sender=None):
        for obj in self.objects:
            if obj.name == obj_name:
                obj.messages_dict.append({sender: message})
                obj.messages.append(message)
                obj.received_message = True
                return

        raise EngineError(f"Error, no object named {obj_name}")

    @property
    def background_image_path(self):
        return self._background_image_path


    @background_image_path.setter
    def background_image_path(self, path):
        self._background_image_path = path
        if path is None:
            self.background_image = None
            return  # stop here if no image
        self.background_image = pygame.image.load(path).convert()
        self.background_image = pygame.transform.scale(self.background_image, self.screen.get_size())
