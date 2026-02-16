import pygame
import sys
import math
import random

# -------------------------------------------------
# INIT
# -------------------------------------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN_CENTER = (WIDTH // 2, HEIGHT // 2)
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultra Mario 3D Bros - Complete Edition (SM64)")
clock = pygame.time.Clock()

# -------------------------------------------------
# COLORS
# -------------------------------------------------
SKY_BLUE       = (100, 149, 237)
NES_BLUE       = (92, 148, 252)
GRASS_GREEN    = (50, 160, 60)
DARK_GREEN     = (30, 120, 30)
STONE_GRAY     = (220, 220, 220)
DARK_GRAY      = (140, 140, 140)
ROOF_RED       = (180, 40, 40)
MOAT_BLUE      = (40, 100, 200)
BLACK          = (20, 20, 20)
WHITE          = (255, 255, 255)
YELLOW         = (255, 230, 0)
MARIO_RED      = (255, 0, 0)
MARIO_BLUE     = (0, 70, 180)
WOOD_BROWN     = (140, 100, 60)
PARCHMENT      = (250, 240, 200)
INK_COLOR      = (50, 40, 100)
TRUNK_BROWN    = (120, 80, 40)
TREE_GREEN     = (40, 140, 40)
STONE_PATH     = (200, 200, 200)
SAND_YELLOW    = (210, 180, 100)
LAVA_RED       = (220, 60, 20)
LAVA_ORANGE    = (255, 120, 30)
SNOW_WHITE     = (240, 245, 255)
ICE_BLUE       = (180, 210, 240)
WATER_BLUE     = (50, 120, 210)
DEEP_WATER     = (20, 60, 150)
PURPLE         = (120, 40, 160)
BRICK_RED      = (160, 60, 50)
DARK_BROWN     = (80, 50, 25)
CAVE_BROWN     = (100, 80, 55)
CAVE_DARK      = (70, 55, 40)
METAL_GRAY     = (170, 175, 180)
GOLD           = (230, 190, 40)
CLOCK_BEIGE    = (220, 200, 160)
RAINBOW_PINK   = (255, 150, 200)
RAINBOW_CYAN   = (100, 240, 255)
RAINBOW_LIME   = (150, 255, 100)
MANSION_PURPLE = (90, 70, 110)
MANSION_GREEN  = (60, 90, 60)
DOCK_BLUE      = (30, 80, 160)
FENCE_BROWN    = (110, 75, 40)
VOLCANO_GRAY   = (90, 80, 75)
VOLCANO_RED    = (170, 50, 30)
PYRAMID_TAN    = (200, 170, 110)
PYRAMID_DARK   = (160, 130, 80)
CHAIN_GRAY     = (80, 80, 80)
CANNON_BLACK   = (40, 40, 40)
PAINTING_FRAME = (180, 140, 60)
SKY_SUNSET     = (200, 120, 80)
SKY_NIGHT      = (20, 20, 60)
SKY_CAVE       = (40, 35, 30)
SKY_LAVA       = (60, 20, 10)
SKY_SNOW       = (180, 200, 230)
SKY_RAINBOW    = (140, 160, 255)
SKY_UNDERWATER = (20, 50, 100)
SKY_DESERT     = (220, 180, 120)
SKY_MANSION    = (30, 20, 40)
STAR_YELLOW    = (255, 255, 100)

# Fonts
try:
    title_font   = pygame.font.SysFont("Arial Black", 55, bold=True)
    letter_font  = pygame.font.SysFont("Georgia", 30, italic=True)
    menu_font    = pygame.font.SysFont("Arial", 28, bold=True)
    hud_font     = pygame.font.SysFont("Courier New", 18, bold=True)
    select_font  = pygame.font.SysFont("Arial", 22, bold=True)
    star_font    = pygame.font.SysFont("Arial Black", 36, bold=True)
    small_font   = pygame.font.SysFont("Arial", 16)
except Exception:
    title_font   = pygame.font.Font(None, 70)
    letter_font  = pygame.font.Font(None, 36)
    menu_font    = pygame.font.Font(None, 40)
    hud_font     = pygame.font.Font(None, 22)
    select_font  = pygame.font.Font(None, 28)
    star_font    = pygame.font.Font(None, 44)
    small_font   = pygame.font.Font(None, 20)

# Game States
STATE_MENU       = 0
STATE_LETTER     = 1
STATE_CASTLE     = 2
STATE_LEVEL_SEL  = 3
STATE_PLAYING    = 4
STATE_STAR_GET   = 5

# -------------------------------------------------
# 3D MATH
# -------------------------------------------------
def rotate_y(x, z, angle):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return x * cos_a - z * sin_a, x * sin_a + z * cos_a

def project_point(x, y, z, cam_x, cam_y, cam_z, cam_yaw, fov=700):
    dx = x - cam_x
    dy = y - cam_y
    dz = z - cam_z
    rx, rz = rotate_y(dx, dz, -cam_yaw)
    ry = dy
    if rz <= 10:
        return None
    scale = fov / rz
    px = rx * scale + SCREEN_CENTER[0]
    py = -ry * scale + SCREEN_CENTER[1]
    return (int(px), int(py), rz)

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# -------------------------------------------------
# MARIO
# -------------------------------------------------
class Mario:
    def __init__(self, x, z):
        self.x, self.y, self.z = x, 0.0, z
        self.vx = self.vy = self.vz = 0.0
        self.ground_accel    = 1.2
        self.air_accel       = 0.4
        self.max_speed       = 22.0
        self.friction        = 0.82
        self.gravity         = 1.3
        self.terminal_vel    = -45.0
        self.jump_force      = 24.0
        self.grounded        = True
        self.yaw             = 0.0
        self.size            = 25
        self.stars_collected  = 0
        self.coins           = 0
        self.lives           = 4
        self.floor_y         = 0.0

    def respawn(self, x, z):
        self.x, self.y, self.z = x, 0.0, z
        self.vx = self.vy = self.vz = 0.0
        self.grounded = True
        self.floor_y = 0.0

    def update(self, keys, cam_yaw, platforms=None):
        move_x = move_z = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: move_x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_x += 1
        if keys[pygame.K_UP]    or keys[pygame.K_w]: move_z += 1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: move_z -= 1

        if move_x or move_z:
            input_angle  = math.atan2(move_x, move_z)
            target_angle = cam_yaw + input_angle
            diff = (target_angle - self.yaw + math.pi) % (2 * math.pi) - math.pi
            self.yaw += diff * 0.25
            accel = self.ground_accel if self.grounded else self.air_accel
            self.vx += math.sin(self.yaw) * accel
            self.vz += math.cos(self.yaw) * accel

        speed = math.hypot(self.vx, self.vz)
        if speed > self.max_speed:
            s = self.max_speed / speed
            self.vx *= s
            self.vz *= s

        if self.grounded:
            self.vx *= self.friction
            self.vz *= self.friction

        self.vy -= self.gravity
        if self.vy < self.terminal_vel:
            self.vy = self.terminal_vel

        self.x += self.vx
        self.y += self.vy
        self.z += self.vz

        # Platform collision
        self.floor_y = 0.0
        if platforms:
            for px, py, pz, pw, ph, pd in platforms:
                hx, hz = pw / 2, pd / 2
                if (px - hx <= self.x <= px + hx and
                    pz - hz <= self.z <= pz + hz):
                    top = py + ph / 2
                    if self.y <= top and self.y + self.vy <= top + 5:
                        if self.floor_y < top:
                            self.floor_y = top

        if self.y <= self.floor_y:
            self.y = self.floor_y
            self.vy = 0
            self.grounded = True
        else:
            self.grounded = False

        if keys[pygame.K_SPACE] and self.grounded:
            self.vy = self.jump_force
            self.grounded = False

        # Death plane
        if self.y < -500:
            self.lives -= 1
            return "death"
        return None

    def get_mesh(self):
        s = self.size
        h = s * 2
        verts = [
            (self.x - s, self.y,     self.z - s),
            (self.x + s, self.y,     self.z - s),
            (self.x + s, self.y,     self.z + s),
            (self.x - s, self.y,     self.z + s),
            (self.x - s, self.y + h, self.z - s),
            (self.x + s, self.y + h, self.z - s),
            (self.x + s, self.y + h, self.z + s),
            (self.x - s, self.y + h, self.z + s),
        ]
        faces = [
            ([0,1,2,3], MARIO_BLUE),
            ([4,5,6,7], MARIO_RED),
            ([0,4,5,1], MARIO_RED),
            ([2,6,7,3], MARIO_RED),
            ([1,5,6,2], MARIO_BLUE),
            ([0,4,7,3], MARIO_BLUE),
        ]
        return verts, faces

