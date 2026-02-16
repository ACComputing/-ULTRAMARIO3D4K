import pygame
import sys
import math

# -------------------------------------------------
# INIT
# -------------------------------------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN_CENTER = (WIDTH // 2, HEIGHT // 2)
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultra Mario 3D Bros - Peach's Castle PC Port")
clock = pygame.time.Clock()

# -------------------------------------------------
# COLORS
# -------------------------------------------------
SKY_BLUE = (100, 149, 237)
NES_BLUE = (92, 148, 252)
GRASS_GREEN = (50, 160, 60)
STONE_GRAY = (220, 220, 220)
ROOF_RED = (180, 40, 40)
MOAT_BLUE = (40, 100, 200)
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
YELLOW = (255, 230, 0)
MARIO_RED = (255, 0, 0)
MARIO_BLUE = (0, 70, 180)
WOOD_BROWN = (140, 100, 60)
PARCHMENT = (250, 240, 200)
INK_COLOR = (50, 40, 100)

# Fonts
try:
    title_font = pygame.font.SysFont("Arial Black", 55, bold=True)
    letter_font = pygame.font.SysFont("Georgia", 30, italic=True)
    menu_font = pygame.font.SysFont("Arial", 28, bold=True)
except:
    title_font = pygame.font.Font(None, 70)
    letter_font = pygame.font.Font(None, 36)
    menu_font = pygame.font.Font(None, 40)

font = pygame.font.SysFont("Courier New", 18, bold=True)

# Game States
STATE_MENU = 0
STATE_LETTER = 1
STATE_GAME = 2

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

# -------------------------------------------------
# MARIO
# -------------------------------------------------
class Mario:
    def __init__(self, x, z):
        self.x, self.y, self.z = x, 0, z
        self.vx = self.vy = self.vz = 0
        self.ground_accel = 1.2
        self.air_accel = 0.4
        self.max_speed = 22
        self.friction = 0.82
        self.gravity = 1.3
        self.terminal_velocity = -45
        self.jump_force = 24
        self.grounded = True
        self.yaw = 0
        self.size = 25

    def update(self, keys, cam_yaw):
        move_x = move_z = 0
        if keys[pygame.K_LEFT]: move_x -= 1
        if keys[pygame.K_RIGHT]: move_x += 1
        if keys[pygame.K_UP]: move_z += 1
        if keys[pygame.K_DOWN]: move_z -= 1
        moving = (move_x or move_z)
        if moving:
            input_angle = math.atan2(move_x, move_z)
            target_angle = cam_yaw + input_angle
            turn_speed = 0.25
            diff = (target_angle - self.yaw)
            diff = (diff + math.pi) % (2 * math.pi) - math.pi
            self.yaw += diff * turn_speed
            accel = self.ground_accel if self.grounded else self.air_accel
            self.vx += math.sin(self.yaw) * accel
            self.vz += math.cos(self.yaw) * accel
        speed = math.hypot(self.vx, self.vz)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vz *= scale
        if self.grounded:
            self.vx *= self.friction
            self.vz *= self.friction
        self.vy -= self.gravity
        if self.vy < self.terminal_velocity:
            self.vy = self.terminal_velocity
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        if self.y <= 0:
            self.y = 0
            self.vy = 0
            self.grounded = True
        else:
            self.grounded = False
        if keys[pygame.K_SPACE] and self.grounded:
            self.vy = self.jump_force
            self.grounded = False

    def get_mesh(self):
        s = self.size
        h = s * 2
        verts = [
            (self.x-s, self.y, self.z-s), (self.x+s, self.y, self.z-s),
            (self.x+s, self.y, self.z+s), (self.x-s, self.y, self.z+s),
            (self.x-s, self.y+h, self.z-s), (self.x+s, self.y+h, self.z-s),
            (self.x+s, self.y+h, self.z+s), (self.x-s, self.y+h, self.z+s)
        ]
        faces = [
            ([0,1,2,3], MARIO_BLUE),
            ([4,5,6,7], MARIO_RED),
            ([0,4,5,1], MARIO_RED),
            ([2,6,7,3], MARIO_RED),
            ([1,5,6,2], MARIO_BLUE),
            ([0,4,7,3], MARIO_BLUE)
        ]
        return verts, faces

