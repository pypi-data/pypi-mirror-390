import os
import importlib.util
import sys
import math
import time
from .shaders import ComputeShader
import moderngl
import numpy as np

class classproperty(property):
    def __get__(self, instance, owner):
        return self.fget(owner)

class vector2d:
    def __init__(self, x, y=None):
        self.x = x
        self.y = y

        if y is None:
            self.y = self.x

    @property
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def sqr_magnitude(self):
        return self.x ** 2 + self.y ** 2

    def normalize(self):
        magnitude = self.magnitude
        self.x = self.x / magnitude
        self.y = self.y / magnitude

    @property
    def normalized(self):
        magnitude = self.magnitude
        return vector2d(self.x, self.y) / magnitude

    def __add__(self, other):
        if isinstance(other, vector2d):
            return vector2d(self.x + other.x, self.y + other.y)
        else:
            return vector2d(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, vector2d):
            return vector2d(self.x - other.x, self.y - other.y)
        else:
            return vector2d(self.x - other, self.y - other)

    def __mul__(self, other):
        if isinstance(other, vector2d):
            return vector2d(self.x * other.x, self.y * other.y)
        else:
            return vector2d(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, vector2d):
            return vector2d(self.x / other.x, self.y / other.y)
        else:
            return vector2d(self.x / other, self.y / other)

    def totuple(self):
        return (self.x, self.y)

    def __radd__(self, other):
        return vector2d(self.x + other, self.y + other)

    def __rsub__(self, other):
        return vector2d(self.x - other, self.y - other)

    def __rtruediv__(self, other):
        return vector2d(self.x / other, self.y / other)

    def __rmul__(self, other):
        return vector2d(self.x * other, self.y * other)

    @classmethod
    def fromtuple(cls, tuple):
        cls.x, cls.y = tuple
        return vector2d(cls.x, cls.y)

    def __repr__(self):
        return f"vector2d({self.x}, {self.y})"

    def copy(self):
        return vector2d(self.x, self.y)

    def __neg__(self):
        return vector2d(-self.x, -self.y)

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __gt__(self, other):
        return self.x > other.x and self.y > other.y

    def __ge__(self, other):
        return self.x >= other.x and self.y >= other.y

    @classproperty
    def up(cls):
        return cls(0, 1)

    @classproperty
    def down(cls):
        return cls(0, -1)

    @classproperty
    def right(cls):
        return cls(1, 0)

    @classproperty
    def left(cls):
        return cls(-1, 0)

    @classproperty
    def one(cls):
        return cls(1, 1)

    @classproperty
    def zero(cls):
        return cls(0, 0)

def rotate(pos: vector2d, angle):
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    x = pos.x * cos_a - pos.y * sin_a
    y = pos.x * sin_a + pos.y * cos_a
    return vector2d(x, y)

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    @staticmethod
    def RGB(r, g, b): return Color(r, g, b)

    @staticmethod
    def hex(hex_string):
        if not hex_string.startswith("#"): raise Exception("String must start with #")
        if not len(hex_string) == 7: raise Exception("String must contain 7 characters")
        r = int(hex_string[1:3], 16)
        g = int(hex_string[3:5], 16)
        b = int(hex_string[5:7], 16)
        return Color(r, g, b)

    def __eq__(self, other):
        if self.r == other.r and self.g == other.g and self.b == other.b:
            return True
        return False

    def to_hex(self):
        if not all(0 <= x <= 255 for x in (self.r, self.g, self.b)):
            raise ValueError("RGB values must be in the range 0-255")
        return "#{:02X}{:02X}{:02X}".format(self.r, self.g, self.b)

    def to_rgb(self):
        return self.r, self.g, self.b

    @classproperty
    def black(cls):
        return cls(0, 0, 0)

    @classproperty
    def white(cls):
        return cls(255, 255, 255)

    @classproperty
    def red(cls): return cls(255, 0, 0)

    @classproperty
    def green(cls): return cls(0, 255, 0)

    @classproperty
    def blue(cls): return cls(0, 0, 255)

    @classproperty
    def yellow(cls): return cls(255, 255, 0)

    @classproperty
    def cyan(cls): return cls(0, 255, 255)

    @classproperty
    def magenta(cls): return cls(255, 0, 255)

    @classproperty
    def grey(cls): return cls(33, 33, 33)

    @classproperty
    def light_grey(cls): return cls(80, 80, 80)

    @classproperty
    def light_red(cls): return cls(253, 89, 111)     # #fd596f

    @classproperty
    def light_green(cls): return cls(0, 190, 160)    # #00bea0

    @classproperty
    def light_yellow(cls): return cls(254, 208, 95)  # #fed05f

    @classproperty
    def orange(cls): return cls(254, 166, 93)        # #fea65d

    @classproperty
    def light_blue(cls): return cls(109, 154, 218)   # #6d9ada

