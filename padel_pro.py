#!/usr/bin/env python3
# Pixel-perfect Padel Scoreboard UI – updates: ALMUS brand, smaller red score, black background

import pygame
import sys
from datetime import datetime

WIDTH, HEIGHT = 1024, 1024
FPS = 60

WHITE = (255, 255, 255)
NEAR_WHITE = (245, 245, 245)
BLACK = (0, 0, 0)
PANEL_BLACK = (25, 25, 25)
GOLD_TOP = (232, 194, 94)
GOLD_BOTTOM = (200, 160, 55)
GOLD_PANEL = (210, 170, 55)
RED = (230, 40, 40)

def round_rect(surface, rect, color, radius=24, width=0):
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)

def draw_shadow(surface, rect, radius=32, spread=18, alpha=90):
    sw = pygame.Surface((rect.width + spread*2, rect.height + spread*2), pygame.SRCALPHA)
    for i in range(spread, 0, -1):
        a = int(alpha * (i / spread))
        pygame.draw.rect(
            sw, (0, 0, 0, a),
            pygame.Rect(i, i, sw.get_width() - i*2, sw.get_height() - i*2),
            border_radius=radius + int(i*0.7)
        )
    surface.blit(sw, (rect.x - spread, rect.y - spread))

def draw_vertical_gradient(surface, rect, top_color, bottom_color, radius=24):
    grad = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        pygame.draw.line(grad, (r, g, b), (0, y), (rect.width, y))
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    round_rect(mask, mask.get_rect(), (255, 255, 255, 255), radius=radius)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(grad, rect.topleft)

class Tennis:
    MAP = {0: "0", 1: "15", 2: "30", 3: "40"}
    def __init__(self): self.reset()
    def reset(self):
        self.bp = self.yp = 0
        self.deuce = False; self.adv = None
        self.bg = self.yg = 0
        self.bs = self.ys = 0
        self.winner = None
    def add(self, side):
        if self.winner: return
        if self.deuce:
            if self.adv is None: self.adv = side; return
            if self.adv == side: self.wingame(side)
            else: self.adv = None
            return
        if side == "black": self.bp += 1
        else: self.yp += 1
        if self.bp >= 3 and self.yp >= 3 and abs(self.bp - self.yp) == 0:
            self.deuce = True; self.adv = None; return
        if self.bp >= 4 and self.bp - self.yp >= 2: self.wingame("black")
        if self.yp >= 4 and self.yp - self.bp >= 2: self.wingame("yellow")
    def wingame(self, side):
        self.bp = self.yp = 0; self.deuce = False; self.adv = None
        if side == "black": self.bg += 1
        else: self.yg += 1
        self.winset_if_needed()
    def winset_if_needed(self):
        b, y = self.bg, self.yg
        if (b >= 6 and b - y >= 2) or b == 7:
            self.bs += 1; self.bg = self.yg = 0
        if (y >= 6 and y - b >= 2) or y == 7:
            self.ys += 1; self.bg = self.yg = 0
        if self.bs >= 2: self.winner = "black"
        if self.ys >= 2: self.winner = "yellow"
    def disp(self, side):
        if self.deuce: return "AD" if self.adv == side else "40"
        return self.MAP.get(self.bp if side == "black" else self.yp, "40")

