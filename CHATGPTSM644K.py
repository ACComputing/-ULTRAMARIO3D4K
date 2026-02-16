
import pygame
import sys
import math
import json
import os
import random
from copy import deepcopy

pygame.init()

# =====================================================
# CONFIG
# =====================================================
WIDTH, HEIGHT = 900, 600
FPS = 60

TITLE = "AC'S SM64 (menu + file select + lakitu intro)"

SAVE_FILE = "ac_sm64_saves.json"
SLOTS = 4
MAX_STARS = 120

# =====================================================
# COLORS
# =====================================================
SKY = (25, 25, 80)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 30, 30)
BLUE = (40, 90, 255)
YELLOW = (255, 220, 0)
GREEN = (40, 220, 120)

PARCHMENT = (245, 235, 205)
PARCHMENT_BORDER = (190, 150, 100)
INK = (70, 40, 25)
DARK_INK = (40, 22, 10)

# =====================================================
# INIT DISPLAY
# =====================================================
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# =====================================================
# HELPERS
# =====================================================
def clamp(x, a, b):
    return a if x < a else b if x > b else x

def lerp(a, b, t):
    return a + (b - a) * t

def smoothstep(t):
    # 0..1 -> eased 0..1
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)

def draw_text(surf, text, font, color, center=None, topleft=None):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center is not None:
        rect.center = center
    if topleft is not None:
        rect.topleft = topleft
    surf.blit(img, rect)
    return rect

def overlay_fade(alpha):
    if alpha <= 0:
        return
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((0, 0, 0, int(alpha)))
    screen.blit(veil, (0, 0))

# =====================================================
# SAVE DATA
# =====================================================
def default_saves():
    return [
        {"exists": False, "stars": 0, "name": f"MARIO {chr(ord('A') + i)}"}
        for i in range(SLOTS)
    ]

def load_saves():
    data = default_saves()
    if not os.path.exists(SAVE_FILE):
        return data
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            return data
        # normalize
        for i in range(min(SLOTS, len(raw))):
            slot = raw[i] if isinstance(raw[i], dict) else {}
            data[i]["exists"] = bool(slot.get("exists", False))
            data[i]["stars"] = int(slot.get("stars", 0))
            data[i]["stars"] = clamp(data[i]["stars"], 0, MAX_STARS)
            name = slot.get("name", data[i]["name"])
            data[i]["name"] = str(name)[:24]
    except Exception:
        return data
    return data

def save_saves(slots):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(slots, f, indent=2)
    except Exception:
        # If saving fails, we keep playing anyway.
        pass

# =====================================================
# SIMPLE 3D (PERSPECTIVE PROJECTION)
# =====================================================
FOV = 550  # bigger = less zoom

def project_point(p):
    """p: (x,y,z) with z>0 in front of camera. Returns (sx,sy,scale,z) or None."""
    x, y, z = p
    if z <= 1:
        return None
    scale = FOV / z
    sx = int(WIDTH / 2 + x * scale)
    sy = int(HEIGHT / 2 - y * scale)
    return sx, sy, scale, z

def rot_y(p, a):
    x, y, z = p
    ca = math.cos(a)
    sa = math.sin(a)
    return (x * ca + z * sa, y, -x * sa + z * ca)

def rot_x(p, a):
    x, y, z = p
    ca = math.cos(a)
    sa = math.sin(a)
    return (x, y * ca - z * sa, y * sa + z * ca)

def make_wire_sphere(radius=220, lat_steps=7, lon_steps=14):
    """Return list of line segments in object space."""
    segs = []
    # latitude rings
    for i in range(1, lat_steps):
        lat = lerp(-math.pi/2, math.pi/2, i / lat_steps)
        ring = []
        for j in range(lon_steps + 1):
            lon = lerp(0, math.tau, j / lon_steps)
            x = radius * math.cos(lat) * math.cos(lon)
            y = radius * math.sin(lat)
            z = radius * math.cos(lat) * math.sin(lon)
            ring.append((x, y, z))
        for j in range(lon_steps):
            segs.append((ring[j], ring[j + 1]))
    # meridians
    for j in range(lon_steps):
        lon = lerp(0, math.tau, j / lon_steps)
        mer = []
        for i in range(lat_steps + 1):
            lat = lerp(-math.pi/2, math.pi/2, i / lat_steps)
            x = radius * math.cos(lat) * math.cos(lon)
            y = radius * math.sin(lat)
            z = radius * math.cos(lat) * math.sin(lon)
            mer.append((x, y, z))
        for i in range(lat_steps):
            segs.append((mer[i], mer[i + 1]))
    return segs

