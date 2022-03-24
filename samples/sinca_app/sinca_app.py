#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.1.beta"

import logging
log = logging.getLogger(__name__)

from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '200')

from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from sisnet.sinca import compress, decompress
from sisnet.sinca import __version__ as sinca_version

class SincaWindow(GridLayout):
    """Main GUI Screen widgets definition"""

    def on_press_button_clear_encoded(self, button):
        if self.textinput_encoded.text == "":
            self.textinput_encoded.text = "530C8003FE3FDC0|A23FF401BFF0|63FB397BBB95BA3B97F091D40*CA"
        else:
            self.textinput_encoded.text = ""

    def on_press_button_clear_decoded(self, button):
        if self.textinput_decoded.text == "":
            self.textinput_decoded.text = "530C8003FE3FDC000000000023FF401BFF0000003FB397BBB95BA3B97F091D40"
        else:
            self.textinput_decoded.text = ""

    def on_press_button_encode(self, instance):
        encoded_message = compress(self.textinput_decoded.text)
        if encoded_message == -1:
            self.textinput_encoded.text = "Error encoding message. Please check input."
        else:
            self.textinput_encoded.text = encoded_message

    def on_press_button_decode(self, instance):
        decoded_message = decompress(self.textinput_encoded.text)
        if decoded_message == -1:
            self.textinput_decoded.text = "Error decoding message. Please check input."
        else:
            self.textinput_decoded.text = decoded_message

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # Main window grid layout
        self.cols = 1
        self.padding = 0
        self.row_force_default = True,
        self.row_default_height = 90
        self.col_force_default = True,
        self.col_default_width = 700

        # Colors
        red = (1, 0, 0, 1)
        green = (0, 1, 0, 1)
        blue = (0, 0, 1, 1)

        # Fonts and sizes
        font_size = 32
        buttons_height = 50

        # Secondary grids
        self.encoded_message = GridLayout(cols=1)
        self.encoded_buttons = GridLayout(cols=3)
        self.decoded_message = GridLayout(cols=1)
        self.decoded_buttons = GridLayout(cols=3)

        # Labels
        self.label_encoded = Label(
            text = "Encoded MSG",
            size_hint_y  = None,
            height = buttons_height,
        )
        self.label_decoded = Label(
            text = "Decoded  MSG",
            size_hint_y  = None,
            height = buttons_height,
        )

        # TextInputs
        self.textinput_encoded = TextInput(
            text = "530C8003FE3FDC0|A23FF401BFF0|63FB397BBB95BA3B97F091D40*CA",
            font_size = font_size,
        )
        self.textinput_decoded = TextInput(
            text = "530C8003FE3FDC000000000023FF401BFF0000003FB397BBB95BA3B97F091D40",
            font_size = font_size,
        )

        # Buttons
        self.button_clear_encoded = Button(
            text = "Clear/Load",
            font_size = font_size,
            size_hint_y  = None,
            height = buttons_height,
        )
        self.button_clear_encoded.bind(on_press=self.on_press_button_clear_encoded)

        self.button_clear_decoded = Button(
            text = "Clear/Load",
            font_size = font_size,
            size_hint_y  = None,
            height = buttons_height
        )
        self.button_clear_decoded.bind(on_press=self.on_press_button_clear_decoded)

        self.button_encode = Button(
            text = "ENCODE",
            background_color = blue,
            font_size = font_size,
            size_hint_y  = None,
            height = buttons_height
        )
        self.button_encode.bind(on_press=self.on_press_button_encode)

        self.button_decode = Button(
            text = "DECODE",
            background_color = green,
            font_size = font_size,
            size_hint_y  = None,
            height = buttons_height
        )
        self.button_decode.bind(on_press=self.on_press_button_decode)


        # Adding the encoded message and its buttons
        self.add_widget(self.encoded_message)
        self.encoded_message.add_widget(self.textinput_encoded)
        self.add_widget(self.encoded_buttons)
        self.encoded_buttons.add_widget(self.button_clear_encoded)
        self.encoded_buttons.add_widget(self.label_encoded)
        self.encoded_buttons.add_widget(self.button_decode)

        # Adding the decoded message and its buttons
        self.add_widget(self.decoded_message)
        self.decoded_message.add_widget(self.textinput_decoded)
        self.add_widget(self.decoded_buttons)
        self.decoded_buttons.add_widget(self.button_clear_decoded)
        self.decoded_buttons.add_widget(self.label_decoded)
        self.decoded_buttons.add_widget(self.button_encode)


class SincaApp(App):
    """GUI application for Sinca"""

    def build(self):
        self.title = "Sinca App v" + __version__ + " / Sinca module v" + sinca_version
        return SincaWindow()

if __name__ == "__main__":
    log.debug("Launching Application")
    SincaApp().run()
