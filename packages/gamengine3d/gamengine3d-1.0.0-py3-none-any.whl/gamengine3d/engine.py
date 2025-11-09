from itertools import product
from pyrr import Matrix44
from .context import Context
import pygame
from .game_objects import Cuboid, GameObject, Sphere
from .helper import Renderer, vector3d, Color, Camera, Light, EngineError, Script
import math

class Engine:
    def __init__(self, width=500, height=500, resizable=True, name="GamEngine3d", background_color=Color.light_grey, ambient_light=.2):
        self.width = width
        self.height = height
        self.resizable = resizable
        self.window_name = name
        self.background_color = background_color
        self.scripts = []

        flags = pygame.DOUBLEBUF | pygame.OPENGL
        if self.resizable:
            flags |= pygame.RESIZABLE

        pygame.display.set_caption(self.window_name)
        self.renderer = Renderer(width, height, flags=flags)
        self.renderer.ambient = ambient_light
        self.clock = pygame.time.Clock()

        self.camera = Camera(position=vector3d(0, 1.5, 3),
                             target=vector3d(0, 0, 0),
                             aspect_ratio=self.width / self.height)

        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.3
        self.pan_sensitivity = 0.005
        self.active_button = None

        self.gameobjects = []

        self.context = Context()

        self.context.functions.draw_cube = self.draw_cuboid
        self.context.functions.draw_sphere = self.draw_sphere
        self.context.functions.add_light = self.add_light
        self.context.functions.add_object = self.add_object
        self.context.functions.draw_cylinder = self.draw_cylinder
        self.context.functions.get_game_object = self.get_object
        self.context.functions.is_colliding = self.is_colliding
        self.context.functions.remove_light = self.remove_light
        self.context.functions.remove_object = self.remove_object

        self.context.game_objects = self.gameobjects
        self.context.engine = self
        self.context.camera = self.camera
        self.context.renderer = self.renderer
        self.context.clock = self.clock

        self.context.lights = self.renderer.lights

    def run(self, fps=60, dynamic_view=True):
        running = True
        self.context.fps = fps
        keys_held = []
        self.context.keys_held = keys_held
        self.init_scripts()

        for script in self.scripts:
            script.run("on_start")

        while running:
            keys_pressed = []
            keys_released = []
            dt = self.clock.get_time() / 1000
            self.mouse_sensitivity = self.context.mouse_sensitivity
            self.pan_sensitivity = self.context.pan_sensitivity
            self.context.fps = self.clock.get_fps()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.resizable and event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.w, event.h
                    self.renderer.resize(self.width, self.height)
                    self.camera.aspect_ratio = self.width / self.height

                if dynamic_view:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button in (1, 3):  # Left or right
                            self.last_mouse_pos = pygame.mouse.get_pos()
                            self.active_button = event.button
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button in (1, 3):
                            self.last_mouse_pos = None
                            self.active_button = None

                    elif event.type == pygame.MOUSEMOTION:
                        if self.last_mouse_pos is not None:
                            x, y = pygame.mouse.get_pos()
                            dx = x - self.last_mouse_pos[0]
                            dy = y - self.last_mouse_pos[1]
                            self.last_mouse_pos = (x, y)

                            if self.active_button == 3:
                                self.camera.rotate_around_target(-dx * self.mouse_sensitivity, dy * self.mouse_sensitivity)

                            elif self.active_button == 1:
                                self._pan_camera(dx, dy)

                    elif event.type == pygame.MOUSEWHEEL:
                        self.camera.zoom(event.y * 0.5)

                if event.type == pygame.KEYDOWN:
                    key_name = pygame.key.name(event.key)
                    keys_pressed.append(key_name)
                    keys_held.append(key_name)

                elif event.type == pygame.KEYUP:
                    key_name = pygame.key.name(event.key)
                    keys_held.remove(key_name)
                    keys_released.append(key_name)

            self.context.keys_pressed = keys_pressed
            self.context.keys_released = keys_released
            self.context.update(dt)

            self.renderer.clear(self.background_color)
            self.camera.update_renderer(self.renderer)

            self.renderer.ambient = self.context.ambient_light

            for script in self.scripts:
                script.update(dt)

            for obj in self.gameobjects:
                obj.update(dt)
                obj.draw(self.renderer)

            if self.context.exit:
                running = False

            self.renderer.swap()
            self.clock.tick(fps)

        for script in self.scripts:
            script.run("on_exit")
        self.renderer.quit()

    def _pan_camera(self, dx, dy):
        forward = (self.camera.target - self.camera.position).normalized
        right = forward.cross(self.camera.up).normalized
        up = self.camera.up.normalized

        pan = (right * -dx + up * dy) * self.pan_sensitivity * self.camera.radius
        self.camera.target += pan
        self.camera.position += pan
        self.camera._update_position()

    def add_light(self, light):
        self.renderer.add_light(light)
        if light.show:
            self.add_object(Sphere(pos=light.position, color=light.color, radius=.1))

    def add_object(self, obj: GameObject):
        self.gameobjects.append(obj)

    def remove_object(self, name):
        obj = self.get_object(name)
        self.gameobjects.remove(obj)

    def remove_light(self, name):
        for light in self.renderer.lights:
            if light.name == name:
                self.renderer.lights.remove(light)
                return

        raise EngineError(f"No Light Object Named {name}")

    def get_object(self, name):
        for obj in self.gameobjects:
            if obj.name == name:
                return obj

        raise EngineError(f"Game Object with name {name} not found")

    def is_colliding(self, name1, name2):
        obj1 = self.get_object(name1)
        obj2 = self.get_object(name2)

        if not (isinstance(obj1, Cuboid) and isinstance(obj2, Cuboid)):
            raise NotImplementedError(f"Cylinder And Sphere Collision Not Implemented")

        corners = obj1.get_corners()
        for corner in corners:
            if obj2.is_point_in(corner):
                return True

        return False

    def draw_cuboid(self, pos: vector3d=vector3d.zero, size: vector3d=vector3d(2), rotation: vector3d=vector3d.zero, color: Color = Color.light_blue):
        faces = [
            [0, 1, 3, 2],
            [4, 6, 7, 5],
            [0, 4, 5, 1],
            [2, 3, 7, 6],
            [0, 2, 6, 4],
            [1, 5, 7, 3],
        ]

        half_size = size / 2

        rot_matrix = Matrix44.from_eulers((
            math.radians(rotation.x),
            math.radians(rotation.y),
            math.radians(rotation.z)
        ))

        corners = []
        for dx, dy, dz in product([-1, 1], repeat=3):
            local = vector3d(dx * half_size.x, dy * half_size.y, dz * half_size.z)

            rotated = vector3d(
                *(rot_matrix @ [local.x, local.y, local.z, 1.0])[:3]
            )

            world = pos + rotated
            corners.append(world)

        for face_idx in faces:
            self.renderer.render_quad(
                corners[face_idx[0]],
                corners[face_idx[1]],
                corners[face_idx[2]],
                corners[face_idx[3]],
                color=color
            )

    def draw_sphere(self, pos: vector3d=vector3d.zero, radius: int=2, color: Color=Color.light_red, segments=32, rings=16):
        self.renderer.render_sphere(center=pos, radius=radius, color=color, segments=segments, rings=rings)

    def draw_cylinder(self, pos: vector3d=vector3d.zero, length: int=2, radius: int=.5, color: Color=Color.light_yellow, segments: int=32, rotation: vector3d=vector3d.zero):
        self.renderer.render_cylinder(center=pos, height=length, radius=radius, color=color, segments=segments, rotation=rotation)

    def attach(self, path):
        script = Script(self, path, self.context)
        script.init_instance()
        self.scripts.append(script)

    def init_scripts(self):
        for script in self.scripts:
            script.init_instance()