SPHERE_SEGS = make_wire_sphere()

def draw_wire_sphere(center=(0, 0, 1100), rot=(0.0, 0.0), color=(180, 210, 255)):
    cy, cx = rot  # a tiny fun: (yaw, pitch)
    base = center
    # draw farther lines first
    proj_lines = []
    for a, b in SPHERE_SEGS:
        pa = rot_x(rot_y(a, cy), cx)
        pb = rot_x(rot_y(b, cy), cx)
        wa = (pa[0] + base[0], pa[1] + base[1], pa[2] + base[2])
        wb = (pb[0] + base[0], pb[1] + base[1], pb[2] + base[2])
        ra = project_point(wa)
        rb = project_point(wb)
        if ra is None or rb is None:
            continue
        ax, ay, _, az = ra
        bx, by, _, bz = rb
        zavg = (az + bz) * 0.5
        proj_lines.append((zavg, (ax, ay, bx, by)))
    proj_lines.sort(reverse=True)  # far to near
    for zavg, (ax, ay, bx, by) in proj_lines:
        # slight depth shading
        shade = clamp(int(255 - (zavg - 850) * 0.08), 90, 255)
        c = (clamp(int(color[0] * shade / 255), 0, 255),
             clamp(int(color[1] * shade / 255), 0, 255),
             clamp(int(color[2] * shade / 255), 0, 255))
        pygame.draw.aaline(screen, c, (ax, ay), (bx, by))

def draw_starfield(stars):
    # stars: list of [x,y,z]
    for x, y, z in stars:
        res = project_point((x, y, z))
        if res is None:
            continue
        sx, sy, scale, zz = res
        if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
            r = max(1, int(2 * scale))
            b = clamp(int(255 - (zz - 300) * 0.09), 90, 255)
            pygame.draw.circle(screen, (b, b, b), (sx, sy), r)