# -------------------------------------------------
# CAMERA
# -------------------------------------------------
class Camera:
    def __init__(self, target):
        self.target = target
        self.yaw    = 0.0
        self.dist   = 700.0
        self.height = 350.0
        self.x = self.y = self.z = 0.0

    def update(self, keys):
        if keys[pygame.K_q]: self.yaw -= 0.04
        if keys[pygame.K_e]: self.yaw += 0.04
        tx = self.target.x - math.sin(self.yaw) * self.dist
        tz = self.target.z - math.cos(self.yaw) * self.dist
        ty = self.target.y + self.height
        self.x += (tx - self.x) * 0.08
        self.y += (ty - self.y) * 0.08
        self.z += (tz - self.z) * 0.08

# -------------------------------------------------
# COLLECTIBLES
# -------------------------------------------------
class Star:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.collected = False
        self.bob = 0.0

    def update(self):
        self.bob += 0.06

    def check(self, mario):
        if self.collected:
            return False
        dx = mario.x - self.x
        dy = mario.y - (self.y + math.sin(self.bob) * 10)
        dz = mario.z - self.z
        if math.sqrt(dx*dx + dy*dy + dz*dz) < 60:
            self.collected = True
            mario.stars_collected += 1
            return True
        return False

    def get_mesh(self):
        if self.collected:
            return [], []
        y_off = math.sin(self.bob) * 10
        s = 15
        cy = self.y + y_off
        verts = [
            (self.x, cy + s*2, self.z),
            (self.x - s, cy + s*0.5, self.z - s),
            (self.x + s, cy + s*0.5, self.z - s),
            (self.x + s, cy + s*0.5, self.z + s),
            (self.x - s, cy + s*0.5, self.z + s),
            (self.x, cy - s, self.z),
        ]
        faces = [
            ([0,1,2], STAR_YELLOW), ([0,2,3], STAR_YELLOW),
            ([0,3,4], STAR_YELLOW), ([0,4,1], STAR_YELLOW),
            ([5,2,1], GOLD),        ([5,3,2], GOLD),
            ([5,4,3], GOLD),        ([5,1,4], GOLD),
        ]
        return verts, faces

class Coin:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.collected = False
        self.spin = 0.0

    def update(self):
        self.spin += 0.08

    def check(self, mario):
        if self.collected:
            return False
        dx = mario.x - self.x
        dy = mario.y - self.y
        dz = mario.z - self.z
        if math.sqrt(dx*dx + dy*dy + dz*dz) < 45:
            self.collected = True
            mario.coins += 1
            return True
        return False

    def get_mesh(self):
        if self.collected:
            return [], []
        s = 8
        w = abs(math.cos(self.spin)) * s + 2
        verts = [
            (self.x - w, self.y,      self.z),
            (self.x + w, self.y,      self.z),
            (self.x + w, self.y + s*2, self.z),
            (self.x - w, self.y + s*2, self.z),
        ]
        faces = [([0,1,2,3], YELLOW)]
        return verts, faces

# -------------------------------------------------
# WORLD BUILDER (base class)
# -------------------------------------------------
class WorldBase:
    def __init__(self):
        self.verts     = []
        self.faces     = []
        self.platforms  = []   # (x, y, z, w, h, d) for collision
        self.stars      = []
        self.coins      = []
        self.spawn      = (0, -400)
        self.sky_color  = SKY_BLUE
        self.name       = "Unknown"
        self.star_count = 0

    def add_box(self, x, y, z, w, h, d, color, collide=False):
        idx = len(self.verts)
        hw, hh, hd = w/2, h/2, d/2
        self.verts += [
            (x-hw, y-hh, z-hd), (x+hw, y-hh, z-hd),
            (x+hw, y+hh, z-hd), (x-hw, y+hh, z-hd),
            (x-hw, y-hh, z+hd), (x+hw, y-hh, z+hd),
            (x+hw, y+hh, z+hd), (x-hw, y+hh, z+hd),
        ]
        for f in [[0,1,2,3],[4,5,6,7],[0,4,7,3],[1,5,6,2],[3,2,6,7],[0,1,5,4]]:
            self.faces.append(([i + idx for i in f], color))
        if collide:
            self.platforms.append((x, y, z, w, h, d))

    def add_roof(self, x, y, z, w, h, d, color):
        idx = len(self.verts)
        hw, hd = w/2, d/2
        self.verts.extend([
            (x-hw, y, z-hd), (x+hw, y, z-hd),
            (x+hw, y, z+hd), (x-hw, y, z+hd),
            (x, y + h, z),
        ])
        for f in [[0,1,4],[1,2,4],[2,3,4],[3,0,4]]:
            self.faces.append(([i + idx for i in f], color))
        self.faces.append(([idx, idx+1, idx+2, idx+3], color))

    def add_slope(self, x, y, z, w, h, d, color):
        """Wedge/ramp shape"""
        idx = len(self.verts)
        hw, hd = w/2, d/2
        self.verts.extend([
            (x-hw, y,   z-hd), (x+hw, y,   z-hd),
            (x+hw, y,   z+hd), (x-hw, y,   z+hd),
            (x-hw, y+h, z+hd), (x+hw, y+h, z+hd),
        ])
        for f in [[0,1,2,3],[2,5,4,3],[0,1,5,4],[0,3,4],[1,2,5]]:
            self.faces.append(([i + idx for i in f], color))

    def add_cylinder_approx(self, x, y, z, r, h, segments, color):
        """Approximate cylinder with polygon faces"""
        idx = len(self.verts)
        bottom_ring = []
        top_ring = []
        for i in range(segments):
            a = (2 * math.pi * i) / segments
            px = x + r * math.cos(a)
            pz = z + r * math.sin(a)
            self.verts.append((px, y, pz))
            bottom_ring.append(idx + i)
            self.verts.append((px, y + h, pz))
            top_ring.append(idx + i * 2 + 1)
            idx_base = len(self.verts) - 2
        # side faces
        for i in range(segments):
            j = (i + 1) % segments
            b0 = idx + i * 2
            b1 = idx + j * 2
            t0 = b0 + 1
            t1 = b1 + 1
            self.faces.append(([b0, b1, t1, t0], color))

    def add_star(self, x, y, z):
        self.stars.append(Star(x, y, z))
        self.star_count += 1

    def add_coins_line(self, x1, y1, z1, x2, y2, z2, count=5):
        for i in range(count):
            t = i / max(count - 1, 1)
            cx = x1 + (x2 - x1) * t
            cy = y1 + (y2 - y1) * t
            cz = z1 + (z2 - z1) * t
            self.coins.append(Coin(cx, cy + 30, cz))

    def add_coins_ring(self, cx, y, cz, r, count=8):
        for i in range(count):
            a = (2 * math.pi * i) / count
            self.coins.append(Coin(cx + r * math.cos(a), y + 30, cz + r * math.sin(a)))

    def add_tree(self, x, z, trunk_h=90, canopy_w=110, canopy_h=90):
        self.add_box(x, 30, z, 35, trunk_h, 35, TRUNK_BROWN)
        self.add_roof(x, trunk_h + 20, z, canopy_w, canopy_h, canopy_w, TREE_GREEN)
        self.add_roof(x, trunk_h + 60, z, canopy_w * 0.7, canopy_h * 0.6, canopy_w * 0.7, TREE_GREEN)

    def build(self):
        pass