class Delay:
    def __init__(self, delay, start_time, callback):
        self.delay = delay
        self.start_time = start_time
        self.callback = callback
        self.finished = False

    def update(self):
        if time.monotonic() - self.start_time > self.delay:
            self.callback()
            self.finished = True
            return

class Functions:
    def __init__(self):
        self.draw_circle = lambda pos, radius, color: None
        self.is_colliding = lambda obj1, obj2_name: False
        self.is_colliding_objects = lambda obj1, obj2: False
        self.draw_text = lambda text, pos, color, font_size=18, center=False: None
        self.draw_rect = lambda pos, color=Color.white, size=vector2d(40), texture=None, rotation=0: None
        self.draw_rect_outline = lambda pos, color=Color.white, size=vector2d(40), thickness=10: None
        self.get_objects_with_prefix = lambda prefix: []
        self.create_sound = lambda name, path: None
        self.is_colliding_pos = lambda pos, name: False
        self.draw_circle_outline = lambda pos=vector2d.zero, radius=10, color=Color.white, line_thickness=10: None
        self.draw_line = lambda pos=vector2d.zero, length=100, rotation=0, thickness=10, color=Color.white: None
        self.draw_line_start_end = lambda start, end, thickness=10, color=Color.white: None
        self.play_sound = lambda name: None

class Context:
    def __init__(self):
        self.functions = Functions()
        self.screen_size = vector2d(0, 0)  # <-- added
        self.settings = []
        self.pause = False
        self.hide_all = False
        self.start_time = None
        self.runtime_vars = {}
        self.game_objects = []
        self.message = lambda message, obj_name, sender: None
        self.ui_elements = []
        self.delays = []
        self.sounds = {}
        self.mouse_down_pos = None
        self.mouse_pos_screen = None
        self.mouse_pos_world = None
        self.mouse_hold_pos = None
        self.compute_shaders: list[ComputeShader] = []
        self.moderngl_context = moderngl.create_standalone_context()
        self.camera = None
        self.keys_pressed = []
        self.keys_released = []
        self.keys_held = set()
        self.key_pressed_callbacks = {}
        self.key_released_callbacks = {}
        self.key_held_callbacks = {}
        self.end = False
        self.fps = 0
        self.pan = None
        self.zoom = None

    def get(self, name):
        for obj in self.game_objects:
            if obj.name == name:
                return obj
        else:
            raise EngineError(f"Error, name '{name}' not found")

    def remove_object(self, obj):
        self.game_objects.remove(obj)

    def add_delay(self, delay, callback):
        self.delays.append(Delay(delay, time.monotonic(), callback))

    def compute_shader(self, name, filename):
        self.compute_shaders.append(ComputeShader(context=self.moderngl_context, name=name, filename=filename))

    def run_shader(self, name, group_x=1, group_y=1, group_z=1):
        for compute_shader in self.compute_shaders:
            if compute_shader.name == name:
                compute_shader.run(group_x=group_x, group_y=group_y, group_z=group_z)
                break
        else:
            raise EngineError(f"Error, no shader has name {name}")

    def bind_buffer(self, shader_name, data=None, reserve=None, buffer_name=None, dtype=np.int32):
        for compute_shader in self.compute_shaders:
            if compute_shader.name == shader_name:
                buffer = compute_shader.new_buffer(data=data, reserve=reserve, name=buffer_name)
                compute_shader.bind_buffer(binding=0, buffer=buffer)
                break

    def read_buffer(self, shader_name, buffer_name):
        for compute_shader in self.compute_shaders:
            if compute_shader.name == shader_name:
                buffer = compute_shader.read_buffer(buffer_name=buffer_name)
                return buffer

        raise EngineError(f"Error, no shader has name {shader_name}")

    def set_uniform(self, shader_name, uniform_name, value):
        for compute_shader in self.compute_shaders:
            if compute_shader.name == shader_name:
                compute_shader.set_uniform(uniform_name, value)

    def on_key_press(self, key_name, callback, args=None):
        if args is None:
            args = []
        self.key_pressed_callbacks[callback] = {"key": key_name, "args": args}

    def on_key_release(self, key_name, callback, args=None):
        if args is None:
            args = []

        self.key_released_callbacks[callback] = {"key": key_name, "args": args}

    def on_key_hold(self, key_name, callback, args=None):
        if args is None:
            args = []
        self.key_held_callbacks[callback] = {"key": key_name, "args": args}

    def update_key_callbacks(self):
        for callback, metadata in self.key_pressed_callbacks.items():
            if metadata["key"] in self.keys_pressed:
                if metadata["args"]:
                    callback(*metadata["args"])
                else:
                    callback()

        for callback, metadata in self.key_released_callbacks.items():
            if metadata["key"] in self.keys_released:
                if metadata["args"]:
                    callback(*metadata["args"])

                else:
                    callback()

        for callback, metadata in self.key_held_callbacks.items():
            if metadata["key"] in self.keys_held:
                if metadata["args"]:
                    callback(*metadata["args"])

                else:
                    callback()

    def update(self):
        self.update_key_callbacks()

