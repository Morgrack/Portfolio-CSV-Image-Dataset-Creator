#PYTHON LIBRARIES
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, InstructionGroup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from functools import partial
from os import listdir, startfile
from os.path import exists, realpath

#PROMPT
class Prompt(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.add_widget(Widget(size_hint=(None, 1), size=(50, 0)))
        boring_boxlayout = BoxLayout(orientation='vertical')
        very_boring_boxlayout = BoxLayout(size_hint=(1, None), size=(0, 350), spacing=30, orientation='vertical')
        self.input_path = TextInput(size_hint=(1, None), size=(0,30), hint_text = 'Image collection path')
        self.output_path = TextInput(size_hint=(1, None), size=(0,30), hint_text = 'CSV output path')
        self.set = TextInput(size_hint=(1, None), size=(0,30), hint_text = 'Set i.e. TEST, TRAINING, VALIDATION')
        self.label = TextInput(size_hint=(1, None), size=(0,30), hint_text = 'Label')
        boring_button = Button(background_normal='', background_color=(0.1, 0.025, 0.2), size_hint=(None, None), size=(150,75), font_size=20, text = 'Proceed')
        boring_button.bind(on_press = self.proceed)
        boring_anchor = (AnchorLayout(size_hint=(1, None), size=(0,75), anchor_y='center', anchor_x='center'))
        boring_anchor.add_widget(boring_button)
        very_boring_boxlayout.add_widget(self.input_path)
        very_boring_boxlayout.add_widget(self.output_path)
        very_boring_boxlayout.add_widget(self.set)
        very_boring_boxlayout.add_widget(self.label)
        very_boring_boxlayout.add_widget(boring_anchor)
        boring_boxlayout.add_widget(Widget())
        boring_boxlayout.add_widget(Label(text='CSVIDC', halign='center', valign='center', font_size=50, size_hint=(1, None), size=(0, 60)))
        boring_boxlayout.add_widget(Label(text='Comma Separated Values Image Dataset Creator', halign='center', valign='center', font_size=20, size_hint=(1, None), size=(0, 30)))
        boring_boxlayout.add_widget(very_boring_boxlayout)
        boring_boxlayout.add_widget(Widget())
        self.add_widget(boring_boxlayout)
        self.add_widget(Widget(size_hint=(None, 1), size=(50, 0)))
    def proceed(self, *args):
        if exists(self.input_path.text) and exists(self.output_path.text):
            self.parent.start(self.input_path.text, self.output_path.text, self.set.text, self.label.text)
        else:
            print('Please enter valid paths.')
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.05, 0.4)
            Rectangle(pos = self.pos, size = self.size)
    def on_pos(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.05, 0.4)
            Rectangle(pos = self.pos, size = self.size)

#CURRENT IMAGE
class CurrentImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False
        self.touches = []
        self.squares = []
        self.obj = None
    def draw_square(self, touch):
        if len(self.touches) > 0:
            bottom_left = (min(self.touches[-1][0][0], touch[0]), min(self.touches[-1][0][1], touch[1]))
            top_right = (max(self.touches[-1][0][0], touch[0]), max(self.touches[-1][0][1], touch[1]))
            rect_size = ((top_right[0] - bottom_left[0]), (top_right[1] - bottom_left[1]))
            if self.obj is not None:
                self.canvas.remove(self.obj)
            self.obj = InstructionGroup()
            self.obj.add(Color(0.2, 0.05, 0.4, 0.5))
            self.obj.add(Rectangle(pos=bottom_left, size=rect_size))
    def clear_canvas(self, *args):
        for square in self.squares:
            self.canvas.remove(square)
    def on_touch_down(self, touch):
        self.touches.append([touch.pos])
        if len(self.squares) > 0:
            self.parent.remove_buttons()
    def on_touch_move(self, touch):
        self.draw_square(touch.pos)
        self.canvas.add(self.obj)
    def on_touch_up(self, touch):
        if self.obj is not None:
            self.touches[-1].append(touch.pos)
            print(self.touches)
            self.squares.append(self.obj)
            self.obj = None
            self.parent.add_buttons()

