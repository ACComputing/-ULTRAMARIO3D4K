import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# -------------------------------------------------
# CONSTANTS & SETUP
# -------------------------------------------------
WIDTH, HEIGHT = 800, 600
SCREEN_CENTER = (WIDTH // 2, HEIGHT // 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultra Mario Bros: Lakitu Engine")
clock = pygame.time.Clock()

# Game States
STATE_MENU = 0
STATE_LETTER = 1
STATE_GAME = 2

# Colors
SKY_BLUE = (135, 206, 235)
NES_BLUE = (92, 148, 252)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 216, 0)
RED = (220, 40, 40)
MARIO_RED = (255, 50, 50)
MARIO_BLUE = (0, 50, 200)
GRASS_GREEN = (34, 177, 76)
STONE_WHITE = (240, 240, 240)
DARK_STONE = (180, 180, 180)
PARCHMENT = (255, 248, 220)
INK_COLOR = (40, 40, 90)
SHADOW = (0, 0, 0, 100)

# Fonts
try:
    title_font = pygame.font.SysFont("Arial Black", 50, bold=True)
    hud_font = pygame.font.SysFont("Courier New", 20, bold=True)
    # Try to find a script/fancy font for the letter
    letter_font = pygame.font.SysFont("Brush Script MT", 35)
    if not letter_font.get_height() > 20: # Fallback check
        raise ValueError
    menu_font = pygame.font.SysFont("Arial", 30, bold=True)
except:
    title_font = pygame.font.Font(None, 60)
    hud_font = pygame.font.Font(None, 24)
    letter_font = pygame.font.SysFont("Times New Roman", 32, italic=True)
    menu_font = pygame.font.Font(None, 40)