class Script:
    def __init__(self, obj, script_path, context):
        self.obj = obj
        self.context = context
        self.script_path = script_path
        self.module = None
        self.cls = None
        self.instance = None
        self.load(script_path)

    def load(self, path):
        if not os.path.exists(path):
            print(f"[Script] File not found: {path}")
            return
        module_name = os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"[Script] Error loading module {path}: {e}")
            return
        self.module = module

        # Class is PascalCase version of file name
        class_name = ''.join(word.capitalize() for word in module_name.split('_'))
        if hasattr(module, class_name):
            self.cls = getattr(module, class_name)
        else:
            print(f"[Script] No class '{class_name}' found in {path}")

    def init_instance(self):
        if self.cls is None or self.instance is not None:
            return
        try:
            self.instance = self.cls(self.obj, self.context)
        except Exception as e:
            print(f"[Script] Failed to instantiate script for {self.obj.name if hasattr(self.obj, "name") else "Engine"}: {e}")
            self.instance = None

        if self.instance and hasattr(self.instance, "start"):
            try:
                self.instance.start()
            except Exception:
                pass

    def update(self, dt):
        if self.instance is None:
            return
        self.instance.update(dt)
# -----------------------------
# Camera
# -----------------------------
class Camera:
    def __init__(self, pos=None, zoom=1, screen_size=None):
        self.pos = pos or vector2d(0, 0)
        self.zoom = zoom
        self.screen_size = screen_size or vector2d(800, 600)
        self.min_zoom = 0.1
        self.max_zoom = 10

    def world_to_screen(self, world_pos: vector2d):
        screen_pos = vector2d(
            (world_pos.x - self.pos.x) * self.zoom,
            (-world_pos.y + self.pos.y) * self.zoom  # invert Y
        )
        screen_pos += vector2d(self.screen_size.x / 2, self.screen_size.y / 2)
        return screen_pos

    def screen_to_world(self, screen_pos: vector2d):
        world_pos = screen_pos - vector2d(self.screen_size.x / 2, self.screen_size.y / 2)
        world_pos = world_pos * (1 / self.zoom) + self.pos
        return world_pos

    def zoom_at(self, zoom_factor, pivot: vector2d):
        old_zoom = self.zoom
        self.zoom *= zoom_factor
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
        self.pos += (pivot - self.pos) * (1 - old_zoom / self.zoom)

class EngineError(Exception):
    pass

def project_polygon(axis, vertices):
    dots = [v.x * axis.x + v.y * axis.y for v in vertices]
    return min(dots), max(dots)

def overlap(p1, p2):
    return p1[0] <= p2[1] and p2[0] <= p1[1]

