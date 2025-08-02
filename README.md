# Raytracer Implementation - Mathematical Documentation

## Overview

This is a complete 3D raytracer implementation in Python that renders spheres with realistic lighting, reflections, and anti-aliasing. The raytracer uses fundamental 3D graphics concepts including vector mathematics, ray-sphere intersection, lighting models, and coordinate system transformations.

## Core Mathematical Concepts

### 1. Vector Mathematics (`Vector3` Class)

The foundation of the raytracer is the 3D vector class that implements essential vector operations:

#### Vector Operations

**Addition and Subtraction:**
$$\vec{v_1} + \vec{v_2} = (x_1 + x_2, y_1 + y_2, z_1 + z_2)$$
$$\vec{v_1} - \vec{v_2} = (x_1 - x_2, y_1 - y_2, z_1 - z_2)$$

**Scalar Multiplication:**
$$k \cdot \vec{v} = (k \cdot x, k \cdot y, k \cdot z)$$

**Dot Product:**
$$\vec{v_1} \cdot \vec{v_2} = x_1x_2 + y_1y_2 + z_1z_2$$

The dot product is used for:
- Computing angles between vectors: $\cos(\theta) = \frac{\vec{v_1} \cdot \vec{v_2}}{|\vec{v_1}| \cdot |\vec{v_2}|}$
- Lighting calculations (surface normal · light direction)
- Reflection computations

**Cross Product:**

$$\vec{v_1} \times \vec{v_2} = \begin{pmatrix} y_1z_2 - z_1y_2 \\ z_1x_2 - x_1z_2 \\ x_1y_2 - y_1x_2 \end{pmatrix}$$

Used for:
- Creating orthogonal vectors
- Camera coordinate system setup
- Surface normal calculations

**Vector Length (Magnitude):**
$$|\vec{v}| = \sqrt{x^2 + y^2 + z^2}$$

**Vector Normalization:**
$$\hat{v} = \frac{\vec{v}}{|\vec{v}|} = \left(\frac{x}{|\vec{v}|}, \frac{y}{|\vec{v}|}, \frac{z}{|\vec{v}|}\right)$$

Creates a unit vector (length = 1) in the same direction.

**Vector Reflection:**
$$\vec{r} = \vec{v} - 2(\vec{v} \cdot \vec{n})\vec{n}$$

Where:
- $\vec{v}$ is the incident vector
- $\vec{n}$ is the surface normal (unit vector)
- $\vec{r}$ is the reflected vector

This formula reflects a vector across a surface defined by its normal.

### 2. Ray Mathematics (`Ray` Class)

A ray is defined parametrically as:
$$\vec{P}(t) = \vec{O} + t \cdot \vec{D}$$

Where:
- $\vec{O}$ is the ray origin (Vector3)
- $\vec{D}$ is the ray direction (normalized Vector3)
- $t$ is the parameter (distance along the ray)
- $\vec{P}(t)$ is any point on the ray

### 3. Ray-Sphere Intersection (`Sphere.intersect`)

The most critical geometric calculation in the raytracer is determining where a ray intersects a sphere.

#### Mathematical Derivation

A sphere is defined as:
$$|\vec{P} - \vec{C}|^2 = r^2$$

Where:
- $\vec{P}$ is any point on the sphere
- $\vec{C}$ is the sphere center
- $r$ is the sphere radius

Substituting the ray equation $\vec{P}(t) = \vec{O} + t \cdot \vec{D}$:
$$|\vec{O} + t \cdot \vec{D} - \vec{C}|^2 = r^2$$

Let $\vec{oc} = \vec{O} - \vec{C}$ (vector from sphere center to ray origin):
$$|\vec{oc} + t \cdot \vec{D}|^2 = r^2$$

Expanding the dot product:
$$(\vec{oc} + t \cdot \vec{D}) \cdot (\vec{oc} + t \cdot \vec{D}) = r^2$$
$$\vec{oc} \cdot \vec{oc} + 2t(\vec{oc} \cdot \vec{D}) + t^2(\vec{D} \cdot \vec{D}) = r^2$$

Since $\vec{D}$ is normalized, $\vec{D} \cdot \vec{D} = 1$:
$$|\vec{oc}|^2 + 2t(\vec{oc} \cdot \vec{D}) + t^2 = r^2$$

Rearranging into standard quadratic form $at^2 + bt + c = 0$:
$$t^2 + 2(\vec{oc} \cdot \vec{D})t + (|\vec{oc}|^2 - r^2) = 0$$

Where:
- $a = 1$ (since $\vec{D}$ is normalized)
- $b = 2(\vec{oc} \cdot \vec{D})$
- $c = |\vec{oc}|^2 - r^2$

#### Quadratic Solution

Using the quadratic formula:
$$t = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

