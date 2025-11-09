import numpy as np
from itertools import product
from pyrr import Matrix44
import math

from .helper import Color, vector3d, Renderer, Script

class GameObject:
    def __init__(self, name):
        self.name = name
        self.scripts = []

    def update(self, dt):
        for script in self.scripts:
            script.update(dt)

    def draw(self, renderer: Renderer):
        pass

    def attach(self, file_path, context):
        script = Script(self, file_path, context)
        script.init_instance()
        self.scripts.append(script)

    def init_scripts(self):
        for script in self.scripts:
            script.init_instance()

class Cuboid(GameObject):
    def __init__(self, pos: vector3d = vector3d.zero,
                 size: vector3d = vector3d(5),
                 color: Color = Color.green,
                 name: str = "Cuboid",
                 rotation: vector3d = vector3d.zero):
        super().__init__(name)
        self.name = name
        self.pos = pos
        self.size = size
        self.color = color
        self.rotation = rotation
        self.visible = True

        self.faces = [
            [0, 1, 3, 2],
            [4, 6, 7, 5],
            [0, 4, 5, 1],
            [2, 3, 7, 6],
            [0, 2, 6, 4],
            [1, 5, 7, 3],
        ]

    def get_rotation_matrix(self):
        """Return 3x3 rotation matrix (without translation)."""
        return Matrix44.from_eulers((
            math.radians(self.rotation.x),
            math.radians(self.rotation.y),
            math.radians(self.rotation.z)
        )).transpose()[:3, :3]  # extract 3x3 rotation

    def get_corners(self):
        """Return the 8 corners of the cuboid with rotation applied."""
        corners = []
        half_size = self.size / 2
        rot = self.get_rotation_matrix()

        for dx, dy, dz in product([-1, 1], repeat=3):
            local = np.array([dx * half_size.x, dy * half_size.y, dz * half_size.z])
            rotated = rot @ local
            world = self.pos + vector3d(*rotated)
            corners.append(world)

        return corners

    def is_point_in(self, point: vector3d) -> bool:
        """
        Checks if a point is inside the cuboid, accounting for full 3D rotation.
        """
        # Convert to numpy for math
        p = np.array([point.x, point.y, point.z])
        center = np.array([self.pos.x, self.pos.y, self.pos.z])
        half = np.array([self.size.x / 2, self.size.y / 2, self.size.z / 2])

        # Get inverse rotation matrix (undo rotation)
        rot = self.get_rotation_matrix()
        inv_rot = rot.T  # inverse of rotation matrix is its transpose

        # Transform point into cuboid's local coordinate system
        local_point = inv_rot @ (p - center)

        # Inside check in local space
        return np.all(np.abs(local_point) <= half + 1e-6)

    def draw(self, renderer: Renderer):
        if not self.visible:
            return
        corners = self.get_corners()
        for face_idx in self.faces:
            renderer.render_quad(
                corners[face_idx[0]],
                corners[face_idx[1]],
                corners[face_idx[2]],
                corners[face_idx[3]],
                color=self.color
            )

class Sphere(GameObject):
    def __init__(self, pos: vector3d = vector3d.zero,
                 radius: float = 5,
                 color: Color = Color.green,
                 segments: int = 32,
                 rings: int = 16,
                 name: str = "Sphere"):
        super().__init__(name)
        self.name = name
        self.pos = pos
        self.radius = radius
        self.color = color
        self.segments = segments
        self.rings = rings
        self.visible = True

    def is_point_in(self, point: vector3d) -> bool:
        dx = point.x - self.pos.x
        dy = point.y - self.pos.y
        dz = point.z - self.pos.z
        distance_squared = dx*dx + dy*dy + dz*dz
        return distance_squared <= self.radius * self.radius

    def draw(self, renderer: Renderer):
        if not self.visible:
            return
        renderer.render_sphere(self.pos, self.radius, self.color, self.segments, self.rings)

class Cylinder(GameObject):
    def __init__(self, pos: vector3d = vector3d.zero,
                 length: float = 2,
                 radius: float = 0.5,
                 color: Color = Color.light_yellow,
                 segments: int = 32,
                 rotation: vector3d = vector3d.zero,
                 name: str = "Cylinder"):
        super().__init__(name)
        self.name = name
        self.pos = pos
        self.length = length
        self.radius = radius
        self.color = color
        self.segments = segments
        self.rotation = rotation  # Euler angles in degrees
        self.visible = True

    def get_rotation_matrix(self):
        rx, ry, rz = math.radians(self.rotation.x), math.radians(self.rotation.y), math.radians(self.rotation.z)
        cx, sx = math.cos(rx), math.sin(rx)
        cy, sy = math.cos(ry), math.sin(ry)
        cz, sz = math.cos(rz), math.sin(rz)
        # Rotation matrices
        Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
        Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
        Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
        return Rz @ Ry @ Rx  # apply in XYZ order

    def is_point_in(self, point: vector3d, eps=1e-9) -> bool:
        p = np.array([point.x, point.y, point.z])
        center = np.array([self.pos.x, self.pos.y, self.pos.z])

        # Transform point into cylinder local space
        R = self.get_rotation_matrix()
        invR = R.T  # inverse rotation
        local = invR @ (p - center)

        # Check axial bounds (Y axis)
        half_length = self.length / 2
        if not (-half_length - eps <= local[1] <= half_length + eps):
            return False

        # Check radial distance in XZ plane
        radial_dist_sq = local[0]**2 + local[2]**2
        return radial_dist_sq <= (self.radius + eps)**2

    def draw(self, renderer: Renderer):
        if not self.visible:
            return
        renderer.render_cylinder(center=self.pos, height=self.length, radius=self.radius,
                                 color=self.color, segments=self.segments, rotation=self.rotation)
