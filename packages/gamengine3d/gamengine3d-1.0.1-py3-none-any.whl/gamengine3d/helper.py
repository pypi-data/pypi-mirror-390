import sys
import importlib.util
import math
import moderngl
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
import importlib.resources as pkg_resources
import numpy as np
from pyrr import Matrix44
import os

class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget(owner)

class vector3d:
    def __init__(self, x, y=None, z=None):
        self.x = x
        self.y = y
        self.z = z

        if y is None and z is None:
            self.y = self.x
            self.z = self.x
        elif z is None:
            self.z = 0.0

    @property
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    @property
    def sqr_magnitude(self):
        return self.x**2 + self.y**2 + self.z**2

    def normalize(self):
        magnitude = self.magnitude
        if magnitude != 0:
            self.x /= magnitude
            self.y /= magnitude
            self.z /= magnitude

    @property
    def normalized(self):
        magnitude = self.magnitude
        if magnitude == 0:
            return vector3d(0, 0, 0)
        return vector3d(self.x / magnitude, self.y / magnitude, self.z / magnitude)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return vector3d(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
            )

    def __add__(self, other):
        if isinstance(other, vector3d):
            return vector3d(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return vector3d(self.x + other, self.y + other, self.z + other)

    def __sub__(self, other):
        if isinstance(other, vector3d):
            return vector3d(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            return vector3d(self.x - other, self.y - other, self.z - other)

    def __mul__(self, other):
        if isinstance(other, vector3d):
            return vector3d(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            return vector3d(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        if isinstance(other, vector3d):
            return vector3d(self.x / other.x, self.y / other.y, self.z / other.z)
        else:
            return vector3d(self.x / other, self.y / other, self.z / other)

    def totuple(self):
        return (self.x, self.y, self.z)

    def __radd__(self, other):
        return vector3d(self.x + other, self.y + other, self.z + other)

    def __rsub__(self, other):
        return vector3d(self.x - other, self.y - other, self.z - other)

    def __rtruediv__(self, other):
        return vector3d(self.x / other, self.y / other, self.z / other)

    def __rmul__(self, other):
        return vector3d(self.x * other, self.y * other, self.z * other)

    @classmethod
    def fromtuple(cls, tuple):
        return cls(*tuple)

    def __repr__(self):
        return f"vector3d({self.x}, {self.y}, {self.z})"

    def copy(self):
        return vector3d(self.x, self.y, self.z)

    def __neg__(self):
        return vector3d(-self.x, -self.y, -self.z)

    @classproperty
    def up(cls):
        return cls(0, 1, 0)

    @classproperty
    def down(cls):
        return cls(0, -1, 0)

    @classproperty
    def right(cls):
        return cls(1, 0, 0)

    @classproperty
    def left(cls):
        return cls(-1, 0, 0)

    @classproperty
    def forward(cls):
        return cls(0, 0, 1)

    @classproperty
    def back(cls):
        return cls(0, 0, -1)

    @classproperty
    def one(cls):
        return cls(1, 1, 1)

    @classproperty
    def zero(cls):
        return cls(0, 0, 0)

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
    def light_red(cls): return cls(253, 89, 111)

    @classproperty
    def light_green(cls): return cls(0, 190, 160)

    @classproperty
    def light_yellow(cls): return cls(254, 208, 95)

    @classproperty
    def orange(cls): return cls(254, 166, 93)

    @classproperty
    def light_blue(cls): return cls(109, 154, 218)

class Light:
    def __init__(self, position: vector3d, color: Color, intensity: float = 1.0, show=False, name="Light"):
        self.position = position
        self.color = color
        self.intensity = intensity
        self.show = show
        self.name = name

class Renderer:
    def __init__(self, width=800, height=600, flags=DOUBLEBUF | OPENGL):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), flags)
        self.ctx = moderngl.create_context()
        self.lights = []
        self.width = width
        self.height = height

        self.ambient = 0.2

        self.ctx.enable(moderngl.DEPTH_TEST)

        self.prog = self._load_shader("default.vert", "default.frag")
        self.prog["model"].write(np.eye(4, dtype="f4").tobytes())

        self.proj = Matrix44.perspective_projection(60.0, width / height, 0.1, 100.0)
        self.view = Matrix44.look_at(
            eye=(3.0, 2.0, 3.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0)
        )

        self.mvp = self.proj * self.view
        self.prog["mvp"].write(self.mvp.astype("f4").tobytes())
        self.prog["ambient"].value = self.ambient

    def resize(self, width, height):
        self.width = width
        self.height = height
        pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF | (
            pygame.RESIZABLE if self.width and self.height else 0))
        self.ctx.viewport = (0, 0, width, height)

        self.proj = Matrix44.perspective_projection(60.0, width / height, 0.1, 100.0)
        self.mvp = self.proj * self.view
        self.prog["mvp"].write(self.mvp.astype("f4").tobytes())

    def add_light(self, light: Light):
        self.lights.append(light)

    def _compute_normal(self, p1, p2, p3):
        u = p2 - p1
        v = p3 - p1
        return u.cross(v).normalized

    def render_plane(self, p1, p2, p3, color):
        normal = self._compute_normal(p1, p2, p3)

        vertices = np.array([
            *p1.totuple(), *color.to_rgb(), *normal.totuple(),
            *p2.totuple(), *color.to_rgb(), *normal.totuple(),
            *p3.totuple(), *color.to_rgb(), *normal.totuple()
        ], dtype="f4")

        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.vertex_array(
            self.prog,
            [(vbo, "3f 3f 3f", "in_vert", "in_color", "in_normal")]
        )

        self._send_lights()
        vao.render()
        vao.release()
        vbo.release()

    def render_quad(self, p1, p2, p3, p4, color):
        normal = self._compute_normal(p1, p2, p3)

        vertices = np.array([
            *p1.totuple(), *color.to_rgb(), *normal.totuple(),
            *p2.totuple(), *color.to_rgb(), *normal.totuple(),
            *p3.totuple(), *color.to_rgb(), *normal.totuple(),
            *p1.totuple(), *color.to_rgb(), *normal.totuple(),
            *p3.totuple(), *color.to_rgb(), *normal.totuple(),
            *p4.totuple(), *color.to_rgb(), *normal.totuple()
        ], dtype="f4")

        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.vertex_array(
            self.prog,
            [(vbo, "3f 3f 3f", "in_vert", "in_color", "in_normal")]
        )

        self._send_lights()
        vao.render()
        vao.release()
        vbo.release()

    def render_sphere(self, center, radius, color, segments=32, rings=16):
        vertices = []
        normals = []

        for i in range(rings):
            theta1 = math.pi * i / rings
            theta2 = math.pi * (i + 1) / rings

            for j in range(segments):
                phi1 = 2 * math.pi * j / segments
                phi2 = 2 * math.pi * (j + 1) / segments

                p1 = vector3d(
                    radius * math.sin(theta1) * math.cos(phi1),
                    radius * math.cos(theta1),
                    radius * math.sin(theta1) * math.sin(phi1)
                ) + center

                p2 = vector3d(
                    radius * math.sin(theta2) * math.cos(phi1),
                    radius * math.cos(theta2),
                    radius * math.sin(theta2) * math.sin(phi1)
                ) + center

                p3 = vector3d(
                    radius * math.sin(theta2) * math.cos(phi2),
                    radius * math.cos(theta2),
                    radius * math.sin(theta2) * math.sin(phi2)
                ) + center

                p4 = vector3d(
                    radius * math.sin(theta1) * math.cos(phi2),
                    radius * math.cos(theta1),
                    radius * math.sin(theta1) * math.sin(phi2)
                ) + center

                for tri in [(p1, p2, p3), (p1, p3, p4)]:
                    n1 = (tri[0] - center).normalized
                    n2 = (tri[1] - center).normalized
                    n3 = (tri[2] - center).normalized

                    vertices.extend([
                        *tri[0].totuple(), *color.to_rgb(), *n1.totuple(),
                        *tri[1].totuple(), *color.to_rgb(), *n2.totuple(),
                        *tri[2].totuple(), *color.to_rgb(), *n3.totuple(),
                    ])

        vertices = np.array(vertices, dtype="f4")

        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.vertex_array(
            self.prog,
            [(vbo, "3f 3f 3f", "in_vert", "in_color", "in_normal")]
        )

        self._send_lights()
        vao.render()
        vao.release()
        vbo.release()


    def render_cylinder(self, center, height, radius, color, segments=32, rotation=vector3d.zero):
        vertices = []

        half_h = height / 2.0

        rx, ry, rz = map(math.radians, (rotation.x, rotation.y, rotation.z))

        rot_x = np.array([
            [1, 0, 0],
            [0, math.cos(rx), -math.sin(rx)],
            [0, math.sin(rx),  math.cos(rx)]
        ], dtype="f4")

        rot_y = np.array([
            [ math.cos(ry), 0, math.sin(ry)],
            [0, 1, 0],
            [-math.sin(ry), 0, math.cos(ry)]
        ], dtype="f4")

        rot_z = np.array([
            [math.cos(rz), -math.sin(rz), 0],
            [math.sin(rz),  math.cos(rz), 0],
            [0, 0, 1]
        ], dtype="f4")

        # Combined rotation matrix (Z * Y * X)
        rotation_matrix = rot_z @ rot_y @ rot_x

        def apply_rotation(v: vector3d):
            vec = np.array([[v.x], [v.y], [v.z]], dtype="f4")
            rotated = rotation_matrix @ vec
            return vector3d(rotated[0][0], rotated[1][0], rotated[2][0])

        for i in range(segments):
            theta1 = 2 * math.pi * i / segments
            theta2 = 2 * math.pi * (i + 1) / segments

            x1, z1 = radius * math.cos(theta1), radius * math.sin(theta1)
            x2, z2 = radius * math.cos(theta2), radius * math.sin(theta2)

            # Cylinder face vertices
            p1 = vector3d(x1, -half_h, z1)
            p2 = vector3d(x2, -half_h, z2)
            p3 = vector3d(x2, half_h, z2)
            p4 = vector3d(x1, half_h, z1)

            # Apply rotation
            p1 = apply_rotation(p1) + center
            p2 = apply_rotation(p2) + center
            p3 = apply_rotation(p3) + center
            p4 = apply_rotation(p4) + center

            n1 = apply_rotation(vector3d(x1, 0, z1).normalized)
            n2 = apply_rotation(vector3d(x2, 0, z2).normalized)

            # Side faces
            vertices.extend([
                *p1.totuple(), *color.to_rgb(), *n1.totuple(),
                *p2.totuple(), *color.to_rgb(), *n2.totuple(),
                *p3.totuple(), *color.to_rgb(), *n2.totuple(),

                *p1.totuple(), *color.to_rgb(), *n1.totuple(),
                *p3.totuple(), *color.to_rgb(), *n2.totuple(),
                *p4.totuple(), *color.to_rgb(), *n1.totuple(),
            ])

            # Base
            base_normal = apply_rotation(vector3d(0, -1, 0))
            vertices.extend([
                *apply_rotation(vector3d(0, -half_h, 0) + center).totuple(), *color.to_rgb(), *base_normal.totuple(),
                *p2.totuple(), *color.to_rgb(), *base_normal.totuple(),
                *p1.totuple(), *color.to_rgb(), *base_normal.totuple(),
            ])

            # Top
            top_normal = apply_rotation(vector3d(0, 1, 0))
            vertices.extend([
                *apply_rotation(vector3d(0, half_h, 0) + center).totuple(), *color.to_rgb(), *top_normal.totuple(),
                *p4.totuple(), *color.to_rgb(), *top_normal.totuple(),
                *p3.totuple(), *color.to_rgb(), *top_normal.totuple(),
            ])

        vertices = np.array(vertices, dtype="f4")
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.vertex_array(
            self.prog,
            [(vbo, "3f 3f 3f", "in_vert", "in_color", "in_normal")]
        )

        self._send_lights()
        vao.render()
        vao.release()
        vbo.release()

    def _send_lights(self):
        max_lights = 8
        num_lights = min(len(self.lights), max_lights)
        self.prog["num_lights"].value = num_lights
        self.prog["ambient"].value = self.ambient
        for i in range(num_lights):
            light = self.lights[i]
            self.prog[f"lights[{i}].position"].value = light.position.totuple()
            self.prog[f"lights[{i}].color"].value = tuple(c / 255 for c in light.color.to_rgb())
            self.prog[f"lights[{i}].intensity"].value = light.intensity

    def clear(self, color=Color(26, 26, 31)):
        color_f = np.array(color.to_rgb(), dtype="f4") / 255.0
        self.ctx.clear(*color_f, depth=1.0)

    def swap(self):
        pygame.display.flip()

    def quit(self):
        pygame.quit()

    def _load_shader(self, vert_name, frag_name):
        vert_src = pkg_resources.read_text(f"{__package__}.shaders", "default.vert")
        frag_src = pkg_resources.read_text(f"{__package__}.shaders", "default.frag")
        return self.ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)