The discriminant $\Delta = b^2 - 4ac$ determines:
- $\Delta < 0$: No intersection (ray misses sphere)
- $\Delta = 0$: One intersection (ray tangent to sphere)
- $\Delta > 0$: Two intersections (ray enters and exits sphere)

We take the smaller positive $t$ value as the first intersection point.

### 4. Surface Normal Calculation

For a sphere, the surface normal at any point $\vec{P}$ is:
$$\vec{n} = \frac{\vec{P} - \vec{C}}{|\vec{P} - \vec{C}|}$$

This gives a unit vector pointing outward from the sphere surface.

## Coordinate System Transformations

### Camera Coordinate System Setup

The camera establishes a local coordinate system for view transformation:

#### 1. Forward Vector (View Direction)
$$\vec{forward} = \frac{\vec{target} - \vec{camera_{position}}}{|\vec{target} - \vec{camera_{position}}|}$$

#### 2. Right Vector (Camera X-axis)
$$\vec{right} = \frac{\vec{world_{up}} \times \vec{forward}}{|\vec{world_{up}} \times \vec{forward}|}$$

Where $\vec{world_{up}}$ is typically $(0, 1, 0)$ (Y-up convention).

#### 3. Up Vector (Camera Y-axis)
$$\vec{up} = \frac{\vec{forward} \times \vec{right}}{|\vec{forward} \times \vec{right}|}$$

This creates an orthonormal basis (three mutually perpendicular unit vectors).

### Screen Space to World Space Transformation

#### Field of View and Screen Dimensions

The field of view (FOV) determines how much of the scene is visible. For a given horizontal FOV:

$$screen_{width} = 2 \cdot \tan\left(\frac{FOV}{2}\right)$$
$$screen_{height} = \frac{screen_{width}}{aspect_{ratio}}$$

Where:
$$aspect_{ratio} = \frac{image_{width}}{image_{height}}$$

#### Pixel to Screen Coordinate Mapping

For a pixel at position $(x, y)$ in the image:

1. **Normalize to [0, 1] range:**
   $$u = \frac{x}{image_{width}}, \quad v = \frac{y}{image_{height}}$$

2. **Convert to screen coordinates [-1, 1] range:**
   $$screen_x = (u \cdot 2 - 1) \cdot \frac{screen_{width}}{2}$$
   $$screen_y = (1 - v \cdot 2) \cdot \frac{screen_{height}}{2}$$
   
   Note: $(1 - v \cdot 2)$ flips the Y-axis since screen coordinates typically have Y increasing downward, while world coordinates have Y increasing upward.

#### Ray Direction Calculation

The ray direction in world space is:
$$\vec{ray_{direction}} = \frac{\vec{right} \cdot screen_x + \vec{up} \cdot screen_y + \vec{forward} \cdot screen_{distance}}{|\vec{right} \cdot screen_x + \vec{up} \cdot screen_y + \vec{forward} \cdot screen_{distance}|}$$

Where:
- $screen_{distance}$ is typically 1 (distance to the virtual screen)
- This creates a ray from the camera through the pixel location on the virtual screen

## Lighting Model (Phong Shading)

The raytracer implements the Phong lighting model with three components:

### 1. Diffuse Lighting (Lambertian Reflection)
$$I_{diffuse} = I_{light} \cdot material_{diffuse} \cdot \max(0, \vec{n} \cdot \vec{l})$$

Where:
- $\vec{n}$ is the surface normal
- $\vec{l}$ is the light direction (normalized)
- The $\max(0, ...)$ ensures no negative lighting

### 2. Specular Lighting (Phong Reflection)
$$I_{specular} = I_{light} \cdot material_{specular} \cdot \max(0, \vec{r} \cdot \vec{v})^{shininess}$$

Where:
- $\vec{r}$ is the reflection direction: $\vec{r} = \vec{l} - 2(\vec{l} \cdot \vec{n})\vec{n}$
- $\vec{v}$ is the view direction (toward camera)
- $shininess$ controls the size of the specular highlight

### 3. Total Lighting
$$I_{total} = I_{diffuse} + I_{specular}$$

Multiple lights are accumulated:
$$I_{final} = \sum_{i=1}^{N} (I_{diffuse,i} + I_{specular,i})$$

## Reflection Implementation

### Recursive Ray Tracing

When a surface has reflectivity > 0:

1. **Calculate reflection ray:**
   $$\vec{reflect_{direction}} = \vec{incident} - 2(\vec{incident} \cdot \vec{n})\vec{n}$$
   $$\vec{reflect_{origin}} = \vec{hit_{point}} + \vec{n} \cdot \epsilon$$
   
   The epsilon offset prevents self-intersection artifacts.

2. **Trace reflection ray recursively:**
   $$reflect_{color} = trace_{ray}(reflect_{ray}, depth + 1)$$

3. **Blend colors:**
   $$final_{color} = (1 - reflectivity) \cdot surface_{color} + reflectivity \cdot reflect_{color}$$

