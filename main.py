from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import CoreLabel
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.uix.gridlayout import GridLayout
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window

import gamemenu

from random import choice


class PongPaddle(Widget):
    score = NumericProperty(0)
    active_switch = NumericProperty(1)

    def check_collision(self, ball, enemy_pad):
        if self.active_switch == 1:
            if self.top + ball.r < ball.center_y:
                return (False, None, None)
            if self.y - ball.r > ball.center_y:
                return (False, None, None)

            if self.x == 0:
                x1, y1, y2 = self.right, self.top, self.y
            else:
                x1, y1, y2 = self.x, self.top, self.y

            if self.top < ball.center_y and self.top + ball.r > ball.center_y:
                D1 = ((x1 - ball.center_x)**2 + (y1 - ball.center_y)**2)**0.5
                if D1 > ball.r:
                    return (False, None, None)
                else:
                    self.active_switch = 0
                    enemy_pad.active_switch = 1
                    return (True, ball.center_x, ball.center_y) 
            
            if self.y > ball.center_y and self.y - ball.r < ball.center_y:
                D2 = ((x1 - ball.center_x)**2 + (y2 - ball.center_y)**2)**0.5
                if D2 > ball.r:
                    return (False, None, None)
                else:
                    self.active_switch = 0
                    enemy_pad.active_switch = 1
                    return (True, ball.center_x, ball.center_y)
            
            D3 = abs(x1 - ball.center_x)
            if D3 > ball.r:
                return (False, None, None)

            self.active_switch = 0
            enemy_pad.active_switch = 1
            return (True, ball.center_x, ball.center_y)
        else:
            return (False, None, None)

    def bounce_ball(self, ball, enemy_pad):
        check, x, y = self.check_collision(ball, enemy_pad)
        if check:
            # print(x, y)
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            if Vector(ball.velocity).length() < ball.max_vel:
                m = 1.1
            else:
                m = 1
            vel = bounced * m
            ball.velocity = vel.x, vel.y + offset * bounced.length() * 0.7


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    r = NumericProperty(25)
    init_vel = NumericProperty(250)
    max_vel = NumericProperty(1000)

    def move(self, dt):
        self.pos = dt * Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

        self.keysPressed = set()
        
        self.p1 = ''
        self.p2 = ''

        self.m_player1 = None
        self.m_player2 = None

        self.max_score = 10

        self.dt = 0

        self.event_update = Clock.schedule_interval(self.update, self.dt)
        self.event_update.cancel()

        self.gm_main_options = ['1 player', '2 players', 'Exit']
        self.gm_main = gamemenu.GameMenu.list_menu_items('Main menu', self.gm_main_options)
        self.add_widget(self.gm_main)
        self.gm_pause_options = ['Resume', 'Return to Main menu', 'Exit']
        self.gm_pause = gamemenu.GameMenu.list_menu_items('Pause', self.gm_pause_options)
        self.gm_end_options = ['Restart', 'Return to Main menu', 'Exit']

        self.state_menu = -1

    def start_game(self):
        self.event_update()
    
    def stop_game(self):
        self.event_update.cancel()

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # print(keycode[1])
        if 'escape' == keycode[1]:
            if 'escape' in self.keysPressed and self.state_menu != -1:
                self.remove_widget(self.gm_pause)
                self.state_menu = 0
                self.start_game()
                self.keysPressed.remove('escape')
            else:
                if self.state_menu != -1:
                    self.stop_game()
                    self.add_widget(self.gm_pause)
                    self.state_menu = 1
                    self.keysPressed.add(keycode[1])
        else:

            if self.state_menu == -1:
                self.gm_main.navigate(keycode[1])
                if 'enter' in keycode[1]:
                    self.menu_actions(self.gm_main_options[self.gm_main.active_item])

            if self.state_menu == 1:
                self.gm_pause.navigate(keycode[1])
                if 'enter' in keycode[1]:
                    self.menu_actions(self.gm_pause_options[self.gm_pause.active_item])

            if self.state_menu == 2:
                self.gm_end.navigate(keycode[1])
                if 'enter' in keycode[1]:
                    self.menu_actions(self.gm_end_options[self.gm_end.active_item])
            
            self.keysPressed.add(keycode[1])
    
    def _on_keyboard_up(self, keybord, keycode):
        if keycode[1] != 'escape':
            if keycode[1] in self.keysPressed:
                if keycode[1] in ['w', 's']:
                    self.m_player1 = None
                if keycode[1] in ['up', 'down']:
                    self.m_player2 = None
                self.keysPressed.remove(keycode[1])

    def menu_actions(self, text):
        if text == 'Exit':
            App.get_running_app().stop()
        elif text == 'Resume':
            self.remove_widget(self.gm_pause)
            self.state_menu = 0
            self.start_game()
            self.keysPressed.remove('escape')
        elif text == '1 player':
            print('AI is not ready.')
        elif text == '2 players':
            self.state_menu = 0
            self.remove_widget(self.gm_main)
            self.serve_ball(vel=(choice([-1, 1])*self.ball.init_vel, 0))
            self.start_game()
        elif text == 'Restart':
            self.remove_widget(self.gm_end)
            self.player1.score = 0
            self.player2.score = 0
            self.player1.center_y = self.center_y
            self.player2.center_y = self.center_y
            self.state_menu = 0
            self.remove_widget(self.gm_main)
            self.serve_ball(vel=(choice([-1, 1])*self.ball.init_vel, 0))
            self.start_game()
        elif text == 'Return to Main menu':
            if self.state_menu == 1:
                self.remove_widget(self.gm_pause)
            else:
                self.remove_widget(self.gm_end)
            self.state_menu = -1
            self.add_widget(self.gm_main)
            self.player1.score = 0
            self.player2.score = 0
            self.player1.center_y = self.center_y
            self.player2.center_y = self.center_y
            self.serve_ball(vel=(self.ball.init_vel, 0))
        else:
            pass

    # def serve_ball(self, vel=(250, 0)):
    def serve_ball(self, vel):
        self.player1.active_switch = 1
        self.player2.active_switch = 1
        self.ball.center = self.center
        self.ball.velocity = vel

    def move_pad(self, dt):
        if self.m_player1:
            if self.m_player1 < 500:
                self.m_player1 += 100
        else:
            self.m_player1 = 100
        
        if self.m_player2:
            if self.m_player2 < 500:
                self.m_player2 += 10
        else:
            self.m_player2 = 100

        step_size1 = self.m_player1 * dt
        step_size2 = self.m_player2 * dt

        if 'w' in self.keysPressed:
            if self.player1.center_y < self.top:
                self.player1.center_y += step_size1

        elif 's' in self.keysPressed:
            if self.player1.center_y > self.y:
                self.player1.center_y -= step_size1

        if 'up' in self.keysPressed:
            if self.player2.center_y < self.top:
                self.player2.center_y += step_size2

        elif 'down' in self.keysPressed:
            if self.player2.center_y > self.y:
                self.player2.center_y -= step_size2

    def ball_update(self, dt):
        self.ball.move(dt)

        # bounce of paddles
        self.player1.bounce_ball(self.ball, self.player2)
        self.player2.bounce_ball(self.ball, self.player1)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) and (self.ball.velocity_y < 0):
            self.ball.velocity_y *= -1
        if (self.ball.top > self.top) and (self.ball.velocity_y > 0):
            self.ball.velocity_y *= -1

        # went of to a side to score point?
        if self.ball.center_x < self.x:
            self.player2.score += 1
            if self.player2.score == self.max_score:
                self.stop_game()
                self.state_menu = 2
                self.gm_end = gamemenu.GameMenu.list_menu_items('Player 2 win!!!', self.gm_end_options)
                self.add_widget(self.gm_end)
            self.serve_ball(vel=(self.ball.init_vel, 0))
        if self.ball.center_x > self.width:
            self.player1.score += 1
            if self.player1.score == self.max_score:
                self.stop_game()
                self.state_menu = 2
                self.gm_end = gamemenu.GameMenu.list_menu_items('Player 1 win!!!', self.gm_end_options)
                self.add_widget(self.gm_end)
            self.serve_ball(vel=(-self.ball.init_vel, 0))
        
    def update(self, dt):
        self.ball_update(dt)
        self.move_pad(dt)


class PongApp(App):
    def build(self):
        game = PongGame()
        return game


if __name__ == '__main__':
    PongApp().run()