class Camera:
    def __init__(self, position=None, target=None, up=None, fov=60.0, aspect_ratio=4/3, near=0.1, far=100.0, orbiting=True):
        self.orbiting = orbiting  # New: toggle automatic look-at behavior
        self.target = target or vector3d(0, 0, 0)
        self.up = up or vector3d.up
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        # Compute spherical coordinates from initial position
        pos = position or vector3d(3, 2, 3)
        if self.orbiting:
            self._update_spherical(pos)
        self.position = pos

        self._update_position()

    def move_to(self, new_position: vector3d):
        """
        Move the camera to a new position.
        If orbiting is enabled, updates spherical coordinates.
        If orbiting is disabled, just sets position directly.
        """
        self.position = new_position
        if self.orbiting:
            self._update_spherical(new_position)
        self._update_position()

    def set_orbiting(self, orbiting: bool):
        """Enable or disable automatic look-at behavior."""
        self.orbiting = orbiting

    def _update_spherical(self, pos):
        """Convert position to spherical coordinates relative to target."""
        dir_vec = pos - self.target
        self.radius = dir_vec.magnitude
        self.azimuth = math.atan2(dir_vec.z, dir_vec.x)  # yaw
        self.elevation = math.asin(dir_vec.y / self.radius)  # pitch

    def _update_position(self):
        """Update Cartesian position and view/projection matrices."""
        if self.orbiting:
            x = self.radius * math.cos(self.elevation) * math.cos(self.azimuth)
            y = self.radius * math.sin(self.elevation)
            z = self.radius * math.cos(self.elevation) * math.sin(self.azimuth)
            self.position = self.target + vector3d(x, y, z)

        look_at = self.target if self.orbiting else self.position + getattr(self, "look_dir", vector3d(0, 0, -1))

        self.view_matrix = Matrix44.look_at(
            self.position.totuple(),
            look_at.totuple(),
            self.up.totuple()
        )
        self.projection_matrix = Matrix44.perspective_projection(
            self.fov, self.aspect_ratio, self.near, self.far
        )

    def rotate_around_target(self, delta_azimuth_degrees, delta_elevation_degrees):
        if not self.orbiting:
            return  # rotation disabled in free mode

        self.azimuth += math.radians(delta_azimuth_degrees)
        self.elevation += math.radians(delta_elevation_degrees)

        # Handle elevation wrapping to allow full rotation without flipping
        while self.elevation > math.pi / 2:
            self.elevation = math.pi - self.elevation
            self.azimuth += math.pi
            self.up = -self.up  # flip up vector

        while self.elevation < -math.pi / 2:
            self.elevation = -math.pi - self.elevation
            self.azimuth += math.pi
            self.up = -self.up  # flip up vector

        self._update_position()

    def zoom(self, amount):
        self.radius = max(self.radius - amount, 0.01)
        self._update_position()

    def update_renderer(self, renderer: Renderer):
        renderer.view = self.view_matrix
        renderer.proj = self.projection_matrix
        renderer.mvp = renderer.proj * renderer.view
        renderer.prog["mvp"].write(renderer.mvp.astype("f4").tobytes())

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

    def run(self, func_name):
        if self.instance is None:
            return

        func = getattr(self.instance, func_name)
        func()

class EngineError(Exception):
    pass
