# from kivy.config import Config
# Config.set('kivy', 'exit_on_escape', '0')
# Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window

class GameMenu(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.menu_items = list()
        self.active_item = 0

        self.color_list = [1, 0.407, 0]
        self.color_f = (self.color_list[0],
                        self.color_list[1], 
                        self.color_list[2], 1)
        self.color = (self.color_list[0],
                      self.color_list[1], 
                      self.color_list[2], 0.2)
    
    @classmethod
    def list_menu_items(cls, menu_title, menu_items):
        gm_cls = cls()
        clr_f = gm_cls.color_f
        clr = gm_cls.color
        fs = 50
        ts = (300, 50)
        top_pos = Window.size[1] * 0.5
        gm_cls.title = menu_title
        title_label = Label(text=menu_title,
                            color=clr_f,
                            font_size=fs*1.5,
                            center_x=Window.width/2,
                            top=top_pos + fs*1.5)
        gm_cls.add_widget(title_label)
        first_item = Label(text=menu_items[0],
                        #    text_size=ts,
                        #    halign='center',
                           color=clr_f,
                           font_size=fs,
                           center_x=Window.width/2,
                           top=top_pos)
        gm_cls.add_widget(first_item)
        gm_cls.menu_items.append(first_item)
        top_pos -= fs
        for menu_item in menu_items[1:]:
            menu_item = Label(text=menu_item,
                            #   text_size=ts,
                            #   halign='center',
                              color=clr,
                              font_size=fs,
                              center_x=Window.width/2,
                              top=top_pos)
            top_pos -= fs
            gm_cls.add_widget(menu_item)
            gm_cls.menu_items.append(menu_item)
        return gm_cls

    def navigate(self, text):
        n = len(self.menu_items)

        self.menu_items[self.active_item].color = self.color
        
        if text == 'down':
            self.active_item += 1
        elif text == 'up':
            self.active_item -= 1
        
        if self.active_item == -1:
            self.active_item = n - 1
        elif self.active_item == n:
            self.active_item = 0
        
        self.menu_items[self.active_item].color = self.color_f        