# -------------------------------------------------
# 3D MATH HELPERS
# -------------------------------------------------
def rotate_y(x, z, angle):
    """Rotates a point (x, z) around the Y-axis (vertical) by angle radians."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return x * cos_a - z * sin_a, x * sin_a + z * cos_a

def project_point(x, y, z, cam_x, cam_y, cam_z, cam_yaw, fov=600):
    """
    Projects a 3D world point to 2D screen coordinates.
    Returns (screen_x, screen_y, depth) or None if behind camera.
    """
    dx = x - cam_x
    dy = y - cam_y
    dz = z - cam_z

    rx, rz = rotate_y(dx, dz, -cam_yaw)
    ry = dy

    if rz <= 1:  # Clip points behind the camera
        return None
    
    scale = fov / rz
    px = rx * scale + SCREEN_CENTER[0]
    py = -ry * scale + SCREEN_CENTER[1]

    return (int(px), int(py), rz)

# -------------------------------------------------
# PLAYER ENGINE
# -------------------------------------------------
class Player:
    def __init__(self, x, z):
        self.x = x
        self.y = 0  # Y is Up
        self.z = z
        self.width = 30
        self.height = 60
        
        # Physics
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.speed = 5
        self.gravity = 0.5
        self.jump_force = 12
        self.friction = 0.85
        self.grounded = True
        self.facing_angle = 0

    def update(self, keys, cam_yaw):
        input_x = 0
        input_z = 0

        if keys[pygame.K_LEFT]: input_x = -1
        if keys[pygame.K_RIGHT]: input_x = 1
        if keys[pygame.K_UP]: input_z = 1
        if keys[pygame.K_DOWN]: input_z = -1

        # Jump
        if keys[pygame.K_SPACE] and self.grounded:
            self.vy = self.jump_force
            self.grounded = False

        # Calculate Movement Vector relative to Camera
        if input_x != 0 or input_z != 0:
            input_angle = math.atan2(input_x, input_z)
            move_angle = cam_yaw + input_angle
            
            self.vx += math.sin(move_angle) * 0.5
            self.vz += math.cos(move_angle) * 0.5
            self.facing_angle = move_angle

        # Physics Application
        self.x += self.vx
        self.z += self.vz
        self.y += self.vy
        self.vy -= self.gravity # Gravity

        # Friction
        self.vx *= self.friction
        self.vz *= self.friction

        # Simple Floor Collision
        if self.y <= 0:
            self.y = 0
            self.vy = 0
            self.grounded = True

    def get_mesh(self):
        """Returns the vertices and faces for Mario (Cube)"""
        w = self.width / 2
        h = self.height
        
        verts = [
            (self.x - w, self.y, self.z - w),     # 0
            (self.x + w, self.y, self.z - w),     # 1
            (self.x + w, self.y, self.z + w),     # 2
            (self.x - w, self.y, self.z + w),     # 3
            (self.x - w, self.y + h, self.z - w), # 4
            (self.x + w, self.y + h, self.z - w), # 5
            (self.x + w, self.y + h, self.z + w), # 6
            (self.x - w, self.y + h, self.z + w)  # 7
        ]
        
        faces = [
            ([0, 1, 2, 3], MARIO_BLUE), # Bottom
            ([4, 5, 6, 7], MARIO_RED),  # Top (Hat)
            ([0, 4, 7, 3], MARIO_BLUE), # Left
            ([1, 5, 6, 2], MARIO_BLUE), # Right
            ([0, 1, 5, 4], MARIO_RED),  # Back
            ([3, 2, 6, 7], MARIO_RED),  # Front
        ]
        return verts, faces

# -------------------------------------------------
# LAKITU CAMERA ENGINE
# -------------------------------------------------
class LakituCamera:
    def __init__(self, target):
        self.target = target
        self.x = 0
        self.y = 200
        self.z = -400
        self.yaw = 0
        
        self.distance = 500
        self.height = 250
        self.smooth_speed = 0.1
        self.rotation_speed = 0.03

    def update(self, keys):
        if keys[pygame.K_q]:
            self.yaw -= self.rotation_speed
        if keys[pygame.K_e]:
            self.yaw += self.rotation_speed

        desired_x = self.target.x - math.sin(self.yaw) * self.distance
        desired_z = self.target.z - math.cos(self.yaw) * self.distance
        desired_y = self.target.y + self.height

        self.x += (desired_x - self.x) * self.smooth_speed
        self.y += (desired_y - self.y) * self.smooth_speed
        self.z += (desired_z - self.z) * self.smooth_speed

# -------------------------------------------------
# SCENES
# -------------------------------------------------

# --- 1. GAME SCENE ---
class GameScene:
    def __init__(self):
        self.player = Player(0, 0)
        self.camera = LakituCamera(self.player)
        self.castle_verts, self.castle_faces = self.create_castle_geometry()
        
        # Reset camera to look good immediately
        self.camera.yaw = 0
        self.camera.x = 0
        self.camera.z = -500

    def create_castle_geometry(self):
        verts = []
        faces = []
        
        def add_prism(x, y, z, w, h, d, color):
            idx = len(verts)
            hw, hh, hd = w/2, h/2, d/2
            vs = [
                (x-hw, y-hh, z-hd), (x+hw, y-hh, z-hd),
                (x+hw, y+hh, z-hd), (x-hw, y+hh, z-hd),
                (x-hw, y-hh, z+hd), (x+hw, y-hh, z+hd),
                (x+hw, y+hh, z+hd), (x-hw, y+hh, z+hd)
            ]
            verts.extend(vs)
            fs = [
                ([0,1,2,3], color), ([5,4,7,6], color),
                ([4,0,3,7], color), ([1,5,6,2], color),
                ([3,2,6,7], color), ([4,5,1,0], color)
            ]
            for f_idxs, col in fs:
                faces.append(([i + idx for i in f_idxs], col))

        def add_pyramid(x, y, z, w, h, d, color):
            idx = len(verts)
            hw, hd = w/2, d/2
            vs = [
                (x-hw, y, z-hd), (x+hw, y, z-hd),
                (x+hw, y, z+hd), (x-hw, y, z+hd),
                (x, y+h, z)
            ]
            verts.extend(vs)
            fs = [
                ([0,1,4], color), ([1,2,4], color),
                ([2,3,4], color), ([3,0,4], color),
                ([3,2,1,0], color)
            ]
            for f_idxs, col in fs:
                faces.append(([i + idx for i in f_idxs], col))

        # Build Castle
        add_prism(0, 75, 200, 300, 150, 200, STONE_WHITE)
        add_prism(0, 175, 200, 100, 200, 100, STONE_WHITE)
        add_pyramid(0, 275, 200, 120, 100, 120, RED)
        add_prism(-150, 100, 200, 80, 200, 80, STONE_WHITE)
        add_pyramid(-150, 200, 200, 90, 100, 90, RED)
        add_prism(150, 100, 200, 80, 200, 80, STONE_WHITE)
        add_pyramid(150, 200, 200, 90, 100, 90, RED)
        add_prism(0, 10, 50, 100, 20, 150, (139, 69, 19)) # Bridge
        return verts, faces

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.camera.yaw)
        self.camera.update(keys)

    def draw(self, screen):
        screen.fill(SKY_BLUE)
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT//2, WIDTH, HEIGHT//2))

        all_faces = []
        
        # World Geometry
        for indices, color in self.castle_faces:
            points = []
            sum_z = 0
            valid = True
            for i in indices:
                vx, vy, vz = self.castle_verts[i]
                res = project_point(vx, vy, vz, self.camera.x, self.camera.y, self.camera.z, self.camera.yaw)
                if res is None: valid = False; break
                points.append((res[0], res[1]))
                sum_z += res[2]
            if valid:
                all_faces.append({'z': sum_z/len(indices), 'points': points, 'color': color, 'outline': DARK_STONE})

        # Player Geometry
        p_verts, p_faces = self.player.get_mesh()
        for indices, color in p_faces:
            points = []
            sum_z = 0
            valid = True
            for i in indices:
                vx, vy, vz = p_verts[i]
                res = project_point(vx, vy, vz, self.camera.x, self.camera.y, self.camera.z, self.camera.yaw)
                if res is None: valid = False; break
                points.append((res[0], res[1]))
                sum_z += res[2]
            if valid:
                all_faces.append({'z': sum_z/len(indices), 'points': points, 'color': color, 'outline': BLACK})

        all_faces.sort(key=lambda f: f['z'], reverse=True)

        for face in all_faces:
            pygame.draw.polygon(screen, face['color'], face['points'])
            pygame.draw.polygon(screen, face['outline'], face['points'], 1)

        # UI
        coords = f"Pos: {int(self.player.x)}, {int(self.player.y)}, {int(self.player.z)}"
        screen.blit(hud_font.render(coords, True, YELLOW), (10, 10))
        screen.blit(hud_font.render(f"Yaw: {int(math.degrees(self.camera.yaw)) % 360}", True, YELLOW), (10, 35))
        screen.blit(hud_font.render("ARROWS: Move | SPACE: Jump | Q/E: Rotate Cam", True, WHITE), (10, HEIGHT - 30))

# --- 2. MENU SCENE ---
class MenuScene:
    def __init__(self):
        self.timer = 0
        self.mario_y = 0
        self.camera_yaw = 0
        # Simple cube for menu
        self.cube_verts = [(-30, -30, -30), (30, -30, -30), (30, 30, -30), (-30, 30, -30),
                           (-30, -30, 30), (30, -30, 30), (30, 30, 30), (-30, 30, 30)]

    def update(self, dt):
        self.timer += dt
        self.camera_yaw += 0.02

    def draw(self, screen):
        screen.fill(NES_BLUE)
        
        # Draw bouncing title
        title_y = 100 + math.sin(self.timer * 0.005) * 10
        title_surf = title_font.render("ULTRA MARIO BROS", True, YELLOW)
        shadow_surf = title_font.render("ULTRA MARIO BROS", True, BLACK)
        
        t_rect = title_surf.get_rect(center=(WIDTH//2, title_y))
        s_rect = shadow_surf.get_rect(center=(WIDTH//2 + 4, title_y + 4))
        
        screen.blit(shadow_surf, s_rect)
        screen.blit(title_surf, t_rect)

        # Draw a spinning 3D cube (Mario Head placeholder) in center
        cube_faces = [
            ([0, 1, 2, 3], MARIO_RED), ([4, 5, 6, 7], MARIO_RED), # F/B
            ([0, 1, 5, 4], MARIO_BLUE), ([2, 3, 7, 6], MARIO_BLUE), # T/B
            ([1, 2, 6, 5], MARIO_RED), ([4, 7, 3, 0], MARIO_RED)  # L/R
        ]
        
        drawn_faces = []
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        for indices, color in cube_faces:
            points = []
            sum_z = 0
            
            for i in indices:
                vx, vy, vz = self.cube_verts[i]
                # Rotate Cube
                rx, rz = rotate_y(vx, vz, self.camera_yaw)
                # Project
                scale = 400 / (rz + 200) # Simple projection
                px = rx * scale + cx
                py = vy * scale + cy
                points.append((px, py))
                sum_z += rz
            
            # Simple backface culling
            if sum_z < 0: # Very rough approximation
                 drawn_faces.append((sum_z, points, color))

        drawn_faces.sort(key=lambda x: x[0], reverse=True)
        for _, pts, col in drawn_faces:
            pygame.draw.polygon(screen, col, pts)
            pygame.draw.polygon(screen, BLACK, pts, 2)

        # Flash text
        if int(self.timer / 500) % 2 == 0:
            msg = menu_font.render("PRESS SPACE TO START", True, WHITE)
            m_rect = msg.get_rect(center=(WIDTH//2, HEIGHT - 100))
            screen.blit(msg, m_rect)

# --- 3. LETTER SCENE ---
class LetterScene:
    def __init__(self):
        self.text_lines = [
            "Dear Mario,",
            "",
            "Please come to the",
            "castle. I've baked",
            "a cake for you.",
            "",
            "Yours truly,",
            "-- Princess Toadstool"
        ]
        self.alpha = 0
        self.fading_in = True
        self.timer = 0
        self.duration = 4000 # Minimum time to stay

    def update(self, dt):
        self.timer += dt
        if self.fading_in:
            self.alpha += 5
            if self.alpha >= 255:
                self.alpha = 255
                self.fading_in = False

    def draw(self, screen):
        screen.fill(BLACK)
        
        # Parchment background
        parchment_rect = pygame.Rect(0, 0, 400, 350)
        parchment_rect.center = SCREEN_CENTER
        
        pygame.draw.rect(screen, PARCHMENT, parchment_rect)
        pygame.draw.rect(screen, DARK_STONE, parchment_rect, 5) # Border

        # Text
        start_y = parchment_rect.top + 40
        for line in self.text_lines:
            txt = letter_font.render(line, True, INK_COLOR)
            rect = txt.get_rect(center=(WIDTH//2, start_y))
            screen.blit(txt, rect)
            start_y += 35
        
        # Fade effect overlay
        if self.alpha < 255:
            fade_s = pygame.Surface((WIDTH, HEIGHT))
            fade_s.set_alpha(255 - self.alpha)
            fade_s.fill(BLACK)
            screen.blit(fade_s, (0,0))
            
        # Continue prompt
        if self.timer > 2000:
             tiny_font = pygame.font.SysFont("Arial", 12)
             cont = tiny_font.render("Press SPACE to continue", True, WHITE)
             screen.blit(cont, (WIDTH - 150, HEIGHT - 30))

# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------
def main():
    state = STATE_MENU
    
    # Initialize Scenes
    menu_scene = MenuScene()
    letter_scene = LetterScene()
    game_scene = None # Init when needed to reset state

    running = True
    while running:
        dt = clock.tick(60)
        
        keys = pygame.key.get_pressed()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # Global Key Handlers for State Switching
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if state == STATE_MENU:
                        state = STATE_LETTER
                        letter_scene = LetterScene() # Reset letter animation
                    elif state == STATE_LETTER and letter_scene.timer > 500:
                        state = STATE_GAME
                        game_scene = GameScene() # Start fresh game
        
        # State Machine Logic
        if state == STATE_MENU:
            menu_scene.update(dt)
            menu_scene.draw(screen)
            
        elif state == STATE_LETTER:
            letter_scene.update(dt)
            letter_scene.draw(screen)
            
        elif state == STATE_GAME:
            if game_scene:
                # Basic escape to menu
                if keys[pygame.K_ESCAPE]:
                    state = STATE_MENU
                
                game_scene.update(dt)
                game_scene.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
