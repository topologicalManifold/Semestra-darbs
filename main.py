import os
import glob

from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
import kivy.properties as properties



class MainScreen(Screen):
    pass



class MainApp(MDApp):
    main_text_color = properties.ColorProperty(None)
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.title = "Lēts Photoshop"

        self.screen_manager = ScreenManager()
        self.main_screen = MainScreen(name="main_screen")
        self.screen_manager.add_widget(self.main_screen)
        return self.screen_manager



    def update_text_color(self):
        if self.theme_cls.theme_style == "Dark":
            self.main_text_color = (1, 1, 1, 1)
        else:
            self.main_text_color = (0, 0, 0, 1)



if __name__ == "__main__":
    for file_path in glob.glob(os.path.join("screens", "*.kv")):
        with open(file_path, 'r', encoding='utf-8') as file:
            Builder.load_string(file.read())
    main_app = MainApp()
    main_app.run()
