import customtkinter
import tkinter
import threading
import simpleaudio
from tkinter import filedialog

class Options_slider_frame(customtkinter.CTkFrame):
    def __init__(self, top_level, default_value, time_string):
        self.new_time = tkinter.IntVar(value=default_value)
        self.new_time_string = tkinter.StringVar()
        self.new_time_string.set(time_string+str(self.new_time.get()))
        self.time_string_default = time_string

        super().__init__(top_level)

        self.label = customtkinter.CTkLabel(self,
                                            textvariable=self.new_time_string,
                                            text_font=('Arial', 12))
        self.label.pack(side='top', pady=(5,0))

        self.slider = customtkinter.CTkSlider(self, 
                                              height=20,
                                              from_=0, 
                                              to=120,
                                              variable=self.new_time,
                                              command=self.change_slider,
                                              number_of_steps=24)
        self.slider.pack(side='left', padx=10, pady=10)
        
    def change_slider(self, *args):
        self.new_time_string.set(self.time_string_default+str(self.new_time.get()))


class Options_toplevel():
    def __init__(self, root):
        self.root = root
        top_level = customtkinter.CTkToplevel() 
        top_level.title("Options")

        self.study_frame = Options_slider_frame(top_level, default_value=50, time_string="Study time: ")
        self.break_frame = Options_slider_frame(top_level, default_value=10, time_string="Break time: ")
        self.study_frame.pack(pady=(30, 0), padx=30)
        self.break_frame.pack(pady=(30, 0), padx=30)
        
        self.upload_music = customtkinter.CTkButton(top_level, 
                                                    text="Add music",
                                                    fg_color="#de333e",
                                                    hover_color="#b02c35",
                                                    command=self.add_music)
        self.upload_music.pack(pady=(30,0), padx=30)

        self.submit_button = customtkinter.CTkButton(top_level, text="Submit", command=self.submit)
        self.submit_button.pack(pady=(30,30), padx=30)

    def add_music(self):
        filetypes = (('wav files', '*.wav'),)
        filename = filedialog.askopenfilename(title='Pick your song',
                                                      initialdir='.',
                                                      filetypes=filetypes)
        if filename:
            print(filename)
            self.root.timer.wave_obj = simpleaudio.WaveObject.from_wave_file(filename)        

    def submit(self):
        # (0, 0, 0, h, m, s, 0, 0, 0)
        study_minutes = self.study_frame.new_time.get()
        break_minutes = self.break_frame.new_time.get()
        study_time = (0, 0, 0, int(study_minutes/60), study_minutes, 0, 0, 0, 0)
        break_time = (0, 0, 0, int(break_minutes/60), break_minutes, 0, 0, 0, 0)
        self.root.timer.update_times(study_time, break_time)
        if threading.active_count() == 1:
            self.root.start_countdown()
            self.root.switch.configure(state='normal')
            