#WORKPLACE
class Workplace(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = Prompt()
        self.add_widget(self.prompt)
        self.button_container = RelativeLayout()
        button_subcontainer = BoxLayout(size_hint=(1, None), size=(0, 100), pos_hint={'y': 0.15})
        self.confirm_button = Button(text='Confirm', background_normal='', background_color=(0, 0.4, 0.1), font_size=20, size_hint=(None, 1), size=(100, 0))
        self.clear_button = Button(text='Clear', background_normal='', background_color=(0.4, 0, 0.1), font_size=20, size_hint=(None, 1), size=(100, 0))
        self.confirm_button.bind(on_press=self.next_image)
        self.clear_button.bind(on_press=self.clear_canvas)
        button_subcontainer.add_widget(Widget())
        button_subcontainer.add_widget(self.confirm_button)
        button_subcontainer.add_widget(Widget())
        button_subcontainer.add_widget(self.clear_button)
        button_subcontainer.add_widget(Widget())
        self.button_container.add_widget(button_subcontainer)
        self.top_left_container = AnchorLayout(anchor_x='left', anchor_y='top')
        top_left_subcontainer = BoxLayout(size_hint=(None, None), size=(100, 50))
        self.counter = Label(text='0/0', color=(0.2, 0.05, 0.4))
        self.back_button = Button(text='<-', background_normal='', background_color=(0.2, 0.05, 0.4))
        self.back_button.bind(on_press=self.previous_image)
        top_left_subcontainer.add_widget(self.back_button)
        top_left_subcontainer.add_widget(self.counter)
        self.top_left_container.add_widget(top_left_subcontainer)
    def start(self, *args):
        self.input_path = args[0]
        self.output_path = args[1]
        self.set = 'set' if args[2] == '' else args[2]
        self.label = 'label' if args[3] == '' else args[3]
        self.input_path_ld = listdir(self.input_path)
        if len(self.input_path_ld) == 0:
            print('The input path is empty, please enter a valid input path')
        else:
            self.remove_widget(self.prompt)
            self.image_no = 0
            self.csv = []
            self.subject_image = CurrentImage()
            self.subject_image.source = self.input_path + '/' + self.input_path_ld[self.image_no]
            self.counter.text='{}/{}'.format(self.image_no + 1, len(self.input_path_ld))
            self.add_widget(self.subject_image, 2)
            self.add_widget(self.top_left_container, 0)
    def next_image(self, *args):
        self.csv.append(('checkpoint', self.image_no))
        for square in self.subject_image.touches:
            x0 = round(square[0][0] / self.size[0], 6)
            y0 = round(1 - square[0][1] / self.size[1], 6)
            x1 = round(square[1][0]  / self.size[0], 6)
            y1 = round(1 - square[1][1] / self.size[1], 6)
            self.csv.append('{},{},{},{},{},,,{},{},,\n'.format(self.set, self.input_path + '/' + self.input_path_ld[self.image_no], self.label, str(x0), str(y0), str(x1), str(y1)))
        if self.image_no == len(self.input_path_ld) - 1:
            result = open(self.output_path + '/result.csv', 'w')
            for line in self.csv:
                if type(line) is not tuple:
                    result.write(line)
            result.close()
            startfile(realpath(self.output_path))
            self.remove_widget(self.button_container)
            self.remove_widget(self.top_left_container)
            self.remove_widget(self.subject_image)
            self.prompt = Prompt()
            self.add_widget(self.prompt)
        else:
            self.remove_widget(self.button_container)
            self.remove_widget(self.subject_image)
            self.subject_image = CurrentImage()
            self.image_no += 1
            self.subject_image.source = self.input_path + '/' + self.input_path_ld[self.image_no]
            self.add_widget(self.subject_image, 2)
            self.counter.text='{}/{}'.format(self.image_no + 1, len(self.input_path_ld))
        print(self.csv)
    def previous_image(self, *args):
        if self.image_no == 0:
            self.csv = []
            self.remove_widget(self.subject_image)
            self.remove_widget(self.top_left_container)
            self.remove_widget(self.button_container)
            self.prompt = Prompt()
            self.add_widget(self.prompt)
        else:
            self.image_no -= 1
            self.csv = self.csv[:self.csv.index(('checkpoint', self.image_no))]
            self.remove_widget(self.button_container)
            self.remove_widget(self.subject_image)
            self.subject_image = CurrentImage()
            self.subject_image.source = self.input_path + '/' + self.input_path_ld[self.image_no]
            self.add_widget(self.subject_image, 2)
            self.counter.text='{}/{}'.format(self.image_no + 1, len(self.input_path_ld))
        print(self.csv)
    def clear_canvas(self, *args):
        self.subject_image.clear_canvas()
        self.subject_image.touches = []
        self.remove_widget(self.button_container)
    def add_buttons(self, *args):
        self.add_widget(self.button_container, 1)
    def remove_buttons (self, *args):
        self.remove_widget(self.button_container)

#BUILD
class CSVIDC(App):
    def build(self):
        return Workplace()

#RUN
if __name__ == '__main__':
    CSVIDC().run()
