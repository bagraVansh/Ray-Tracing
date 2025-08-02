from __future__ import annotations
from math import sqrt, tan, radians
from numpy import zeros, uint8
from PIL import Image


class Vector3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other: Vector3) -> Vector3:
        x_comp = self.x + other.x
        y_comp = self.y + other.y
        z_comp = self.z + other.z
        return Vector3(x_comp, y_comp, z_comp)

    def __neg__(self) -> Vector3:
        return Vector3(-self.x, -self.y, -self.z)

    def __sub__(self, other: Vector3) -> Vector3:
        x_comp = self.x - other.x
        y_comp = self.y - other.y
        z_comp = self.z - other.z
        return Vector3(x_comp, y_comp, z_comp)

    def __mul__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        raise TypeError("Unsupported operand type")

    __rmul__ = __mul__  # to support scalar * vec

    def __truediv__(self, scalar: float) -> Vector3:
        if scalar == 0:
            raise ValueError("Division by zero")
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __itruediv__(self, scalar: float) -> Vector3:
        if scalar == 0:
            raise ValueError("Division by zero")
        self.x = self.x / scalar
        self.y = self.y / scalar
        self.z = self.z / scalar
        return self

    def dot(self, other: Vector3) -> float:
        x_comp = self.x * other.x
        y_comp = self.y * other.y
        z_comp = self.z * other.z
        return x_comp + y_comp + z_comp

    def cross(self, other: Vector3) -> Vector3:
        x_comp = (self.y * other.z) - (self.z * other.y)
        y_comp = -(self.x * other.z) + (self.z * other.x)
        z_comp = (self.x * other.y) - (self.y * other.x)
        return Vector3(x_comp, y_comp, z_comp)

    def length(self) -> float:
        x2 = self.x ** 2
        y2 = self.y ** 2
        z2 = self.z ** 2
        length = sqrt(x2 + y2 + z2)
        return length

    def normalize(self) -> Vector3:
        length = self.length()
        if length != 0:
            x = self.x / length
            y = self.y / length
            z = self.z / length
            return Vector3(x, y, z)
        return Vector3(0, 0, 0)

    def reflect(self, normal: Vector3) -> Vector3:
        return self - 2 * self.dot(normal) * normal

    def rgb(self) -> list[uint8]:
        # Clamp values to [0, 1] range before converting
        r = max(0, min(1, self.x))
        g = max(0, min(1, self.y))
        b = max(0, min(1, self.z))
        return [uint8(r * 255), uint8(g * 255), uint8(b * 255)]

    def __str__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return self.__str__()


class Ray:
    def __init__(self, origin: Vector3, direction: Vector3):
        self.origin = origin
        self.direction = direction

    def point(self, t: float) -> Vector3:
        return self.origin + (self.direction * t)

    def color(self, scene: Scene, depth: int, max_depth=3):
        epsilon = 0.01
        hit_point, obj = scene.hit(self)
        if hit_point is None or depth >= max_depth:
            alpha = 0.5 * (self.direction.y + 1)
            color = Vector3(1, 1, 1) * (1 - alpha) + Vector3(0.5, 0.7, 1.0) * alpha
            return color
        normal = obj.normal_vector(hit_point)
        view_dir = -self.direction.normalize()
        color = Vector3(0, 0, 0)

        for light in scene.lighting:
            light_dir = (light.position - hit_point).normalize()

            # SHADOW CHECK
            """
            shadow_ray = Ray(hit_point + normal * epsilon, light_dir)
            if in_shadow(shadow_ray):
                continue  # skip this light
            """
            i_diff = max(normal.dot(light_dir), 0)
            diffuse = obj.material.diffuse_color * light.color * i_diff

            reflect_dir = (-view_dir).reflect(normal)
            i_spec = max(reflect_dir.dot(view_dir), 0) ** obj.material.shininess
            specular = obj.material.specular_color * light.color * i_spec
            try:
                color = color + diffuse + specular
            except TypeError:
                print(f"Color: {color}\tDiffuse:{diffuse}\tSpecular:{specular}")

        if obj.material.reflectivity > 0:
            reflect_dir = self.direction.reflect(normal)
            ref_ray = Ray(hit_point + normal * epsilon, reflect_dir)
            ref_color = ref_ray.color(scene, depth + 1)
            color = Ray.mix_color(color, ref_color, obj.material.reflectivity)
        return color

    @staticmethod
    def mix_color(a, b, t):
        return (1 - t) * a + t * b


class Material:
    def __init__(self,
                 diffuse_color=Vector3(1, 1, 1),
                 specular_color=Vector3(1, 1, 1),
                 ambient_color=None,
                 shininess=32,
                 reflectivity=0.0,
                 transparency=0.0,
                 refractive_index=1.0,
                 emission_color=(0, 0, 0)):
        self.diffuse_color = diffuse_color
        self.specular_color = specular_color
        self.ambient_color = ambient_color if ambient_color else diffuse_color
        self.shininess = shininess

        self.reflectivity = reflectivity
        self.transparency = transparency
        self.refractive_index = refractive_index

        self.emission_color = emission_color


class Light:
    def __init__(self, position: Vector3, color=Vector3(1, 1, 1), intensity=1.0):
        self.position = position
        self.color = color
        self.intensity = intensity


