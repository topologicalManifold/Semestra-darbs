import os
import glob
import json

from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
import kivy.properties as properties

# load config file
with open("config.json", 'r') as config_file:
    data = json.load(config_file)

class MainScreen(Screen):
    pass



class MainApp(MDApp):
    text_color = properties.ColorProperty(None)
    def build(self):
        self.theme_cls.theme_style = data['theme']
        self.theme_cls.primary_palette = "BlueGray"
        self.title = "Lēts Photoshop"

        self.screen_manager = ScreenManager()
        self.main_screen = MainScreen(name="main_screen")
        self.screen_manager.add_widget(self.main_screen)
        return self.screen_manager


    def update_text_color(self):
        if self.theme_cls.theme_style == "Dark":
            self.text_color = (1, 1, 1, 1)
        else:
            self.text_color = (0, 0, 0, 1)

    def write_data_to_config_file(self):
        with open("config.json", "w") as config_file:
            json.dump(data, config_file)

if __name__ == "__main__":
    for file_path in glob.glob(os.path.join("screens", "*.kv")):
        with open(file_path, 'r', encoding='utf-8') as file:
            Builder.load_string(file.read())

    main_app = MainApp()
    main_app.run()