# =================================================
# COURSE 0: CASTLE GROUNDS (Hub World)
# =================================================
class CastleGrounds(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Peach's Castle"
        self.sky_color = SKY_BLUE
        self.spawn = (0, -720)
        self.build()

    def build(self):
        # Courtyard floor
        self.add_box(0, 0, 0, 2000, 10, 2000, GRASS_GREEN)
        # Stone path
        self.add_box(0, 5, 150, 180, 10, 900, STONE_PATH)
        # Walls
        self.add_box(-1000, 100, 0, 40, 200, 2000, STONE_GRAY)
        self.add_box(1000, 100, 0, 40, 200, 2000, STONE_GRAY)
        self.add_box(0, 100, 1000, 2000, 200, 40, STONE_GRAY)
        # Castle
        self.add_box(0, 150, 750, 550, 300, 450, STONE_GRAY)
        self.add_box(0, 350, 750, 160, 220, 160, STONE_GRAY)
        self.add_roof(0, 470, 750, 200, 160, 200, ROOF_RED)
        # Side towers
        self.add_box(-240, 200, 750, 110, 350, 110, STONE_GRAY)
        self.add_roof(-240, 420, 750, 130, 110, 130, ROOF_RED)
        self.add_box(240, 200, 750, 110, 350, 110, STONE_GRAY)
        self.add_roof(240, 420, 750, 130, 110, 130, ROOF_RED)
        # Moat
        self.add_box(0, -5, 450, 700, 8, 100, MOAT_BLUE)
        self.add_box(-350, -5, 600, 100, 8, 400, MOAT_BLUE)
        self.add_box(350, -5, 600, 100, 8, 400, MOAT_BLUE)
        # Bridge over moat
        self.add_box(0, 5, 450, 180, 14, 110, WOOD_BROWN, collide=True)
        # Trees
        self.add_tree(-550, -450)
        self.add_tree(-700, 300)
        self.add_tree(550, -450)
        self.add_tree(700, 300)
        self.add_tree(-300, -600)
        self.add_tree(300, -600)
        # Coins
        self.add_coins_line(-400, 0, -200, 400, 0, -200, 8)
        self.add_coins_ring(0, 0, -400, 120, 8)


# =================================================
# COURSE 1: BOB-OMB BATTLEFIELD
# =================================================
class BobOmbBattlefield(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Bob-omb Battlefield"
        self.sky_color = SKY_BLUE
        self.spawn = (0, -800)
        self.build()

    def build(self):
        # Main grassy field
        self.add_box(0, 0, 0, 2400, 10, 2400, GRASS_GREEN)
        # Central mountain (King Bob-omb)
        self.add_box(0, 100, 400, 600, 200, 600, DARK_GREEN, collide=True)
        self.add_box(0, 250, 400, 400, 100, 400, GRASS_GREEN, collide=True)
        self.add_box(0, 350, 400, 200, 100, 200, DARK_GREEN, collide=True)
        self.add_roof(0, 420, 400, 240, 120, 240, GRASS_GREEN)
        # Ramp up the mountain
        self.add_slope(200, 5, 200, 150, 100, 300, STONE_PATH)
        # Chain Chomp post area
        self.add_box(-500, 15, -300, 40, 80, 40, WOOD_BROWN)
        self.add_box(-500, 5, -300, 120, 12, 120, DARK_GREEN)
        # Chain Chomp (sphere approximation)
        self.add_box(-500, 80, -300, 80, 80, 80, CHAIN_GRAY)
        # Cannon areas
        self.add_box(600, 0, -500, 60, 40, 60, CANNON_BLACK)
        self.add_box(-600, 0, 600, 60, 40, 60, CANNON_BLACK)
        # Fence path
        for i in range(-6, 7):
            self.add_box(i * 80, 15, -200, 10, 40, 10, FENCE_BROWN)
        # Bridge
        self.add_box(0, 80, -100, 200, 12, 60, WOOD_BROWN, collide=True)
        # Trees
        self.add_tree(-800, -600)
        self.add_tree(800, -600)
        self.add_tree(-700, 800)
        self.add_tree(700, 800)
        self.add_tree(-300, -700)
        self.add_tree(400, -500)
        # Boulders
        self.add_box(-200, 15, 600, 60, 40, 60, DARK_GRAY)
        self.add_box(300, 15, 700, 50, 35, 50, DARK_GRAY)
        # Stars
        self.add_star(0, 450, 400)        # Top of mountain
        self.add_star(-500, 100, -300)     # Chain Chomp star
        self.add_star(600, 50, -500)       # Cannon star
        # Coins
        self.add_coins_line(-300, 0, -500, 300, 0, -500, 8)
        self.add_coins_ring(0, 200, 400, 100, 8)
        self.add_coins_line(-700, 0, 0, -700, 0, 600, 5)


# =================================================
# COURSE 2: WHOMP'S FORTRESS
# =================================================
class WhompsFortress(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Whomp's Fortress"
        self.sky_color = SKY_BLUE
        self.spawn = (0, -500)
        self.build()

    def build(self):
        # Base platform
        self.add_box(0, 0, 0, 800, 10, 800, STONE_GRAY)
        # Fortress walls - ascending tiers
        self.add_box(0, 60, 200, 600, 120, 600, STONE_GRAY, collide=True)
        self.add_box(50, 180, 250, 400, 120, 400, DARK_GRAY, collide=True)
        self.add_box(0, 300, 300, 250, 120, 250, STONE_GRAY, collide=True)
        # Top platform
        self.add_box(0, 420, 300, 200, 30, 200, STONE_PATH, collide=True)
        # Side ledges
        self.add_box(-350, 60, 0, 100, 20, 200, STONE_PATH, collide=True)
        self.add_box(350, 120, 100, 100, 20, 200, STONE_PATH, collide=True)
        self.add_box(-250, 180, 350, 100, 20, 100, STONE_PATH, collide=True)
        # Thwomp blocks
        self.add_box(100, 200, 100, 80, 80, 80, DARK_GRAY)
        self.add_box(-100, 320, 250, 80, 80, 80, DARK_GRAY)
        # Ramps
        self.add_slope(-200, 0, 100, 120, 60, 200, STONE_PATH)
        self.add_slope(150, 120, 200, 100, 60, 150, STONE_PATH)
        # Tower
        self.add_box(0, 400, 350, 80, 200, 80, STONE_GRAY)
        self.add_roof(0, 550, 350, 100, 60, 100, ROOF_RED)
        # Plank bridge
        self.add_box(-200, 250, 200, 180, 8, 40, WOOD_BROWN, collide=True)
        # Bullet Bill launcher
        self.add_box(350, 140, 350, 40, 60, 40, CANNON_BLACK)
        # Stars
        self.add_star(0, 460, 300)         # Top of fortress
        self.add_star(0, 580, 350)         # Tower top
        self.add_star(-350, 90, 0)         # Side ledge
        # Coins
        self.add_coins_line(-300, 0, -300, 300, 0, -300, 6)
        self.add_coins_line(-200, 260, 200, 100, 260, 200, 5)
        self.add_coins_ring(0, 420, 300, 80, 8)


# =================================================
# COURSE 3: JOLLY ROGER BAY
# =================================================
class JollyRogerBay(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Jolly Roger Bay"
        self.sky_color = SKY_UNDERWATER
        self.spawn = (0, -600)
        self.build()

    def build(self):
        # Beach
        self.add_box(0, 0, -400, 1200, 10, 500, SAND_YELLOW)
        # Water surface
        self.add_box(0, -10, 300, 1800, 8, 1400, WATER_BLUE)
        # Deep water floor
        self.add_box(0, -200, 300, 1800, 10, 1400, DEEP_WATER)
        # Sunken ship
        self.add_box(300, -150, 500, 250, 60, 80, WOOD_BROWN)
        self.add_box(300, -120, 500, 200, 30, 60, DARK_BROWN)
        self.add_box(300, -90, 500, 20, 100, 10, WOOD_BROWN)  # mast
        # Underwater cave entrance
        self.add_box(-400, -100, 700, 200, 120, 200, CAVE_BROWN)
        self.add_box(-400, -50, 700, 160, 60, 160, CAVE_DARK)
        # Rock platforms in water
        self.add_box(-200, -30, 200, 100, 30, 100, DARK_GRAY, collide=True)
        self.add_box(100, -20, 350, 80, 30, 80, DARK_GRAY, collide=True)
        self.add_box(0, -40, 600, 120, 30, 120, DARK_GRAY, collide=True)
        # Cliff face
        self.add_box(0, 80, -650, 1200, 180, 40, CAVE_BROWN)
        # Dock
        self.add_box(500, 10, -300, 200, 14, 80, WOOD_BROWN, collide=True)
        # Pirate treasure chests
        self.add_box(-300, -180, 400, 40, 30, 30, DARK_BROWN)
        self.add_box(200, -180, 600, 40, 30, 30, DARK_BROWN)
        # Eel cave
        self.add_box(500, -160, 800, 150, 100, 150, CAVE_DARK)
        # Stars
        self.add_star(300, -80, 500)       # Sunken ship
        self.add_star(-400, -40, 700)      # Cave
        self.add_star(0, -30, 600)         # Platform
        # Coins
        self.add_coins_line(-400, 0, -400, 400, 0, -400, 8)
        self.add_coins_ring(0, -150, 400, 150, 8)


# =================================================
# COURSE 4: COOL, COOL MOUNTAIN
# =================================================
class CoolCoolMountain(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Cool, Cool Mountain"
        self.sky_color = SKY_SNOW
        self.spawn = (0, -300)
        self.build()

    def build(self):
        # Base snowy ground
        self.add_box(0, 0, 0, 2000, 10, 2000, SNOW_WHITE)
        # Mountain core - ascending tiers
        self.add_box(0, 80, 300, 900, 160, 900, SNOW_WHITE, collide=True)
        self.add_box(0, 220, 350, 600, 120, 600, ICE_BLUE, collide=True)
        self.add_box(0, 360, 400, 350, 100, 350, SNOW_WHITE, collide=True)
        self.add_box(0, 470, 400, 180, 80, 180, SNOW_WHITE, collide=True)
        self.add_roof(0, 540, 400, 220, 140, 220, SNOW_WHITE)
        # Slide entrance (chimney at top)
        self.add_box(60, 540, 400, 50, 80, 50, BRICK_RED)
        # Cabin at bottom
        self.add_box(-500, 30, -500, 150, 100, 120, WOOD_BROWN)
        self.add_roof(-500, 100, -500, 180, 70, 150, SNOW_WHITE)
        # Ice bridge
        self.add_box(-200, 150, 100, 250, 10, 60, ICE_BLUE, collide=True)
        # Snowman body
        self.add_box(400, 25, -300, 80, 60, 80, SNOW_WHITE)
        self.add_box(400, 65, -300, 60, 50, 60, SNOW_WHITE)
        self.add_box(400, 100, -300, 40, 40, 40, SNOW_WHITE)
        # Penguin slide area
        self.add_slope(-100, 160, 0, 200, -100, 400, ICE_BLUE)
        # Frozen lake
        self.add_box(300, -5, -600, 500, 8, 400, ICE_BLUE)
        # Pine trees (cone shaped)
        for pos in [(-700, -700), (-600, -400), (700, -600), (600, -300), (-800, 500), (800, 400)]:
            self.add_box(pos[0], 25, pos[1], 25, 80, 25, TRUNK_BROWN)
            self.add_roof(pos[0], 80, pos[1], 80, 100, 80, DARK_GREEN)
            self.add_roof(pos[0], 140, pos[1], 60, 70, 60, DARK_GREEN)
        # Stars
        self.add_star(0, 560, 400)         # Mountain peak
        self.add_star(-500, 100, -500)     # Cabin
        self.add_star(400, 140, -300)      # Snowman
        # Coins
        self.add_coins_line(-400, 0, -200, 400, 0, -200, 8)
        self.add_coins_ring(0, 350, 400, 100, 8)


# =================================================
# COURSE 5: BIG BOO'S HAUNT
# =================================================
class BigBoosHaunt(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Big Boo's Haunt"
        self.sky_color = SKY_MANSION
        self.spawn = (0, -500)
        self.build()

    def build(self):
        # Dead grass ground
        self.add_box(0, 0, 0, 2000, 10, 2000, MANSION_GREEN)
        # Mansion main building
        self.add_box(0, 150, 300, 500, 300, 400, MANSION_PURPLE)
        self.add_roof(0, 350, 300, 550, 200, 450, DARK_GRAY)
        # Porch
        self.add_box(0, 20, 50, 300, 40, 100, STONE_GRAY, collide=True)
        # Porch pillars
        self.add_box(-120, 60, 50, 20, 100, 20, STONE_GRAY)
        self.add_box(120, 60, 50, 20, 100, 20, STONE_GRAY)
        # Door
        self.add_box(0, 80, 100, 60, 100, 10, DARK_BROWN)
        # Windows (dark recesses)
        self.add_box(-150, 200, 100, 60, 60, 10, BLACK)
        self.add_box(150, 200, 100, 60, 60, 10, BLACK)
        self.add_box(-150, 350, 100, 50, 50, 10, BLACK)
        self.add_box(150, 350, 100, 50, 50, 10, BLACK)
        # Side wings
        self.add_box(-350, 100, 300, 200, 200, 250, MANSION_PURPLE)
        self.add_roof(-350, 230, 300, 230, 120, 280, DARK_GRAY)
        self.add_box(350, 100, 300, 200, 200, 250, MANSION_PURPLE)
        self.add_roof(350, 230, 300, 230, 120, 280, DARK_GRAY)
        # Graveyard stones
        for gx, gz in [(-600,-200),(-500,-300),(-700,-100),(-550,-400),
                        (600,-200),(500,-300),(700,-100),(550,-400)]:
            self.add_box(gx, 20, gz, 30, 50, 10, STONE_GRAY)
        # Dead trees
        self.add_box(-800, 30, -500, 25, 120, 25, DARK_BROWN)
        self.add_box(-780, 100, -500, 60, 8, 8, DARK_BROWN)
        self.add_box(800, 30, -500, 25, 120, 25, DARK_BROWN)
        self.add_box(810, 90, -500, 50, 8, 8, DARK_BROWN)
        # Fence
        for i in range(-4, 5):
            self.add_box(i * 120, 15, -600, 8, 40, 8, FENCE_BROWN)
        # Balcony
        self.add_box(0, 280, 100, 200, 10, 60, STONE_GRAY, collide=True)
        # Stars
        self.add_star(0, 400, 300)         # Mansion attic
        self.add_star(-350, 220, 300)      # Left wing
        self.add_star(350, 220, 300)       # Right wing
        # Coins
        self.add_coins_ring(0, 0, -300, 200, 8)
        self.add_coins_line(-400, 0, -200, 400, 0, -200, 6)


# =================================================
# COURSE 6: HAZY MAZE CAVE
# =================================================
class HazyMazeCave(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Hazy Maze Cave"
        self.sky_color = SKY_CAVE
        self.spawn = (0, -400)
        self.build()

    def build(self):
        # Cave floor
        self.add_box(0, 0, 0, 2400, 10, 2400, CAVE_BROWN)
        # Cave ceiling
        self.add_box(0, 400, 0, 2400, 10, 2400, CAVE_DARK)
        # Main cavern pillars
        for px, pz in [(-400, -400), (400, -400), (-400, 400), (400, 400), (0, 0)]:
            self.add_box(px, 200, pz, 80, 400, 80, CAVE_BROWN)
        # Maze walls
        self.add_box(-600, 50, 0, 40, 100, 800, CAVE_DARK)
        self.add_box(600, 50, 0, 40, 100, 800, CAVE_DARK)
        self.add_box(0, 50, -800, 1200, 100, 40, CAVE_DARK)
        self.add_box(-300, 50, 400, 600, 100, 40, CAVE_DARK)
        self.add_box(300, 50, -400, 40, 100, 400, CAVE_DARK)
        self.add_box(-200, 50, -200, 40, 100, 400, CAVE_DARK)
        # Underground lake
        self.add_box(-700, -10, 600, 600, 8, 600, DEEP_WATER)
        # Dorrie island
        self.add_box(-700, 0, 600, 150, 20, 150, CAVE_BROWN, collide=True)
        # Metal cap area
        self.add_box(700, 0, 700, 200, 20, 200, METAL_GRAY, collide=True)
        self.add_box(700, 30, 700, 40, 60, 40, METAL_GRAY)
        # Elevator platform
        self.add_box(0, 50, 800, 100, 10, 100, STONE_PATH, collide=True)
        # Raised paths
        self.add_box(-400, 30, -600, 200, 15, 60, STONE_PATH, collide=True)
        self.add_box(400, 60, -600, 200, 15, 60, STONE_PATH, collide=True)
        self.add_box(0, 90, -600, 200, 15, 60, STONE_PATH, collide=True)
        # Rolling rocks area
        self.add_box(800, 20, -400, 60, 50, 60, DARK_GRAY)
        self.add_box(850, 20, -500, 50, 40, 50, DARK_GRAY)
        # Stars
        self.add_star(-700, 40, 600)       # Underground lake
        self.add_star(700, 50, 700)        # Metal cap
        self.add_star(0, 110, -600)        # Raised path
        # Coins
        self.add_coins_line(-500, 0, -300, 500, 0, -300, 8)
        self.add_coins_ring(0, 0, 0, 200, 8)


# =================================================
# COURSE 7: LETHAL LAVA LAND
# =================================================
class LethalLavaLand(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Lethal Lava Land"
        self.sky_color = SKY_LAVA
        self.spawn = (0, -600)
        self.build()

    def build(self):
        # Lava sea
        self.add_box(0, -20, 0, 3000, 10, 3000, LAVA_RED)
        self.add_box(0, -15, 0, 3000, 6, 3000, LAVA_ORANGE)
        # Starting island
        self.add_box(0, 10, -600, 300, 40, 300, DARK_GRAY, collide=True)
        # Stepping stone platforms
        for i, (px, pz) in enumerate([(-200,-300),(0,-200),(200,-100),(300,100),(100,300)]):
            h = 20 + i * 10
            self.add_box(px, h, pz, 120, 30, 120, STONE_GRAY, collide=True)
        # Volcano
        self.add_box(0, 80, 600, 500, 160, 500, VOLCANO_GRAY, collide=True)
        self.add_box(0, 200, 600, 300, 120, 300, VOLCANO_GRAY, collide=True)
        self.add_box(0, 300, 600, 150, 80, 150, VOLCANO_RED, collide=True)
        self.add_roof(0, 370, 600, 180, 100, 180, VOLCANO_RED)
        # Lava pool inside volcano rim
        self.add_box(0, 310, 600, 100, 5, 100, LAVA_ORANGE)
        # Bully platform
        self.add_box(-500, 30, 300, 200, 50, 200, DARK_GRAY, collide=True)
        # Rotating fire platforms (static representations)
        self.add_box(500, 20, -300, 100, 20, 100, METAL_GRAY, collide=True)
        self.add_box(500, 20, 0, 100, 20, 100, METAL_GRAY, collide=True)
        # Log bridge
        self.add_box(-300, 15, 0, 200, 12, 40, WOOD_BROWN, collide=True)
        # Wing cap block
        self.add_box(600, 50, 300, 40, 40, 40, YELLOW)
        # Stars
        self.add_star(0, 400, 600)         # Volcano top
        self.add_star(-500, 80, 300)       # Bully
        self.add_star(100, 80, 300)        # Platform path end
        # Coins
        self.add_coins_line(-200, 30, -300, 300, 60, 100, 6)
        self.add_coins_ring(0, 250, 600, 100, 8)


# =================================================
# COURSE 8: SHIFTING SAND LAND
# =================================================
class ShiftingSandLand(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Shifting Sand Land"
        self.sky_color = SKY_DESERT
        self.spawn = (0, -700)
        self.build()

    def build(self):
        # Desert floor
        self.add_box(0, 0, 0, 3000, 10, 3000, SAND_YELLOW)
        # Quicksand pit (visual only - slightly lower)
        self.add_box(-400, -8, 0, 400, 6, 400, DARK_BROWN)
        # Main Pyramid
        self.add_box(0, 40, 400, 500, 80, 500, PYRAMID_TAN, collide=True)
        self.add_box(0, 100, 400, 380, 60, 380, PYRAMID_TAN, collide=True)
        self.add_roof(0, 160, 400, 420, 250, 420, PYRAMID_DARK)
        # Pyramid entrance
        self.add_box(0, 50, 150, 80, 60, 10, BLACK)
        # Oasis
        self.add_box(600, -3, -500, 250, 8, 250, WATER_BLUE)
        self.add_tree(600, -500, 60, 80, 60)
        self.add_tree(650, -450, 60, 80, 60)
        # Pillars
        for px, pz in [(-600, 400), (-700, 200), (600, 400), (700, 200)]:
            self.add_box(px, 50, pz, 50, 100, 50, SAND_YELLOW)
        # Tox Box path
        self.add_box(-600, 5, -300, 600, 10, 80, STONE_PATH)
        self.add_box(-600, 20, -300, 80, 80, 80, METAL_GRAY)  # Tox box representation
        # Klepto's nest (raised platform)
        self.add_box(700, 60, 700, 150, 120, 150, SAND_YELLOW, collide=True)
        # Stone arches
        self.add_box(-200, 40, -500, 30, 80, 30, PYRAMID_DARK)
        self.add_box(200, 40, -500, 30, 80, 30, PYRAMID_DARK)
        self.add_box(0, 90, -500, 440, 20, 30, PYRAMID_DARK)
        # Stars
        self.add_star(0, 420, 400)         # Pyramid top
        self.add_star(700, 180, 700)       # Klepto's nest
        self.add_star(-600, 30, -300)      # Tox box path
        # Coins
        self.add_coins_line(-400, 0, -600, 400, 0, -600, 8)
        self.add_coins_ring(0, 100, 400, 150, 8)


# =================================================
# COURSE 9: DIRE, DIRE DOCKS
# =================================================
class DireDireDocks(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Dire, Dire Docks"
        self.sky_color = SKY_UNDERWATER
        self.spawn = (0, -400)
        self.build()

    def build(self):
        # Dock platform
        self.add_box(0, 0, -400, 600, 10, 300, STONE_GRAY)
        # Water
        self.add_box(0, -15, 300, 2000, 8, 1500, DOCK_BLUE)
        # Deep floor
        self.add_box(0, -300, 300, 2000, 10, 1500, DEEP_WATER)
        # Dock walkways
        self.add_box(-200, 10, -200, 80, 14, 300, WOOD_BROWN, collide=True)
        self.add_box(200, 10, -200, 80, 14, 300, WOOD_BROWN, collide=True)
        # Bowser sub dock
        self.add_box(0, -10, 500, 300, 60, 120, METAL_GRAY)
        self.add_box(0, 20, 500, 250, 40, 80, DARK_GRAY)
        self.add_box(0, 50, 450, 30, 60, 10, METAL_GRAY)  # periscope
        # Underwater rings/poles
        for i in range(5):
            z = 200 + i * 150
            self.add_box(300 * (1 if i % 2 == 0 else -1), -100, z, 80, 8, 80, YELLOW)
        # Manta ray area
        self.add_box(-600, -200, 600, 100, 20, 200, DEEP_WATER)
        # Whirlpool center (visual)
        self.add_box(0, -280, 800, 100, 10, 100, BLACK)
        # Cage/treasure chest
        self.add_box(500, -250, 700, 60, 50, 60, METAL_GRAY)
        # Pipe to Fire Sea
        self.add_box(-500, -200, 800, 60, 60, 60, DARK_GREEN)
        # Platform islands
        self.add_box(-400, -20, 200, 120, 30, 120, STONE_GRAY, collide=True)
        self.add_box(400, -30, 400, 100, 30, 100, STONE_GRAY, collide=True)
        # Stars
        self.add_star(0, 60, 500)          # Sub
        self.add_star(-600, -160, 600)     # Manta
        self.add_star(500, -200, 700)      # Treasure
        # Coins
        self.add_coins_line(-200, 0, -400, 200, 0, -400, 6)
        self.add_coins_ring(0, -100, 400, 200, 8)


# =================================================
# COURSE 10: SNOWMAN'S LAND
# =================================================
class SnowmansLand(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Snowman's Land"
        self.sky_color = SKY_SNOW
        self.spawn = (0, -600)
        self.build()

    def build(self):
        # Snow ground
        self.add_box(0, 0, 0, 2400, 10, 2400, SNOW_WHITE)
        # Giant Snowman (3 sphere tiers)
        self.add_box(0, 60, 500, 300, 120, 300, SNOW_WHITE, collide=True)
        self.add_box(0, 170, 500, 220, 100, 220, SNOW_WHITE, collide=True)
        self.add_box(0, 270, 500, 140, 80, 140, SNOW_WHITE, collide=True)
        # Hat
        self.add_box(0, 330, 500, 160, 15, 160, BLACK)
        self.add_box(0, 350, 500, 100, 40, 100, BLACK)
        # Eyes (dark)
        self.add_box(-30, 290, 428, 20, 20, 5, BLACK)
        self.add_box(30, 290, 428, 20, 20, 5, BLACK)
        # Nose
        self.add_box(0, 270, 425, 10, 10, 30, LAVA_ORANGE)
        # Frozen lake
        self.add_box(-500, -5, -300, 500, 8, 500, ICE_BLUE)
        # Igloo
        self.add_box(500, 30, -400, 160, 80, 160, SNOW_WHITE)
        self.add_roof(500, 90, -400, 180, 60, 180, SNOW_WHITE)
        self.add_box(500, 30, -320, 50, 50, 10, DARK_BROWN)  # door
        # Ice platforms
        self.add_box(-300, 30, 200, 100, 15, 100, ICE_BLUE, collide=True)
        self.add_box(-500, 60, 300, 100, 15, 100, ICE_BLUE, collide=True)
        self.add_box(-700, 90, 200, 100, 15, 100, ICE_BLUE, collide=True)
        # Chill Bully arena
        self.add_box(600, 30, 500, 200, 15, 200, ICE_BLUE, collide=True)
        # Snow trees
        for tx, tz in [(-800,-600),(-700,700),(800,-500),(700,600),(-400,-700),(400,-600)]:
            self.add_box(tx, 25, tz, 22, 70, 22, TRUNK_BROWN)
            self.add_roof(tx, 70, tz, 70, 90, 70, SNOW_WHITE)
        # Stars
        self.add_star(0, 380, 500)         # Snowman head
        self.add_star(500, 80, -400)       # Igloo
        self.add_star(-700, 120, 200)      # Ice platforms
        # Coins
        self.add_coins_line(-400, 0, -500, 400, 0, -500, 8)
        self.add_coins_ring(0, 100, 500, 120, 8)


# =================================================
# COURSE 11: WET-DRY WORLD
# =================================================
class WetDryWorld(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Wet-Dry World"
        self.sky_color = SKY_BLUE
        self.spawn = (0, -400)
        self.build()

    def build(self):
        # Base floor
        self.add_box(0, 0, 0, 1800, 10, 1800, STONE_GRAY)
        # Water at low level
        self.add_box(0, 30, 0, 1800, 5, 1800, WATER_BLUE)
        # City buildings
        self.add_box(-400, 100, 300, 200, 200, 200, STONE_GRAY, collide=True)
        self.add_box(-400, 230, 300, 160, 60, 160, DARK_GRAY, collide=True)
        self.add_box(400, 80, 300, 180, 160, 180, STONE_GRAY, collide=True)
        self.add_box(400, 190, 300, 140, 50, 140, DARK_GRAY, collide=True)
        self.add_box(0, 120, 500, 150, 240, 150, STONE_GRAY, collide=True)
        self.add_box(0, 280, 500, 110, 60, 110, DARK_GRAY, collide=True)
        # Diamond switches (water level changers)
        self.add_box(-200, 40, -200, 30, 30, 30, PURPLE)
        self.add_box(300, 120, -100, 30, 30, 30, PURPLE)
        self.add_box(0, 250, 500, 30, 30, 30, PURPLE)
        # Cage area
        self.add_box(-600, 80, -300, 250, 160, 250, METAL_GRAY)
        self.add_box(-600, 170, -300, 200, 10, 200, METAL_GRAY, collide=True)
        # Floating planks
        self.add_box(-200, 60, 0, 150, 8, 60, WOOD_BROWN, collide=True)
        self.add_box(100, 90, 100, 150, 8, 60, WOOD_BROWN, collide=True)
        self.add_box(-100, 120, 200, 150, 8, 60, WOOD_BROWN, collide=True)
        # Arrow lifts (static)
        self.add_box(600, 50, 0, 80, 8, 80, YELLOW, collide=True)
        self.add_box(600, 120, 200, 80, 8, 80, YELLOW, collide=True)
        # Fence/walls
        self.add_box(0, 50, -900, 1800, 100, 30, STONE_GRAY)
        self.add_box(-900, 50, 0, 30, 100, 1800, STONE_GRAY)
        self.add_box(900, 50, 0, 30, 100, 1800, STONE_GRAY)
        # Stars
        self.add_star(0, 340, 500)         # Tallest building
        self.add_star(-600, 190, -300)     # Cage top
        self.add_star(600, 140, 200)       # Arrow lift
        # Coins
        self.add_coins_line(-500, 0, -600, 500, 0, -600, 8)
        self.add_coins_ring(0, 60, 0, 150, 8)


# =================================================
# COURSE 12: TALL, TALL MOUNTAIN
# =================================================
class TallTallMountain(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Tall, Tall Mountain"
        self.sky_color = SKY_BLUE
        self.spawn = (0, -400)
        self.build()

    def build(self):
        # Valley floor with grass
        self.add_box(0, 0, 0, 1600, 10, 1600, GRASS_GREEN)
        # Mountain - 6 ascending tiers
        self.add_box(0, 50, 300, 700, 100, 700, DARK_GREEN, collide=True)
        self.add_box(50, 140, 350, 550, 80, 550, GRASS_GREEN, collide=True)
        self.add_box(0, 220, 400, 400, 80, 400, DARK_GREEN, collide=True)
        self.add_box(-30, 300, 400, 300, 60, 300, GRASS_GREEN, collide=True)
        self.add_box(0, 370, 400, 200, 50, 200, DARK_GREEN, collide=True)
        self.add_box(0, 430, 400, 120, 40, 120, GRASS_GREEN, collide=True)
        # Cliff face
        self.add_box(0, 150, 700, 700, 300, 30, CAVE_BROWN)
        # Waterfall
        self.add_box(250, 200, 695, 60, 300, 10, WATER_BLUE)
        # Mushroom platforms
        self.add_box(-300, 80, -200, 30, 80, 30, STONE_GRAY)
        self.add_box(-300, 110, -200, 80, 10, 80, MARIO_RED, collide=True)
        self.add_box(-100, 130, -100, 30, 120, 30, STONE_GRAY)
        self.add_box(-100, 170, -100, 80, 10, 80, MARIO_RED, collide=True)
        # Slide entrance at peak
        self.add_box(40, 460, 400, 50, 60, 50, DARK_BROWN)
        # Monkey bridge
        self.add_box(200, 180, 200, 250, 8, 40, WOOD_BROWN, collide=True)
        # Log bridge
        self.add_box(-200, 100, 200, 180, 12, 30, WOOD_BROWN, collide=True)
        # Cloud platforms (white boxes high up)
        self.add_box(-400, 350, 0, 100, 15, 100, WHITE, collide=True)
        self.add_box(-200, 400, 100, 100, 15, 100, WHITE, collide=True)
        # Trees at base
        self.add_tree(-600, -500)
        self.add_tree(600, -500)
        self.add_tree(-500, -300)
        self.add_tree(500, -200)
        # Stars
        self.add_star(0, 480, 400)         # Peak
        self.add_star(-200, 420, 100)      # Cloud
        self.add_star(-300, 130, -200)     # Mushroom
        # Coins
        self.add_coins_line(-400, 0, -400, 400, 0, -400, 8)
        self.add_coins_ring(0, 300, 400, 100, 8)


# =================================================
# COURSE 13: TINY-HUGE ISLAND
# =================================================
class TinyHugeIsland(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Tiny-Huge Island"
        self.sky_color = SKY_BLUE
        self.spawn = (0, -600)
        self.build()

    def build(self):
        # Main island (huge version proportions)
        self.add_box(0, 0, 0, 2200, 10, 2200, GRASS_GREEN)
        # Central mountain
        self.add_box(0, 80, 300, 500, 160, 500, DARK_GREEN, collide=True)
        self.add_box(0, 200, 300, 300, 100, 300, GRASS_GREEN, collide=True)
        self.add_roof(0, 300, 300, 350, 150, 350, DARK_GREEN)
        # Beach area
        self.add_box(0, -3, -700, 800, 8, 300, SAND_YELLOW)
        self.add_box(0, -8, -900, 800, 6, 200, WATER_BLUE)
        # Goombas area (tiny mushrooms as size reference)
        self.add_box(-400, 10, -300, 20, 15, 20, DARK_BROWN)
        self.add_box(-400, 20, -300, 25, 8, 25, MARIO_RED)
        # Pipe to tiny world
        self.add_box(-600, 10, 400, 60, 50, 60, DARK_GREEN)
        self.add_box(600, 10, -400, 60, 50, 60, DARK_GREEN)
        # Wiggler cave
        self.add_box(300, 150, 500, 120, 80, 120, CAVE_BROWN)
        self.add_box(300, 150, 500, 80, 60, 80, CAVE_DARK)
        # Koopa shell area
        self.add_box(-500, 5, -500, 250, 10, 250, STONE_PATH)
        # Tiny buildings
        self.add_box(400, 20, -200, 80, 40, 80, STONE_GRAY)
        self.add_roof(400, 50, -200, 100, 30, 100, ROOF_RED)
        self.add_box(500, 15, -100, 60, 30, 60, STONE_GRAY)
        self.add_roof(500, 35, -100, 80, 25, 80, ROOF_RED)
        # Piranha plants (stems)
        for px, pz in [(-200, 200), (-100, 350), (200, 150)]:
            self.add_box(px, 15, pz, 15, 40, 15, DARK_GREEN)
            self.add_box(px, 40, pz, 30, 15, 30, MARIO_RED)
        # Water pools
        self.add_box(-700, -5, 700, 300, 6, 300, WATER_BLUE)
        # Trees
        self.add_tree(-800, -200)
        self.add_tree(800, -300)
        self.add_tree(-300, 700)
        self.add_tree(500, 700)
        # Stars
        self.add_star(0, 400, 300)         # Mountain top
        self.add_star(300, 200, 500)       # Wiggler
        self.add_star(-600, 60, 400)       # Pipe
        # Coins
        self.add_coins_line(-600, 0, -300, 600, 0, -300, 10)
        self.add_coins_ring(0, 100, 300, 120, 8)


# =================================================
# COURSE 14: TICK TOCK CLOCK
# =================================================
class TickTockClock(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Tick Tock Clock"
        self.sky_color = SKY_CAVE
        self.spawn = (0, -200)
        self.build()

    def build(self):
        # Clock bottom
        self.add_box(0, 0, 0, 600, 10, 600, CLOCK_BEIGE)
        # Vertical shaft walls (clock interior)
        self.add_box(-300, 400, 0, 20, 800, 600, CLOCK_BEIGE)
        self.add_box(300, 400, 0, 20, 800, 600, CLOCK_BEIGE)
        self.add_box(0, 400, -300, 600, 800, 20, CLOCK_BEIGE)
        self.add_box(0, 400, 300, 600, 800, 20, CLOCK_BEIGE)
        # Ascending platforms (clock hands/gears)
        platforms = [
            (0, 40, 0, 200, 12, 200, METAL_GRAY),
            (-100, 100, 50, 150, 10, 60, METAL_GRAY),
            (100, 170, -50, 150, 10, 60, METAL_GRAY),
            (0, 240, 100, 120, 10, 120, METAL_GRAY),
            (-80, 310, -80, 100, 10, 100, METAL_GRAY),
            (80, 380, 80, 100, 10, 100, METAL_GRAY),
            (0, 450, 0, 150, 10, 80, METAL_GRAY),
            (-100, 520, 100, 100, 10, 100, METAL_GRAY),
            (100, 590, -100, 100, 10, 100, METAL_GRAY),
            (0, 660, 0, 180, 10, 180, METAL_GRAY),
            (0, 740, 0, 250, 10, 250, METAL_GRAY),
        ]
        for px, py, pz, pw, ph, pd, c in platforms:
            self.add_box(px, py, pz, pw, ph, pd, c, collide=True)
        # Gear decorations
        for gy in [150, 350, 550]:
            self.add_box(-280, gy, 0, 15, 80, 80, GOLD)
            self.add_box(280, gy, 0, 15, 80, 80, GOLD)
        # Pendulum (static representation)
        self.add_box(0, 300, -280, 10, 200, 10, METAL_GRAY)
        self.add_box(0, 200, -280, 40, 40, 10, GOLD)
        # Clock face at top
        self.add_box(0, 780, 0, 280, 10, 280, WHITE)
        # Clock hands
        self.add_box(0, 790, 0, 120, 4, 12, BLACK)
        self.add_box(0, 790, 0, 8, 4, 80, BLACK)
        # Numbers (small blocks around clock face)
        for i in range(12):
            a = (2 * math.pi * i) / 12
            nx = math.sin(a) * 120
            nz = math.cos(a) * 120
            self.add_box(nx, 790, nz, 15, 6, 15, BLACK)
        # Stars
        self.add_star(0, 800, 0)           # Top of clock
        self.add_star(0, 470, 0)           # Mid level
        self.add_star(-100, 530, 100)      # Side platform
        # Coins
        self.add_coins_line(-100, 100, 0, 100, 100, 0, 4)
        self.add_coins_ring(0, 450, 0, 60, 6)
        self.add_coins_ring(0, 740, 0, 100, 8)


# =================================================
# COURSE 15: RAINBOW RIDE
# =================================================
class RainbowRide(WorldBase):
    def __init__(self):
        super().__init__()
        self.name = "Rainbow Ride"
        self.sky_color = SKY_RAINBOW
        self.spawn = (0, -300)
        self.build()

    def build(self):
        # Starting platform
        self.add_box(0, 0, -300, 250, 15, 250, STONE_GRAY, collide=True)
        # Rainbow carpet path (series of floating colored platforms)
        rainbow_colors = [MARIO_RED, LAVA_ORANGE, YELLOW, GRASS_GREEN,
                          SKY_BLUE, PURPLE, RAINBOW_PINK]
        for i in range(14):
            c = rainbow_colors[i % len(rainbow_colors)]
            z_off = i * 100
            x_off = math.sin(i * 0.5) * 150
            y_off = i * 15
            self.add_box(x_off, y_off, z_off, 80, 8, 80, c, collide=True)
        # Flying ship
        self.add_box(-300, 200, 800, 250, 50, 100, WOOD_BROWN, collide=True)
        self.add_box(-300, 230, 800, 200, 30, 70, DARK_BROWN)
        self.add_box(-300, 270, 800, 10, 100, 10, WOOD_BROWN)  # mast
        self.add_box(-300, 340, 800, 80, 5, 40, WHITE)  # sail
        # House in the sky
        self.add_box(400, 250, 600, 180, 120, 150, STONE_GRAY, collide=True)
        self.add_roof(400, 340, 600, 220, 80, 180, ROOF_RED)
        self.add_box(400, 270, 525, 40, 60, 5, DARK_BROWN)  # door
        # Floating islands
        self.add_box(-500, 100, 300, 150, 20, 150, GRASS_GREEN, collide=True)
        self.add_box(500, 150, 400, 120, 20, 120, GRASS_GREEN, collide=True)
        self.add_box(-200, 300, 1000, 100, 20, 100, GRASS_GREEN, collide=True)
        # Tricky triangles area
        self.add_box(200, 80, 200, 80, 8, 80, RAINBOW_CYAN, collide=True)
        self.add_box(300, 120, 300, 80, 8, 80, RAINBOW_LIME, collide=True)
        self.add_box(200, 160, 400, 80, 8, 80, RAINBOW_PINK, collide=True)
        # Swinging platforms (static)
        self.add_box(-400, 150, 500, 100, 8, 60, WOOD_BROWN, collide=True)
        self.add_box(-100, 200, 700, 100, 8, 60, WOOD_BROWN, collide=True)
        # Bob-omb buddy cannon
        self.add_box(-600, 80, 100, 50, 40, 50, CANNON_BLACK)
        # Clouds
        for cx, cy, cz in [(300, 400, 300), (-200, 350, 600), (0, 450, 900)]:
            self.add_box(cx, cy, cz, 120, 20, 80, WHITE)
        # Stars
        self.add_star(-300, 320, 800)      # Ship
        self.add_star(400, 380, 600)       # House
        self.add_star(-200, 330, 1000)     # Floating island
        # Coins
        for i in range(7):
            z_off = i * 100
            x_off = math.sin(i * 0.5) * 150
            y_off = i * 15 + 30
            self.coins.append(Coin(x_off, y_off, z_off))
        self.add_coins_ring(-300, 250, 800, 80, 8)


# =================================================
# ALL COURSES REGISTRY
# =================================================
COURSE_LIST = [
    ("Castle Grounds",       CastleGrounds,      "(Hub World)",     STONE_GRAY),
    ("Bob-omb Battlefield",  BobOmbBattlefield,   "Course 1",       GRASS_GREEN),
    ("Whomp's Fortress",     WhompsFortress,      "Course 2",       STONE_GRAY),
    ("Jolly Roger Bay",      JollyRogerBay,       "Course 3",       WATER_BLUE),
    ("Cool, Cool Mountain",  CoolCoolMountain,    "Course 4",       SNOW_WHITE),
    ("Big Boo's Haunt",      BigBoosHaunt,        "Course 5",       MANSION_PURPLE),
    ("Hazy Maze Cave",       HazyMazeCave,        "Course 6",       CAVE_BROWN),
    ("Lethal Lava Land",     LethalLavaLand,      "Course 7",       LAVA_RED),
    ("Shifting Sand Land",   ShiftingSandLand,    "Course 8",       SAND_YELLOW),
    ("Dire, Dire Docks",     DireDireDocks,       "Course 9",       DOCK_BLUE),
    ("Snowman's Land",       SnowmansLand,        "Course 10",      SNOW_WHITE),
    ("Wet-Dry World",        WetDryWorld,         "Course 11",      WATER_BLUE),
    ("Tall, Tall Mountain",  TallTallMountain,    "Course 12",      DARK_GREEN),
    ("Tiny-Huge Island",     TinyHugeIsland,      "Course 13",      GRASS_GREEN),
    ("Tick Tock Clock",      TickTockClock,       "Course 14",      CLOCK_BEIGE),
    ("Rainbow Ride",         RainbowRide,         "Course 15",      RAINBOW_PINK),
]

# -------------------------------------------------
# RENDER ENGINE
# -------------------------------------------------
def render_world(screen, world, mario, cam):
    screen.fill(world.sky_color)
    render_list = []

    # World geometry
    for indices, color in world.faces:
        pts = []
        z_sum = 0
        visible = True
        for i in indices:
            res = project_point(*world.verts[i], cam.x, cam.y, cam.z, cam.yaw)
            if not res:
                visible = False
                break
            pts.append((res[0], res[1]))
            z_sum += res[2]
        if visible and len(pts) >= 3:
            render_list.append((z_sum / len(indices), pts, color))

    # Collectibles
    for star in world.stars:
        star.update()
        sv, sf = star.get_mesh()
        for indices, color in sf:
            pts = []
            z_sum = 0
            visible = True
            for i in indices:
                res = project_point(*sv[i], cam.x, cam.y, cam.z, cam.yaw)
                if not res:
                    visible = False
                    break
                pts.append((res[0], res[1]))
                z_sum += res[2]
            if visible and len(pts) >= 3:
                render_list.append((z_sum / len(indices), pts, color))

    for coin in world.coins:
        coin.update()
        cv, cf = coin.get_mesh()
        for indices, color in cf:
            pts = []
            z_sum = 0
            visible = True
            for i in indices:
                res = project_point(*cv[i], cam.x, cam.y, cam.z, cam.yaw)
                if not res:
                    visible = False
                    break
                pts.append((res[0], res[1]))
                z_sum += res[2]
            if visible and len(pts) >= 3:
                render_list.append((z_sum / len(indices), pts, color))

    # Mario
    m_verts, m_faces = mario.get_mesh()
    for indices, color in m_faces:
        pts = []
        z_sum = 0
        visible = True
        for i in indices:
            res = project_point(*m_verts[i], cam.x, cam.y, cam.z, cam.yaw)
            if not res:
                visible = False
                break
            pts.append((res[0], res[1]))
            z_sum += res[2]
        if visible and len(pts) >= 3:
            render_list.append((z_sum / len(indices), pts, color))

    # Painter's algorithm
    render_list.sort(key=lambda x: x[0], reverse=True)
    for _, pts, color in render_list:
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, BLACK, pts, 1)


# -------------------------------------------------
# HUD
# -------------------------------------------------
def draw_hud(screen, mario, world_name):
    # Background bar
    pygame.draw.rect(screen, (0, 0, 0, 128), (0, 0, WIDTH, 45))
    pygame.draw.rect(screen, (0, 0, 0), (0, 44, WIDTH, 2))

    # Stars
    star_txt = star_font.render(f"★{mario.stars_collected}", True, STAR_YELLOW)
    screen.blit(star_txt, (15, 2))

    # Coins
    coin_txt = hud_font.render(f"×{mario.coins:03d}", True, YELLOW)
    screen.blit(coin_txt, (120, 14))

    # Lives
    life_txt = hud_font.render(f"♥{mario.lives}", True, MARIO_RED)
    screen.blit(life_txt, (220, 14))

    # Level name
    name_txt = hud_font.render(world_name, True, WHITE)
    screen.blit(name_txt, (WIDTH - name_txt.get_width() - 15, 14))

    # Controls (bottom)
    ctrl = small_font.render("WASD/ARROWS: Move | SPACE: Jump | Q/E: Camera | ESC: Level Select", True, WHITE)
    screen.blit(ctrl, (WIDTH//2 - ctrl.get_width()//2, HEIGHT - 22))


# -------------------------------------------------
# MENU SCENE
# -------------------------------------------------
class MenuScene:
    def __init__(self):
        self.ticks = 0
        self.yaw = 0.0

    def update(self):
        self.ticks += 1
        self.yaw += 0.03

    def draw(self, screen):
        screen.fill(NES_BLUE)
        # Spinning cube
        cx, cy = WIDTH // 2, HEIGHT // 2 + 50
        pts = []
        raw_v = [(-50,-50,-50),(50,-50,-50),(50,50,-50),(-50,50,-50),
                 (-50,-50,50),(50,-50,50),(50,50,50),(-50,50,50)]
        for v in raw_v:
            rx, rz = rotate_y(v[0], v[2], self.yaw)
            s = 400 / (rz + 300)
            pts.append((rx * s + cx, v[1] * s + cy))
        for f in [[0,1,2,3],[4,5,6,7],[0,4,7,3],[1,5,6,2]]:
            poly = [pts[i] for i in f]
            col = MARIO_RED if f[0] < 4 else MARIO_BLUE
            pygame.draw.polygon(screen, col, poly)
            pygame.draw.polygon(screen, BLACK, poly, 2)

        # Title
        shadow = title_font.render("ULTRA MARIO 3D BROS", True, BLACK)
        title  = title_font.render("ULTRA MARIO 3D BROS", True, YELLOW)
        tr = title.get_rect(center=(WIDTH // 2, 130))
        screen.blit(shadow, (tr.x + 4, tr.y + 4))
        screen.blit(title, tr)

        # Subtitle
        sub = menu_font.render("~ Complete 64 Edition ~", True, WHITE)
        screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 195)))

        # Prompt
        if (self.ticks // 30) % 2 == 0:
            prompt = menu_font.render("PRESS SPACE TO START", True, WHITE)
            screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT - 80)))


# -------------------------------------------------
# LETTER SCENE
# -------------------------------------------------
class LetterScene:
    def __init__(self):
        self.lines = [
            "Dear Mario,",
            "",
            "Please come to the castle.",
            "I've baked a cake for you.",
            "",
            "Yours truly,",
            "Princess Toadstool",
            "  ~ Peach"
        ]
        self.timer = 0

    def update(self):
        self.timer += 1

    def draw(self, screen):
        screen.fill(BLACK)
        paper = pygame.Rect(0, 0, 450, 400)
        paper.center = SCREEN_CENTER
        pygame.draw.rect(screen, PARCHMENT, paper)
        pygame.draw.rect(screen, INK_COLOR, paper, 4)

        y = paper.top + 50
        for line in self.lines:
            txt = letter_font.render(line, True, INK_COLOR)
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))
            y += 40

        if self.timer > 60:
            prompt = hud_font.render("Press SPACE to Continue", True, WHITE)
            screen.blit(prompt, (WIDTH - 280, HEIGHT - 40))


# -------------------------------------------------
# LEVEL SELECT SCENE
# -------------------------------------------------
class LevelSelectScene:
    def __init__(self, total_stars=0):
        self.cursor = 0
        self.scroll = 0
        self.total_stars = total_stars
        self.visible_count = 8

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.cursor = max(0, self.cursor - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.cursor = min(len(COURSE_LIST) - 1, self.cursor + 1)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return self.cursor
        # Scroll follow
        if self.cursor < self.scroll:
            self.scroll = self.cursor
        if self.cursor >= self.scroll + self.visible_count:
            self.scroll = self.cursor - self.visible_count + 1
        return None

    def draw(self, screen):
        screen.fill((20, 15, 40))

        # Title
        title = title_font.render("SELECT COURSE", True, STAR_YELLOW)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 55)))

        # Star count
        star_txt = menu_font.render(f"Total Stars: ★ {self.total_stars}", True, YELLOW)
        screen.blit(star_txt, star_txt.get_rect(center=(WIDTH // 2, 105)))

        # Course list
        y_start = 145
        row_h = 52
        for i in range(self.scroll, min(self.scroll + self.visible_count, len(COURSE_LIST))):
            name, _, label, color = COURSE_LIST[i]
            y = y_start + (i - self.scroll) * row_h
            # Highlight
            if i == self.cursor:
                pygame.draw.rect(screen, (50, 45, 80), (60, y - 4, WIDTH - 120, row_h - 4))
                pygame.draw.rect(screen, STAR_YELLOW, (60, y - 4, WIDTH - 120, row_h - 4), 2)
            # Color swatch
            pygame.draw.rect(screen, color, (80, y + 4, 30, 30))
            pygame.draw.rect(screen, WHITE, (80, y + 4, 30, 30), 1)
            # Label
            lbl = small_font.render(label, True, (180, 180, 180))
            screen.blit(lbl, (125, y + 2))
            # Name
            n = select_font.render(name, True, WHITE if i == self.cursor else (200, 200, 200))
            screen.blit(n, (125, y + 18))

        # Scroll indicators
        if self.scroll > 0:
            arr = menu_font.render("▲", True, WHITE)
            screen.blit(arr, arr.get_rect(center=(WIDTH // 2, y_start - 15)))
        if self.scroll + self.visible_count < len(COURSE_LIST):
            arr = menu_font.render("▼", True, WHITE)
            screen.blit(arr, arr.get_rect(center=(WIDTH // 2, y_start + self.visible_count * row_h + 5)))

        # Controls
        ctrl = small_font.render("UP/DOWN: Navigate | SPACE/ENTER: Select | ESC: Back to Menu", True, (150, 150, 150))
        screen.blit(ctrl, ctrl.get_rect(center=(WIDTH // 2, HEIGHT - 20)))


# -------------------------------------------------
# STAR GET SCENE
# -------------------------------------------------
class StarGetScene:
    def __init__(self):
        self.timer = 0

    def update(self):
        self.timer += 1

    def draw(self, screen, total_stars):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(min(self.timer * 4, 180))
        screen.blit(overlay, (0, 0))

        if self.timer > 20:
            # Star burst
            bob = math.sin(self.timer * 0.1) * 5
            star_size = min(self.timer - 20, 30)
            for angle in range(0, 360, 72):
                a = math.radians(angle + self.timer * 2)
                sx = WIDTH // 2 + math.cos(a) * (star_size * 2 + 20)
                sy = HEIGHT // 2 - 30 + math.sin(a) * (star_size * 2 + 20) + bob
                pygame.draw.circle(screen, STAR_YELLOW, (int(sx), int(sy)), max(3, star_size // 3))

            txt = star_font.render("★ STAR GET! ★", True, STAR_YELLOW)
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

            count = menu_font.render(f"Total: {total_stars}", True, WHITE)
            screen.blit(count, count.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

        if self.timer > 120:
            prompt = small_font.render("Press SPACE to continue", True, WHITE)
            screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))


# -------------------------------------------------
# MAIN GAME LOOP
# -------------------------------------------------
def main():
    state       = STATE_MENU
    menu_scene  = MenuScene()
    letter_scene = LetterScene()
    level_sel   = LevelSelectScene()
    star_scene  = StarGetScene()

    mario       = None
    cam         = None
    world       = None
    total_stars = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # ---- STATE MACHINE ----
        if state == STATE_MENU:
            menu_scene.update()
            menu_scene.draw(screen)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    letter_scene = LetterScene()
                    state = STATE_LETTER

        elif state == STATE_LETTER:
            letter_scene.update()
            letter_scene.draw(screen)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    level_sel = LevelSelectScene(total_stars)
                    state = STATE_LEVEL_SEL

        elif state == STATE_LEVEL_SEL:
            level_sel.total_stars = total_stars
            choice = level_sel.update(events)
            level_sel.draw(screen)
            if choice is not None:
                _, WorldClass, _, _ = COURSE_LIST[choice]
                world = WorldClass()
                mario = Mario(*world.spawn)
                cam = Camera(mario)
                state = STATE_PLAYING
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = STATE_MENU

        elif state == STATE_PLAYING:
            result = mario.update(keys, cam.yaw, world.platforms)
            cam.update(keys)

            # Check star collection
            got_star = False
            for star in world.stars:
                if star.check(mario):
                    total_stars += 1
                    got_star = True
            for coin in world.coins:
                coin.check(mario)

            render_world(screen, world, mario, cam)
            draw_hud(screen, mario, world.name)

            if got_star:
                star_scene = StarGetScene()
                state = STATE_STAR_GET

            if result == "death":
                if mario.lives <= 0:
                    state = STATE_MENU
                    total_stars = 0
                else:
                    mario.respawn(*world.spawn)

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    level_sel = LevelSelectScene(total_stars)
                    state = STATE_LEVEL_SEL

        elif state == STATE_STAR_GET:
            # Keep rendering world behind
            render_world(screen, world, mario, cam)
            draw_hud(screen, mario, world.name)
            star_scene.update()
            star_scene.draw(screen, total_stars)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if star_scene.timer > 60:
                        state = STATE_PLAYING

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
