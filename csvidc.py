#PYTHON LIBRARIES
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from functools import partial
from os import listdir
from os.path import exists

#PROMPT
class Prompt(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.input_path = TextInput(hint_text = "Input path ...")
        self.output_path = TextInput(hint_text = "Output path ...")
        boring_button = Button(text = "Proceed")
        boring_button.bind(on_press = self.proceed)
        self.add_widget(self.input_path)
        self.add_widget(self.output_path)
        self.add_widget(boring_button)
    def proceed(self, *args):
        if exists(self.input_path.text) and exists(self.output_path.text):
            self.parent.start(self.input_path.text, self.output_path.text)
        else:
            print("Please enter valid paths.")

#CURRENT IMAGE
class currentImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False
        self.touches = []
    def on_touch_down(self, touch):
        self.touches.append(touch.pos)
        if len(self.touches) == 2:
            bottom_left = (min(self.touches[0][0], self.touches[1][0]), min(self.touches[0][1], self.touches[1][1]))
            top_right = (max(self.touches[0][0], self.touches[1][0]), max(self.touches[0][1], self.touches[1][1]))
            rect_size = ((top_right[0] - bottom_left[0]), (top_right[1] - bottom_left[1]))
            with self.canvas:
                Color(0, 0, 0, 0.5)
                Rectangle(pos = bottom_left, size = rect_size)
            Clock.schedule_once(partial(self.parent.nextImage, self.touches[:2]), 0.1)

#WORKPLACE
class Workplace(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = Prompt()
        self.add_widget(self.prompt)
    def start(self, *args):
        self.input_path = args[0]
        self.output_path = args[1]
        self.input_path_ld = listdir(self.input_path)
        if len(self.input_path_ld) == 0:
            print("The input path is empty, please enter a valid input path")
        else:
            self.remove_widget(self.prompt)
            self.image_no = 0
            self.csv = []
            self.subject_image = currentImage()
            self.subject_image.source = self.input_path + "/" + self.input_path_ld[self.image_no]
            self.add_widget(self.subject_image)
    def nextImage(self, *args):
        print(args[0])
        x0 = round(args[0][0][0] / self.size[0], 6)
        y0 = round(1 - args[0][0][1] / self.size[1], 6)
        x1 = round(args[0][1][0] / self.size[0],6)
        y1 = round(1 - args[0][1][1] / self.size[1], 6)
        print(x0,y0)
        print(x1,y1)
        if self.image_no == len(self.input_path_ld) - 1:
            self.csv.append("<set>," + self.input_path + "/" + self.input_path_ld[self.image_no] + ",<label>," + str(x0) + "," + str(y0) + ",,," + str(x1) + "," + str(y1) + ",,\n")
            result = open(self.output_path + "/result.csv", "w")
            for line in self.csv:
                result.write(line)
            result.close()
            self.remove_widget(self.subject_image)
            self.prompt = Prompt()
            self.add_widget(self.prompt)
        else:
            self.csv.append("<set>," + self.input_path + "/" + self.input_path_ld[self.image_no] + ",<label>," + str(x0) + "," + str(y0) + ",,," + str(x1) + "," + str(y1) + ",,\n")
            self.image_no = self.image_no + 1
            self.remove_widget(self.subject_image)
            self.subject_image = currentImage()
            self.subject_image.source = self.input_path + "/" + self.input_path_ld[self.image_no]
            self.add_widget(self.subject_image)

#BUILD
class CSVIDC(App):
    def build(self):
        return Workplace()

#RUN
if __name__ == '__main__':
    CSVIDC().run()
