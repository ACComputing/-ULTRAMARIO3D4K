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
pygame.display.set_caption("Ultra Mario Bros: Castle Edition")
clock = pygame.time.Clock()

# Colors
SKY_BLUE = (135, 206, 235)
NES_BLUE = (92, 148, 252)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 216, 0)
GRAY = (200, 200, 200)
STONE_WHITE = (240, 240, 240)
ROOF_RED = (220, 40, 40)
GRASS_GREEN = (34, 177, 76)
WATER_BLUE = (0, 162, 232)

# Fonts
try:
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    menu_font = pygame.font.SysFont("Arial", 36)
    nes_font = pygame.font.SysFont("Courier New", 28, bold=True)
except:
    title_font = pygame.font.Font(None, 60)
    menu_font = pygame.font.Font(None, 36)
    nes_font = pygame.font.Font(None, 28)

# -------------------------------------------------
# ENGINE CORE
# -------------------------------------------------
class Scene:
    def handle_event(self, event):
        pass
    def update(self, dt):
        pass
    def draw(self, screen):
        pass

class SceneManager:
    def __init__(self):
        self.current_scene = None

    def switch_to(self, scene):
        self.current_scene = scene

manager = SceneManager()

# -------------------------------------------------
# SCENE 1: MAIN MENU
# -------------------------------------------------
class MainMenu(Scene):
    def __init__(self):
        self.options = ["Start Game", "Exit"]
        self.selected_index = 0
        self.blink_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected_index == 0:
                    manager.switch_to(DearMarioScene())
                else:
                    pygame.quit()
                    sys.exit()

    def update(self, dt):
        self.blink_timer += dt
        if self.blink_timer > 1000:
            self.blink_timer = 0

    def draw(self, screen):
        screen.fill(NES_BLUE)
        
        # Title Shadow
        title_surf = title_font.render("ULTRA MARIO 64", True, BLACK)
        title_rect = title_surf.get_rect(center=(WIDTH//2 + 4, 154))
        screen.blit(title_surf, title_rect)
        
        # Title Main
        title_surf = title_font.render("ULTRA MARIO 64", True, YELLOW)
        title_rect = title_surf.get_rect(center=(WIDTH//2, 150))
        screen.blit(title_surf, title_rect)

        # Options
        for i, option in enumerate(self.options):
            color = WHITE
            prefix = ""
            if i == self.selected_index:
                color = YELLOW
                prefix = "> "
            
            text_surf = menu_font.render(prefix + option, True, color)
            text_rect = text_surf.get_rect(center=(WIDTH//2, 350 + i * 50))
            screen.blit(text_surf, text_rect)

        # Copyright
        copy_surf = nes_font.render("© 1996-2024 NINTENDO", True, WHITE)
        screen.blit(copy_surf, copy_surf.get_rect(center=(WIDTH//2, HEIGHT - 50)))

# -------------------------------------------------
# SCENE 2: DEAR MARIO (The Letter)
# -------------------------------------------------
class DearMarioScene(Scene):
    def __init__(self):
        self.lines = [
            "DEAR MARIO:",
            "",
            "PLEASE COME TO THE CASTLE.",
            "I'VE BAKED A CAKE FOR YOU.",
            "",
            "YOURS TRULY--",
            "PRINCESS TOADSTOOL",
            "",
            "Peach"
        ]
        self.voice_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                manager.switch_to(CastleScene())

    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw background paper/border
        border_rect = pygame.Rect(50, 50, WIDTH-100, HEIGHT-100)
        pygame.draw.rect(screen, (255, 240, 200), border_rect)
        pygame.draw.rect(screen, (200, 100, 100), border_rect, 5)

        # Render Text
        start_y = 120
        for i, line in enumerate(self.lines):
            color = (50, 50, 50)
            if "Peach" in line:
                color = (200, 0, 0) # Signature in red
            
            text_surf = nes_font.render(line, True, color)
            screen.blit(text_surf, (100, start_y + i * 40))

        # Prompt
        prompt_surf = menu_font.render("PRESS SPACE TO CONTINUE", True, NES_BLUE)
        blink = (pygame.time.get_ticks() // 500) % 2 == 0
        if blink:
            screen.blit(prompt_surf, prompt_surf.get_rect(center=(WIDTH//2, HEIGHT - 80)))

# -------------------------------------------------
# SCENE 3: PEACH'S CASTLE (3D Renderer)
# -------------------------------------------------
class CastleScene(Scene):
    def __init__(self):
        self.angle = 0.0
        self.vertices, self.faces = self.create_castle_model()
        self.fov = 600
        self.camera_dist = 800

    def create_castle_model(self):
        verts = []
        faces = []
        
        # Helper to add a box
        # cx, cy, cz: center position
        # w, h, d: dimensions
        # color: (r,g,b)
        def add_box(cx, cy, cz, w, h, d, color):
            hw, hh, hd = w/2, h/2, d/2
            # 8 corners
            v_start = len(verts)
            corners = [
                (cx-hw, cy-hh, cz-hd), (cx+hw, cy-hh, cz-hd),
                (cx+hw, cy+hh, cz-hd), (cx-hw, cy+hh, cz-hd),
                (cx-hw, cy-hh, cz+hd), (cx+hw, cy-hh, cz+hd),
                (cx+hw, cy+hh, cz+hd), (cx-hw, cy+hh, cz+hd)
            ]
            verts.extend(corners)
            
            # 6 faces (indices)
            # format: [indices], color
            new_faces = [
                ([0,1,2,3], color), # Front
                ([5,4,7,6], color), # Back
                ([4,0,3,7], color), # Left
                ([1,5,6,2], color), # Right
                ([3,2,6,7], color), # Top
                ([4,5,1,0], color)  # Bottom
            ]
            # Offset indices by current vertex count
            for f_verts, f_col in new_faces:
                offset_verts = [x + v_start for x in f_verts]
                faces.append((offset_verts, f_col))

        # Helper to add a pyramid (roof)
        def add_pyramid(cx, cy, cz, w, h, d, color):
            hw, hd = w/2, d/2
            v_start = len(verts)
            # Base corners + Apex
            corners = [
                (cx-hw, cy, cz-hd), (cx+hw, cy, cz-hd),
                (cx+hw, cy, cz+hd), (cx-hw, cy, cz+hd),
                (cx, cy-h, cz) # Apex (Note: Y is inverted in Pygame screen coords roughly, but we handle it in project)
            ]
            verts.extend(corners)
            
            new_faces = [
                ([0,1,4], color), # Front tri
                ([1,2,4], color), # Right tri
                ([2,3,4], color), # Back tri
                ([3,0,4], color), # Left tri
                ([3,2,1,0], color) # Base
            ]
            for f_verts, f_col in new_faces:
                offset_verts = [x + v_start for x in f_verts]
                faces.append((offset_verts, f_col))

        # --- BUILD CASTLE GEOMETRY ---
        
        # Main Base (White Stone)
        add_box(0, 100, 0, 300, 150, 300, STONE_WHITE)
        
        # Central Tower
        add_box(0, -50, 0, 120, 200, 120, STONE_WHITE)
        
        # Central Roof (Red)
        add_pyramid(0, -150, 0, 140, 120, 140, ROOF_RED)
        
        # Side Tower Left
        add_box(-150, 50, 0, 80, 200, 80, STONE_WHITE)
        add_pyramid(-150, -50, 0, 90, 80, 90, ROOF_RED)

        # Side Tower Right
        add_box(150, 50, 0, 80, 200, 80, STONE_WHITE)
        add_pyramid(150, -50, 0, 90, 80, 90, ROOF_RED)

        # Bridge
        add_box(0, 175, 200, 100, 10, 150, (139, 69, 19))
        
        # Door window (Stained Glass)
        add_box(0, -80, -61, 40, 60, 5, SKY_BLUE)

        return verts, faces

    def update(self, dt):
        # Rotate the castle automatically
        self.angle += 0.01

    def project(self, x, y, z):
        # 1. Rotate around Y axis
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        
        rx = x * cos_a - z * sin_a
        rz = x * sin_a + z * cos_a
        ry = y
        
        # 2. Translate camera (Push object away into screen)
        rz += self.camera_dist
        
        # 3. Project to 2D
        if rz <= 1: # Clip if behind camera
            return None
            
        f = self.fov / rz
        px = rx * f + SCREEN_CENTER[0]
        py = ry * f + SCREEN_CENTER[1]
        
        return (px, py, rz) # Return rz for Z-sorting

    def draw(self, screen):
        screen.fill(SKY_BLUE)
        
        # Draw Grass Horizon
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT//2 + 50, WIDTH, HEIGHT//2))
        
        # Project all vertices
        projected_verts = []
        for v in self.vertices:
            p = self.project(v[0], v[1], v[2])
            projected_verts.append(p)
            
        # Prepare faces to draw
        faces_to_draw = []
        for indices, color in self.faces:
            # Get projected points for this face
            points = []
            avg_z = 0
            valid = True
            
            for idx in indices:
                p = projected_verts[idx]
                if p is None:
                    valid = False
                    break
                points.append((p[0], p[1]))
                avg_z += p[2]
            
            if valid:
                avg_z /= len(indices)
                faces_to_draw.append((avg_z, points, color))
        
        # Sort by depth (Painter's Algorithm) - furthest first
        faces_to_draw.sort(key=lambda x: x[0], reverse=True)
        
        # Draw polygons
        for _, points, color in faces_to_draw:
            # Simple lighting effect based on color brightness
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, BLACK, points, 1) # Wireframe outline

        # UI Text
        info = nes_font.render("WELCOME TO PEACH'S CASTLE", True, YELLOW)
        screen.blit(info, info.get_rect(center=(WIDTH//2, 50)))

# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------
def main():
    manager.switch_to(MainMenu())
    
    running = True
    while running:
        dt = clock.tick(60) # 60 FPS
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if manager.current_scene:
                manager.current_scene.handle_event(event)
        
        if manager.current_scene:
            manager.current_scene.update(dt)
            manager.current_scene.draw(screen)
            
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
