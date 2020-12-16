import os
import glob
import json

from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
import kivy.properties as properties
from kivy.uix.rst import RstDocument
# load config file
with open("config.json", 'r') as config_file:
    data = json.load(config_file)

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

        self.about_screen = AboutScreen(name="about")
        self.screen_manager.add_widget(self.about_screen)

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
        pass
    
    def open_file_and_set_image_screen(self):
        pass

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
    
    def open_start_screen_and_save_settings(self):
        self.screen_manager.current = "main"
        data["theme"] = self.theme_cls.theme_style
        self.write_data_to_config_file()

    def open_main_screen(self):
        self.screen_manager.current = "main"
    
if __name__ == "__main__":
    for file_path in glob.glob(os.path.join("screens", "*.kv")):
        with open(file_path, 'r', encoding='utf-8') as file:
            Builder.load_string(file.read())

    main_app = MainApp()
    main_app.run()
