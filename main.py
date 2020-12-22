import os
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
import PIL

# disabling multitouch
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.core.window import Window
with open("config.json", 'r') as config_file:
    data = json.load(config_file)
if data.get("maximize", "normal") == "down":
    Window.maximize()

from kivymd.app import MDApp

from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
import kivy.properties as properties
from kivy.uix.rst import RstDocument
from kivy.uix.gridlayout import GridLayout
from filemanager import MDFileManager
from kivy.utils import get_color_from_hex
from kivy.graphics import Rectangle, Color
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image

the_answer_to_the_ultimate_question_of_life_the_universe_and_everything = 42

class ResizableImage(Scatter):
    def __init__(self, **kwargs):
        super(ResizableImage, self).__init__(**kwargs)
        self.start_pos = None
        self.end_pos = None
    def on_touch_down(self, touch):
        self.start_pos = None
        if main_app.image_screen.selecting and touch.pos[0] < Window.width*0.8:
            if self.if_cursor_inside_image(self.pos, self.size, touch.pos) and not touch.is_mouse_scrolling:
                self.start_pos = touch.pos
            else:
                self.start_pos = None
        elif ((not main_app.image_screen.selecting) and touch.pos[0] < Window.width*0.8):
            super(ResizableImage, self).on_touch_down(touch)

    def on_touch_move(self, touch): #BLACK MAGIC! DO NOT TOUCH!
        self.end_pos = None
        if main_app.image_screen.selecting:
            if touch.pos[0] < Window.width*0.8:
                if self.start_pos:
                    if self.if_cursor_inside_image(self.pos, self.size, touch.pos):

                        img = main_app.image_screen.ids.canvas_widget
                        img.canvas.after.clear()
                        with img.canvas.after:
                            
                            Color(1, 1, 1, 0.3)
                            _size = [abs(self.start_pos[0] - touch.pos[0]), abs(self.start_pos[1] - touch.pos[1])]
                            _pos = [min((self.start_pos[0], touch.pos[0])), min((self.start_pos[1], touch.pos[1]))]
                            self.rect = Rectangle(pos=_pos, size=_size)
                            self.end_pos = touch.pos
                else:
                    main_app.image_screen.ids.canvas_widget.canvas.after.clear()
                    self.start_pos = None


        else:
            if touch.pos[0] < Window.width*0.8:
                super(ResizableImage, self).on_touch_move(touch)


    def on_touch_up(self, touch):
        if main_app.image_screen.selecting:
            if self.start_pos and self.end_pos:
                s, e = self.calculate_position(self.start_pos, self.end_pos, self.pos, self.size)
                self.create_histogram_and_calculate_average_color(s, e)
                self.insert_histogram()
                self.insert_average_color()
        else:
            super(ResizableImage, self).on_touch_up(touch)

    def create_histogram_and_calculate_average_color(self, s, e):
        image = PIL.Image.open(main_app.image_path)
        image = image.crop((*s, *e))
        image_grayscale = np.array(image.convert("L"))
        plt.cla()
        plt.hist(image_grayscale.flatten())
        plt.savefig("histogram.png")
        average_color_per_row = np.average(image, axis=0)
        average_color = np.average(average_color_per_row, axis=0) / 255
        average_color = [average_color[0], average_color[1], average_color[2], 1]
        main_app.image_screen.average_color = average_color

    def insert_histogram(self):
        main_app.image_screen.ids.histogram.opacity = 1
        main_app.image_screen.ids.histogram.source = "histogram.png"
        main_app.image_screen.ids.histogram.reload()


    def insert_average_color(self):
        main_app.image_screen.ids.average_color = main_app.image_screen.average_color

    def calculate_position(self, s_pos, e_pos, i_pos, size):
        real_start_pos = [s_pos[0] - i_pos[0], s_pos[1] - i_pos[1]]
        real_end_pos = [e_pos[0] - i_pos[0], e_pos[1] - i_pos[1]]
        img = PIL.Image.open(main_app.image_path)
        w, h = img.size
        img_pos_start = [round(w * real_start_pos[0] / size[0], 0), round(h * real_start_pos[1] / size[1], 0)]
        img_pos_end = [round(w * real_end_pos[0] / size[0], 0), round(h * real_end_pos[1] / size[1], 0)]

        _s = min((img_pos_start[0], img_pos_end[0])), h - max((img_pos_start[1], img_pos_end[1]))
        _e = max((img_pos_start[0], img_pos_end[0])), h - min((img_pos_start[1], img_pos_end[1]))
        return _s, _e
    
    def if_cursor_inside_image(self, pos, size, point):
        if (point[0] > pos[0] and point[0] < pos[0]+size[0] and point[1] > pos[1] and point[1] < pos[1]+size[1]): 
            return True
        else : 
            return False