# -------------------------------------------------
# CAMERA
# -------------------------------------------------
class Camera:
    def __init__(self, target):
        self.target = target
        self.yaw = 0
        self.dist = 700
        self.height = 350
        self.x = 0
        self.y = 0
        self.z = 0

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
# WORLD
# -------------------------------------------------
class World:
    def __init__(self):
        self.verts = []
        self.faces = []
        self.build()

    def add_box(self, x, y, z, w, h, d, color):
        idx = len(self.verts)
        hw, hh, hd = w/2, h/2, d/2
        self.verts += [
            (x-hw, y-hh, z-hd), (x+hw, y-hh, z-hd), (x+hw, y+hh, z-hd), (x-hw, y+hh, z-hd),
            (x-hw, y-hh, z+hd), (x+hw, y-hh, z+hd), (x+hw, y+hh, z+hd), (x-hw, y+hh, z+hd)
        ]
        for f in [[0,1,2,3], [4,5,6,7], [0,4,7,3], [1,5,6,2], [3,2,6,7], [0,1,5,4]]:
            self.faces.append(([i + idx for i in f], color))

    def add_roof(self, x, y, z, w, h, d, color):
        idx = len(self.verts)
        hw, hd = w/2, d/2
        self.verts.extend([
            (x-hw, y, z-hd), (x+hw, y, z-hd),
            (x+hw, y, z+hd), (x-hw, y, z+hd),
            (x, y + h, z)
        ])
        for f in [[0,1,4], [1,2,4], [2,3,4], [3,0,4]]:
            self.faces.append(([i + idx for i in f], color))
        self.faces.append(([0,1,2,3], color))

    def build(self):
        self.add_box(0, -20, 0, 3200, 40, 3200, MOAT_BLUE)
        self.add_box(0, 0, 0, 1400, 10, 1400, GRASS_GREEN)
        self.add_box(0, 150, 400, 400, 300, 300, STONE_GRAY)
        self.add_box(0, 350, 400, 150, 200, 150, STONE_GRAY)
        self.add_roof(0, 450, 400, 180, 150, 180, ROOF_RED)
        self.add_box(-220, 200, 400, 100, 400, 100, STONE_GRAY)
        self.add_roof(-220, 400, 400, 120, 100, 120, ROOF_RED)
        self.add_box(220, 200, 400, 100, 400, 100, STONE_GRAY)
        self.add_roof(220, 400, 400, 120, 100, 120, ROOF_RED)
        self.add_box(0, 10, -250, 120, 20, 520, WOOD_BROWN)
        self.add_roof(-850, 0, 850, 700, 380, 700, GRASS_GREEN)
        self.add_roof(850, 0, 950, 550, 320, 550, GRASS_GREEN)

# -------------------------------------------------
# SCENES
# -------------------------------------------------
class MenuScene:
    def __init__(self):
        self.ticks = 0
        self.yaw = 0

    def update(self):
        self.ticks += 1
        self.yaw += 0.03

    def draw(self, screen):
        screen.fill(NES_BLUE)
        scale = 1.0 + math.sin(self.ticks * 0.1) * 0.05
        title_surf = title_font.render("ULTRA MARIO 3D BROS", True, YELLOW)
        title_rect = title_surf.get_rect(center=(WIDTH//2, 150))
        shadow = title_font.render("ULTRA MARIO 3D BROS", True, BLACK)
        screen.blit(shadow, (title_rect.x + 5, title_rect.y + 5))
        screen.blit(title_surf, title_rect)

        # Spinning cube
        cx, cy = WIDTH//2, HEIGHT//2 + 50
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

        if (self.ticks // 30) % 2 == 0:
            prompt = menu_font.render("PRESS SPACE TO START", True, WHITE)
            screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, HEIGHT - 100)))

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
            "Peach"
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
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, y)))
            y += 40
        
        if self.timer > 60:
            prompt = font.render("Press SPACE to Continue", True, WHITE)
            screen.blit(prompt, (WIDTH - 250, HEIGHT - 40))

class GameScene:
    def __init__(self):
        self.mario = Mario(0, -620)
        self.cam = Camera(self.mario)
        self.world = World()

    def update(self, keys):
        self.mario.update(keys, self.cam.yaw)
        self.cam.update(keys)

    def draw(self, screen):
        screen.fill(SKY_BLUE)
        render = []
        # World
        for indices, color in self.world.faces:
            pts = []
            z_sum = 0
            visible = True
            for i in indices:
                res = project_point(*self.world.verts[i], self.cam.x, self.cam.y, self.cam.z, self.cam.yaw)
                if not res:
                    visible = False
                    break
                pts.append((res[0], res[1]))
                z_sum += res[2]
            if visible:
                render.append((z_sum / len(indices), pts, color))
        # Mario
        m_verts, m_faces = self.mario.get_mesh()
        for indices, color in m_faces:
            pts = []
            z_sum = 0
            visible = True
            for i in indices:
                res = project_point(*m_verts[i], self.cam.x, self.cam.y, self.cam.z, self.cam.yaw)
                if not res:
                    visible = False
                    break
                pts.append((res[0], res[1]))
                z_sum += res[2]
            if visible:
                render.append((z_sum / len(indices), pts, color))
        render.sort(key=lambda x: x[0], reverse=True)
        for _, pts, color in render:
            pygame.draw.polygon(screen, color, pts)
            pygame.draw.polygon(screen, BLACK, pts, 1)

        hud = font.render("ARROWS: MOVE | SPACE: JUMP | Q/E: CAMERA | ESC: MENU", True, WHITE)
        screen.blit(hud, (20, 20))

# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    state = STATE_MENU
    menu = MenuScene()
    letter = LetterScene()
    game = None

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if state == STATE_MENU:
                        state = STATE_LETTER
                    elif state == STATE_LETTER:
                        game = GameScene()
                        state = STATE_GAME
                if event.key == pygame.K_ESCAPE:
                    state = STATE_MENU

        if state == STATE_MENU:
            menu.update()
            menu.draw(screen)
        elif state == STATE_LETTER:
            letter.update()
            letter.draw(screen)
        elif state == STATE_GAME:
            game.update(keys)
            game.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