class Sphere:
    def __init__(self, center: Vector3, radius: float, material: Material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray: Ray) -> float | None:
        oc = ray.origin - self.center

        a = ray.direction.dot(ray.direction)
        b = 2 * oc.dot(ray.direction)
        c = oc.dot(oc) - (self.radius ** 2)
        d = b ** 2 - 4 * a * c

        if d < 0:
            return None
        sq = sqrt(d)
        t1 = (-b - sq) / (2 * a)
        t2 = (-b + sq) / (2 * a)
        if t1 > 0.001:
            return t1
        elif t2 > 0.001:
            return t2

        return None

    def normal_vector(self, point: Vector3) -> Vector3:
        normal = (point - self.center).normalize()
        return normal


class Camera:
    def __init__(self, position: Vector3, target: Vector3, fov: float, width: int,
                 height: int):  # Note: width, height order
        self.position = position
        self.width = width
        self.height = height
        self.aspect_ratio = float(width) / height  # CORRECTED: width/height

        self.screen_distance = 1
        self.screen_width = 2 * tan(radians(fov / 2))
        self.screen_height = self.screen_width / self.aspect_ratio  # CORRECTED: divide by aspect ratio

        self.forward = (target - position).normalize()
        world_up = Vector3(0, 1, 0)
        self.right = world_up.cross(self.forward).normalize()

        if self.right.length() < 0.001:
            world_up = Vector3(0, 0, 1)
            self.right = world_up.cross(self.forward).normalize()

        self.up = self.forward.cross(self.right).normalize()

    def get_ray(self, x: float, y: float) -> Ray:
        screen_x = (x * 2 - 1) * self.screen_width / 2
        screen_y = (1 - y * 2) * self.screen_height / 2

        ray_direction = (self.right * screen_x +
                         self.up * screen_y +
                         self.forward * self.screen_distance).normalize()

        return Ray(self.position, ray_direction)


class Scene:
    def __init__(self, lighting: list[Light], objects: list[Sphere]):
        self.lighting = lighting
        self.objects = objects

    def add_object(self, obj: Sphere):
        self.objects.append(obj)

    def add_lighting(self, light: Light):
        self.lighting.append(light)

    # def hit(self, ray: Ray):
    #     closest_t = float('inf')
    #     closest_obj = None
    #     for obj in self.objects:
    #         t = obj.intersect(ray)
    #         if t and t < closest_t:
    #             closest_t, closest_obj = t, obj
    #     if closest_obj:
    #         hit_point = ray.point(closest_t)
    #         return hit_point, closest_obj
    #     return None, None

    def hit(self, ray: Ray):
        closest_t = float('inf')
        closest_obj = None

        for obj in self.objects:
            t = obj.intersect(ray)
            if t is not None and t < closest_t:
                closest_t = t
                closest_obj = obj

        if closest_obj is not None:
            hit_point = ray.point(closest_t)
            return hit_point, closest_obj
        return None, None


def render_scene():
    width, height = 1000, 800
    camera_pos = Vector3(0, 0, 0)
    target = Vector3(0, 0, 5)
    camera = Camera(camera_pos, target, 75, width, height)
    plastic_red = Material(
        diffuse_color=Vector3(1.0, 0.0, 0.0),  # Red plastic
        specular_color=Vector3(1.0, 1.0, 1.0),  # White specular highlight
        shininess=64,  # Moderate shininess
        reflectivity=0.05,  # Slight reflectivity
        transparency=0.0,  # Opaque
        refractive_index=1.0  # Not relevant since it's opaque
    )
    glass_blue = Material(
        diffuse_color=Vector3(0.1, 0.2, 0.9),
        specular_color=Vector3(1.0, 1.0, 1.0),
        shininess=128,
        reflectivity=0.1,
        transparency=0.9,
        refractive_index=1.52
    )
    chrome_silver = Material(
        diffuse_color=Vector3(0.6, 0.6, 0.6),
        specular_color=Vector3(1.0, 1.0, 1.0),
        shininess=256,
        reflectivity=0.9,
        transparency=0.0,
        refractive_index=1.0
    )

    sphere1 = Sphere(Vector3(0, 0, 6), 1.0, glass_blue)
    sphere2 = Sphere(Vector3(-1.8, -0.5, 4.5), 0.7, plastic_red)
    sphere3 = Sphere(Vector3(1.8, -0.5, 5), 0.7, chrome_silver)

    light1 = Light(Vector3(5, 5, -2), Vector3(1, 1, 1), 1.2)
    light2 = Light(Vector3(-4, 2, -1), Vector3(0.6, 0.6, 1), 0.5)
    light3 = Light(Vector3(0, 5, 10), Vector3(1, 1, 1), 0.3)

    scene = Scene([light1, light2, light3], [sphere1, sphere2, sphere3])
    image_buffer = zeros((height, width, 3), dtype=uint8)

    for y in range(height):
        if y % 50 == 0:  # Progress indicator
            print(f"  Row {y}/{height}")

        for x in range(width):
            # Generate ray from camera through pixel
            total_color = Vector3(0, 0, 0)
            sample = 2
            for sy in range(sample):
                for sx in range(sample):
                    offset_x = (sx + 0.5) / sample
                    offset_y = (sy + 0.5) / sample
                    u = (x + offset_x) / width
                    v = (y + offset_y) / height
                    ray = camera.get_ray(u, v)
                    # Get pixel color
                    color = ray.color(scene, 2)
                    total_color = total_color + color
            total_color /= (sample ** 2)
            image_buffer[y][x] = total_color.rgb()

    return image_buffer


if __name__ == "__main__":
    image_array = render_scene()
    # Create PIL image from array
    image = Image.fromarray(image_array)
    # Save the image
    image.save("Raytracer_output.png")
    image.show("Raytracer_output.png")