class CustomIconButtonGroup(GridLayout):
    def on_move(self):
        main_app.image_screen.selecting = False
        self.ids.move_button.text_color = get_color_from_hex("#f3ab44")
        self.ids.select_button.text_color = get_color_from_hex("#ffffff")
        main_app.image_screen.ids.canvas_widget.canvas.after.clear()

    def on_select(self):
        main_app.image_screen.selecting = True
        self.ids.move_button.text_color = get_color_from_hex("#ffffff")
        self.ids.select_button.text_color = get_color_from_hex("#f3ab44")


class ImageScreen(Screen):
    selecting = properties.BooleanProperty(False)
    average_color = properties.ColorProperty([0, 0, 0, 0])

class MainScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class AboutScreen(Screen):
    text = properties.StringProperty("")

    def __init__(self, **kwargs):
        super(AboutScreen, self).__init__(**kwargs)
        with open("about.txt", "r", encoding="utf-8") as f:
            self.text = f.read()

class MainApp(MDApp):
    text_color = properties.ColorProperty(None)
    image_path = properties.StringProperty("")
    def build(self):
        self.theme_cls.theme_style = data['theme']
        self.theme_cls.primary_palette = "BlueGray"
        self.title = "Lēts Photoshop"
        
        self.update_text_color()

        self.screen_manager = ScreenManager()
        self.main_screen = MainScreen(name="main")
        self.screen_manager.add_widget(self.main_screen)

        self.settings_screen = SettingsScreen(name="settings")
        self.screen_manager.add_widget(self.settings_screen)
        self.settings_screen.ids.maximize_screen.state = data.get("maximize", "normal")


        self.about_screen = AboutScreen(name="about")
        self.screen_manager.add_widget(self.about_screen)

        self.image_screen = ImageScreen(name="image")
        self.screen_manager.add_widget(self.image_screen)


        return self.screen_manager


    def update_text_color(self):
        if self.theme_cls.theme_style == "Dark":
            self.text_color = (1, 1, 1, 1)
        else:
            self.text_color = (0, 0, 0, 1)

    def write_data_to_config_file(self):
        with open("config.json", "w") as config_file:
            json.dump(data, config_file)

    def open_file_manager(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            ext=[".jpg", '.png', "jpeg"]
        )
        self.file_manager.show("\\")

    def select_path(self, path):
        self.exit_manager()
        self.main_screen.ids.image_path_input.text = path

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()
    
    def open_file_and_set_image_screen(self):   # sometimes I believe compiler ignores all my comments
        path = self.main_screen.ids.image_path_input.text
        if os.path.isfile(path) and os.path.splitext(path)[1] in [".png", ".jpg", "jpeg"]:
            self.image_path = path
            self.screen_manager.current = "image"

    def open_about_screen(self):
        self.screen_manager.current = "about"

    def open_settings_screen(self):
        self.screen_manager.current = "settings"
        if self.theme_cls.theme_style == "Dark":
            self.settings_screen.ids.change_theme_button.text = "Switch to Light theme"
        else:
            self.settings_screen.ids.change_theme_button.text = "Switch to Dark theme"
    
    def cahnge_theme(self):
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
            self.update_text_color()
            self.settings_screen.ids.change_theme_button.text = "Switch to Light theme"
        else:
            self.theme_cls.theme_style = "Light"
            self.update_text_color()
            self.settings_screen.ids.change_theme_button.text = "Switch to Dark theme"
    
    def open_main_screen_and_save_settings(self):
        self.screen_manager.current = "main"
        data["theme"] = self.theme_cls.theme_style
        data["maximize"] = self.settings_screen.ids.maximize_screen.state
        self.write_data_to_config_file()

    def open_main_screen(self):
        self.screen_manager.current = "main"
    
if __name__ == "__main__":
    for file_path in glob.glob(os.path.join("screens", "*.kv")):
        with open(file_path, 'r', encoding='utf-8') as file:
            Builder.load_string(file.read())

    main_app = MainApp()
    main_app.run()
