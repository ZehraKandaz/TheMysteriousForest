from .GameScene import GameScene
from . import settings
import pygame
import os
from .UI import Mouse, Button, Font, CheckBox
import random


class StartMenu(GameScene):
    """
    Başlatıldıktan sonra "Beginning" klasöründeki 1.jpg–10.jpg görsellerini
    Space ile geçip sonunda level_manager sahnesine başlatır.
    """
    bg = None

    @staticmethod
    def _load_resources():
        if StartMenu.bg is None:
            StartMenu.bg = pygame.transform.smoothscale(
                pygame.image.load(os.path.join(settings.img_folder, "HUD", "main_menu_bg_50.png")),
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            )

    def __init__(self, goto_scene):
        self._goto_scene = goto_scene
        super().__init__()
        self._load_resources()
        Mouse.set_visible(True)

        # Beginning klasöründeki görselleri yükle
        self.images = [
            pygame.image.load(
                os.path.join(settings.img_folder, "Beginning", f"{i}.jpg")
            ).convert()
            for i in range(1, 11)
        ]
        self.current = 0
        self.show_images = True

        # Menü başlığı ve butonlar (gizli kalacak sonradan)
        self._title = pygame.image.load(os.path.join(settings.img_folder, "title_text.png"))
        self._text_rect = self._title.get_rect()
        self._text_x = (settings.SCREEN_WIDTH - self._text_rect.width) // 2
        self._text_y = self._text_rect.height // 2

        y = self._text_rect.bottom + 100
        w, h = 150, 50
        self.start_bttn = Button(
            (settings.SCREEN_WIDTH//2 - 75, y), (w, h), "Start",
            lambda: goto_scene("level_manager")
        )
        self.settings_bttn = Button(
            (settings.SCREEN_WIDTH//2 - 75, y + 75), (w, h), "Settings",
            lambda: goto_scene("settings_menu")
        )
        self.exit_bttn = Button(
            (settings.SCREEN_WIDTH//2 - 75, y + 150), (w, h), "Quit",
            lambda: goto_scene("quit")
        )

    def render(self, surface):
        # Görseller sıralı gösterim
        if self.show_images:
            img = pygame.transform.scale(
                self.images[self.current],
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            )
            surface.blit(img, (0, 0))
            return

        # Normal menu
        surface.blit(self.bg, (0, 0))
        surface.blit(self._title, (self._text_x, self._text_y))
        self.start_bttn.render(surface)
        self.settings_bttn.render(surface)
        self.exit_bttn.render(surface)

    def update(self, delta_time):
        pass

    def handle_events(self, event):
        # Görsel gösterimindeyken Space ile ilerle
        if self.show_images and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.current += 1
            if self.current >= len(self.images):
                self.show_images = False
            return

        # Menü olayları
        self.start_bttn.handle_events(event)
        self.settings_bttn.handle_events(event)
        self.exit_bttn.handle_events(event)
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_ESCAPE):
            self._goto_scene("quit")


class PauseMenu(GameScene):
    def __init__(self, goto_scene):
        self._goto_scene = goto_scene
        GameScene.__init__(self)
        Mouse.set_visible(True)
        w, h = 150, 50

        self._text_surface = Font.get_render("Paused", size="big")
        self._text_rect = self._text_surface.get_rect()
        self._text_x = (settings.SCREEN_WIDTH - self._text_rect.width) // 2
        self._text_y = self._text_rect.height // 2

        self.continue_bttn = Button(((settings.SCREEN_WIDTH-w)//2, self._text_rect.bottom + 50), (w, h),
                                    "Continue", lambda: goto_scene("previous"))
        self.settings_bttn = Button(((settings.SCREEN_WIDTH - w) // 2, self._text_rect.bottom + 125), (w, h),
                                    "Settings", lambda: goto_scene("settings_menu"))
        self.start_menu_bttn = Button(((settings.SCREEN_WIDTH - w) // 2, self._text_rect.bottom + 200), (w, h), "Start Menu",
                                lambda: goto_scene("start_menu"))
        self.exit_bttn = Button(((settings.SCREEN_WIDTH - w) // 2, self._text_rect.bottom + 275), (w, h), "Quit",
                                lambda: goto_scene("quit"))

    def render(self, surface):
        surface.fill((35, 25, 40))
        surface.blit(self._text_surface, (self._text_x, self._text_y))
        self.continue_bttn.render(surface)
        self.settings_bttn.render(surface)
        self.start_menu_bttn.render(surface)
        self.exit_bttn.render(surface)

    def update(self, delta_time):
        pass

    def handle_events(self, event):
        self.continue_bttn.handle_events(event)
        self.settings_bttn.handle_events(event)
        self.start_menu_bttn.handle_events(event)
        self.exit_bttn.handle_events(event)

        if event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_ESCAPE):
            self._goto_scene("previous")


class SettingsMenu(GameScene):
    def __init__(self, goto_scene, update_display_config):
        self._goto_scene = goto_scene
        self._update_display_config = update_display_config

        GameScene.__init__(self)
        Mouse.set_visible(True)
        w, h = 150, 50

        self._text_surface = Font.get_render("Settings", size="big")
        self._text_rect = self._text_surface.get_rect()
        self._text_x = (settings.SCREEN_WIDTH - self._text_rect.width) // 2
        self._text_y = self._text_rect.height//2

        self._fullscreen_checkbox = CheckBox((50, self._text_rect.bottom+50), "Fullscreen")
        self._fullscreen_checkbox.selected = settings.FULLSCREEN
        self._scale_checkbox = CheckBox((50, self._text_rect.bottom + 100), "Scale to 1280x720")
        self._scale_checkbox.selected = (settings.FINAL_HEIGHT != settings.SCREEN_HEIGHT)
        self._fps_checkbox = CheckBox((50, self._text_rect.bottom + 150), "Show FPS")
        self._fps_checkbox.selected = settings.SHOW_FPS

        self.continue_bttn = Button((50, (settings.SCREEN_HEIGHT - h - 25)), (w, h),
                                    "Done", self._on_done)

    def _on_done(self):
        settings.SHOW_FPS = self._fps_checkbox.selected
        h = 720 if self._scale_checkbox.selected else 480
        self._update_display_config(self._fullscreen_checkbox.selected, h)
        self._goto_scene("previous")

    def render(self, surface):
        surface.fill((35, 25, 40))
        surface.blit(self._text_surface, (self._text_x, self._text_y))
        self._fullscreen_checkbox.render(surface)
        self._scale_checkbox.render(surface)
        self._fps_checkbox.render(surface)
        self.continue_bttn.render(surface)

    def update(self, delta_time):
        pass

    def handle_events(self, event):
        self._fullscreen_checkbox.handle_events(event)
        self._scale_checkbox.handle_events(event)
        self._fps_checkbox.handle_events(event)
        self.continue_bttn.handle_events(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._goto_scene("previous")


class EndMenu(GameScene):
    class Confetti:
        def __init__(self, color):
            self.color = color
            self.speed = random.randint(200, 500)
            self.size = random.randint(2, 6)
            self.pos = [random.randrange(5, settings.SCREEN_WIDTH-5), 0]
            self._t = 0
            self._dx = 0

        def render(self, surface):
            pygame.draw.rect(surface, self.color, (self.pos, (self.size, self.size)))

        def update(self, delta_time):
            self.pos[1] += self.speed * delta_time
            if self.pos[1] >= settings.SCREEN_HEIGHT:
                self.pos[1] = 0
                self.pos[0] = random.randrange(5, settings.SCREEN_WIDTH-5)
            self._t += delta_time
            if self._t > 0.5:
                self._t = 0
                self._dx = random.choice([-50, 50])
            self.pos[0] += self._dx * delta_time

    def __init__(self, goto_scene, coins_collected, total_coins, total_deaths):
        self._goto_scene = goto_scene
        Mouse.set_visible(True)
        super().__init__()

        # 1) END klasöründeki 1.jpg–7.jpg resimlerini yükle
        self.images = [
            pygame.image.load(os.path.join(settings.img_folder, "END", f"{i}.jpg")).convert()
            for i in range(1, 11)
        ]
        self.current_image = 0
        self.show_images = True

        # 2) Mevcut confetti, ses ve skor alanı hazırlıkları
        self.victory_sound = pygame.mixer.Sound(os.path.join(settings.music_folder, 'victory.wav'))
        self.victory_sound.set_volume(0.5)
        self._colors = [(250,20,20),(20,250,20),(250,20,250),(250,250,20),(20,250,250)]
        self._color_i = 0
        self._elapsed_time = 0
        self._confettis = [self.Confetti(random.choice(self._colors)) for _ in range(30)]

        # Başlık ve metinler
        self._heading_text_surface = Font.get_render("Congratulations!!", size="big")
        self._heading_text_rect = self._heading_text_surface.get_rect()
        self._heading_text_x = (settings.SCREEN_WIDTH - self._heading_text_rect.width)//2
        self._heading_text_y = self._heading_text_rect.height//2

        self._text_surface = Font.get_render("You have completed your journey!", size="normal")
        self._text_rect = self._text_surface.get_rect()
        self._text_x = (settings.SCREEN_WIDTH - self._text_rect.width)//2
        self._text_y = self._heading_text_y + self._heading_text_rect.height*2

        self._stat_text_surface = Font.get_render(f"Coins Collected:  {coins_collected}/{total_coins}", size="normal")
        self._stat_text_rect = self._stat_text_surface.get_rect()
        self._stat_text_x = (settings.SCREEN_WIDTH - self._stat_text_rect.width)//2
        self._stat_text_y = self._text_y + self._text_rect.height*3//2

        self._death_text_surface = Font.get_render(f"Total Deaths:  {total_deaths}", size="normal")
        self._death_text_rect = self._death_text_surface.get_rect()
        self._death_text_x = (settings.SCREEN_WIDTH - self._death_text_rect.width)//2
        self._death_text_y = self._stat_text_y + self._stat_text_rect.height*3//2

        # Butonlar
        w, h = 150, 50
        button_y = self._death_text_y + self._death_text_rect.height
        self.start_menu_bttn = Button(((settings.SCREEN_WIDTH-w)//2, button_y+50), (w,h), "Start Menu", lambda: goto_scene("start_menu"))
        self.exit_bttn       = Button(((settings.SCREEN_WIDTH-w)//2, button_y+125), (w,h), "Quit",       lambda: goto_scene("quit"))

        # Victory sound (istersen burada da tutabilirsin)
        self.victory_sound.play()

    def render(self, surface):
        # 1) Görsel dizisi gösteriliyorsa:
        if self.show_images:
            img = pygame.transform.scale(self.images[self.current_image],
                                         (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            surface.blit(img, (0,0))
            return

        # 2) Sonra orijinal EndMenu render’ı:
        surface.fill((35,25,40))
        heading = Font.get_render("Congratulations!!", color=self._colors[self._color_i], size="big")
        surface.blit(heading, (self._heading_text_x, self._heading_text_y))
        surface.blit(self._text_surface, (self._text_x, self._text_y))
        surface.blit(self._stat_text_surface, (self._stat_text_x, self._stat_text_y))
        surface.blit(self._death_text_surface, (self._death_text_x, self._death_text_y))
        self.start_menu_bttn.render(surface)
        self.exit_bttn.render(surface)
        for conf in self._confettis:
            conf.render(surface)

    def update(self, delta_time):
        # Sadece skor ekranındayken confetti ve renk döngüsü
        if not self.show_images:
            self._elapsed_time += delta_time
            if self._elapsed_time >= 0.25:
                self._elapsed_time = 0
                self._color_i = (self._color_i + 1) % len(self._colors)
            for conf in self._confettis:
                conf.update(delta_time)

    def handle_events(self, event):
        # Space tuşu ile resim değiştir
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.show_images:
            self.current_image += 1
            if self.current_image >= len(self.images):
                self.show_images = False
            return

        # Skor ekranındayken butonları işle
        self.start_menu_bttn.handle_events(event)
        self.exit_bttn.handle_events(event)
        if event.type == pygame.KEYDOWN and (event.key in (pygame.K_p, pygame.K_ESCAPE)):
            self._goto_scene("start_menu")