def draw_viewfinder(alpha=200):
    # simple viewfinder corners like SM64 camera
    a = clamp(int(alpha), 0, 255)
    if a <= 0:
        return
    vf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    col = (255, 255, 255, a)
    pad = 30
    L = 35
    # top-left
    pygame.draw.line(vf, col, (pad, pad), (pad + L, pad), 2)
    pygame.draw.line(vf, col, (pad, pad), (pad, pad + L), 2)
    # top-right
    pygame.draw.line(vf, col, (WIDTH - pad, pad), (WIDTH - pad - L, pad), 2)
    pygame.draw.line(vf, col, (WIDTH - pad, pad), (WIDTH - pad, pad + L), 2)
    # bottom-left
    pygame.draw.line(vf, col, (pad, HEIGHT - pad), (pad + L, HEIGHT - pad), 2)
    pygame.draw.line(vf, col, (pad, HEIGHT - pad), (pad, HEIGHT - pad - L), 2)
    # bottom-right
    pygame.draw.line(vf, col, (WIDTH - pad, HEIGHT - pad), (WIDTH - pad - L, HEIGHT - pad), 2)
    pygame.draw.line(vf, col, (WIDTH - pad, HEIGHT - pad), (WIDTH - pad, HEIGHT - pad - L), 2)
    # center dot
    pygame.draw.circle(vf, (255, 255, 255, a), (WIDTH // 2, HEIGHT // 2), 3)
    screen.blit(vf, (0, 0))

def draw_lakitu_2d(screen_x, screen_y, scale, bob=0.0):
    # 2D Lakitu-ish drawing, scaled by perspective.
    s = max(0.15, min(2.0, scale))
    cx = int(screen_x)
    cy = int(screen_y + math.sin(bob) * 6 * s)

    # cloud
    cloud_r = max(4, int(20 * s))
    offsets = [(-1.0, 0.3), (-0.3, -0.2), (0.4, -0.3), (1.1, 0.2), (0.2, 0.6)]
    for ox, oy in offsets:
        pygame.draw.circle(screen, WHITE, (int(cx + ox * cloud_r), int(cy + oy * cloud_r)), cloud_r)

    # body
    body_r = max(3, int(10 * s))
    pygame.draw.circle(screen, (240, 200, 80), (cx, int(cy - 1.0 * cloud_r)), body_r)

    # goggles
    g_r = max(2, int(5 * s))
    pygame.draw.circle(screen, (60, 60, 70), (int(cx - 6 * s), int(cy - 1.0 * cloud_r)), g_r, 2)
    pygame.draw.circle(screen, (60, 60, 70), (int(cx + 6 * s), int(cy - 1.0 * cloud_r)), g_r, 2)
    pygame.draw.line(screen, (60, 60, 70),
                     (int(cx - 1 * s), int(cy - 1.0 * cloud_r)),
                     (int(cx + 1 * s), int(cy - 1.0 * cloud_r)), max(1, int(2 * s)))

    # camera
    cam_w = max(8, int(28 * s))
    cam_h = max(6, int(18 * s))
    cam = pygame.Rect(0, 0, cam_w, cam_h)
    cam.center = (int(cx + 28 * s), int(cy - 1.2 * cloud_r))
    pygame.draw.rect(screen, (30, 30, 40), cam, border_radius=max(2, int(4 * s)))
    lens_r = max(3, int(7 * s))
    pygame.draw.circle(screen, (80, 120, 255), cam.center, lens_r)
    pygame.draw.circle(screen, (15, 15, 20), cam.center, lens_r, max(1, int(2 * s)))

# =====================================================
# SCREENS
# =====================================================
def title_screen():
    title_font = pygame.font.SysFont("Arial", 72, bold=True)
    sub_font = pygame.font.SysFont("Arial", 40, bold=True)
    press_font = pygame.font.SysFont("Arial", 34, bold=True)
    small_font = pygame.font.SysFont("Arial", 18)

    fade = 255
    exiting = False
    pulse = 0.0

    while True:
        dt = clock.tick(FPS)
        pulse += dt / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE,):
                    return "quit"
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if fade <= 0 and not exiting:
                        exiting = True

        # animate fade
        if not exiting:
            fade = max(0, fade - dt * 0.8)
        else:
            fade = min(255, fade + dt * 1.2)
            if fade >= 255:
                return "lakitu"

        # draw
        screen.fill(SKY)

        # Subtle background stars
        random.seed(1)
        for i in range(60):
            x = (i * 37) % WIDTH
            y = (i * 91) % HEIGHT
            pygame.draw.circle(screen, (90, 90, 120), (x, y), 1)

        # Title
        draw_text(screen, "AC'S SM64", title_font, RED, center=(WIDTH // 2, 190))
        draw_text(screen, "SUPER MARIO 64", sub_font, BLUE, center=(WIDTH // 2, 265))

        # Pulsing PRESS START
        glow = 180 + int(70 * math.sin(pulse * 4))
        press_color = (glow, glow, 255)
        draw_text(screen, "PRESS START", press_font, press_color, center=(WIDTH // 2, 410))
        draw_text(screen, "ENTER / SPACE", small_font, WHITE, center=(WIDTH // 2, 470))

        overlay_fade(fade)
        pygame.display.flip()

def lakitu_intro():
    big_font = pygame.font.SysFont("Arial", 56, bold=True)
    small_font = pygame.font.SysFont("Arial", 18)

    # starfield points in 3D space
    stars = []
    for _ in range(180):
        stars.append([random.uniform(-1200, 1200),
                      random.uniform(-800, 800),
                      random.uniform(350, 3300)])

    fade = 255
    exiting = False
    t = 0.0
    intro_ms = 3200  # main animation length
    hold_ms = 250

    while True:
        dt = clock.tick(FPS)
        t += dt

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE,):
                    # skip straight to file select
                    exiting = True
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # skip faster
                    exiting = True

        # update stars (move toward camera)
        speed = dt * 0.55
        for s in stars:
            s[2] -= speed
            if s[2] < 320:
                s[0] = random.uniform(-1200, 1200)
                s[1] = random.uniform(-800, 800)
                s[2] = random.uniform(2500, 3600)

        # timing and fade
        if not exiting:
            fade = max(0, fade - dt * 1.1)
            if t >= intro_ms + hold_ms:
                exiting = True
        else:
            fade = min(255, fade + dt * 1.4)
            if fade >= 255:
                return "file_select"

        # progress
        u = smoothstep(min(1.0, t / intro_ms))

        # 3D scene: wire sphere rotates a bit (Mario head placeholder)
        yaw = u * math.tau * 0.35
        pitch = math.sin(u * math.tau) * 0.15

        screen.fill((10, 10, 25))
        draw_starfield(stars)
        draw_wire_sphere(center=(0, -20, 1180), rot=(yaw, pitch), color=(160, 190, 255))

        # Lakitu flies in (3D-ish)
        start = (-760, 260, 2700)
        end = (0, 90, 860)

        # spiral that calms down as he gets close
        spiral = 360 * (1 - u)
        lx = lerp(start[0], end[0], u) + math.sin(u * math.tau * 2.2) * spiral
        ly = lerp(start[1], end[1], u) + math.cos(u * math.tau * 1.7) * spiral * 0.35
        lz = lerp(start[2], end[2], u)

        res = project_point((lx, ly, lz))
        if res is not None:
            sx, sy, sc, _ = res
            draw_lakitu_2d(sx, sy, sc, bob=u * math.tau * 2.0)

        # logo text
        logo_alpha = 220 if u > 0.2 else int(220 * (u / 0.2))
        logo_col = (255, 255, 255)
        draw_text(screen, "SUPER MARIO 64", big_font, logo_col, center=(WIDTH // 2, 110))
        draw_text(screen, "LAKITU CAM (3D-ish)", small_font, (180, 180, 200), center=(WIDTH // 2, 155))

        # viewfinder overlay fades in during intro
        vf_alpha = clamp(int(220 * u), 0, 220)
        draw_viewfinder(vf_alpha)

        overlay_fade(fade)
        pygame.display.flip()

def file_select_screen(slots):
    title_font = pygame.font.SysFont("Arial", 54, bold=True)
    slot_font = pygame.font.SysFont("Arial", 28, bold=True)
    small_font = pygame.font.SysFont("Arial", 18)
    tiny_font = pygame.font.SysFont("Arial", 14)

    fade = 255
    exiting = False
    next_state = None
    selected = 0

    mode = "SELECT"  # SELECT, COPY_SRC, COPY_DST, ERASE_CONFIRM
    copy_src = None

    # geometry
    slot_w, slot_h = 360, 150
    gap_x, gap_y = 40, 28
    grid_w = slot_w * 2 + gap_x
    left = (WIDTH - grid_w) // 2
    top = 170

    slot_rects = []
    for i in range(SLOTS):
        row = i // 2
        col = i % 2
        r = pygame.Rect(left + col * (slot_w + gap_x),
                        top + row * (slot_h + gap_y),
                        slot_w, slot_h)
        slot_rects.append(r)

    def move_sel(dx, dy):
        nonlocal selected
        row = selected // 2
        col = selected % 2
        row = clamp(row + dy, 0, 1)
        col = clamp(col + dx, 0, 1)
        selected = row * 2 + col

    while True:
        dt = clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit", None
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    if mode != "SELECT":
                        mode = "SELECT"
                        copy_src = None
                    else:
                        exiting = True
                        next_state = ("title", None)

                if e.key in (pygame.K_LEFT, pygame.K_a):
                    move_sel(-1, 0)
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    move_sel(1, 0)
                if e.key in (pygame.K_UP, pygame.K_w):
                    move_sel(0, -1)
                if e.key in (pygame.K_DOWN, pygame.K_s):
                    move_sel(0, 1)

                if mode == "SELECT":
                    if e.key == pygame.K_c:
                        mode = "COPY_SRC"
                        copy_src = None
                    if e.key == pygame.K_e:
                        if slots[selected]["exists"]:
                            mode = "ERASE_CONFIRM"
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # create file if needed
                        if not slots[selected]["exists"]:
                            slots[selected]["exists"] = True
                            slots[selected]["stars"] = 0
                            save_saves(slots)
                        exiting = True
                        next_state = ("letter", selected)

                elif mode == "COPY_SRC":
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if slots[selected]["exists"]:
                            copy_src = selected
                            mode = "COPY_DST"
                    if e.key == pygame.K_c:
                        mode = "SELECT"
                        copy_src = None

                elif mode == "COPY_DST":
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if copy_src is not None and selected != copy_src:
                            slots[selected] = deepcopy(slots[copy_src])
                            save_saves(slots)
                        mode = "SELECT"
                        copy_src = None
                    if e.key == pygame.K_c:
                        mode = "SELECT"
                        copy_src = None

                elif mode == "ERASE_CONFIRM":
                    if e.key in (pygame.K_y, pygame.K_RETURN):
                        slots[selected]["exists"] = False
                        slots[selected]["stars"] = 0
                        save_saves(slots)
                        mode = "SELECT"
                    if e.key in (pygame.K_n, pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        mode = "SELECT"

        # fade handling
        if not exiting:
            fade = max(0, fade - dt * 0.9)
        else:
            fade = min(255, fade + dt * 1.3)
            if fade >= 255:
                return next_state if next_state else ("title", None)

        # draw background
        screen.fill(SKY)
        # panel
        panel = pygame.Surface((WIDTH - 120, HEIGHT - 120), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 60))
        screen.blit(panel, (60, 60))

        draw_text(screen, "SELECT FILE", title_font, WHITE, center=(WIDTH // 2, 100))

        # draw slots
        for i, r in enumerate(slot_rects):
            # slot body
            pygame.draw.rect(screen, PARCHMENT, r, border_radius=14)
            pygame.draw.rect(screen, PARCHMENT_BORDER, r, 4, border_radius=14)

            # highlight
            if i == selected:
                pygame.draw.rect(screen, YELLOW, r.inflate(10, 10), 6, border_radius=16)

            slot = slots[i]
            name = slot.get("name", f"FILE {i + 1}")
            header = f"FILE {i + 1}  —  {name}"
            draw_text(screen, header, tiny_font, INK, topleft=(r.x + 16, r.y + 14))

            if slot["exists"]:
                stars = slot.get("stars", 0)
                draw_text(screen, f"{stars:02d} ★", slot_font, DARK_INK, topleft=(r.x + 24, r.y + 52))
                status = "OK"
                col = GREEN
            else:
                draw_text(screen, "NEW", slot_font, (90, 60, 40), topleft=(r.x + 24, r.y + 52))
                status = "EMPTY"
                col = (140, 110, 80)

            draw_text(screen, status, small_font, col, topleft=(r.x + 24, r.y + 112))

        # bottom help text
        help_y = HEIGHT - 58
        if mode == "SELECT":
            msg = "ARROWS/WASD: Move   ENTER/SPACE: Select   C: Copy   E: Erase   ESC: Back"
        elif mode == "COPY_SRC":
            msg = "COPY: Pick a SOURCE file (must exist). ENTER to choose. C / ESC: Cancel"
        elif mode == "COPY_DST":
            msg = "COPY: Pick a DESTINATION file. ENTER to copy. C / ESC: Cancel"
        else:
            msg = "ERASE FILE?  Y = yes   N/ESC = no"
        draw_text(screen, msg, small_font, WHITE, center=(WIDTH // 2, help_y))

        overlay_fade(fade)
        pygame.display.flip()

def dear_mario_screen(slot_idx, slots):
    title_font = pygame.font.SysFont("Times New Roman", 38, bold=True)
    body_font = pygame.font.SysFont("Times New Roman", 26)
    small_font = pygame.font.SysFont("Arial", 18)

    lines = [
        "Dear Mario,",
        "",
        "Please come to the castle.",
        "I've baked a cake for you.",
        "",
        "Yours truly,",
        "Princess Toadstool"
    ]

    fade = 255
    exiting = False
    next_state = None

    while True:
        dt = clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit", None
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    exiting = True
                    next_state = ("file_select", None)
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    exiting = True
                    next_state = ("game", slot_idx)

        if not exiting:
            fade = max(0, fade - dt * 0.9)
        else:
            fade = min(255, fade + dt * 1.3)
            if fade >= 255:
                return next_state if next_state else ("game", slot_idx)

        screen.fill(SKY)

        # Card
        card = pygame.Surface((620, 410), pygame.SRCALPHA)
        card.fill(PARCHMENT)
        pygame.draw.rect(card, PARCHMENT_BORDER, card.get_rect(), 6)

        y = 60
        for i, line in enumerate(lines):
            if i == 0:
                text = title_font.render(line, True, INK)
                card.blit(text, (60, y))
                y += 60
            else:
                text = body_font.render(line, True, INK)
                card.blit(text, (60, y))
                y += 35

        # slot label
        if slot_idx is not None and 0 <= slot_idx < len(slots):
            slot = slots[slot_idx]
            label = f"FILE {slot_idx + 1} — {slot.get('name', '')}   ({slot.get('stars', 0)} ★)"
            tag = small_font.render(label, True, INK)
            card.blit(tag, (60, 20))

        hint = small_font.render("PRESS START TO CONTINUE  (ESC: back)", True, INK)
        card.blit(hint, (140, 360))

        screen.blit(card, card.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        overlay_fade(fade)
        pygame.display.flip()

def game_placeholder(slot_idx, slots):
    big = pygame.font.SysFont("Arial", 50, bold=True)
    small = pygame.font.SysFont("Arial", 18)

    fade = 255
    exiting = False
    next_state = None

    while True:
        dt = clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit", None
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    exiting = True
                    next_state = ("file_select", None)

                # tiny test: add a star to verify saving works
                if e.key == pygame.K_s and slot_idx is not None:
                    slots[slot_idx]["stars"] = clamp(slots[slot_idx]["stars"] + 1, 0, MAX_STARS)
                    save_saves(slots)

        if not exiting:
            fade = max(0, fade - dt * 1.2)
        else:
            fade = min(255, fade + dt * 1.4)
            if fade >= 255:
                return next_state if next_state else ("file_select", None)

        screen.fill((0, 0, 0))
        draw_text(screen, "GAME START!", big, WHITE, center=(WIDTH // 2, HEIGHT // 2 - 60))
        draw_text(screen, "(placeholder)", small, (180, 180, 180), center=(WIDTH // 2, HEIGHT // 2 - 20))

        if slot_idx is not None:
            stars = slots[slot_idx].get("stars", 0)
            draw_text(screen, f"FILE {slot_idx + 1} — {stars} ★", small, (200, 200, 255),
                      center=(WIDTH // 2, HEIGHT // 2 + 30))

        draw_text(screen, "Press S to add a star (test save).  ESC to go back.", small, (200, 200, 200),
                  center=(WIDTH // 2, HEIGHT - 40))

        overlay_fade(fade)
        pygame.display.flip()

# =====================================================
# MAIN LOOP
# =====================================================
def main():
    slots = load_saves()

    state = "title"
    selected_slot = None

    while True:
        if state == "title":
            nxt = title_screen()
            if nxt == "quit":
                break
            state = nxt

        elif state == "lakitu":
            nxt = lakitu_intro()
            if nxt == "quit":
                break
            state = nxt

        elif state == "file_select":
            nxt, payload = file_select_screen(slots)
            if nxt == "quit":
                break
            state = nxt
            selected_slot = payload

        elif state == "letter":
            nxt, payload = dear_mario_screen(selected_slot, slots)
            if nxt == "quit":
                break
            state = nxt
            # payload might be slot idx
            if payload is not None:
                selected_slot = payload

        elif state == "game":
            nxt, payload = game_placeholder(selected_slot, slots)
            if nxt == "quit":
                break
            state = nxt

        else:
            state = "title"

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