class Scoreboard:
    def __init__(self, size=(WIDTH, HEIGHT)):
        pygame.init()
        pygame.display.set_caption("Padel Scoreboard - Pixel Perfect")
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.score = Tennis()
        self.f = {}

    def scale_fonts(self, w, h):
        self.f["brand"] = pygame.font.SysFont("Arial Black", int(h * 0.045))
        self.f["time"]  = pygame.font.SysFont("Arial Black", int(h * 0.07))
        self.f["pill"]  = pygame.font.SysFont("Arial Black", int(h * 0.04))
        self.f["panel"] = pygame.font.SysFont("Arial Black", int(h * 0.048))
        self.f["big"]   = pygame.font.SysFont("Arial Black", int(h * 0.30))
        self.f["vs"]    = pygame.font.SysFont("Arial Black", int(h * 0.08))
        # Smaller bottom red number (changed from 0.06 to 0.05)
        self.f["caps"]  = pygame.font.SysFont("Arial Black", int(h * 0.05))  # smaller

    def draw(self):
        w, h = self.screen.get_size()
        self.scale_fonts(w, h)

        # Background changed to true black
        self.screen.fill(BLACK)  # was NEAR_WHITE

        # Card with shadow
        margin = int(min(w, h) * 0.06)
        card = pygame.Rect(margin, margin, w - 2*margin, h - 2*margin)
        draw_shadow(self.screen, card, radius=36, spread=22, alpha=130)
        round_rect(self.screen, card, WHITE, radius=36)

        # Brand changed to ALMUS
        brand = self.f["brand"].render("ALMUS", True, BLACK)  # ALTUS -> ALMUS
        self.screen.blit(brand, (card.centerx - brand.get_width()//2, card.y - int(h*0.04)))

        header_h = int(card.height * 0.145)
        header = pygame.Rect(card.x, card.y, card.width, header_h)
        draw_vertical_gradient(self.screen, header, GOLD_TOP, GOLD_BOTTOM, radius=36)

        left_x = header.x + int(header.height * 0.6)
        wajdi = self.f["brand"].render("WAJDI", True, BLACK)
        self.screen.blit(wajdi, (left_x, header.centery - wajdi.get_height()//2))

        time_txt = self.f["time"].render("15H30", True, BLACK)
        self.screen.blit(time_txt, (header.centerx - time_txt.get_width()//2,
                                    header.centery - time_txt.get_height()//2))

        pill_h = int(header_h * 0.5)
        pill_w = int(pill_h * 1.8)
        pill = pygame.Rect(header.right - pill_w - int(header_h*0.4),
                           header.centery - pill_h//2, pill_w, pill_h)
        round_rect(self.screen, pill, RED, radius=pill_h//2)
        live = self.f["pill"].render("LIVE", True, WHITE)
        self.screen.blit(live, (pill.centerx - live.get_width()//2,
                                pill.centery - live.get_height()//2))

        inner = pygame.Rect(card.x + int(card.width*0.02),
                            header.bottom + int(card.height*0.01),
                            card.width - int(card.width*0.04),
                            card.height - header_h - int(card.height*0.22))
        round_rect(self.screen, inner, WHITE, radius=24, width=2)

        split_x = inner.centerx
        left = pygame.Rect(inner.x, inner.y, split_x - inner.x, inner.height)
        right = pygame.Rect(split_x, inner.y, inner.right - split_x, inner.height)
        round_rect(self.screen, left, PANEL_BLACK, radius=24)
        round_rect(self.screen, right, GOLD_PANEL, radius=24)
        pygame.draw.rect(self.screen, PANEL_BLACK, (left.right-24, left.y, 24, left.height))
        pygame.draw.rect(self.screen, GOLD_PANEL, (right.x, right.y, 24, right.height))
        pygame.draw.line(self.screen, WHITE, (split_x, inner.y + int(inner.height*0.02)),
                         (split_x, inner.bottom - int(inner.height*0.02)), 3)

        bt = self.f["panel"].render("BLACK TEAM", True, WHITE)
        yt = self.f["panel"].render("YELLOW TEAM", True, WHITE)
        self.screen.blit(bt, (left.x + int(left.width*0.06), left.y + int(left.height*0.06)))
        self.screen.blit(yt, (right.x + int(right.width*0.06), right.y + int(right.height*0.06)))

        bscore = self.f["big"].render(self.score.disp("black"), True, WHITE)
        yscore = self.f["big"].render(self.score.disp("yellow"), True, WHITE)
        self.screen.blit(bscore, (left.centerx - bscore.get_width()//2,
                                  left.centery - bscore.get_height()//2 + int(left.height*0.04)))
        self.screen.blit(yscore, (right.centerx - yscore.get_width()//2,
                                  right.centery - yscore.get_height()//2 + int(right.height*0.04)))

        vs = self.f["vs"].render("VS", True, WHITE)
        vs_bg = pygame.Surface((vs.get_width()+32, vs.get_height()+32), pygame.SRCALPHA)
        pygame.draw.ellipse(vs_bg, (0, 0, 0, 140), vs_bg.get_rect())
        self.screen.blit(vs_bg, (inner.centerx - vs_bg.get_width()//2,
                                 inner.centery - vs_bg.get_height()//2))
        self.screen.blit(vs, (inner.centerx - vs.get_width()//2,
                              inner.centery - vs.get_height()//2))

        cap_w = int(card.width * 0.58)
        cap_h = int(card.height * 0.20)
        capsule = pygame.Rect(card.centerx - cap_w//2,
                              inner.bottom - int(cap_h*0.25),
                              cap_w, cap_h)
        draw_shadow(self.screen, capsule, radius=cap_h//2, spread=18, alpha=130)
        round_rect(self.screen, capsule, (10, 10, 10), radius=cap_h//2)

        cap_lbl = self.f["caps"].render("SCORE GAME", True, WHITE)
        self.screen.blit(cap_lbl, (capsule.centerx - cap_lbl.get_width()//2,
                                   capsule.top + int(cap_h*0.18)))

        # Smaller red score (reduced font earlier); keep centering
        games_str = f"{self.score.bg}.{self.score.yg}"
        games = self.f["caps"].render(games_str, True, RED)  # use smaller font for red number
        self.screen.blit(games, (capsule.centerx - games.get_width()//2,
                                 capsule.centery - games.get_height()//2 + int(cap_h*0.14)))

        pygame.draw.rect(self.screen, BLACK, card, width=2, border_radius=36)

    def handle_click(self, pos):
        w, h = self.screen.get_size()
        margin = int(min(w, h) * 0.06)
        card = pygame.Rect(margin, margin, w - 2*margin, h - 2*margin)
        header_h = int(card.height * 0.145)
        inner = pygame.Rect(card.x + int(card.width*0.02),
                            card.y + header_h + int(card.height*0.01),
                            card.width - int(card.width*0.04),
                            card.height - header_h - int(card.height*0.22))
        if pos[0] < inner.centerx: self.score.add("black")
        else: self.score.add("yellow")

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit(0)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit(0)
                    if e.key == pygame.K_r: self.score.reset()
                    if e.key == pygame.K_1: self.score.add("black")
                    if e.key == pygame.K_2: self.score.add("yellow")
                    if e.key == pygame.K_f: pygame.display.toggle_fullscreen()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(e.pos)
            self.draw(); pygame.display.flip(); self.clock.tick(FPS)

if __name__ == "__main__":
    Scoreboard().run()
