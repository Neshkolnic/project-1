from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from plyer import filechooser
from kivy.clock import Clock
from PyPDF2 import PdfReader

import aspose.words as aw
import os
import xml.etree.ElementTree as ET

class TextReaderApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_path = None
        self.words_per_minute = 0
        self.words = []
        self.content = ''
        self.index = 0
        self.button_Pressed = False
        self.button_Pressed1 = False


    def build(self):
        layout = BoxLayout(orientation='vertical', size=(360, 640))
        file_button = Button(text='Select File', size_hint=(0.5, 0.7), pos_hint={"center_x": 0.5, "center_y": 0.5},
                             font_size=50)
        file_button.bind(on_release=self.select_file)
        layout.add_widget(file_button)

        global speed_label
        speed_label = Label(font_size=50)
        layout.add_widget(speed_label)

        global speed_input
        speed_input = Label( size_hint=(0.125, 0.4), pos_hint={"center_x": 0.5, "center_y": 0.5},
                                font_size=50, text='0' )
        layout.add_widget(speed_input)

        start_button = Button(text='Start', on_press=self.start_reading)
        layout.add_widget(start_button)


        global pause_button
        pause_button = Button(text='Pause', on_press=self.pause_reading)
        layout.add_widget(pause_button)

        global slider_button
        slider_button = Slider(min=0, max=1000, value=0)
        slider_button.bind(value=self.on_value_change)
        layout.add_widget(slider_button)

        global label1
        label1 = Label()
        layout.add_widget(label1)

        return layout

    def presed(self, dt):
        if self.button_Pressed:
            self.button_Pressed = False
            self.words = []

        else:
            self.button_Pressed = True
            self.words = self.content.split()
            self.button_Pressed1 = True


    def on_value_change(self, instance, value):
        speed_input.text = str(int(round(value, -1)))

    def select_file(self, instance):
        label1.text = 'Файл открыт'
        #Popup(title='Уведомление', content=Label(text='Получено новое сообщение')).open()
        filechooser.open_file(on_selection=self.on_file_selected, filters=[('*.pdf'),('*.txt'),('*.docx'),('*fb2')])


    def on_file_selected(self, selection):

        if selection:
            self.file_path = selection[0]
            if self.file_path:

                if self.file_path[-3:] == 'pdf':
                    reader = PdfReader(self.file_path)
                    num_pages = len(reader.pages)
                    for i in range(num_pages):
                        self.content = self.content + reader.pages[i].extract_text()
                if self.file_path[-3:] == 'txt':
                    with open(self.file_path, 'r', encoding='utf-8') as file:
                        self.content = file.read()
                if self.file_path[-4:] == 'docx':
                    os.remove("Output.txt")
                    doc = aw.Document(self.file_path)
                    doc.save("Output.txt")
                    with open("Output.txt", 'r', encoding='utf-8') as file:
                        self.content = file.read()
                if self.file_path[-3:] == 'fb2':
                    if os.path.exists("Outputfb2.txt"):
                        os.remove("Outputfb2.txt")
                    tree = ET.parse(self.file_path)
                    root = tree.getroot()
                    with open("Outputfb2.txt", "w", encoding="utf-8") as txt:
                        for element in root.iter():
                            if element.tag.endswith('p') and element.text is not None:
                                 txt.write(element.text)
                    with open("Outputfb2.txt", 'r', encoding='utf-8') as file:
                        self.content = file.read()


             # надо сделать чтобы тут происходило открытие файла а не при нажатии на старт
    def start_reading(self, instance):
        self.index = 0
        Clock.unschedule(self.show_next_word)
        if len(self.content) > 0:
            self.words_per_minute = slider_button.value

            if self.button_Pressed:
                self.button_Pressed = False
                self.words = []
            else:
                self.button_Pressed = True
                self.words = self.content.split()

            #self.words = self.content.split()
            global words_per_second
            words_per_second = self.words_per_minute / 60.0

            global interval
            try:
                interval = 1 / words_per_second

                Clock.schedule_interval(self.show_next_word, interval)
            except:
                pass

    def show_next_word(self, dt):
        if self.words:

            word = self.words.pop(0)
            self.index = self.index + 1

            speed_label.text = word
            #print(word)  # Здесь можно изменить вывод текста

        else:
         Clock.unschedule(self.show_next_word)



    def pause_reading(self, dt):
       if self.button_Pressed:
        if not self.button_Pressed1:
            self.button_Pressed1 = True
            self.words = []
            pause_button.text = "Continue"
            Clock.unschedule(self.show_next_word)


        else:
            Clock.unschedule(self.show_next_word)
            self.button_Pressed1 = False
            self.words = self.content.split()
            self.words = self.words[self.index:]

            pause_button.text = "Pause"
            interval = 1 / (int(speed_input.text)/60)

            Clock.schedule_interval(self.show_next_word, interval)


if __name__ == '__main__':
    TextReaderApp().run()