## Anti-Aliasing (Supersampling)

The raytracer implements 2×2 supersampling:

1. **For each pixel, cast multiple rays:**
   $$u_{sample} = \frac{x + \frac{s_x + 0.5}{samples}}{width}$$
   $$v_{sample} = \frac{y + \frac{s_y + 0.5}{samples}}{height}$$
   
   Where $s_x, s_y \in \{0, 1, ..., samples-1\}$

2. **Average the results:**
   $$final_{color} = \frac{1}{samples^2} \sum_{s_x=0}^{samples-1} \sum_{s_y=0}^{samples-1} color(u_{sample}, v_{sample})$$

This reduces jagged edges (aliasing) by sampling multiple points within each pixel.

## Color Space and Gamma

### RGB Color Representation

Colors are represented as Vector3 with components in [0, 1] range:
- $(1, 0, 0)$ = Pure red
- $(0, 1, 0)$ = Pure green  
- $(0, 0, 1)$ = Pure blue
- $(1, 1, 1)$ = White

### Color Clamping and Conversion

Before output, colors are:

1. **Clamped to [0, 1] range:**
   $$r_{clamped} = \max(0, \min(1, color_x))$$

2. **Converted to 8-bit integers:**
   $$pixel_{value} = \lfloor r_{clamped} \cdot 255 \rfloor$$

## Scene Organization

### Scene Graph Structure

The scene contains:
- **Objects**: List of renderable objects (spheres)
- **Lights**: List of light sources
- **Camera**: View transformation and projection

### Ray-Scene Intersection

For each ray, find the closest intersection:

$$t_{closest} = \min_{i} \{t_i : t_i = intersect(ray, object_i) \text{ and } t_i > \epsilon\}$$

Where $\epsilon > 0$ is a small value to prevent self-intersection.

## Performance Considerations

### Computational Complexity

**Per-pixel cost**: $O(objects \times lights \times reflection_{depth})$

**Total cost**: $O(width \times height \times samples^2 \times objects \times lights \times reflection_{depth})$

### Optimization Techniques Used

1. **Early ray termination**: Stop tracing after maximum depth
2. **Epsilon offsetting**: Prevent self-intersection using $\vec{origin} + \vec{n} \cdot \epsilon$
3. **Efficient vector operations**: Minimize object creation
4. **Supersampling**: Quality vs. performance trade-off

## Usage Example

```python
# Create scene
width, height = 1000, 800
camera = Camera(Vector3(0, 0, 0), Vector3(0, 0, 5), 75, width, height)

# Materials with different properties
red_plastic = Material(diffuse_color=Vector3(1, 0, 0), reflectivity=0.05)
blue_glass = Material(diffuse_color=Vector3(0.1, 0.2, 0.9), reflectivity=0.1)
chrome = Material(diffuse_color=Vector3(0.6, 0.6, 0.6), reflectivity=0.9)

# Objects
spheres = [
    Sphere(Vector3(0, 0, 6), 1.0, blue_glass),
    Sphere(Vector3(-1.8, -0.5, 4.5), 0.7, red_plastic),
    Sphere(Vector3(1.8, -0.5, 5), 0.7, chrome)
]

# Lighting
lights = [
    Light(Vector3(5, 5, -2), Vector3(1, 1, 1), 1.2),
    Light(Vector3(-4, 2, -1), Vector3(0.6, 0.6, 1), 0.5)
]

# Render
image_array = render_scene()
```

## Key Mathematical Insights

### Ray-Sphere Intersection Geometric Interpretation

The quadratic equation $t^2 + 2(\vec{oc} \cdot \vec{D})t + (|\vec{oc}|^2 - r^2) = 0$ has a beautiful geometric interpretation:

- The term $|\vec{oc}|^2 - r^2$ represents the squared distance from ray origin to sphere center minus the sphere's radius squared
- When this is negative, the ray origin is inside the sphere
- The discriminant $\Delta = 4[(\vec{oc} \cdot \vec{D})^2 - (|\vec{oc}|^2 - r^2)]$ determines intersection existence

### Camera Matrix Mathematics

The camera transformation can be represented as a 4×4 matrix:

$$ M_{view} = \begin{pmatrix} r_x & r_y & r_z & -\vec{r} \cdot \vec{pos} \\ u_x & u_y & u_z & -\vec{u} \cdot \vec{pos} \\ -f_x & -f_y & -f_z & \vec{f} \cdot \vec{pos} \\ 0 & 0 & 0 & 1 \end{pmatrix} $$

Where $\vec{r}$, $\vec{u}$, $\vec{f}$ are the right, up, and forward vectors, and $\vec{pos}$ is the camera position.

This raytracer demonstrates fundamental 3D graphics concepts and provides a foundation for understanding more advanced rendering techniques like path tracing, global illumination, and physically-based rendering.
