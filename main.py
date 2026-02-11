from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture
import random
import os
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def res(path):
    return os.path.join(BASE_DIR, path)

# Игровые константы
GAME_W = 480
GAME_H = 800
CAR_W = 50
CAR_H = 60
ROAD_LEFT = 60
ROAD_RIGHT = GAME_W - 60
LANES = [80, 150, 220, 290, 360]
COIN_LANES = [100, 170, 240, 310, 380]

def load_records():
    p = res("records.txt")
    if os.path.exists(p):
        try:
            with open(p, "r") as f:
                records = []
                for line in f.readlines():
                    line = line.strip()
                    if line:
                        records.append(int(line))
                return sorted(records, reverse=True)[:5]
        except:
            return []
    return []

def save_record(score):
    records = load_records()
    records.append(score)
    records = sorted(records, reverse=True)[:5]
    try:
        with open(res("records.txt"), "w") as f:
            for r in records:
                f.write(str(r) + "\n")
    except:
        pass
    return records

def get_place(score):
    records = load_records()
    for i, r in enumerate(records):
        if score >= r:
            return i + 1
    if len(records) < 5:
        return len(records) + 1
    return 0


class GameWidget(Widget):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.reset()
        self.touch_left = False
        self.touch_right = False
        self.scale_x = 1
        self.scale_y = 1
        self.offset_x = 0
        self.offset_y = 0
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def reset(self):
        self.player_x = GAME_W // 2 - CAR_W // 2
        self.player_y = 100
        self.enemies = []
        self.coins = []
        self.explosions = []
        self.score = 0
        self.lives = 3
        self.speed = 5.0
        self.max_speed = 30
        self.speed_increase = 0.003
        self.frame = 0
        self.road_offset = 0
        self.coin_timer = 0
        self.game_over = False
        self.paused = False

    def on_size(self, *args):
        self.scale_x = self.width / GAME_W
        self.scale_y = self.height / GAME_H

    def sx(self, x):
        return x * self.scale_x

    def sy(self, y):
        return y * self.scale_y

    def on_touch_down(self, touch):
        if self.game_over:
            return
        tx = touch.x / self.scale_x
        ty = touch.y / self.scale_y
        if ty > GAME_H - 160:
            if tx > GAME_W // 2:
                self.touch_right = True
            else:
                self.touch_left = True
        elif ty > GAME_H - 200:
            self.paused = not self.paused

    def on_touch_up(self, touch):
        self.touch_left = False
        self.touch_right = False

    def update(self, dt):
        if self.game_over or self.paused:
            self.draw()
            return

        self.frame += 1

        if self.touch_left and self.player_x > ROAD_LEFT + 5:
            self.player_x -= 6
        if self.touch_right and self.player_x < ROAD_RIGHT - CAR_W - 5:
            self.player_x += 6

        spawn_delay = max(15, int(45 - self.speed * 1.5))
        if self.frame % spawn_delay == 0:
            x = random.choice(LANES)
            self.enemies.append([x, GAME_H + CAR_H])

        self.coin_timer += 1
        if self.coin_timer > 80:
            cx = random.choice(COIN_LANES)
            self.coins.append([cx, GAME_H + 30])
            self.coin_timer = 0

        pr = [self.player_x + 15, self.player_y + 15, CAR_W - 30, CAR_H - 30]

        for enemy in self.enemies[:]:
            enemy[1] -= int(self.speed)
            er = [enemy[0] + 15, enemy[1] + 15, CAR_W - 30, CAR_H - 30]
            if self.rects_collide(pr, er):
                self.lives -= 1
                self.explosions.append([enemy[0] + CAR_W // 2, enemy[1] + CAR_H // 2, 0])
                self.enemies.remove(enemy)
            elif enemy[1] < -CAR_H:
                self.enemies.remove(enemy)
                self.score += 10

        for coin in self.coins[:]:
            coin[1] -= int(self.speed)
            cr = [coin[0], coin[1], 25, 25]
            pr2 = [self.player_x + 5, self.player_y + 5, CAR_W - 10, CAR_H - 10]
            if self.rects_collide(pr2, cr):
                self.coins.remove(coin)
                self.score += 50
            elif coin[1] < -30:
                self.coins.remove(coin)

        for exp in self.explosions[:]:
            exp[2] += 1
            if exp[2] > 20:
                self.explosions.remove(exp)

        if self.speed < self.max_speed:
            self.speed += self.speed_increase

        self.road_offset = (self.road_offset + self.speed * 3) % 60

        if self.lives <= 0:
            self.game_over = True
            save_record(self.score)

        self.draw()

    def rects_collide(self, a, b):
        return (a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and
                a[1] < b[1] + b[3] and a[1] + a[3] > b[1])

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            # Трава
            Color(0.13, 0.55, 0.13)
            Rectangle(pos=(0, 0), size=(self.width, self.height))

            # Дорога
            Color(0.31, 0.31, 0.31)
            Rectangle(pos=(self.sx(50), 0), size=(self.sx(GAME_W - 100), self.height))

            # Бордюр
            for i in range(0, GAME_H + 60, 30):
                y = (i - self.road_offset) % (GAME_H + 60)
                if (i // 30) % 2 == 0:
                    Color(0.9, 0.1, 0.1)
                else:
                    Color(1, 1, 1)
                Rectangle(pos=(self.sx(40), self.sy(y)), size=(self.sx(12), self.sy(15)))
                Rectangle(pos=(self.sx(GAME_W - 52), self.sy(y)), size=(self.sx(12), self.sy(15)))

            # Разметка
            Color(1, 1, 1)
            for i in range(0, GAME_H + 60, 60):
                y = (i - self.road_offset) % (GAME_H + 60)
                Rectangle(pos=(self.sx(GAME_W // 2 - 3), self.sy(y)), size=(self.sx(6), self.sy(30)))

            # Враги
            Color(0.9, 0.1, 0.1)
            for enemy in self.enemies:
                Rectangle(pos=(self.sx(enemy[0]), self.sy(enemy[1])), size=(self.sx(CAR_W), self.sy(CAR_H)))
            Color(0.3, 0.3, 0.3)
            for enemy in self.enemies:
                Rectangle(pos=(self.sx(enemy[0] + 5), self.sy(enemy[1] + 5)), size=(self.sx(CAR_W - 10), self.sy(15)))

            # Монетки
            Color(1, 1, 0)
            for coin in self.coins:
                Ellipse(pos=(self.sx(coin[0]), self.sy(coin[1])), size=(self.sx(25), self.sy(25)))

            # Игрок
            Color(0.1, 0.5, 1)
            Rectangle(pos=(self.sx(self.player_x), self.sy(self.player_y)), size=(self.sx(CAR_W), self.sy(CAR_H)))
            Color(0.6, 0.8, 1)
            Rectangle(pos=(self.sx(self.player_x + 5), self.sy(self.player_y + CAR_H - 20)), size=(self.sx(CAR_W - 10), self.sy(15)))

            # Взрывы
            for exp in self.explosions:
                progress = exp[2] / 20.0
                r = int(40 * progress)
                Color(1, progress * 0.5, 0)
                Ellipse(pos=(self.sx(exp[0] - r), self.sy(exp[1] - r)), size=(self.sx(r * 2), self.sy(r * 2)))
                Color(1, 1, 1)
                r2 = max(1, int(10 * (1 - progress)))
                Ellipse(pos=(self.sx(exp[0] - r2), self.sy(exp[1] - r2)), size=(self.sx(r2 * 2), self.sy(r2 * 2)))

            # Кнопки управления
            Color(1, 1, 1, 0.3)
            Rectangle(pos=(self.sx(10), self.sy(20)), size=(self.sx(100), self.sy(80)))
            Rectangle(pos=(self.sx(GAME_W - 110), self.sy(20)), size=(self.sx(100), self.sy(80)))

            # Панель
            Color(0, 0, 0)
            Rectangle(pos=(0, self.height - self.sy(80)), size=(self.width, self.sy(80)))

        # Текст панели
        self.draw_label("O: " + str(self.score), self.sx(10), self.height - self.sy(30), color=(1, 1, 0, 1))
        self.draw_label("X " + str(self.lives), self.sx(10), self.height - self.sy(60), color=(1, 0, 0, 1))
        self.draw_label("x" + str(round(self.speed, 1)), self.sx(GAME_W - 100), self.height - self.sy(30), color=(1, 1, 1, 1))
        self.draw_label("L", self.sx(45), self.sy(50), color=(1, 1, 1, 1))
        self.draw_label("R", self.sx(GAME_W - 75), self.sy(50), color=(1, 1, 1, 1))

        if self.paused:
            self.draw_label("PAUSED", self.width // 2 - 60, self.height // 2, color=(1, 1, 0, 1), size=40)

        if self.game_over:
            self.draw_label("GAME OVER", self.width // 2 - 80, self.height // 2 + 40, color=(1, 0, 0, 1), size=40)
            self.draw_label("Score: " + str(self.score), self.width // 2 - 60, self.height // 2, color=(1, 1, 0, 1), size=30)
            self.draw_label("Tap to restart", self.width // 2 - 60, self.height // 2 - 40, color=(1, 1, 1, 1), size=20)

    def draw_label(self, text, x, y, color=(1, 1, 1, 1), size=24):
        label = Label(text=text, pos=(x, y), font_size=size, color=color, size_hint=(None, None))
        label.texture_update()
        with self.canvas:
            Color(*color)
            Rectangle(texture=label.texture, pos=(x, y), size=label.texture_size)

    def on_touch_down(self, touch):
        if self.game_over:
            self.reset()
            return True

        tx = touch.x / self.scale_x
        ty = touch.y / self.scale_y

        if ty < 120:
            if tx < GAME_W // 2:
                self.touch_left = True
            else:
                self.touch_right = True
        return True

    def on_touch_up(self, touch):
        self.touch_left = False
        self.touch_right = False
        return True


class RacingApp(App):
    def build(self):
        game = GameWidget(self)
        return game


if __name__ == "__main__":
    RacingApp().run()
