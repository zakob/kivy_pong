
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

    def check_collision(self, ball):

        if self.top < ball.y or self.y > ball.top:
            return (false, None, None)

        if self.x == 0:
            back = self.x
            front = self.right
            back_ball = ball.right
            front_ball = ball.x
        else:
            back = self.right
            front = self.x
            back_ball = ball.x
            front_ball = ball.right

        if ball.center_y < self.top and ball.center_y > self.y: pass


        if ball.center_x:
            pass

    def bounce_ball(self, ball, dt, max_vel=1100):
        if self.collide_widget(ball):
            if ball.top > self.y and ball.y < self.top:
                vx, vy = ball.velocity
                offset = (ball.center_y - self.center_y) / (self.height / 2)
                bounced = Vector(-1 * vx, vy)
                if Vector(ball.velocity).length() < max_vel:
                    m = 1.1
                else:
                    m = 1
                vel = bounced * m
                # print(Vector(ball.velocity).length())
                ball.velocity = vel.x, vel.y + offset / dt


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

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

        # self.p1_init_pos = self.player1.center
        # self.p2_init_pos = self.player2.center

        self.m_player1 = None
        self.m_player2 = None

        self.max_score = 10

        self.event_ball = Clock.schedule_interval(self.ball_update, 0)
        self.event_ball.cancel()
        self.event_players = Clock.schedule_interval(self.move_pad, 0)
        self.event_players.cancel()

        self.gm_main_options = ['1 player', '2 players', 'Exit']
        self.gm_main = gamemenu.GameMenu.list_menu_items('Main menu', self.gm_main_options)
        self.add_widget(self.gm_main)
        self.gm_pause_options = ['Resume', 'Return to Main menu', 'Exit']
        self.gm_pause = gamemenu.GameMenu.list_menu_items('Pause', self.gm_pause_options)
        self.gm_end_options = ['Restart', 'Return to Main menu', 'Exit']
        # self.gm_end = gamemenu.GameMenu.list_menu_items('End', self.gm_pause_options)

        self.state_menu = -1

    def start_game(self):
        # print(1)
        self.event_players()
        self.event_ball()
    
    def stop_game(self):
        self.event_ball.cancel()
        self.event_players.cancel()

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
                    # print(self.gm_main_options[self.gm_main.active_item])
                    self.menu_actions(self.gm_main_options[self.gm_main.active_item])

            if self.state_menu == 1:
                self.gm_pause.navigate(keycode[1])
                if 'enter' in keycode[1]:
                    # print(self.gm_pause_options[self.gm_pause.active_item])
                    self.menu_actions(self.gm_pause_options[self.gm_pause.active_item])

            if self.state_menu == 2:
                self.gm_end.navigate(keycode[1])
                if 'enter' in keycode[1]:
                    # print(self.gm_end_options[self.gm_end.active_item])
                    self.menu_actions(self.gm_end_options[self.gm_end.active_item])
            
            self.keysPressed.add(keycode[1])
    
    def _on_keyboard_up(self, keybord, keycode):
        text = keycode[1]
        # print(text)
        if text != 'escape':
            if text in self.keysPressed:
                if text in ['w', 's']:
                    self.m_player1 = None
                if text in ['up', 'down']:
                    self.m_player2 = None
                self.keysPressed.remove(text)
                self.step_size = None

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
            self.serve_ball(vel=(choice([-1, 1])*250, 0))
            self.start_game()
        elif text == 'Restart':
            self.remove_widget(self.gm_end)
            self.player1.score = 0
            self.player2.score = 0
            self.player1.center_y = self.center_y
            self.player2.center_y = self.center_y
            # print(self.p1_init_pos)
            # print(self.p2_init_pos)
            self.state_menu = 0
            self.remove_widget(self.gm_main)
            self.serve_ball(vel=(choice([-1, 1])*250, 0))
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
            self.serve_ball(vel=(250, 0))
        else:
            pass

    def serve_ball(self, vel=(250, 0)):
        # print(self.center)
        # self.ball.center = (400, 300)
        self.ball.center = self.center
        self.ball.velocity = vel

    def move_pad(self, dt):
        if self.state_menu == 0:

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
        if self.state_menu == 0:
            self.ball.move(dt)

            # bounce of paddles
            self.player1.bounce_ball(self.ball, dt)
            self.player2.bounce_ball(self.ball, dt)

            # bounce ball off bottom or top
            if (self.ball.y < self.y) or (self.ball.top > self.top):
                self.ball.velocity_y *= -1

            # went of to a side to score point?
            if self.ball.center_x < self.x:
                self.player2.score += 1
                if self.player2.score == self.max_score:
                    # print('Player 2 win!!!')
                    self.stop_game()
                    self.state_menu = 2
                    self.gm_end = gamemenu.GameMenu.list_menu_items('Player 2 win!!!', self.gm_end_options)
                    self.add_widget(self.gm_end)
                self.serve_ball(vel=(250, 0))
            if self.ball.center_x > self.width:
                self.player1.score += 1
                if self.player1.score == self.max_score:
                    # print('Player 1 win!!!')
                    self.stop_game()
                    self.state_menu = 2
                    self.gm_end = gamemenu.GameMenu.list_menu_items('Player 1 win!!!', self.gm_end_options)
                    self.add_widget(self.gm_end)
                self.serve_ball(vel=(-250, 0))


class PongApp(App):
    def build(self):
        game = PongGame()
        # game.serve_ball()
        # game.start_game()
        return game


if __name__ == '__main__':
    PongApp().run()