import base64
from pathlib import Path
from urllib.parse import unquote

import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
from pygltflib import GLTF2


GL_COMPONENT_DTYPES = {
    5120: np.int8,      # BYTE
    5121: np.uint8,     # UNSIGNED_BYTE
    5122: np.int16,     # SHORT
    5123: np.uint16,    # UNSIGNED_SHORT
    5125: np.uint32,    # UNSIGNED_INT
    5126: np.float32,   # FLOAT
}

GL_TYPE_COUNTS = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT2": 4,
    "MAT3": 9,
    "MAT4": 16,
}

camera_yaw = 0.0      # 좌우 각도
camera_pitch = 20.0   # 위아래 각도
camera_dist = 6.0 


def get_buffer_data(gltf, gltf_path, buffer_index):
    buffer = gltf.buffers[buffer_index]
    uri = buffer.uri

    if uri is None:
        return gltf.binary_blob()

    if uri.startswith("data:"):
        encoded = uri.split(",", 1)[1]
        return base64.b64decode(encoded)

    buffer_path = gltf_path.parent / unquote(uri)
    return buffer_path.read_bytes()


def read_accessor(gltf, gltf_path, accessor_index):
    accessor = gltf.accessors[accessor_index]
    buffer_view = gltf.bufferViews[accessor.bufferView]

    raw = get_buffer_data(gltf, gltf_path, buffer_view.buffer)

    component_dtype = GL_COMPONENT_DTYPES[accessor.componentType]
    component_count = GL_TYPE_COUNTS[accessor.type]

    accessor_offset = accessor.byteOffset or 0
    buffer_view_offset = buffer_view.byteOffset or 0
    start = buffer_view_offset + accessor_offset

    item_size = np.dtype(component_dtype).itemsize * component_count
    stride = buffer_view.byteStride or item_size

    values = []
    for i in range(accessor.count):
        offset = start + i * stride
        chunk = raw[offset:offset + item_size]
        value = np.frombuffer(chunk, dtype=component_dtype, count=component_count)
        values.append(value)

    arr = np.array(values)

    if accessor.normalized:
        if accessor.componentType == 5120:
            arr = np.maximum(arr / 127.0, -1.0)
        elif accessor.componentType == 5121:
            arr = arr / 255.0
        elif accessor.componentType == 5122:
            arr = np.maximum(arr / 32767.0, -1.0)
        elif accessor.componentType == 5123:
            arr = arr / 65535.0

    return arr


def get_material_color(gltf, material_index):
    return [0.45, 0.25, 0.12, 1.0]


def load_gltf_triangles(filename):
    gltf_path = Path(filename)
    gltf = GLTF2().load(str(gltf_path))

    batches = []
    all_vertices = []

    for mesh in gltf.meshes:
        for primitive in mesh.primitives:
            position_accessor_index = primitive.attributes.POSITION
            positions = read_accessor(gltf, gltf_path, position_accessor_index).astype(np.float32)

            if primitive.indices is not None:
                indices = read_accessor(gltf, gltf_path, primitive.indices).reshape(-1).astype(np.uint32)
                triangles = positions[indices]
            else:
                triangles = positions

            usable_count = len(triangles) - (len(triangles) % 3)
            triangles = triangles[:usable_count].reshape(-1, 3, 3)

            color = get_material_color(gltf, primitive.material)

            batches.append({
                "triangles": triangles,
                "color": color,
            })

            all_vertices.append(triangles.reshape(-1, 3))

    if not all_vertices:
        raise ValueError("gltf 안에서 렌더링 가능한 POSITION 데이터를 찾지 못했습니다.")

    all_vertices = np.vstack(all_vertices)
    center = all_vertices.mean(axis=0)

    size = all_vertices.max(axis=0) - all_vertices.min(axis=0)
    max_size = float(np.max(size))
    scale = 2.5 / max_size if max_size > 0 else 1.0

    for batch in batches:
        batch["triangles"] = (batch["triangles"] - center) * scale

    return batches


def make_fallback_triangle():
    return [{
        "triangles": np.array([
            [[0, 1, 0], [-1, -1, 0], [1, -1, 0]]
        ], dtype=np.float32),
        "color": [1.0, 0.8, 0.2, 1.0],
    }]


def draw_batches(batches):
    for batch in batches:
        color = batch["color"]
        glColor4f(color[0], color[1], color[2], color[3])

        glBegin(GL_TRIANGLES)
        for triangle in batch["triangles"]:
            for vertex in triangle:
                glVertex3fv(vertex)
        glEnd()


def main():
    pygame.init()

    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Pygame + OpenGL glTF Viewer")

    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    glClearColor(0.08, 0.08, 0.1, 1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, display[0] / display[1], 0.1, 100.0)

    try:
        batches = load_gltf_triangles("./assets/table/scene.gltf")
        print("모델 로드 성공")
    except Exception as e:
        print(f"모델을 로드할 수 없습니다: {e}")
        batches = make_fallback_triangle()

    clock = pygame.time.Clock()
    running = True
    angle = 0

    camera_yaw = 0.0
    camera_pitch = 20.0
    camera_dist = 6.0

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #angle += 45.0 * (dt / 1000.0)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            camera_yaw += 1.5
        if keys[pygame.K_RIGHT]:
            camera_yaw -= 1.5
        if keys[pygame.K_UP]:
            camera_pitch -= 1.5
        if keys[pygame.K_DOWN]:
            camera_pitch += 1.5
        if keys[pygame.K_w]:
            camera_dist -= 0.1
        if keys[pygame.K_s]:
            camera_dist += 0.1

        camera_pitch = max(-85.0, min(85.0, camera_pitch))
        camera_dist = max(1.0, min(30.0, camera_dist))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        yaw_rad = np.radians(camera_yaw)
        pitch_rad = np.radians(camera_pitch)

        cam_x = camera_dist * np.cos(pitch_rad) * np.sin(yaw_rad)
        cam_y = camera_dist * np.sin(pitch_rad)
        cam_z = camera_dist * np.cos(pitch_rad) * np.cos(yaw_rad)

        gluLookAt(
            cam_x, cam_y, cam_z,
            0.0, 0.0, 0.0,
            0.0, 1.0, 0.0
        )

        glTranslatef(0.0, -3.0, -5.0)
        # glRotatef(20.0, 1.0, 0.0, 0.0)
        glRotatef(180, 1, 0.0, 0.0)
        glRotatef(-135, 0.0, 1.0, 0.0)
        glRotatef(142, 0.0, 0.0, 1.0)

        draw_batches(batches)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()