def is_colliding(poly1, poly2):
    # poly1, poly2 = lists of vector2d
    for polygon in (poly1, poly2):
        for i in range(len(polygon)):
            # get edge
            p1, p2 = polygon[i], polygon[(i + 1) % len(polygon)]
            edge = vector2d(p2.x - p1.x, p2.y - p1.y)
            # perpendicular axis
            axis = vector2d(-edge.y, edge.x)
            # project both polygons
            proj1 = project_polygon(axis, poly1)
            proj2 = project_polygon(axis, poly2)
            # check overlap
            if not overlap(proj1, proj2):
                return False
    return True

def point_near_line(p, a, b, threshold=5):
    """Check if point p is within threshold pixels of line segment a-b."""
    ax, ay = a
    bx, by = b
    px, py = p

    lab2 = (bx - ax) ** 2 + (by - ay) ** 2
    if lab2 == 0:
        return (px - ax) ** 2 + (py - ay) ** 2 < threshold ** 2

    t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / lab2))
    projx = ax + t * (bx - ax)
    projy = ay + t * (by - ay)

    dist2 = (px - projx) ** 2 + (py - projy) ** 2
    return dist2 < threshold ** 2


def get_edge_point(obj, direction_angle):
    """Return world position of the edge in given direction (degrees)."""
    angle = math.radians(direction_angle)
    dx, dy = math.cos(angle), math.sin(angle)

    # Half-size projected onto this direction
    half_extent = (obj.size.x / 2 * abs(dx)) + (obj.size.y / 2 * abs(dy))
    return obj.pos + vector2d(dx, dy) * half_extent

class UIElement:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.scripts = []
        self.call_update = True
        self.is_held = False

    def attach(self, file_path, context):
        script = Script(self, file_path, context)
        script.init_instance()
        self.scripts.append(script)

    def init_scripts(self):
        for script in self.scripts:
            script.init_instance()

    def update_internal(self, mouse_down_pos, mouse_pos, mouse_pressed):
        if not self.call_update:
            return

        held_before_update = self.is_held

        self.update_scripts(mouse_pos)

        if mouse_pos is not None and self.is_inside(mouse_pos):
            self.on_hover(mouse_pos)

        if mouse_down_pos is not None and self.is_inside(mouse_down_pos):
            self.is_held = True
            self.on_click(mouse_down_pos)

        if self.is_held and mouse_pressed:
            if mouse_pos is not None and self.is_inside(mouse_pos):
                self.on_hold(mouse_pos)
                self.is_held = True
            else:
                self.is_held = False

        if not mouse_pressed:
            self.is_held = False

        if held_before_update and not self.is_held:
            self.on_release(mouse_pos)

    def on_release(self, mouse_pos):
        for script in self.scripts:
            if hasattr(script.instance, 'on_release'):
                script.instance.on_release(mouse_pos)

    def on_hold(self, mouse_pos):
        for script in self.scripts:
            if hasattr(script.instance, "on_hold"):
                script.instance.on_hold(mouse_pos)

    def update_scripts(self, mouse_pos):
        for script in self.scripts:
            if hasattr(script.instance, 'update'):
                script.update(mouse_pos)

    def is_inside(self, pos):
        half_size = self.size / 2
        obj_pos = self.pos
        return (obj_pos.x - half_size.x <= pos.x <= obj_pos.x + half_size.x) and \
            (obj_pos.y - half_size.y <= pos.y <= obj_pos.y + half_size.y)

    def on_click(self, mouse_pos):
        for script in self.scripts:
            if hasattr(script.instance, "on_click"):
                script.instance.on_click(mouse_pos)

    def on_hover(self, mouse_pos):
        for script in self.scripts:
            if hasattr(script.instance, "on_hover"):
                script.instance.on_hover(mouse_pos)

    def draw(self, screen, camera: Camera, mouse_down_pos, mouse_pos, mouse_pressed):
        pass

def circle_rect_collision(circle, rect):
    # rect.get_corners() returns [top_left, top_right, bottom_right, bottom_left]
    corners = rect.get_corners()
    xs = [p.x for p in corners]
    ys = [p.y for p in corners]
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)

    # Find the closest point on the rectangle to the circle's center
    closest_x = max(left, min(circle.pos.x, right))
    closest_y = max(top, min(circle.pos.y, bottom))

    # Distance from circle center to that point
    dx = circle.pos.x - closest_x
    dy = circle.pos.y - closest_y

    return (dx * dx + dy * dy) <= (circle.radius * circle.radius)
